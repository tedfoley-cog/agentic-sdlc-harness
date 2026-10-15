"""Incremental traceability: requirement -> design -> code -> test -> PR.
Each stage appends rows as it finishes; the matrix is never produced as a late
documentation pass."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class TraceMatrix:
    KINDS = ("design", "code", "test", "pr", "doc")

    def __init__(self, path: str | Path, requirement_id_pattern: str):
        self.path = Path(path)
        self.pattern = re.compile(requirement_id_pattern)
        self.rows: list[dict[str, Any]] = []
        self.requirements: dict[str, str] = {}
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.rows = data.get("rows", [])
            self.requirements = data.get("requirements", {})

    def register_requirements(self, text: str) -> list[str]:
        """Pull requirement ids (and their sentence) out of a specification."""
        found = []
        for line in text.splitlines():
            for m in self.pattern.finditer(line):
                rid = m.group(0)
                self.requirements.setdefault(rid, line.strip())
                found.append(rid)
        self._save()
        return sorted(set(found))

    def append(self, stage: str, rows: list[dict[str, str]]) -> int:
        added = 0
        for row in rows:
            if row["kind"] not in self.KINDS:
                raise ValueError(f"unknown trace kind {row['kind']}")
            if not self.pattern.fullmatch(row["requirement_id"]):
                raise ValueError(f"{row['requirement_id']} does not match requirement id pattern")
            entry = {"requirement_id": row["requirement_id"], "kind": row["kind"], "ref": row["ref"], "stage": stage}
            if entry not in self.rows:
                self.rows.append(entry)
                added += 1
        self._save()
        return added

    def coverage(self) -> dict[str, Any]:
        per_req: dict[str, dict[str, list[str]]] = {
            rid: {k: [] for k in self.KINDS} for rid in self.requirements}
        for r in self.rows:
            per_req.setdefault(r["requirement_id"], {k: [] for k in self.KINDS})[r["kind"]].append(r["ref"])
        total = len(per_req)
        with_test = sum(1 for v in per_req.values() if v["test"])
        with_code = sum(1 for v in per_req.values() if v["code"])
        return {
            "requirements": total,
            "with_design": sum(1 for v in per_req.values() if v["design"]),
            "with_code": with_code,
            "with_test": with_test,
            "with_pr": sum(1 for v in per_req.values() if v["pr"]),
            "test_coverage": round(with_test / total, 3) if total else 0.0,
            "orphans": sorted(rid for rid, v in per_req.items() if not any(v.values())),
            "matrix": per_req,
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(
            {"requirements": self.requirements, "rows": self.rows, "coverage": self.coverage()}, indent=2))

    def to_markdown(self) -> str:
        cov = self.coverage()
        lines = ["| Requirement | Design | Code | Test | PR |", "|---|---|---|---|---|"]
        for rid, v in sorted(cov["matrix"].items()):
            cell = lambda xs: "<br>".join(f"`{x}`" for x in xs) if xs else "—"  # noqa: E731
            lines.append(f"| {rid} | {cell(v['design'])} | {cell(v['code'])} | {cell(v['test'])} | {cell(v['pr'])} |")
        lines.append("")
        lines.append(f"Requirement test coverage: **{cov['test_coverage']:.0%}** "
                     f"({cov['with_test']}/{cov['requirements']}); orphans: {cov['orphans'] or 'none'}")
        return "\n".join(lines)
