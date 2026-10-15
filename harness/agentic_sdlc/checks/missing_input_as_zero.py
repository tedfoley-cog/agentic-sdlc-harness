"""Known failure mode 3: missing or invalid input treated as a valid zero.

Flags newly added lines that coerce absence to zero: `.get(key, 0)`, `or 0`,
`?? 0`, `|| 0`, `except ...: x = 0`, `if x is None: x = 0`, `Optional[...] = 0`,
`float(x or 0)`, `nan_to_num`, `fillna(0)`, `.unwrap_or(0)`, `: 0.0 = field(default=0`.
Explicit, documented zero defaults can be allow-listed with `# harness: zero-ok <reason>`."""

from __future__ import annotations

import re
from typing import Any

from .diffs import DiffFile

PATTERNS = [
    (re.compile(r"\.get\([^,()]+,\s*0(\.0)?\)"), "dict.get(..., 0) treats a missing key as zero"),
    (re.compile(r"\bor\s+0(\.0)?\b"), "`or 0` turns None/invalid into zero"),
    (re.compile(r"(\?\?|\|\|)\s*0(\.0)?\b"), "`?? 0` / `|| 0` turns missing into zero"),
    (re.compile(r"^\s*(except\b.*:|catch\b.*)\s*\w+\s*=\s*0(\.0)?\s*$"), "exception handler assigns zero"),
    (re.compile(r"if\s+\w+\s+is\s+None:\s*\w+\s*=\s*0(\.0)?"), "None replaced with zero"),
    (re.compile(r"Optional\[[^\]]+\]\s*=\s*0(\.0)?"), "optional input defaults to zero"),
    (re.compile(r"\bfloat\(\s*\w+\s+or\s+0\s*\)"), "float(x or 0) masks missing telemetry"),
    (re.compile(r"\b(nan_to_num|fillna\(0|unwrap_or\(0|unwrap_or_default)\b"), "NaN/absent coerced to zero"),
    (re.compile(r"\|\s*None\s*=\s*0(\.0)?\b"), "nullable field defaults to zero"),
]
ALLOW = re.compile(r"#\s*harness:\s*zero-ok\s+\S+")


def check_missing_input_as_zero(files: list[DiffFile]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for f in files:
        if f.is_deleted:
            continue
        pending_handler = False
        for no, text in f.added_lines:
            stripped = text.strip()
            if ALLOW.search(text) or stripped.startswith(("#", "//", "*")):
                pending_handler = False
                continue
            if re.match(r"^\s*(except\b.*:|catch\b.*\{?)\s*$", text):
                pending_handler = True
                continue
            if pending_handler and re.match(r"^\s*\w+(\[[^\]]+\])?\s*=\s*0(\.0)?\s*$", text):
                findings.append({"file": f.path, "line": no, "rule": "missing-input-as-zero",
                                 "text": stripped, "why": "exception handler assigns zero",
                                 "fix": "Propagate the error or mark the value unavailable; never substitute 0."})
                pending_handler = False
                continue
            pending_handler = False
            for pat, why in PATTERNS:
                if pat.search(text):
                    findings.append({"file": f.path, "line": no, "rule": "missing-input-as-zero",
                                     "text": stripped, "why": why,
                                     "fix": "Refuse or flag the missing/invalid input (raise, return None/Unavailable, "
                                            "or mark quality=bad). Add `# harness: zero-ok <reason>` only when a "
                                            "standard explicitly defines zero as the safe default."})
                    break
    return findings
