"""The orchestrator: one instruction in, a reviewed, traced, merge-ready draft PR out.

It is a resumable state machine. Every transition is appended to the run log first;
`state.json` is a cache that `replay()` can rebuild. Stages run as Devin child
sessions through a SessionBackend; human gates are read through a GateProvider.
Bounded feedback loops escalate to NEEDS-HUMAN when the limit is hit."""

from __future__ import annotations

import json
import re
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import checks
from .brief import compile_brief, write_brief
from .config import HarnessConfig
from .gates import GateDecision, GateProvider, provider_from_config
from .kpis import compute as compute_kpis
from .runlog import RunLog, now
from .sessions.base import SessionBackend, SessionRequest, SessionResult
from .sessions.relay import AwaitingSession
from .standards import StandardMissing, StandardsStore
from .trace import TraceMatrix
from .verdicts import VERDICT_SCHEMA, Verdict

FEATURE_PLAN = ["specify", "gate:after-specify", "decompose", "design-architect-loop", "gate:after-architect",
                "coding-waves", "integrate", "document", "trace", "gate:before-merge", "release", "finish"]
RCA_PLAN = ["explore-evaluate-loop", "review", "gate:after-review", "fix-wave", "integrate", "document", "trace",
            "gate:before-merge", "finish"]

STAGE_STANDARDS_DEFAULT = {  # which standards each stage must load; harness.yaml may extend
    "specify": ["STD-REQ"], "decompose": ["STD-REQ"], "design": ["STD-ARCH"], "architect": ["STD-ARCH"],
    "coding": ["STD-CODE", "STD-SAFETY"], "qa": ["STD-QA", "STD-SAFETY"], "integrate": ["STD-GOV"],
    "document": ["STD-DOC"], "trace": ["STD-REQ", "STD-GOV"], "release": ["STD-GOV"],
    "explore": ["STD-RCA"], "evaluate": ["STD-RCA"], "review": ["STD-RCA", "STD-SAFETY"],
    "fix": ["STD-CODE", "STD-SAFETY"],
}


class Paused(Exception):
    """The run is waiting on something outside the orchestrator (human or session)."""

    def __init__(self, reason: str, detail: dict[str, Any] | None = None):
        super().__init__(reason)
        self.reason, self.detail = reason, detail or {}


