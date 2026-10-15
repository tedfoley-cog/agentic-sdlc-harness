"""Scope and governance checks: touched files ⊆ brief; branch prefix; draft PR;
`ai-generated` label; AI-Governance trailer on every commit."""

from __future__ import annotations

import fnmatch
import re
from typing import Any

from .diffs import DiffFile


def check_scope(files: list[DiffFile], brief_files: list[str]) -> list[dict[str, Any]]:
    findings = []
    for f in files:
        if not any(fnmatch.fnmatch(f.path, pat) for pat in brief_files):
            findings.append({"file": f.path, "rule": "outside-brief",
                             "fix": "Only files named in the brief may change; raise BLOCKED if the brief is wrong."})
    return findings


def check_governance(commit_messages: list[str], pr: dict[str, Any], governance: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    trailer = governance.get("trailer", "AI-Governance")
    pat = re.compile(rf"^{re.escape(trailer)}:\s*run=\S+\s+stage=\S+\s+agent=\S+", re.M)
    for i, msg in enumerate(commit_messages):
        if not pat.search(msg):
            findings.append({"rule": "missing-governance-trailer", "commit": i,
                             "fix": f"Add `{trailer}: run=<id> stage=<stage> agent=devin model=<mode>` trailer."})
    if pr:
        if governance.get("draft_only", True) and not pr.get("draft", False):
            findings.append({"rule": "pr-not-draft", "fix": "Agents open draft PRs only."})
        labels = {lbl if isinstance(lbl, str) else lbl.get("name") for lbl in pr.get("labels", [])}
        if governance.get("pr_label", "ai-generated") not in labels:
            findings.append({"rule": "missing-ai-generated-label", "fix": "Apply the `ai-generated` label."})
        prefix = governance.get("branch_prefix", "agent/")
        head = pr.get("head", "")
        if head and not head.startswith(prefix):
            findings.append({"rule": "branch-prefix", "head": head, "fix": f"Agent branches start with `{prefix}`."})
        if pr.get("merged"):
            findings.append({"rule": "merged-by-agent", "fix": "Agents never merge. Escalate."})
    return findings
