"""Turn a `devin_session_interact get` text dump into `sessions/<key>.result.json` for the relay backend.

Usage: python tools/relay_result.py <dump.txt> <run-id> <stage-key>
The dump is the human-readable session block; structured_output lines are `    key: value` where list
values are comma-joined Python reprs. This is the glue between the parent Devin session's tooling and
the harness — the rest_v3 backend does the same thing straight from the API."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

LIST_KEYS = {"questions", "evidence", "trace", "files_touched", "standards_loaded"}


def parse_dump(text: str) -> dict:
    head, _, so = text.partition("structured_output:\n")
    meta = dict(re.findall(r"^\s{2}(\w+): (.*)$", head, re.M))
    out: dict = {}
    for line in so.splitlines():
        m = re.match(r"^\s{4}(\w+): (.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if k in LIST_KEYS:
            if v == "(empty)":
                out[k] = []
            elif v.startswith("{"):
                out[k] = ast.literal_eval("[" + v + "]")
            else:
                out[k] = [s.strip() for s in v.split(",") if s.strip()]
        elif k == "artifacts":
            out[k] = ast.literal_eval(v) if v.startswith("{") else {}
        else:
            out[k] = v
    return meta, out


def main() -> None:
    dump, run_id, key = sys.argv[1:4]
    text = Path(dump).read_text()
    if text.lstrip().startswith("{"):  # a raw structured_output JSON (e.g. copied from the session) is accepted as-is
        so = json.loads(text)
        meta = {"url": so.get("session_url"), "devin_mode": so.get("model")}
    else:
        meta, so = parse_dump(text)
    sess_dir = Path("runs") / run_id / "sessions"
    res = {
        "session_id": meta.get("session_id"),
        "session_url": meta.get("url"),
        "status": meta.get("status_detail", "finished"),
        "devin_mode": meta.get("devin_mode"),
        "acus": float(meta.get("acus_consumed") or 0),
        "structured_output": so,
    }
    (sess_dir / f"{key}.result.json").write_text(json.dumps(res, indent=2))
    print(key, "->", so.get("verdict"), f"questions={len(so.get('questions', []))}", f"evidence={len(so.get('evidence', []))}")


if __name__ == "__main__":
    main()
