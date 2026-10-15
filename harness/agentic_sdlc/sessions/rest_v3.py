"""Devin REST API v3 backend. Base URL https://api.devin.ai/v3 (or the enterprise
domain). Only v3 endpoints are used."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from .base import SessionBackend, SessionRequest, SessionResult

TERMINAL = {"finished", "blocked", "stopped", "expired", "terminated", "suspended", "exit"}


class RestV3Backend(SessionBackend):
    name = "rest_v3"

    def __init__(self, org_id: str | None = None, api_key: str | None = None, base_url: str | None = None,
                 poll_seconds: int = 30, timeout_minutes: int = 180, _opener=None):
        self.org_id = org_id or os.environ.get("DEVIN_ORG_ID", "")
        self.api_key = api_key or os.environ.get("DEVIN_API_KEY", "")
        self.base_url = (base_url or os.environ.get("DEVIN_API_BASE", "https://api.devin.ai/v3")).rstrip("/")
        if not self.base_url.endswith("/v3"):
            raise ValueError("Devin API base must be the v3 API (…/v3); v1 endpoints are not supported")
        if not (self.org_id and self.api_key):
            raise ValueError("DEVIN_ORG_ID and DEVIN_API_KEY are required for the rest_v3 backend")
        self.poll_seconds = poll_seconds
        self.timeout_minutes = timeout_minutes
        self._opener = _opener or urllib.request.urlopen

    def _call(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        req = urllib.request.Request(f"{self.base_url}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Authorization": f"Bearer {self.api_key}",
                                              "Content-Type": "application/json"})
        try:
            with self._opener(req, timeout=60) as resp:
                return json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"Devin API {method} {path} -> {exc.code}: {detail[:300]}") from exc

    def create(self, request: SessionRequest) -> dict[str, Any]:
        return self._call("POST", f"/organizations/{self.org_id}/sessions", request.to_v3_payload())

    def get(self, session_id: str) -> dict[str, Any]:
        return self._call("GET", f"/organizations/{self.org_id}/sessions/{session_id}")

    def message(self, session_id: str, text: str) -> dict[str, Any]:
        return self._call("POST", f"/organizations/{self.org_id}/sessions/{session_id}/messages", {"message": text})

    def run(self, request: SessionRequest, *, run_dir, stage_key: str) -> SessionResult:
        created = self.create(request)
        sid = created["session_id"]
        deadline = time.time() + self.timeout_minutes * 60
        detail = created
        while time.time() < deadline:
            detail = self.get(sid)
            status = (detail.get("status_detail") or detail.get("status") or "").lower()
            if detail.get("structured_output") or status in TERMINAL:
                break
            time.sleep(self.poll_seconds)
        return SessionResult(
            session_id=sid,
            session_url=detail.get("url", f"https://app.devin.ai/sessions/{sid.removeprefix('devin-')}"),
            status=detail.get("status_detail") or detail.get("status", "unknown"),
            structured_output=detail.get("structured_output"),
            devin_mode=detail.get("devin_mode", request.devin_mode),
            acus=float(detail.get("acus_consumed") or 0),
            raw=detail,
        )