@dataclass
class Orchestrator:
    cfg: HarnessConfig
    run_dir: Path
    backend: SessionBackend
    standards: StandardsStore
    skills_dir: Path
    gate_factory: Any = None            # callable(gates_cfg, run_dir, gate) -> GateProvider
    target_clone: Path | None = None    # local clone of the target repo for deterministic verification
    verify_commands: bool = True

    # ------------------------------------------------------------------ lifecycle
    def __post_init__(self) -> None:
        self.run_dir = Path(self.run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.log = RunLog(self.run_dir / "runlog.jsonl")
        self.state_path = self.run_dir / "state.json"
        self.state: dict[str, Any] = json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        self.trace = TraceMatrix(self.run_dir / "trace.json", self.cfg.requirement_id_pattern)
        self.gate_factory = self.gate_factory or provider_from_config

    def start(self, workflow: str, requirement: str, requirement_ref: str, run_id: str | None = None,
              story_points: float = 1.0) -> str:
        if self.state:
            raise RuntimeError("run already started; use resume()")
        run_id = run_id or f"run-{now()[:10]}-{uuid.uuid4().hex[:6]}"
        self.state = {
            "run_id": run_id, "workflow": workflow, "requirement": requirement, "requirement_ref": requirement_ref,
            "plan": list(FEATURE_PLAN if workflow == "feature" else RCA_PLAN), "cursor": 0, "attempts": {},
            "artifacts": {}, "units": [], "waves_done": [], "questions": [], "answers": [], "loops": {},
            "gates": {}, "status": "running", "story_points": story_points, "prs": [], "branches": [],
            "verify_results": {},
        }
        self.log.append("run.created", run_id=run_id, workflow=workflow, target_repo=self.cfg.repo,
                        requirement=requirement_ref, instruction=f"Implement according to {requirement_ref}",
                        safety_classification=self.cfg.safety_classification, models=self.cfg.models,
                        backend=self.backend.name)
        self.trace.register_requirements(requirement)
        self._save()
        return run_id

    def resume(self) -> dict[str, Any]:
        """Advance until the run finishes or pauses. Returns the state."""
        if not self.state:
            raise RuntimeError("no run to resume")
        try:
            while self.state["status"] == "running":
                step = self.state["plan"][self.state["cursor"]]
                self._execute(step)
        except Paused as p:
            self.state["paused_on"] = {"reason": p.reason, **p.detail}
            self.log.append("run.paused", reason=p.reason, **{k: v for k, v in p.detail.items() if k != "reason"})
        self._save()
        self._export()
        return self.state

    # ------------------------------------------------------------------ steps
    def _execute(self, step: str) -> None:
        if step.startswith("gate:"):
            self._gate(step.split(":", 1)[1])
        elif step == "specify":
            self._specify()
        elif step == "decompose":
            self._decompose()
        elif step == "design-architect-loop":
            self._design_architect_loop()
        elif step == "coding-waves":
            self._coding_waves()
        elif step == "explore-evaluate-loop":
            self._explore_evaluate_loop()
        elif step == "review":
            self._simple_stage("review", ok=("CONFIRMED",), artifact="review")
        elif step == "fix-wave":
            self._fix_wave()
        elif step in ("integrate", "document"):
            self._simple_stage(step, ok=("PASS",), artifact=step)
        elif step == "trace":
            self._trace_stage()
        elif step == "release":
            if (self.cfg.raw.get("release") or {}).get("enabled"):
                self._simple_stage("release", ok=("PASS",), artifact="release")
            else:
                self.log.append("stage.skipped", stage="release", reason="release.enabled is false")
                self._advance()
        elif step == "finish":
            self._finish("ready-to-merge")
        else:
            raise RuntimeError(f"unknown plan step {step}")

    def _advance(self) -> None:
        self.state["cursor"] += 1
        self._save()

    def _finish(self, status: str) -> None:
        self.state["status"] = status
        self.log.append("run.finished", status=status, prs=self.state["prs"], branches=self.state["branches"])
        self._save()
        compute_kpis(self.run_dir, story_points=self.state.get("story_points", 1.0))

    # ------------------------------------------------------------------ stage runner
    def _run_stage(self, stage: str, *, unit: dict[str, Any] | None = None, feedback: list | None = None,
                   artifacts: dict[str, Any] | None = None, evidence_only: bool = False,
                   repos: list[str] | None = None) -> Verdict:
        unit_id = unit["id"] if unit else "-"
        key_base = f"{stage}:{unit_id}"
        attempt = self.state["attempts"].get(key_base, 0) + 1
        self.state["attempts"][key_base] = attempt
        stage_key = f"{key_base}:{attempt}"
        model = self.cfg.model_for(stage)
        try:
            std_ids = (self.cfg.standards.get("by_stage") or {}).get(stage) or STAGE_STANDARDS_DEFAULT.get(stage, [])
            std_ids = sorted(set(std_ids) | set(self.cfg.standards.get("required", [])))
            standards = self.standards.load_required(std_ids)
        except StandardMissing as exc:
            self.log.append("stage.started", stage=stage, unit=unit_id, attempt=attempt, model=model, brief_ref=None)
            v = Verdict("BLOCKED", str(exc), evidence=[{"kind": "standard", "ref": sid} for sid in std_ids])
            self._complete(stage, unit_id, attempt, v, None)
            raise Paused("standard-missing", {"stage": stage, "missing": str(exc)}) from exc
        skill_text = self._skill_text(stage)
        brief = compile_brief(stage=stage, cfg=self.cfg, run_id=self.state["run_id"], attempt=attempt,
                              skill_text=skill_text, standards=standards, artifacts=artifacts or {},
                              requirement=self.state["requirement"], feedback=feedback, unit=unit,
                              answers=self.state["answers"], model=model, evidence_only=evidence_only)
        brief_path = write_brief(self.run_dir, stage_key, brief)
        self.log.append("stage.started", stage=stage, unit=unit_id, attempt=attempt, model=model,
                        brief_ref=str(brief_path.relative_to(self.run_dir)), standards=[s.id for s in standards],
                        artifacts_read=sorted((artifacts or {}).keys()), evidence_only=evidence_only)
        request = SessionRequest(
            title=f"[{self.state['run_id']}] {stage} {unit_id if unit else ''} #{attempt}".strip(),
            prompt=brief, repos=[] if evidence_only else (repos or [self.cfg.repo]), devin_mode=model,
            structured_output_schema=VERDICT_SCHEMA, tags=["agentic-sdlc", self.state["run_id"], stage],
            max_acu_limit=int((self.cfg.raw.get("limits") or {}).get("max_acu_per_stage", 15)))
        try:
            result = self.backend.run(request, run_dir=self.run_dir, stage_key=stage_key)
        except AwaitingSession as exc:
            # roll back the attempt counter: nothing happened yet
            self.state["attempts"][key_base] = attempt - 1
            self._save()
            raise Paused("awaiting-session", {"stage": stage, "unit": unit_id, "attempt": attempt,
                                              "request": str(exc.request_path.relative_to(self.run_dir))}) from exc
        verdict = self._verdict_from(result, stage)
        self._complete(stage, unit_id, attempt, verdict, result)
        return verdict

    def _verdict_from(self, result: SessionResult, stage: str) -> Verdict:
        if not result.structured_output:
            return Verdict("INSUFFICIENT_EVIDENCE" if stage in ("evaluate", "qa") else "FAIL",
                           f"session ended with status {result.status} and no structured output",
                           evidence=[{"kind": "session", "ref": result.session_url}])
        try:
            v = Verdict.from_dict(result.structured_output)
        except Exception as exc:  # schema violation is a FAIL with the violation as evidence
            return Verdict("FAIL", f"structured output violated the verdict schema: {exc}"[:500],
                           evidence=[{"kind": "session", "ref": result.session_url}])
        if not v.allowed_for(stage):
            v = Verdict("FAIL", f"stage {stage} emitted disallowed verdict {v.verdict}: {v.summary}",
                        evidence=v.evidence)
        v.session_url = v.session_url or result.session_url
        v.model = v.model or result.devin_mode
        return v

    def _complete(self, stage: str, unit_id: str, attempt: int, v: Verdict, result: SessionResult | None) -> None:
        rows = 0
        if v.trace:
            try:
                rows = self.trace.append(stage, v.trace)
            except ValueError as exc:
                v.evidence.append({"kind": "note", "ref": "trace-rejected", "detail": str(exc)})
        if v.pr_url and v.pr_url not in self.state["prs"]:
            self.state["prs"].append(v.pr_url)
        if v.branch and v.branch not in self.state["branches"]:
            self.state["branches"].append(v.branch)
        self.log.append("stage.completed", stage=stage, unit=unit_id, attempt=attempt, verdict=v.verdict,
                        summary=v.summary, evidence=v.evidence, questions=v.questions,
                        artifacts_produced=sorted(v.artifacts.keys()), files_touched=v.files_touched,
                        standards_loaded=v.standards_loaded, session_url=v.session_url, model=v.model,
                        acus=result.acus if result else 0, pr_url=v.pr_url, branch=v.branch)
        if rows:
            self.log.append("trace.appended", stage=stage, rows=rows, coverage=self.trace.coverage()["test_coverage"])
        for q in v.questions:
            if q["id"] not in {x["id"] for x in self.state["questions"]}:
                self.state["questions"].append({**q, "stage": stage, "status": "open"})
        for name, art in v.artifacts.items():
            self.state["artifacts"][f"{stage}.{name}" if unit_id == "-" else f"{stage}.{unit_id}.{name}"] = art
        self._save()

    def _skill_text(self, stage: str) -> str:
        p = self.skills_dir / stage / "SKILL.md"
        if not p.exists():
            raise FileNotFoundError(f"stage skill missing: {p}")
        contract = self.skills_dir / "CONTRACT.md"
        return (contract.read_text() + "\n\n" if contract.exists() else "") + p.read_text()

    # ------------------------------------------------------------------ feature stages
    def _specify(self) -> None:
        feedback = self.state.get("feedback", {}).pop("specify", None)
        v = self._run_stage("specify", artifacts=self._arts("gate"), feedback=feedback)
        if v.verdict == "PASS":
            spec = v.artifacts.get("specification") or v.summary
            self.state["artifacts"]["specification"] = spec
            self.trace.register_requirements(spec if isinstance(spec, str) else json.dumps(spec))
            self._advance()
            return
        open_q = [q for q in self.state["questions"] if q["status"] == "open"]
        if v.verdict == "BLOCKED" and open_q:
            raise Paused("questions-open", {"stage": "specify", "questions": [q["id"] for q in open_q]})
        raise Paused("needs-human", {"stage": "specify", "summary": v.summary})

    def _decompose(self) -> None:
        v = self._run_stage("decompose", artifacts=self._arts("specification"))
        units = v.artifacts.get("units")
        if isinstance(units, str):
            units = json.loads(units)
        if v.verdict != "PASS" or not units:
            raise Paused("needs-human", {"stage": "decompose", "summary": v.summary})
        for u in units:
            u.setdefault("depends_on", [])
            u.setdefault("files", ["**"])
        self.state["units"] = units
        self.state["artifacts"]["units"] = units
        self._advance()

    def _design_architect_loop(self) -> None:
        limit = self.cfg.loops["architect"]
        feedback = None
        for i in range(1, limit + 1):
            d = self._run_stage("design", artifacts=self._arts("specification", "units"), feedback=feedback)
            if d.verdict != "PASS":
                raise Paused("needs-human", {"stage": "design", "summary": d.summary})
            self.state["artifacts"]["design"] = d.artifacts.get("design") or d.summary
            a = self._run_stage("architect", artifacts=self._arts("specification", "units", "design"))
            resolved = a.verdict == "CONFIRMED"
            self.log.append("loop.iteration", loop="design-architect", iteration=i, verdict=a.verdict,
                            resolved=resolved, findings=a.evidence)
            if resolved:
                self.state["artifacts"]["architecture_review"] = a.artifacts.get("review") or a.summary
                self._advance()
                return
            if a.verdict != "VIOLATION":
                raise Paused("needs-human", {"stage": "architect", "summary": a.summary})
            feedback = [{"from": "architect", "iteration": i, "verdict": a.verdict, "summary": a.summary,
                         "findings": a.evidence, "review": a.artifacts.get("review")}]
        self.log.append("loop.escalated", loop="design-architect", iterations=limit)
        raise Paused("needs-human", {"stage": "architect", "reason": f"loop limit {limit} reached"})

    def _waves(self, units: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """Group units into dependency waves; units in a wave are independent."""
        done: set[str] = set()
        waves: list[list[dict[str, Any]]] = []
        remaining = list(units)
        while remaining:
            wave = [u for u in remaining if set(u.get("depends_on", [])) <= done]
            if not wave:
                raise RuntimeError("dependency cycle in units")
            waves.append(wave)
            done |= {u["id"] for u in wave}
            remaining = [u for u in remaining if u["id"] not in done]
        return waves

    def _coding_waves(self) -> None:
        blocked_units = {u for q in self.state["questions"] if q["status"] == "open" for u in q.get("blocking_units", [])}
        for wave in self._waves(self.state["units"]):
            runnable = [u for u in wave if u["id"] not in blocked_units and u["id"] not in self.state["waves_done"]]
            for u in runnable:  # independent: the relay backend fans these out as parallel child sessions
                self._coding_qa_loop(u, stage="coding")
                self.state["waves_done"].append(u["id"])
                self._save()
        skipped = [u["id"] for u in self.state["units"] if u["id"] in blocked_units]
        if skipped:
            self.log.append("units.blocked", units=skipped, reason="open questions")
            raise Paused("questions-open", {"stage": "coding", "units": skipped})
        self._advance()

    def _coding_qa_loop(self, unit: dict[str, Any], stage: str) -> None:
        limit = self.cfg.loops["qa"]
        feedback: list[dict[str, Any]] | None = None
        arts = self._arts("specification", "design", "architecture_review", "root_cause", "review")
        for i in range(1, limit + 1):
            c = self._run_stage(stage, unit=unit, artifacts=arts, feedback=feedback)
            if c.verdict == "BLOCKED":
                raise Paused("questions-open", {"stage": stage, "unit": unit["id"], "summary": c.summary})
            if c.verdict != "PASS":
                feedback = [{"from": stage, "iteration": i, "summary": c.summary, "evidence": c.evidence}]
                self.log.append("loop.iteration", loop=f"{stage}-qa", unit=unit["id"], iteration=i,
                                verdict=c.verdict, resolved=False)
                continue
            # deterministic verification — results go straight back to the next attempt
            vres = self._verify(unit, c)
            if vres["verdict"] == "FAIL":
                feedback = [{"from": "verify", "iteration": i, "checks": vres["checks"], "commands": vres["commands"]}]
                self.log.append("loop.iteration", loop=f"{stage}-qa", unit=unit["id"], iteration=i,
                                verdict="FAIL", resolved=False, source="verify")
                continue
            q = self._run_stage("qa", unit=unit, artifacts={**arts, "coding_report": c.to_dict(),
                                                            "deterministic_checks": vres})
            resolved = q.verdict == "PASS"
            self.log.append("loop.iteration", loop=f"{stage}-qa", unit=unit["id"], iteration=i,
                            verdict=q.verdict, resolved=resolved, source="qa")
            if resolved:
                return
            if q.verdict in ("BLOCKED", "INSUFFICIENT_EVIDENCE"):
                raise Paused("needs-human", {"stage": "qa", "unit": unit["id"], "summary": q.summary})
            feedback = [{"from": "qa", "iteration": i, "summary": q.summary, "evidence": q.evidence,
                         "report": q.artifacts.get("qa_report")}]
        self.log.append("loop.escalated", loop=f"{stage}-qa", unit=unit["id"], iterations=limit)
        raise Paused("needs-human", {"stage": "qa", "unit": unit["id"], "reason": f"loop limit {limit} reached"})

    def _verify(self, unit: dict[str, Any], c: Verdict) -> dict[str, Any]:
        """Deterministic checks on the branch the Coding session produced."""
        diff_text, commits, pr = "", [], {}
        commands: dict[str, Any] = {}
        if self.target_clone and c.branch:
            diff_text, commits, pr = self._fetch_branch(c.branch, c.pr_url)
            if self.verify_commands:
                commands = self._run_commands(c.branch)
        model_globs = (self.cfg.raw.get("checks") or {}).get("model_globs", ["**/models.py", "**/settings*.py"])
        results = checks.run_all(diff_text, brief_files=unit.get("files"), commit_messages=commits, pr=pr,
                                 governance=self.cfg.governance, model_globs=model_globs)
        verdict = checks.overall(results)
        if any(r.get("returncode", 0) != 0 for r in commands.values()):
            verdict = "FAIL"
        out = {"verdict": verdict, "checks": [r.to_dict() for r in results], "commands": commands,
               "branch": c.branch, "files_in_diff": [f.path for f in checks.parse_unified_diff(diff_text)]}
        self.state["verify_results"][f"{unit['id']}:{self.state['attempts'].get('coding:' + unit['id'], 0)}"] = out
        self.log.append("stage.started", stage="verify", unit=unit["id"], attempt=1, model="deterministic")
        self.log.append("stage.completed", stage="verify", unit=unit["id"], attempt=1, verdict=verdict,
                        summary=f"{sum(1 for r in results if r.verdict == 'FAIL')} check(s) failed; "
                                f"commands: {[k for k, v in commands.items() if v.get('returncode')]} failed",
                        evidence=[{"kind": "artifact", "ref": r.name, "detail": r.detail} for r in results]
                        + [{"kind": "command", "ref": k, "detail": f"rc={v.get('returncode')}"} for k, v in commands.items()],
                        model="deterministic")
        return out

    def _fetch_branch(self, branch: str, pr_url: str | None) -> tuple[str, list[str], dict[str, Any]]:
        clone = str(self.target_clone)
        subprocess.run(["git", "-C", clone, "fetch", "origin", branch, self.cfg.default_branch], check=True,
                       capture_output=True)
        diff = subprocess.run(["git", "-C", clone, "diff", f"origin/{self.cfg.default_branch}...origin/{branch}"],
                              check=True, capture_output=True, text=True).stdout
        commits = subprocess.run(["git", "-C", clone, "log", "--format=%B%x00",
                                  f"origin/{self.cfg.default_branch}..origin/{branch}"],
                                 check=True, capture_output=True, text=True).stdout.split("\x00")
        commits = [c.strip() for c in commits if c.strip()]
        pr: dict[str, Any] = {}
        if pr_url:
            try:
                out = subprocess.run(["gh", "pr", "view", pr_url, "--json", "isDraft,labels,headRefName,mergedAt"],
                                     check=True, capture_output=True, text=True).stdout
                d = json.loads(out)
                pr = {"draft": d["isDraft"], "labels": [lbl["name"] for lbl in d["labels"]],
                      "head": d["headRefName"], "merged": bool(d.get("mergedAt"))}
            except Exception as exc:  # pragma: no cover
                pr = {"error": str(exc)}
        return diff, commits, pr

    def _run_commands(self, branch: str) -> dict[str, Any]:
        clone = str(self.target_clone)
        wt = self.run_dir / "worktrees" / re.sub(r"[^A-Za-z0-9_.-]", "_", branch)
        if not wt.exists():
            subprocess.run(["git", "-C", clone, "worktree", "add", "--detach", str(wt), f"origin/{branch}"],
                           check=True, capture_output=True)
        else:
            subprocess.run(["git", "-C", str(wt), "checkout", "--detach", f"origin/{branch}"], check=True,
                           capture_output=True)
        out: dict[str, Any] = {}
        for name in ("build", "lint", "test"):
            cmd = self.cfg.commands.get(name)
            if not cmd:
                continue
            res = subprocess.run(cmd, shell=True, cwd=str(wt), capture_output=True, text=True, timeout=1800)
            out[name] = {"cmd": cmd, "returncode": res.returncode, "tail": (res.stdout + res.stderr)[-2000:]}
        return out

    # ------------------------------------------------------------------ RCA stages
    def _explore_evaluate_loop(self) -> None:
        limit = self.cfg.loops["rca"]
        feedback = None
        for i in range(1, limit + 1):
            e = self._run_stage("explore", feedback=feedback)
            if e.verdict != "PASS":
                raise Paused("needs-human", {"stage": "explore", "summary": e.summary})
            package = {"hypothesis": e.artifacts.get("hypothesis") or e.summary,
                       "evidence_package": e.artifacts.get("evidence_package") or e.evidence}
            self.state["artifacts"]["evidence_package"] = package
            ev = self._run_stage("evaluate", artifacts={"evidence_package": package}, evidence_only=True)
            resolved = ev.verdict == "CONFIRMED"
            self.log.append("loop.iteration", loop="explore-evaluate", iteration=i, verdict=ev.verdict,
                            resolved=resolved, objections=ev.evidence)
            if resolved:
                self.state["artifacts"]["root_cause"] = {"hypothesis": package["hypothesis"],
                                                         "evaluation": ev.artifacts.get("evaluation") or ev.summary}
                self._advance()
                return
            feedback = [{"from": "evaluate", "iteration": i, "verdict": ev.verdict, "summary": ev.summary,
                         "objections": ev.evidence, "constraints": "treat each objection as a constraint"}]
        self.log.append("loop.escalated", loop="explore-evaluate", iterations=limit)
        self.state["artifacts"]["retraction"] = {"reason": f"root cause not confirmed after {limit} rounds",
                                                 "last_feedback": feedback}
        self.log.append("stage.completed", stage="review", unit="-", attempt=1, verdict="RETRACTION",
                        summary=f"Published retraction: hypothesis not confirmed after {limit} rounds",
                        evidence=[], model="orchestrator")
        self._finish("retracted")

    def _fix_wave(self) -> None:
        unit = {"id": "fix", "title": "Apply the reviewed root-cause fix",
                "files": (self.cfg.raw.get("rca") or {}).get("fix_files", ["**"]), "depends_on": []}
        self.state["units"] = [unit]
        self._coding_qa_loop(unit, stage="fix")
        self._advance()

    # ------------------------------------------------------------------ generic
    def _simple_stage(self, stage: str, *, ok: tuple[str, ...], artifact: str) -> None:
        arts = self._arts("specification", "design", "root_cause", "evidence_package")
        arts["prs"] = self.state["prs"]
        arts["branches"] = self.state["branches"]
        arts["trace_matrix"] = self.trace.to_markdown()
        v = self._run_stage(stage, artifacts=arts)
        if v.verdict in ok:
            self.state["artifacts"][artifact] = v.artifacts.get(artifact) or v.summary
            self._advance()
            return
        raise Paused("needs-human", {"stage": stage, "summary": v.summary})

    def _trace_stage(self) -> None:
        cov = self.trace.coverage()
        verdict = "PASS" if cov["requirements"] and not cov["orphans"] and cov["with_test"] == cov["requirements"] else "FAIL"
        self.log.append("stage.started", stage="trace", unit="-", attempt=1, model="deterministic")
        self.log.append("stage.completed", stage="trace", unit="-", attempt=1, verdict=verdict,
                        summary=f"{cov['with_test']}/{cov['requirements']} requirements traced to tests; "
                                f"orphans: {cov['orphans'] or 'none'}",
                        evidence=[{"kind": "artifact", "ref": "trace.json"}], model="deterministic")
        (self.run_dir / "trace.md").write_text(self.trace.to_markdown())
        if verdict == "PASS":
            self._advance()
        else:
            raise Paused("needs-human", {"stage": "trace", "coverage": cov["test_coverage"], "orphans": cov["orphans"]})

    def _gate(self, gate: str) -> None:
        info = self.state["gates"].get(gate)
        meta = {"pr_url": self.state["prs"][0] if self.state["prs"] else None,
                "reviewers_required": self.cfg.reviewers_required(self._all_files_touched())}
        if gate == "before-merge" and not meta["pr_url"]:
            raise Paused("needs-human", {"gate": gate, "reason": "no draft PR recorded for the merge gate"})
        provider: GateProvider = self.gate_factory(self.cfg.gates, self.run_dir, gate)
        if not info:
            title = f"[{self.state['run_id']}] Gate: {gate}"
            body = self._gate_body(gate, meta)
            ref = provider.open(gate, title, body, meta)
            info = {"ref": ref, "opened": now(), "status": "waiting"}
            self.state["gates"][gate] = info
            self.log.append("gate.opened", gate=gate, ref=ref, reviewers_required=meta["reviewers_required"])
            self._save()
        decision: GateDecision = provider.poll(info["ref"], meta)
        if decision.decision == "waiting":
            raise Paused("gate-waiting", {"gate": gate, "ref": info["ref"], "reviewers": decision.reviewers,
                                          "reviewers_required": meta["reviewers_required"]})
        info.update(status=decision.decision, actor=decision.actor, decided=decision.at or now())
        self.log.append("gate.decided", gate=gate, decision=decision.decision, actor=decision.actor,
                        actor_type=decision.actor_type, ref=info["ref"], comment=decision.comment,
                        reviewers=decision.reviewers, reviewers_required=meta["reviewers_required"])
        if decision.decision == "approved":
            self._advance()
            return
        # rejected: send the human's comment back to the stage that produced the gated artifact
        back = {"after-specify": "specify", "after-architect": "design-architect-loop",
                "after-review": "explore-evaluate-loop", "before-merge": "coding-waves"}[gate]
        self.state.setdefault("feedback", {})["specify" if back == "specify" else back] = [
            {"from": f"human@{gate}", "actor": decision.actor, "comment": decision.comment}]
        del self.state["gates"][gate]
        self.state["cursor"] = self.state["plan"].index(back)
        self._save()

    def _gate_body(self, gate: str, meta: dict[str, Any]) -> str:
        arts = self.state["artifacts"]
        parts = [f"Run `{self.state['run_id']}` — workflow **{self.state['workflow']}** on `{self.cfg.repo}`.", "",
                 f"Requirement: {self.state['requirement_ref']}", "",
                 f"Apply **{self.cfg.gates.get('approve_label', 'gate:approved')}** or "
                 f"**{self.cfg.gates.get('reject_label', 'gate:rejected')}** (comment first if rejecting). "
                 "Only a human account may apply these labels; bot labels are ignored.", ""]
        if gate == "after-specify":
            parts += ["## Specification", "", str(arts.get("specification", ""))]
        elif gate == "after-architect":
            parts += ["## Design", "", str(arts.get("design", "")), "", "## Architecture review", "",
                      str(arts.get("architecture_review", ""))]
        elif gate == "after-review":
            parts += ["## Root cause", "", json.dumps(arts.get("root_cause", {}), indent=2), "", "## Review", "",
                      str(arts.get("review", ""))]
        parts += ["", f"Reviewers required: {meta['reviewers_required']}", "", "## Trace so far", "",
                  self.trace.to_markdown()]
        return "\n".join(parts)

    def _all_files_touched(self) -> list[str]:
        files: set[str] = set()
        for rec in self.log:
            if rec["event"] == "stage.completed":
                files |= set(rec.get("files_touched") or [])
        return sorted(files)

    def _arts(self, *names: str) -> dict[str, Any]:
        return {n: self.state["artifacts"][n] for n in names if n in self.state["artifacts"]}

    # ------------------------------------------------------------------ human actions
    def answer(self, question_id: str, answer: str, actor: str) -> None:
        for q in self.state["questions"]:
            if q["id"] == question_id:
                q.update(status="answered", answer=answer, by=actor)
                self.state["answers"].append({"id": question_id, "answer": answer, "by": actor})
                self.log.append("question.answered", question_id=question_id, answer=answer, actor=actor,
                                actor_type="User")
                self._save()
                return
        raise KeyError(question_id)

    def record_human_time(self, minutes: float, actor: str, note: str = "") -> None:
        self.log.append("human.time", minutes=minutes, actor=actor, note=note)

    # ------------------------------------------------------------------ persistence
    def _save(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2, default=str))

    def _export(self) -> None:
        """Write runs/index.json so the console can list runs without a server."""
        root = self.run_dir.parent
        entries = []
        for d in sorted(p for p in root.iterdir() if p.is_dir() and (p / "state.json").exists()):
            st = json.loads((d / "state.json").read_text())
            entries.append({"run_id": st["run_id"], "workflow": st["workflow"], "status": st["status"],
                            "target_repo": self.cfg.repo if d == self.run_dir else st.get("target_repo", ""),
                            "requirement_ref": st.get("requirement_ref"), "dir": d.name,
                            "prs": st.get("prs", []), "updated": now()})
        (root / "index.json").write_text(json.dumps(entries, indent=2))
