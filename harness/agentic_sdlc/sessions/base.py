from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionRequest:
    """Mirrors the fields of POST /v3/organizations/{org}/sessions we rely on."""

    title: str
    prompt: str
    repos: list[str]
    devin_mode: str
    structured_output_schema: dict[str, Any]
    tags: list[str] = field(default_factory=list)
    max_acu_limit: int | None = None
    attachment_urls: list[str] = field(default_factory=list)

    def to_v3_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "prompt": self.prompt,
            "title": self.title,
            "repos": self.repos,
            "devin_mode": self.devin_mode,
            "structured_output_schema": self.structured_output_schema,
            "structured_output_required": True,
            "tags": self.tags,
        }
        if self.max_acu_limit:
            payload["max_acu_limit"] = self.max_acu_limit
        if self.attachment_urls:
            payload["attachment_urls"] = self.attachment_urls
        return payload


@dataclass
class SessionResult:
    session_id: str
    session_url: str
    status: str
    structured_output: dict[str, Any] | None
    devin_mode: str
    acus: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


class SessionBackend:
    name = "base"

    def run(self, request: SessionRequest, *, run_dir, stage_key: str) -> SessionResult:  # pragma: no cover
        raise NotImplementedError
