"""Governing-standards store. A markdown directory stands in for Confluence; a
Confluence REST store is a drop-in. Every stage loads its required standards at
runtime and must stop (BLOCKED) when one is missing — it never proceeds without them."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path


class StandardMissing(RuntimeError):
    """Raised when a required governing standard cannot be loaded."""


@dataclass
class Standard:
    id: str
    title: str
    body: str
    source: str
    version: str = ""

    def clauses(self) -> list[tuple[str, str]]:
        """(clause-id, text) pairs; clause ids look like `STD-ARCH-3`."""
        return [(m.group(1), m.group(2).strip())
                for m in re.finditer(r"^\s*-\s*\*\*([A-Z][A-Z0-9-]+)\*\*:?\s*(.+)$", self.body, re.M)]


class StandardsStore:
    def get(self, std_id: str) -> Standard:  # pragma: no cover - interface
        raise NotImplementedError

    def load_required(self, ids: list[str]) -> list[Standard]:
        loaded, missing = [], []
        for std_id in ids:
            try:
                loaded.append(self.get(std_id))
            except StandardMissing:
                missing.append(std_id)
        if missing:
            raise StandardMissing(
                "Required governing standard(s) not available: "
                + ", ".join(missing)
                + ". Stage must stop with BLOCKED; do not proceed on assumptions."
            )
        return loaded


class MarkdownStandardsStore(StandardsStore):
    """`standards/<ID>.md` with a `# Title` first line and optional `Version:` line."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def get(self, std_id: str) -> Standard:
        path = self.root / f"{std_id}.md"
        if not path.exists():
            raise StandardMissing(std_id)
        text = path.read_text()
        title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), std_id)
        version = next((ln.split(":", 1)[1].strip() for ln in text.splitlines()
                        if ln.lower().startswith("version:")), "")
        return Standard(std_id, title, text, str(path), version)

    def list_ids(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.md") if p.stem.isupper() or "-" in p.stem)


class ConfluenceStandardsStore(StandardsStore):
    """Confluence Cloud REST v2 pages by title inside one space. Credentials from env
    (CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN); never from config files."""

    def __init__(self, space_key: str, base_url: str | None = None):
        self.space_key = space_key
        self.base_url = (base_url or os.environ.get("CONFLUENCE_BASE_URL", "")).rstrip("/")
        self.email = os.environ.get("CONFLUENCE_EMAIL", "")
        self.token = os.environ.get("CONFLUENCE_API_TOKEN", "")
        if not (self.base_url and self.email and self.token):
            raise StandardMissing("confluence credentials not configured")

    def _get(self, url: str) -> dict:
        import base64

        auth = base64.b64encode(f"{self.email}:{self.token}".encode()).decode()
        req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}",
                                                   "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())

    def get(self, std_id: str) -> Standard:
        q = urllib.parse.quote(std_id)
        url = f"{self.base_url}/wiki/api/v2/pages?title={q}&space-key={self.space_key}&body-format=storage"
        try:
            data = self._get(url)
        except Exception as exc:  # network / auth problems are also "missing"
            raise StandardMissing(f"{std_id} ({exc})") from exc
        results = data.get("results") or []
        if not results:
            raise StandardMissing(std_id)
        page = results[0]
        body = page.get("body", {}).get("storage", {}).get("value", "")
        return Standard(std_id, page.get("title", std_id), body,
                        f"{self.base_url}/wiki/pages/{page.get('id')}", str(page.get("version", {}).get("number", "")))


def store_from_config(standards_cfg: dict, harness_root: str | Path) -> StandardsStore:
    provider = standards_cfg.get("provider", "markdown")
    if provider == "markdown":
        location = standards_cfg.get("location", "standards")
        root = Path(location)
        if not root.is_absolute():
            root = Path(harness_root) / location
        return MarkdownStandardsStore(root)
    if provider == "confluence":
        return ConfluenceStandardsStore(standards_cfg["space_key"], standards_cfg.get("base_url"))
    raise StandardMissing(f"unknown standards provider {provider!r}")


import urllib.parse  # noqa: E402  (kept at bottom to keep the public surface first)
