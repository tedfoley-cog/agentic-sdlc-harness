"""Per-run KPIs computed from the run log + trace, persisted to runs/<id>/kpis.json
and appended to runs/kpi_history.jsonl for trend rendering."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .runlog import RunLog, replay

ACU_USD_RATE = 2.25          # list price per ACU; override via config.governance.acu_usd
LOOP_STAGES = {"architect": ("VIOLATION", "CONFIRMED"), "qa": ("FAIL", "PASS"), "evaluate": ("REFUTED", "CONFIRMED")}


def _minutes(a: str, b: str) -> float:
    fa = datetime.fromisoformat(a.replace("Z", "+00:00"))
    fb = datetime.fromisoformat(b.replace("Z", "+00:00"))
    return round((fb - fa).total_seconds() / 60, 1)


def compute(run_dir: str | Path, story_points: float = 1.0, acu_usd: float = ACU_USD_RATE,
            acus: float | None = None, human_minutes_override: float | None = None) -> dict[str, Any]:
    run_dir = Path(run_dir)
    log = RunLog(run_dir / "runlog.jsonl")
    state = replay(log)
    stages = state["stages"]
    records = list(log)

    # Autonomy: share of stage completions that needed no human intervention
    human_touch = {s["stage"] for s in stages if s["verdict"] in ("BLOCKED", "NEEDS-HUMAN")}
    autonomy = round(1 - len(human_touch) / max(1, len({s["stage"] for s in stages})), 3)

    # First-pass approval per stage (attempt 1 produced the passing verdict)
    first_pass: dict[str, bool] = {}
    for s in stages:
        if s["stage"] in first_pass:
            continue
        if s["attempt"] == 1 and s["verdict"] in ("PASS", "CONFIRMED"):
            first_pass[s["stage"]] = True
        elif s["attempt"] == 1:
            first_pass[s["stage"]] = False

    # a round replayed after pause/resume is recorded again in state; count distinct rounds, not records
    loops = {name: len({(r.get("unit"), r.get("iteration")) for r in v}) for name, v in state["loops"].items()}
    resolved = {name: any(r.get("resolved") for r in v) for name, v in state["loops"].items()}
    loop_resolution_rate = round(sum(resolved.values()) / len(resolved), 3) if resolved else None

    trace_path = run_dir / "trace.json"
    req_cov = json.loads(trace_path.read_text())["coverage"]["test_coverage"] if trace_path.exists() else None

    # Human review time: gate open -> decision, plus explicit human time entries
    review_min = sum(g.get("review_minutes") or 0 for g in state["gates"] if g.get("review_minutes") is not None)
    for g in state["gates"]:
        if g.get("review_minutes") is None and g.get("decided"):
            review_min += _minutes(g["opened"], g["decided"])
    review_min += sum(r.get("minutes", 0) for r in records if r["event"] == "human.time")
    if human_minutes_override is not None:
        review_min = human_minutes_override

    cycle = _minutes(records[0]["ts"], records[-1]["ts"]) if records else 0.0
    acus_total = acus if acus is not None else sum(r.get("acus", 0) for r in records if r["event"] == "stage.completed")
    cost = round(acus_total * acu_usd, 2)

    kpis = {
        "run_id": state["run_id"],
        "workflow": state["workflow"],
        "status": state["status"],
        "autonomy": autonomy,
        "first_pass_approval": first_pass,
        "first_pass_rate": round(sum(first_pass.values()) / len(first_pass), 3) if first_pass else None,
        "loop_iterations": loops,
        "loop_resolution_rate": loop_resolution_rate,
        "requirement_test_coverage": req_cov,
        "human_review_minutes": round(review_min, 1),
        "human_review_hours": round(review_min / 60, 2),
        "cycle_time_minutes": cycle,
        "acus": acus_total,
        "inference_cost_usd": cost,
        "story_points": story_points,
        "inference_cost_per_story_point": round(cost / story_points, 2) if story_points else None,
        "gates": [{"gate": g["gate"], "status": g["status"], "decision": g["status"], "actor": g.get("actor"),
                   "minutes": g.get("review_minutes")} for g in state["gates"]],
        "computed_at": records[-1]["ts"] if records else None,
    }
    (run_dir / "kpis.json").write_text(json.dumps(kpis, indent=2))
    history = run_dir.parent / "kpi_history.jsonl"
    existing = [json.loads(ln) for ln in history.read_text().splitlines() if ln.strip()] if history.exists() else []
    existing = [e for e in existing if e["run_id"] != kpis["run_id"]] + [kpis]
    history.write_text("".join(json.dumps(e) + "\n" for e in existing))
    return kpis
