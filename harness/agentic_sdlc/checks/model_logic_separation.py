"""Known failure mode 1: data models, settings and scaling constants mixed with logic.

A file is a *model file* if it matches a configured glob (e.g. `**/models.py`,
`**/settings*.py`) or if more than half of its added top-level statements are
dataclass/pydantic/TypedDict/struct declarations. In a model file, added control
flow (if/for/while/try, non-trivial method bodies) is a finding. In a non-model
file, newly introduced model classes are a finding."""

from __future__ import annotations

import fnmatch
import re
from typing import Any

from .diffs import DiffFile

MODEL_DECL = re.compile(r"^\s*(@dataclass|class \w+\((BaseModel|TypedDict|NamedTuple|Struct)\)|"
                        r"class \w+\(.*(Model|Settings|Config)\)|typedef struct|struct \w+ \{|"
                        r"(export )?(interface|type) \w+ (=|\{))")
CONTROL_FLOW = re.compile(r"^\s*(if |elif |for |while |try:|except|switch ?\(|match )")
SCALING_CONST = re.compile(r"^\s*[A-Z][A-Z0-9_]*(_SCALE|_FACTOR|_RATIO|_GAIN|_BASE|_PU)\s*[:=]")
METHOD_DEF = re.compile(r"^\s{4,}def (?!__(init|post_init|repr|eq|hash|str)__)\w+\(")


def _is_model_file(f: DiffFile, model_globs: list[str]) -> bool:
    if any(fnmatch.fnmatch(f.path, g) for g in model_globs):
        return True
    added = [t for _, t in f.added_lines if t.strip() and not t.startswith((" ", "\t", "#"))]
    if not added:
        return False
    decls = sum(1 for t in added if MODEL_DECL.match(t))
    return decls / len(added) > 0.5


def check_model_logic_separation(files: list[DiffFile], model_globs: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for f in files:
        if f.is_deleted:
            continue
        if _is_model_file(f, model_globs):
            for no, text in f.added_lines:
                if CONTROL_FLOW.match(text):
                    findings.append({"file": f.path, "line": no, "rule": "logic-in-model-file",
                                     "text": text.strip(),
                                     "fix": "Move control flow out of the data-model module into the logic module."})
                elif METHOD_DEF.match(text):
                    findings.append({"file": f.path, "line": no, "rule": "behaviour-method-in-model",
                                     "text": text.strip(),
                                     "fix": "Models carry data only; put behaviour in a service/function module."})
        else:
            for no, text in f.added_lines:
                if MODEL_DECL.match(text) and not text.lstrip().startswith("@"):
                    findings.append({"file": f.path, "line": no, "rule": "model-in-logic-file",
                                     "text": text.strip(),
                                     "fix": "Declare data models in the designated models module, not next to logic."})
                if SCALING_CONST.match(text) and not any(fnmatch.fnmatch(f.path, g) for g in model_globs):
                    findings.append({"file": f.path, "line": no, "rule": "scaling-constant-in-logic",
                                     "text": text.strip(),
                                     "fix": "Scaling/per-unit constants belong in the settings/model module with a source."})
    return findings
