"""`harness` command line.

  harness run     --workflow feature|rca --config harness.yaml --requirement REQ.md [--run-id ID] [--backend relay|rest_v3|fake]
  harness resume  RUN_ID            advance after a session result / gate decision / answer landed
  harness answer  RUN_ID Q-ID --actor LOGIN --text "..."
  harness time    RUN_ID --minutes N --actor LOGIN
  harness status  RUN_ID
  harness replay  RUN_ID            rebuild state from the log and verify the hash chain
  harness check   --diff FILE [--brief-files GLOB...]   run the deterministic checks on a diff
  harness kpis    RUN_ID [--story-points N]
  harness export                    refresh runs/index.json for the console
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import checks
from .config import HarnessConfig
from .kpis import compute as compute_kpis
from .orchestrator import Orchestrator
from .runlog import RunLog, now, replay
from .sessions import backend_from_name
from .standards import store_from_config

HARNESS_ROOT = Path(os.environ.get("HARNESS_ROOT", Path(__file__).resolve().parents[2]))
RUNS_DIR = Path(os.environ.get("HARNESS_RUNS", HARNESS_ROOT / "runs"))


def _orch(run_dir: Path, cfg_path: str | None, backend_name: str, target_clone: str | None,
          verify_commands: bool = True) -> Orchestrator:
    state_cfg = run_dir / "harness.yaml"
    if cfg_path:
        cfg = HarnessConfig.load(cfg_path)
        run_dir.mkdir(parents=True, exist_ok=True)
        state_cfg.write_text(Path(cfg_path).read_text())  # freeze the contract with the run
    else:
        cfg = HarnessConfig.load(state_cfg)
    meta_path = run_dir / "meta.json"
    if meta_path.exists() and not target_clone:
        meta = json.loads(meta_path.read_text())
        backend_name, target_clone = meta.get("backend", backend_name), meta.get("target_clone")
        verify_commands = meta.get("verify_commands", verify_commands)
    else:
        meta_path.write_text(json.dumps({"backend": backend_name, "target_clone": target_clone,
                                         "verify_commands": verify_commands}))
    kwargs = {}
    if backend_name == "fake":
        kwargs["script_path"] = str(run_dir / "fake_script.json")
    return Orchestrator(cfg=cfg, run_dir=run_dir, backend=backend_from_name(backend_name, **kwargs),
                        standards=store_from_config(cfg.standards, HARNESS_ROOT), skills_dir=HARNESS_ROOT / "plugin/skills",
                        target_clone=Path(target_clone) if target_clone else None, verify_commands=verify_commands)


def _print_state(st: dict) -> None:
    print(f"run {st['run_id']} [{st['workflow']}] status={st['status']} step={st['plan'][min(st['cursor'], len(st['plan'])-1)]}")
    if st.get("paused_on"):
        print("paused on:", json.dumps(st["paused_on"]))
    for q in st.get("questions", []):
        print(f"  {q['id']} [{q['status']}] {q['question']}")
    for g, info in st.get("gates", {}).items():
        print(f"  gate {g}: {info['status']} {info.get('actor') or ''} {info['ref']}")
    for pr in st.get("prs", []):
        print("  PR:", pr)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="harness", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--workflow", choices=["feature", "rca"], required=True)
    r.add_argument("--config", required=True)
    r.add_argument("--requirement", required=True, help="path to the requirement / defect report (markdown)")
    r.add_argument("--run-id")
    r.add_argument("--backend", default="relay", choices=["relay", "rest_v3", "fake"])
    r.add_argument("--target-clone", help="local clone of the target repo for deterministic verification")
    r.add_argument("--no-verify-commands", action="store_true")
    r.add_argument("--story-points", type=float, default=1.0)
    for name in ("resume", "status", "replay"):
        sub.add_parser(name).add_argument("run_id")
    a = sub.add_parser("answer")
    a.add_argument("run_id")
    a.add_argument("question_id")
    a.add_argument("--actor", required=True)
    a.add_argument("--text", required=True)
    x = sub.add_parser("extend", help="human extends an escalated bounded loop by N rounds")
    x.add_argument("run_id")
    x.add_argument("--loop", required=True, choices=["architect", "qa", "rca", "questions"])
    x.add_argument("--rounds", type=int, default=1)
    x.add_argument("--actor", required=True)
    x.add_argument("--reason", required=True)
    w = sub.add_parser("waive", help="human waives test coverage for one traced id (Trace NEEDS-HUMAN)")
    w.add_argument("run_id")
    w.add_argument("--requirement", required=True)
    w.add_argument("--actor", required=True)
    w.add_argument("--reason", required=True)
    t = sub.add_parser("time")
    t.add_argument("run_id")
    t.add_argument("--minutes", type=float, required=True)
    t.add_argument("--actor", required=True)
    t.add_argument("--note", default="")
    c = sub.add_parser("check")
    c.add_argument("--diff", required=True)
    c.add_argument("--brief-files", nargs="*")
    c.add_argument("--model-globs", nargs="*")
    k = sub.add_parser("kpis")
    k.add_argument("run_id")
    k.add_argument("--story-points", type=float, default=1.0)
    sub.add_parser("export")
    args = p.parse_args(argv)

    if args.cmd == "run":
        req = Path(args.requirement).read_text()
        run_id = args.run_id or f"run-{now()[:10]}-{Path(args.requirement).stem}"
        orch = _orch(RUNS_DIR / run_id, args.config, args.backend, args.target_clone, not args.no_verify_commands)
        orch.start(args.workflow, req, args.requirement, run_id=run_id, story_points=args.story_points)
        _print_state(orch.resume())
        return 0
    if args.cmd == "resume":
        orch = _orch(RUNS_DIR / args.run_id, None, "relay", None)
        _print_state(orch.resume())
        return 0
    if args.cmd == "status":
        _print_state(json.loads((RUNS_DIR / args.run_id / "state.json").read_text()))
        return 0
    if args.cmd == "replay":
        log = RunLog(RUNS_DIR / args.run_id / "runlog.jsonl")
        ok, msg = log.verify_chain()
        print(f"hash chain: {msg}")
        print(json.dumps(replay(log), indent=2, default=str))
        return 0 if ok else 1
    if args.cmd == "answer":
        orch = _orch(RUNS_DIR / args.run_id, None, "relay", None)
        orch.answer(args.question_id, args.text, args.actor)
        print(f"recorded answer to {args.question_id} by {args.actor}")
        return 0
    if args.cmd == "extend":
        orch = _orch(RUNS_DIR / args.run_id, None, "relay", None)
        orch.extend_loop(args.loop, args.rounds, args.actor, args.reason)
        print(f"loop {args.loop} extended by {args.rounds} by {args.actor}")
        return 0
    if args.cmd == "waive":
        orch = _orch(RUNS_DIR / args.run_id, None, "relay", None)
        orch.waive_requirement(args.requirement, args.actor, args.reason)
        print(f"{args.requirement} waived from test coverage by {args.actor}")
        return 0
    if args.cmd == "time":
        orch = _orch(RUNS_DIR / args.run_id, None, "relay", None)
        orch.record_human_time(args.minutes, args.actor, args.note)
        return 0
    if args.cmd == "check":
        results = checks.run_all(Path(args.diff).read_text(), brief_files=args.brief_files,
                                 model_globs=args.model_globs or ["**/models.py", "**/settings*.py"])
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return 0 if checks.overall(results) == "PASS" else 1
    if args.cmd == "kpis":
        print(json.dumps(compute_kpis(RUNS_DIR / args.run_id, story_points=args.story_points), indent=2))
        return 0
    if args.cmd == "export":
        entries = []
        for d in sorted(x for x in RUNS_DIR.iterdir() if x.is_dir() and (x / "state.json").exists()):
            st = json.loads((d / "state.json").read_text())
            cfg = HarnessConfig.load(d / "harness.yaml") if (d / "harness.yaml").exists() else None
            entries.append({"run_id": st["run_id"], "workflow": st["workflow"], "status": st["status"],
                            "target_repo": cfg.repo if cfg else "", "requirement_ref": st.get("requirement_ref"),
                            "dir": d.name, "prs": st.get("prs", []), "updated": now()})
        (RUNS_DIR / "index.json").write_text(json.dumps(entries, indent=2))
        print(f"{len(entries)} run(s) exported")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
