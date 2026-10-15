import io
import json

import pytest

from agentic_sdlc.sessions.base import SessionRequest
from agentic_sdlc.sessions.rest_v3 import RestV3Backend
from agentic_sdlc.verdicts import VERDICT_SCHEMA


class FakeResp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): return False


def test_rest_v3_uses_v3_endpoints_and_polls(tmp_path):
    calls = []
    answers = [{"session_id": "devin-abc", "url": "https://app.devin.ai/sessions/abc"},
               {"session_id": "devin-abc", "status_detail": "working", "url": "https://app.devin.ai/sessions/abc"},
               {"session_id": "devin-abc", "status_detail": "finished", "structured_output": {"verdict": "PASS"},
                "acus_consumed": 1.5, "devin_mode": "ultra", "url": "https://app.devin.ai/sessions/abc"}]

    def opener(req, timeout):
        calls.append((req.get_method(), req.full_url, req.data))
        return FakeResp(json.dumps(answers.pop(0)).encode())

    be = RestV3Backend(org_id="org-1", api_key="k", poll_seconds=0, _opener=opener)
    res = be.run(SessionRequest("t", "p", ["o/r"], "ultra", VERDICT_SCHEMA), run_dir=tmp_path, stage_key="qa:-:1")
    assert calls[0][0] == "POST" and calls[0][1] == "https://api.devin.ai/v3/organizations/org-1/sessions"
    assert json.loads(calls[0][2])["devin_mode"] == "ultra" and json.loads(calls[0][2])["structured_output_required"]
    assert calls[1][1].endswith("/v3/organizations/org-1/sessions/devin-abc")
    assert res.structured_output == {"verdict": "PASS"} and res.acus == 1.5


def test_rest_v3_rejects_non_v3_base():
    with pytest.raises(ValueError):
        RestV3Backend(org_id="o", api_key="k", base_url="https://api.devin.ai/v1")
