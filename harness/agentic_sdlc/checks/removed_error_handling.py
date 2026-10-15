"""Known failure mode 2: error handling deleted during refactoring.

Per hunk, count removed error-handling constructs (raise/throw/except/catch,
guard clauses `if x is None: raise/return`, assert, `.unwrap_or`, `errno` checks).
A hunk that removes more than it adds is a finding, with the removed lines quoted."""

from __future__ import annotations

import re
from typing import Any

from .diffs import DiffFile

ERROR_HANDLING = re.compile(
    r"(\braise\b|\bthrow\b|\bexcept\b|\bcatch\b|\bassert\b|\bFlisrError\b|Error\(|Exception\(|"
    r"\bif\b.*\b(is None|== None|is not None|not \w+|< 0|<= 0|len\(\w+\) == 0)\b.*:|"
    r"\breturn (None|null|nullptr|-1|false|False|E[A-Z]+)\b|\bpanic\b|\bperror\b|\bstatus\b.*!=\s*0)"
)


def _count(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return [(no, t) for no, t in lines if ERROR_HANDLING.search(t) and not t.strip().startswith(("#", "//"))]


def check_removed_error_handling(files: list[DiffFile]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for f in files:
        if f.is_deleted:
            continue
        for h in f.hunks:
            removed = _count(h.removed)
            added = _count(h.added)
            if len(removed) > len(added):
                findings.append({
                    "file": f.path, "line": h.old_start, "rule": "error-handling-removed",
                    "removed": [t.strip() for _, t in removed],
                    "kept_or_added": [t.strip() for _, t in added],
                    "fix": "Restore the guard/raise or show an equivalent handler in the same hunk; "
                           "refactors must not silently widen accepted inputs.",
                })
    return findings
