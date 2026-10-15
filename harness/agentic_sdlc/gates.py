"""Human approval gates. Decisions are *read* from a system of record where only a
human could have acted; the orchestrator never infers or defaults a decision.

GitHub-native (default): one gate issue per gate in the harness repo; a human adds
`gate:approved` or `gate:rejected`. The `labeled` event carries the actor; bot
actors are refused. Gate 3 (before merge) counts approving PR reviews from humans
against the reviewer count the repo contract requires.

Jira/Linear implement the same interface (status transition by a human) and are
optional adapters, never dependencies."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass
class GateDecision:
    decision: str            # approved | rejected | waiting
    actor: str | None = None
    actor_type: str | None = None
    at: str | None = None
    ref: str | None = None
    comment: str | None = None
    reviewers: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class GateProvider:
    def open(self, gate: str, title: str, body: str, meta: dict[str, Any]) -> str:  # pragma: no cover
        raise NotImplementedError

    def poll(self, ref: str, meta: dict[str, Any]) -> GateDecision:  # pragma: no cover
        raise NotImplementedError


def _gh(args: list[str], token_env: str = "HARNESS_GH_TOKEN") -> Any:
    env = dict(os.environ)
    tok = os.environ.get(token_env)
    if tok:
        env["GH_TOKEN"] = tok
    out = subprocess.run(["gh", *args], capture_output=True, text=True, env=env, check=True).stdout
    return json.loads(out) if out.strip().startswith(("{", "[")) else out


class GitHubIssueGate(GateProvider):
    def __init__(self, repo: str, approve_label: str = "gate:approved", reject_label: str = "gate:rejected",
                 gh=_gh):
        self.repo, self.approve_label, self.reject_label, self.gh = repo, approve_label, reject_label, gh

    def ensure_labels(self) -> None:
        for name, color, desc in ((self.approve_label, "0e8a16", "Human approved this gate"),
                                  (self.reject_label, "b60205", "Human rejected this gate"),
                                  ("gate", "5319e7", "Agentic SDLC approval gate")):
            try:
                self.gh(["label", "create", name, "--repo", self.repo, "--color", color, "--description", desc,
                         "--force"])
            except subprocess.CalledProcessError:
                pass

    def open(self, gate: str, title: str, body: str, meta: dict[str, Any]) -> str:
        self.ensure_labels()
        out = self.gh(["issue", "create", "--repo", self.repo, "--title", title, "--body", body, "--label", "gate"])
        return out.strip().splitlines()[-1]

    def poll(self, ref: str, meta: dict[str, Any]) -> GateDecision:
        number = ref.rstrip("/").split("/")[-1]
        events = self.gh(["api", f"repos/{self.repo}/issues/{number}/events", "--paginate"])
        decision = GateDecision("waiting", ref=ref)
        for ev in events:
            if ev.get("event") != "labeled":
                continue
            label = ev.get("label", {}).get("name")
            actor = ev.get("actor", {}) or {}
            if label not in (self.approve_label, self.reject_label):
                continue
            if actor.get("type") != "User" or actor.get("login", "").endswith("[bot]"):
                # An automation applied a gate label: refuse it and keep waiting.
                continue
            decision = GateDecision("approved" if label == self.approve_label else "rejected",
                                    actor=actor.get("login"), actor_type=actor.get("type"),
                                    at=ev.get("created_at"), ref=ref)
        if decision.decision != "waiting":
            comments = self.gh(["api", f"repos/{self.repo}/issues/{number}/comments"])
            human = [c for c in comments if (c.get("user") or {}).get("type") == "User"]
            if human:
                decision.comment = human[-1].get("body")
        return decision


class GitHubPRReviewGate(GateProvider):
    """Gate 3: approving reviews on the draft PR itself."""

    def __init__(self, gh=_gh):
        self.gh = gh

    def open(self, gate: str, title: str, body: str, meta: dict[str, Any]) -> str:
        return meta["pr_url"]

    def poll(self, ref: str, meta: dict[str, Any]) -> GateDecision:
        parts = ref.rstrip("/").split("/")
        owner, repo, number = parts[-4], parts[-3], parts[-1]
        reviews = self.gh(["api", f"repos/{owner}/{repo}/pulls/{number}/reviews", "--paginate"])
        latest: dict[str, dict[str, Any]] = {}
        for r in reviews:
            user = r.get("user") or {}
            if user.get("type") != "User" or user.get("login", "").endswith("[bot]"):
                continue
            if r.get("state") in ("APPROVED", "CHANGES_REQUESTED"):
                latest[user["login"]] = r
        approvals = [r for r in latest.values() if r["state"] == "APPROVED"]
        rejected = [r for r in latest.values() if r["state"] == "CHANGES_REQUESTED"]
        required = int(meta.get("reviewers_required", 1))
        if rejected:
            r = rejected[-1]
            return GateDecision("rejected", actor=r["user"]["login"], actor_type="User", at=r.get("submitted_at"),
                                ref=ref, comment=r.get("body"), reviewers=len(approvals))
        if len(approvals) >= required:
            r = approvals[-1]
            return GateDecision("approved", actor=", ".join(a["user"]["login"] for a in approvals),
                                actor_type="User", at=r.get("submitted_at"), ref=ref, reviewers=len(approvals))
        return GateDecision("waiting", ref=ref, reviewers=len(approvals))


class FileGate(GateProvider):
    """Offline/test provider: a human writes `<run>/gates/<gate>.decision.json`."""

    def __init__(self, run_dir):
        from pathlib import Path

        self.dir = Path(run_dir) / "gates"
        self.dir.mkdir(parents=True, exist_ok=True)

    def open(self, gate: str, title: str, body: str, meta: dict[str, Any]) -> str:
        path = self.dir / f"{gate}.md"
        path.write_text(f"# {title}\n\n{body}\n")
        return str(path)

    def poll(self, ref: str, meta: dict[str, Any]) -> GateDecision:
        from pathlib import Path

        path = Path(ref).with_suffix(".decision.json")
        if not path.exists():
            return GateDecision("waiting", ref=ref)
        data = json.loads(path.read_text())
        if data.get("actor_type", "User") != "User":
            return GateDecision("waiting", ref=ref)
        return GateDecision(data["decision"], actor=data["actor"], actor_type="User", at=data.get("at"),
                            ref=ref, comment=data.get("comment"), reviewers=int(data.get("reviewers", 1)))


def provider_from_config(gates_cfg: dict[str, Any], run_dir, gate: str) -> GateProvider:
    provider = gates_cfg.get("provider", "github")
    if provider == "file":
        return FileGate(run_dir)
    if provider == "github":
        if gate == "before-merge":
            return GitHubPRReviewGate()
        return GitHubIssueGate(gates_cfg["repo"], gates_cfg.get("approve_label", "gate:approved"),
                               gates_cfg.get("reject_label", "gate:rejected"))
    if provider in ("jira", "linear"):
        raise NotImplementedError(f"{provider} gate adapter: implement GateProvider.open/poll against the "
                                  f"tracker's transition log; GitHub-native gates are the default")
    raise ValueError(f"unknown gate provider {provider!r}")
