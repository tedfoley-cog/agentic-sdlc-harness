"""Per-repository contract: harness.yaml (in the target repo, or an overlay)."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


@dataclass
class ProtectedPath:
    pattern: str
    reviewers: int = 2
    reason: str = ""


@dataclass
class StageBoundary:
    allowed: list[str] = field(default_factory=lambda: ["**"])
    forbidden: list[str] = field(default_factory=list)
    codebase_access: bool = True

    def permits(self, path: str) -> bool:
        if any(fnmatch.fnmatch(path, pat) for pat in self.forbidden):
            return False
        return any(fnmatch.fnmatch(path, pat) for pat in self.allowed)


@dataclass
class HarnessConfig:
    repo: str
    default_branch: str
    commands: dict[str, str]
    requirement_id_pattern: str
    safety_classification: str
    protected_paths: list[ProtectedPath]
    standards: dict[str, Any]
    instructions: list[str]
    boundaries: dict[str, StageBoundary]
    layers: dict[str, list[str]]
    loops: dict[str, int]
    models: dict[str, str]
    gates: dict[str, Any]
    governance: dict[str, Any]
    raw: dict[str, Any] = field(default_factory=dict)

    REQUIRED = ("repo", "commands", "requirement_id_pattern", "safety_classification", "standards")

    @classmethod
    def load(cls, path: str | Path) -> HarnessConfig:
        data = yaml.safe_load(Path(path).read_text()) or {}
        return cls.from_dict(data, source=str(path))

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: str = "<dict>") -> HarnessConfig:
        missing = [k for k in cls.REQUIRED if k not in data]
        if missing:
            raise ConfigError(f"{source}: missing required keys {missing}")
        for cmd in ("build", "test", "lint"):
            if cmd not in data["commands"]:
                raise ConfigError(f"{source}: commands.{cmd} is required")
        if data["safety_classification"] not in ("none", "safety-related", "safety-critical"):
            raise ConfigError(f"{source}: safety_classification must be none|safety-related|safety-critical")
        std = data["standards"]
        if "required" not in std or not std["required"]:
            raise ConfigError(f"{source}: standards.required must list at least one governing standard")
        boundaries = {
            stage: StageBoundary(
                allowed=b.get("allowed", ["**"]),
                forbidden=b.get("forbidden", []),
                codebase_access=b.get("codebase_access", True),
            )
            for stage, b in (data.get("boundaries") or {}).items()
        }
        # Evaluate is evidence-only by contract; a repo cannot opt it back in.
        boundaries["evaluate"] = StageBoundary(allowed=[], forbidden=["**"], codebase_access=False)
        protected = [
            ProtectedPath(p["pattern"], int(p.get("reviewers", 2)), p.get("reason", ""))
            for p in data.get("protected_paths", [])
        ]
        loops = {"architect": 3, "qa": 3, "rca": 2}
        loops.update(data.get("loops") or {})
        models = {"default": "normal", "qa": "ultra", "evaluate": "ultra"}
        models.update(data.get("models") or {})
        if models.get("qa", models["default"]) == models.get("coding", models["default"]):
            raise ConfigError(f"{source}: models.qa must differ from models.coding (independent QA)")
        gates = {"provider": "github", "repo": None, "approve_label": "gate:approved",
                 "reject_label": "gate:rejected", "min_reviewers": 1}
        gates.update(data.get("gates") or {})
        governance = {"branch_prefix": "agent/", "draft_only": True, "pr_label": "ai-generated",
                      "trailer": "AI-Governance"}
        governance.update(data.get("governance") or {})
        return cls(
            repo=data["repo"],
            default_branch=data.get("default_branch", "main"),
            commands=dict(data["commands"]),
            requirement_id_pattern=data["requirement_id_pattern"],
            safety_classification=data["safety_classification"],
            protected_paths=protected,
            standards=std,
            instructions=list(data.get("instructions") or []),
            boundaries=boundaries,
            layers=dict(data.get("layers") or {}),
            loops=loops,
            models=models,
            gates=gates,
            governance=governance,
            raw=data,
        )

    def boundary(self, stage: str) -> StageBoundary:
        return self.boundaries.get(stage, StageBoundary())

    def model_for(self, stage: str) -> str:
        return self.models.get(stage, self.models["default"])

    def reviewers_required(self, files: list[str]) -> int:
        required = int(self.gates.get("min_reviewers", 1))
        for f in files:
            for p in self.protected_paths:
                if fnmatch.fnmatch(f, p.pattern):
                    required = max(required, p.reviewers)
        if self.safety_classification == "safety-critical":
            required = max(required, 2)
        return required

    def protected_hits(self, files: list[str]) -> list[tuple[str, ProtectedPath]]:
        return [(f, p) for f in files for p in self.protected_paths if fnmatch.fnmatch(f, p.pattern)]
