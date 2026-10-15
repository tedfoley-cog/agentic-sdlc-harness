"""Append-only, hash-chained audit log. One JSON object per line. Nothing is ever
rewritten; `replay()` rebuilds state from the log alone."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class RunLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._tail_hash()

    def _tail_hash(self) -> str:
        last = "0" * 64
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                if line.strip():
                    last = json.loads(line)["hash"]
        return last

    def append(self, event: str, **fields: Any) -> dict[str, Any]:
        record = {"seq": self.count(), "ts": now(), "event": event, **fields, "prev": self._last_hash}
        payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
        record["hash"] = hashlib.sha256(payload.encode()).hexdigest()
        with self.path.open("a") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        self._last_hash = record["hash"]
        return record

    def count(self) -> int:
        if not self.path.exists():
            return 0
        return sum(1 for ln in self.path.read_text().splitlines() if ln.strip())

    def __iter__(self) -> Iterator[dict[str, Any]]:
        if not self.path.exists():
            return iter(())
        return (json.loads(ln) for ln in self.path.read_text().splitlines() if ln.strip())

    def verify_chain(self) -> tuple[bool, str]:
        prev = "0" * 64
        for rec in self:
            body = {k: v for k, v in rec.items() if k != "hash"}
            if body.get("prev") != prev:
                return False, f"seq {rec['seq']}: prev pointer mismatch"
            digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if digest != rec["hash"]:
                return False, f"seq {rec['seq']}: hash mismatch (log was edited)"
            prev = rec["hash"]
        return True, "chain intact"


def replay(log: RunLog) -> dict[str, Any]:
    """Rebuild orchestrator state purely from the log."""
    state: dict[str, Any] = {"run_id": None, "workflow": None, "status": "created", "stages": [],
                             "gates": [], "loops": {}, "open_questions": [], "trace_rows": 0,
                             "sessions": [], "prs": [], "humans": set()}
    current: dict[str, dict[str, Any]] = {}
    for rec in log:
        ev = rec["event"]
        if ev == "run.created":
            state.update(run_id=rec["run_id"], workflow=rec["workflow"], status="running",
                         target_repo=rec.get("target_repo"), requirement=rec.get("requirement"))
        elif ev == "stage.started":
            key = f"{rec['stage']}:{rec.get('unit', '-')}:{rec.get('attempt', 1)}"
            current[key] = {"stage": rec["stage"], "unit": rec.get("unit"), "attempt": rec.get("attempt", 1),
                            "started": rec["ts"], "model": rec.get("model"), "brief": rec.get("brief_ref"),
                            "artifacts_read": rec.get("artifacts_read", [])}
        elif ev == "stage.completed":
            key = f"{rec['stage']}:{rec.get('unit', '-')}:{rec.get('attempt', 1)}"
            row = current.pop(key, {"stage": rec["stage"], "unit": rec.get("unit"), "attempt": rec.get("attempt", 1)})
            row.update(finished=rec["ts"], verdict=rec["verdict"], summary=rec.get("summary"),
                       evidence=rec.get("evidence", []), artifacts_produced=rec.get("artifacts_produced", []),
                       session=rec.get("session_url"), questions=rec.get("questions", []))
            state["stages"].append(row)
            if rec.get("session_url"):
                state["sessions"].append(rec["session_url"])
            if rec.get("pr_url"):
                state["prs"].append(rec["pr_url"])
            for q in rec.get("questions", []):
                state["open_questions"].append({**q, "stage": rec["stage"], "status": "open"})
        elif ev == "question.answered":
            for q in state["open_questions"]:
                if q["id"] == rec["question_id"]:
                    q.update(status="answered", answer=rec["answer"], by=rec["actor"])
        elif ev == "loop.iteration":
            state["loops"].setdefault(rec["loop"], []).append(rec)
        elif ev == "gate.opened":
            state["gates"].append({"gate": rec["gate"], "opened": rec["ts"], "ref": rec.get("ref"),
                                   "status": "waiting"})
        elif ev == "gate.decided":
            for g in state["gates"]:
                if g["gate"] == rec["gate"] and g["status"] == "waiting":
                    g.update(status=rec["decision"], decided=rec["ts"], actor=rec["actor"],
                             actor_type=rec.get("actor_type"), review_minutes=rec.get("review_minutes"))
            state["humans"].add(rec["actor"])
        elif ev == "trace.appended":
            state["trace_rows"] += rec.get("rows", 0)
        elif ev == "run.finished":
            state["status"] = rec["status"]
        elif ev == "run.paused":
            state["status"] = "paused"
    state["humans"] = sorted(state["humans"])
    state["in_flight"] = list(current.values())
    return state
