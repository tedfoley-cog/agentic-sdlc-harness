"""Create two offline example runs with the scripted (fake) backend so the console, the
Playwright gauntlet and CI have deterministic data. Real dry-run worked examples recorded
through Devin child sessions live alongside these under runs/ and are not overwritten.

    python tools/make_example_runs.py && harness export
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from agentic_sdlc.config import HarnessConfig
from agentic_sdlc.gates import FileGate
from agentic_sdlc.orchestrator import Orchestrator
from agentic_sdlc.sessions import FakeBackend
from agentic_sdlc.standards import MarkdownStandardsStore

ROOT = Path(__file__).resolve().parents[1]
RUNS = Path(os.environ.get("HARNESS_RUNS", ROOT / "runs"))
CFG = ROOT / "examples/targets/adms/harness.yaml"


def v(verdict: str, summary: str, **extra):
    return {"verdict": verdict, "summary": summary,
            "evidence": extra.pop("evidence", [{"kind": "note", "ref": "scripted example"}]), **extra}


def orch(run_dir: Path, script: dict) -> Orchestrator:
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    shutil.copy(CFG, run_dir / "harness.yaml")
    (run_dir / "meta.json").write_text(json.dumps({"backend": "fake", "target_clone": None, "verify_commands": False}))
    (run_dir / "fake_script.json").write_text(json.dumps(script))
    cfg = HarnessConfig.load(CFG)
    return Orchestrator(cfg=cfg, run_dir=run_dir, backend=FakeBackend(script_path=run_dir / "fake_script.json"),
                        standards=MarkdownStandardsStore(ROOT / "standards"), skills_dir=ROOT / "plugin/skills",
                        gate_factory=lambda g, d, name: FileGate(d), verify_commands=False)


def decide(run_dir: Path, gate: str, actor: str, decision="approved", comment="Reviewed the artifacts; proceed."):
    (run_dir / "gates").mkdir(exist_ok=True)
    (run_dir / "gates" / f"{gate}.decision.json").write_text(json.dumps(
        {"decision": decision, "actor": actor, "actor_type": "User", "reviewers": 2, "comment": comment}))


def feature():
    rid = "example-feature-tie-capacity"
    reqs = ["REQ-FLISR-101", "REQ-FLISR-102", "REQ-FLISR-103"]
    spec = "\n".join(f"{r} ..." for r in reqs)
    pr = "https://github.com/example-org/product-repo/pull/101"
    tr = lambda r, k, ref: {"requirement_id": r, "kind": k, "ref": ref}  # noqa: E731
    script = {
        "specify": [v("BLOCKED", "Source does not say what to do when tie-switch capacity telemetry is stale.",
                      questions=[{"id": "Q-SPEC-1", "question": "When tie capacity is stale (>30 s), refuse restoration or hold last value?", "blocking_units": ["U2"]}]),
                    v("PASS", "Specification with 3 testable requirements; stale telemetry refuses restoration (answer to Q-SPEC-1).",
                      artifacts={"specification": spec}, standards_loaded=["STD-REQ", "STD-GOV", "STD-SAFETY"])],
        "decompose": [v("PASS", "Two units; U2 depends on U1.", artifacts={"units": [
            {"id": "U1", "title": "Capacity model + guard", "depends_on": [], "files": ["backend/app/flisr.py", "backend/tests/test_flisr_capacity.py"], "requirement_ids": reqs[:2]},
            {"id": "U2", "title": "Stale telemetry refusal", "depends_on": ["U1"], "files": ["backend/app/flisr.py", "backend/tests/test_flisr_stale.py"], "requirement_ids": reqs[2:]}]})],
        "design": [v("PASS", "Capacity lookup in flisr.py; TieCapacity dataclass placed in flisr.py for locality.",
                     artifacts={"design": "v1"}, trace=[tr(r, "design", "D-FLISR-1") for r in reqs]),
                   v("PASS", "TieCapacity moved to models.py; flisr.py imports it (STD-ARCH-1).", artifacts={"design": "v2"})],
        "architect": [v("VIOLATION", "STD-ARCH-1: data model declared inside logic module.", artifacts={"review": "move TieCapacity to models"},
                        evidence=[{"kind": "standard", "ref": "STD-ARCH-1", "detail": "TieCapacity in flisr.py"}]),
                      v("CONFIRMED", "Design conforms; every requirement mapped.", artifacts={"review": "ok"})],
        "coding:U1:1": [v("PASS", "Failing tests first, then guard; draft PR opened.", branch="agent/example/U1", pr_url=pr,
                          files_touched=["backend/app/flisr.py", "backend/tests/test_flisr_capacity.py"],
                          trace=[tr(reqs[0], "code", "backend/app/flisr.py::tie_capacity"), tr(reqs[0], "test", "test_flisr_capacity.py::test_req_flisr_101"),
                                 tr(reqs[1], "code", "backend/app/flisr.py::plan_restoration"), tr(reqs[1], "test", "test_flisr_capacity.py::test_req_flisr_102")])],
        "qa:U1:1": [v("FAIL", "Vector 7 (capacity exactly at load) restores; spec says refuse at equality.", artifacts={"qa_report": "..."},
                     evidence=[{"kind": "test", "ref": "oracle vector 7", "detail": "observed restore, expected refuse"}])],
        "coding:U1:2": [v("PASS", "Comparison tightened to <=; QA vector added as regression test.", branch="agent/example/U1", pr_url=pr,
                          files_touched=["backend/app/flisr.py", "backend/tests/test_flisr_capacity.py"])],
        "qa:U1:2": [v("PASS", "Independent oracle agrees on 40 vectors incl. boundary and missing input.", artifacts={"qa_report": "..."})],
        "coding:U2:1": [v("PASS", "Stale telemetry refuses restoration with quality flag.", branch="agent/example/U2", pr_url=pr,
                          files_touched=["backend/app/flisr.py", "backend/tests/test_flisr_stale.py"],
                          trace=[tr(reqs[2], "code", "backend/app/flisr.py::plan_restoration"), tr(reqs[2], "test", "test_flisr_stale.py::test_req_flisr_103")])],
        "qa:U2:1": [v("PASS", "Stale path verified; no zero coercion.", artifacts={"qa_report": "..."})],
        "integrate": [v("PASS", "Units merged on agent/example/integration; suite green; PR ready for review.", pr_url=pr, branch="agent/example/integration",
                        trace=[tr(r, "pr", pr) for r in reqs])],
        "document": [v("PASS", "Operator guide updated with stale-telemetry behaviour.", trace=[tr(r, "doc", "docs/flisr.md") for r in reqs])],
    }
    o = orch(RUNS / rid, script)
    o.start("feature", spec, "examples/targets/adms/requirements/REQ-tie-capacity.md", run_id=rid, story_points=3)
    o.resume()
    o.answer("Q-SPEC-1", "Refuse restoration and raise an operator alarm; never hold last value.", actor="ops-lead")
    o.resume()
    decide(o.run_dir, "after-specify", "ops-lead")
    o.resume()
    decide(o.run_dir, "after-architect", "principal-engineer")
    o.resume()
    decide(o.run_dir, "before-merge", "protection-reviewer")
    st = o.resume()
    print(rid, st["status"])


def rca():
    rid = "example-rca-backfeed"
    pr = "https://github.com/example-org/product-repo/pull/102"
    script = {
        "explore": [v("PASS", "Hypothesis: restoration back-feeds because the faulted section check uses the pre-isolation topology.",
                      artifacts={"hypothesis": "stale topology snapshot", "evidence_package": "repro test + excerpts"}),
                    v("PASS", "Round 2: added call-graph evidence showing snapshot taken before isolate() returns.",
                      artifacts={"hypothesis": "snapshot ordering", "evidence_package": "repro + ordering trace"})],
        "evaluate": [v("REFUTED", "Evidence shows the symptom but not the ordering mechanism; alternative (telemetry lag) not ruled out."),
                     v("CONFIRMED", "Ordering trace demonstrates the mechanism and excludes telemetry lag.")],
        "review": [v("CONFIRMED", "Blast radius: restoration planning only; fail-safe fix: re-snapshot after isolate; protected path, 2 reviewers.",
                     artifacts={"review": "..."})],
        "fix:fix:1": [v("PASS", "Failing repro committed first; snapshot re-taken after isolation; invariant over 500 seeds.", branch="agent/example/fix", pr_url=pr,
                        files_touched=["backend/app/flisr.py", "backend/tests/test_flisr.py"],
                        trace=[{"requirement_id": "DEF-FLISR-7", "kind": "code", "ref": "backend/app/flisr.py::plan_restoration"},
                               {"requirement_id": "DEF-FLISR-7", "kind": "test", "ref": "test_flisr.py::test_def_flisr_7_no_backfeed"}])],
        "qa:fix:1": [v("PASS", "Independent invariant check over 1000 seeds: no back-feed.")],
        "integrate": [v("PASS", "PR ready for review.", pr_url=pr, trace=[{"requirement_id": "DEF-FLISR-7", "kind": "pr", "ref": pr}])],
        "document": [v("PASS", "Release note added.")],
    }
    o = orch(RUNS / rid, script)
    o.start("rca", "DEF-FLISR-7 Restoration back-fed a de-energised section during drill 14.", "examples/targets/adms/defects/DEF-FLISR-7.md", run_id=rid, story_points=2)
    o.resume()
    decide(o.run_dir, "after-review", "protection-reviewer")
    o.resume()
    decide(o.run_dir, "before-merge", "ops-lead")
    st = o.resume()
    print(rid, st["status"])


if __name__ == "__main__":
    feature()
    rca()
