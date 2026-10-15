"""Verdict vocabulary shared by every stage skill and the orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VERDICTS = (
    "PASS",
    "FAIL",
    "BLOCKED",
    "CONFIRMED",
    "VIOLATION",
    "NEEDS-HUMAN",
    "REFUTED",
    "INSUFFICIENT_EVIDENCE",
    "RETRACTION",
)

# Which verdicts each stage may legitimately emit. Anything else is a contract breach.
ALLOWED_BY_STAGE: dict[str, tuple[str, ...]] = {
    "specify": ("PASS", "BLOCKED", "NEEDS-HUMAN"),
    "decompose": ("PASS", "BLOCKED"),
    "design": ("PASS", "BLOCKED"),
    "architect": ("CONFIRMED", "VIOLATION", "BLOCKED", "NEEDS-HUMAN"),
    "coding": ("PASS", "FAIL", "BLOCKED"),
    "verify": ("PASS", "FAIL"),
    "qa": ("PASS", "FAIL", "BLOCKED", "INSUFFICIENT_EVIDENCE"),
    "integrate": ("PASS", "FAIL", "BLOCKED"),
    "document": ("PASS", "BLOCKED"),
    "trace": ("PASS", "FAIL"),
    "release": ("PASS", "BLOCKED", "NEEDS-HUMAN"),
    "explore": ("PASS", "BLOCKED", "INSUFFICIENT_EVIDENCE"),
    "evaluate": ("CONFIRMED", "REFUTED", "INSUFFICIENT_EVIDENCE"),
    "review": ("CONFIRMED", "REFUTED", "NEEDS-HUMAN", "RETRACTION"),
    "fix": ("PASS", "FAIL", "BLOCKED"),
}

VERDICT_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["verdict", "summary", "evidence"],
    "properties": {
        "verdict": {"type": "string", "enum": list(VERDICTS)},
        "summary": {"type": "string", "minLength": 1},
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["kind", "ref"],
                "properties": {
                    "kind": {
                        "type": "string",
                        "enum": [
                            "file", "test", "command", "pr", "commit", "url", "standard",
                            "requirement", "artifact", "session", "note",
                        ],
                    },
                    "ref": {"type": "string"},
                    "detail": {"type": "string"},
                },
            },
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "question"],
                "properties": {
                    "id": {"type": "string", "pattern": "^Q-[A-Z0-9-]+$"},
                    "question": {"type": "string"},
                    "blocking_units": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "artifacts": {"type": "object", "additionalProperties": True},
        "trace": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["requirement_id", "kind", "ref"],
                "properties": {
                    "requirement_id": {"type": "string"},
                    "kind": {"type": "string", "enum": ["design", "code", "test", "pr", "doc"]},
                    "ref": {"type": "string"},
                },
            },
        },
        "standards_loaded": {"type": "array", "items": {"type": "string"}},
        "files_touched": {"type": "array", "items": {"type": "string"}},
        "branch": {"type": "string"},
        "pr_url": {"type": "string"},
        "session_url": {"type": "string"},
        "model": {"type": "string"},
    },
}


@dataclass
class Verdict:
    verdict: str
    summary: str
    evidence: list[dict[str, str]] = field(default_factory=list)
    questions: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    trace: list[dict[str, str]] = field(default_factory=list)
    standards_loaded: list[str] = field(default_factory=list)
    files_touched: list[str] = field(default_factory=list)
    branch: str | None = None
    pr_url: str | None = None
    session_url: str | None = None
    model: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Verdict:
        import jsonschema

        jsonschema.validate(data, VERDICT_SCHEMA)
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})

    def to_dict(self) -> dict[str, Any]:
        out = {k: v for k, v in self.__dict__.items() if v not in (None, [], {})}
        out.setdefault("evidence", [])
        return out

    def allowed_for(self, stage: str) -> bool:
        return self.verdict in ALLOWED_BY_STAGE.get(stage, VERDICTS)
