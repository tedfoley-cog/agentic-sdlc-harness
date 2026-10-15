"""Deterministic verification checks run after every Coding/Fix attempt. Their
results are fed straight back into the next Coding brief — no human relays them."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .diffs import DiffFile, parse_unified_diff
from .governance import check_governance, check_scope
from .missing_input_as_zero import check_missing_input_as_zero
from .model_logic_separation import check_model_logic_separation
from .removed_error_handling import check_removed_error_handling


@dataclass
class CheckResult:
    name: str
    verdict: str                     # PASS | FAIL
    findings: list[dict[str, Any]] = field(default_factory=list)
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "verdict": self.verdict, "findings": self.findings, "detail": self.detail}


def run_all(diff_text: str, *, brief_files: list[str] | None = None, commit_messages: list[str] | None = None,
            pr: dict[str, Any] | None = None, governance: dict[str, Any] | None = None,
            model_globs: list[str] | None = None) -> list[CheckResult]:
    files: list[DiffFile] = parse_unified_diff(diff_text)
    results = [
        _wrap("model_logic_separation", check_model_logic_separation(files, model_globs or [])),
        _wrap("removed_error_handling", check_removed_error_handling(files)),
        _wrap("missing_input_as_zero", check_missing_input_as_zero(files)),
    ]
    if brief_files is not None:
        results.append(_wrap("scope", check_scope(files, brief_files)))
    if governance is not None:
        results.append(_wrap("governance", check_governance(commit_messages or [], pr or {}, governance)))
    return results


def _wrap(name: str, findings: list[dict[str, Any]]) -> CheckResult:
    return CheckResult(name, "FAIL" if findings else "PASS", findings,
                       f"{len(findings)} finding(s)" if findings else "no findings")


def overall(results: list[CheckResult]) -> str:
    return "FAIL" if any(r.verdict == "FAIL" for r in results) else "PASS"


__all__ = ["CheckResult", "run_all", "overall", "parse_unified_diff"]
