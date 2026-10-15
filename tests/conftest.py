import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

BASE_CFG = {
    "repo": "example-org/product-repo", "default_branch": "main",
    "commands": {"build": "true", "test": "true", "lint": "true"},
    "requirement_id_pattern": r"REQ-[A-Z]+-\d{3}", "safety_classification": "safety-critical",
    "protected_paths": [{"pattern": "backend/app/flisr.py", "reviewers": 2, "reason": "isolation logic"}],
    "standards": {"provider": "markdown", "location": "standards", "required": ["STD-GOV"]},
    "boundaries": {"coding": {"allowed": ["backend/**"], "forbidden": ["backend/app/models.py"]}},
    "loops": {"architect": 2, "qa": 2, "rca": 2},
    "models": {"default": "normal", "coding": "normal", "qa": "ultra", "evaluate": "ultra"},
    "gates": {"provider": "file"},
}


@pytest.fixture
def cfg_dict():
    return json.loads(json.dumps(BASE_CFG))


@pytest.fixture
def harness_root():
    return ROOT


def verdict(v, summary="ok", **extra):
    return {"verdict": v, "summary": summary, "evidence": [{"kind": "note", "ref": "test"}], **extra}
