"""Session backends. Every stage runs as a Devin child session created from a
self-contained brief; the backend only changes *how* the create call is issued.

  rest_v3    – Devin REST API v3 (production / CI).
  relay      – a Devin session that is running the orchestrator issues the create
               call with its own session tooling; the request/result are exchanged
               through files in the run directory (same v3 fields and semantics).
  fake       – scripted verdicts for tests.
"""

from __future__ import annotations

from .base import SessionBackend, SessionRequest, SessionResult
from .fake import FakeBackend
from .relay import RelayBackend
from .rest_v3 import RestV3Backend


def backend_from_name(name: str, **kwargs) -> SessionBackend:
    if name == "rest_v3":
        return RestV3Backend(**kwargs)
    if name == "relay":
        return RelayBackend(**kwargs)
    if name == "fake":
        return FakeBackend(**kwargs)
    raise ValueError(f"unknown session backend {name!r}")


__all__ = ["SessionBackend", "SessionRequest", "SessionResult", "RestV3Backend", "RelayBackend",
           "FakeBackend", "backend_from_name"]
