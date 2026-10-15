"""Relay backend: the orchestrator writes `sessions/<stage_key>.request.json` (the
exact v3 payload) and pauses. Whatever Devin session is driving the harness issues
the create call with its own v3 session tooling, then drops the child's structured
output into `sessions/<stage_key>.result.json`. `harness resume` picks it up. The
request/result pair is what the audit log records, so the two transports are
indistinguishable in the evidence."""

from __future__ import annotations

import json
from pathlib import Path

from .base import SessionBackend, SessionRequest, SessionResult


class AwaitingSession(RuntimeError):
    def __init__(self, request_path: Path):
        super().__init__(f"session request written to {request_path}; run `harness resume` once the "
                         f"result file exists")
        self.request_path = request_path


class RelayBackend(SessionBackend):
    name = "relay"

    def run(self, request: SessionRequest, *, run_dir, stage_key: str) -> SessionResult:
        sess_dir = Path(run_dir) / "sessions"
        sess_dir.mkdir(parents=True, exist_ok=True)
        req_path = sess_dir / f"{stage_key}.request.json"
        res_path = sess_dir / f"{stage_key}.result.json"
        if res_path.exists():
            data = json.loads(res_path.read_text())
            return SessionResult(
                session_id=data["session_id"], session_url=data["session_url"],
                status=data.get("status", "finished"), structured_output=data.get("structured_output"),
                devin_mode=data.get("devin_mode", request.devin_mode), acus=float(data.get("acus") or 0), raw=data)
        if not req_path.exists():
            req_path.write_text(json.dumps(request.to_v3_payload(), indent=2))
        raise AwaitingSession(req_path)
