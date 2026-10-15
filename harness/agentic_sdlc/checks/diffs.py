from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Hunk:
    old_start: int
    new_start: int
    added: list[tuple[int, str]] = field(default_factory=list)
    removed: list[tuple[int, str]] = field(default_factory=list)
    context: list[str] = field(default_factory=list)


@dataclass
class DiffFile:
    path: str
    old_path: str
    hunks: list[Hunk] = field(default_factory=list)
    is_new: bool = False
    is_deleted: bool = False

    @property
    def added_lines(self) -> list[tuple[int, str]]:
        return [ln for h in self.hunks for ln in h.added]

    @property
    def removed_lines(self) -> list[tuple[int, str]]:
        return [ln for h in self.hunks for ln in h.removed]


_HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def parse_unified_diff(text: str) -> list[DiffFile]:
    files: list[DiffFile] = []
    cur: DiffFile | None = None
    hunk: Hunk | None = None
    old_no = new_no = 0
    for raw in text.splitlines():
        if raw.startswith("diff --git"):
            parts = raw.split()
            old_path = parts[2][2:] if len(parts) > 3 else ""
            cur = DiffFile(path=parts[3][2:] if len(parts) > 3 else old_path, old_path=old_path)
            files.append(cur)
            hunk = None
        elif raw.startswith("--- "):
            if cur is not None and raw.strip() == "--- /dev/null":
                cur.is_new = True
        elif raw.startswith("+++ "):
            if cur is not None:
                if raw.strip() == "+++ /dev/null":
                    cur.is_deleted = True
                elif raw.startswith("+++ b/"):
                    cur.path = raw[6:].strip()
        elif raw.startswith("@@") and cur is not None:
            m = _HUNK.match(raw)
            if m:
                old_no, new_no = int(m.group(1)), int(m.group(2))
                hunk = Hunk(old_no, new_no)
                cur.hunks.append(hunk)
        elif hunk is not None:
            if raw.startswith("+"):
                hunk.added.append((new_no, raw[1:]))
                new_no += 1
            elif raw.startswith("-"):
                hunk.removed.append((old_no, raw[1:]))
                old_no += 1
            elif raw.startswith("\\"):
                continue
            else:
                hunk.context.append(raw[1:] if raw else "")
                old_no += 1
                new_no += 1
    return files
