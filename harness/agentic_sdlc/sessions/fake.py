"""Scripted backend for tests and offline demos: verdicts keyed by stage name
(optionally `stage#attempt`) are returned in order."""

from __future__ import annotations

import json
from typing import Any

from .base import SessionBackend, SessionRequest, SessionResult


class FakeBackend(SessionBackend):
    name = "fake"

    def __init__(self, script: dict[str, list[dict[str, Any]]] | None = None, script_path: str | None = None):
        if script_path:
            script = json.load(open(script_path))
        self.script = {k: list(v) for k, v in (script or {}).items()}
        self.requests: list[SessionRequest] = []
        self.counter = 0

    def run(self, request: SessionRequest, *, run_dir, stage_key: str) -> SessionResult:
        self.requests.append(request)
        stage = stage_key.split(":")[0]
        queue = self.script.get(stage_key) or self.script.get(stage)
        if not queue:
            raise AssertionError(f"fake backend has no scripted verdict for {stage_key}")
        output = queue.pop(0)
        self.counter += 1
        sid = f"fake-{self.counter:04d}"
        return SessionResult(session_id=sid, session_url=f"fake://sessions/{sid}", status="finished",
                             structured_output=output, devin_mode=request.devin_mode,
                             acus=float(output.get("_acus", 0.5)))
