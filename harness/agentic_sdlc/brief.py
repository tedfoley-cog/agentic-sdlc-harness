"""Compiles the self-contained brief a stage subagent receives. A child session sees
nothing but this prompt, the target repo (unless the stage is evidence-only) and the
structured-output schema — so everything it needs is in here: role, contract, governing
standards, repo contract, boundaries, prior artifacts and loop feedback."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import HarnessConfig
from .standards import Standard
from .verdicts import ALLOWED_BY_STAGE

ROLE = {
    "specify": "Specification engineer. Turn the source requirement into a numbered, testable specification.",
    "decompose": "Delivery planner. Split the approved specification into independent, dependency-ordered units.",
    "design": "Designer. Produce the design for the specification within the repo's architecture.",
    "architect": "Architecture reviewer. Independently check the design against the governing standards.",
    "coding": "Implementer. Write a failing test first, then the smallest change that makes it pass.",
    "qa": "Independent QA. Re-run every check yourself with your own oracle/test vectors; trust nothing from Coding.",
    "integrate": "Integrator. Assemble unit branches into one draft PR with the required governance metadata.",
    "document": "Technical writer. Update user/operator documentation for what actually changed.",
    "trace": "Traceability auditor. Confirm every requirement id maps to design, code, test and PR.",
    "release": "Release engineer. Prepare release notes and a tagged candidate; never publish without a human.",
    "explore": "Investigator. Reproduce the defect and gather evidence for a root-cause hypothesis.",
    "evaluate": "Evidence assessor. Judge the root-cause hypothesis from the evidence package alone.",
    "review": "Independent reviewer. Decide whether the confirmed root cause is fit to act on.",
    "fix": "Fixer. Reproduce with a failing test, then apply the smallest fail-safe fix.",
}


def compile_brief(*, stage: str, cfg: HarnessConfig, run_id: str, attempt: int, skill_text: str,
                  standards: list[Standard], artifacts: dict[str, Any], requirement: str,
                  feedback: list[dict[str, Any]] | None, unit: dict[str, Any] | None,
                  answers: list[dict[str, Any]] | None, model: str, evidence_only: bool = False) -> str:
    boundary = cfg.boundary(stage)
    allowed = ", ".join(ALLOWED_BY_STAGE.get(stage, ()))
    parts: list[str] = []
    parts.append(f"# Agentic SDLC stage brief — {stage.upper()} (run {run_id}, attempt {attempt})\n")
    parts.append(f"Role: {ROLE.get(stage, stage)}\n")
    parts.append(
        "## Contract\n"
        "Work in four phases and report each in your final output: **prepare** (load the governing "
        "standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, "
        "**verify** (re-check your own output against the standards and the repo contract), **deliver** "
        "(structured verdict with evidence).\n\n"
        f"Allowed verdicts for this stage: {allowed}. Every verdict needs `evidence[]` entries that point at "
        "files, tests, commands, commits, PRs or standard clauses you actually used or produced.\n"
        "Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with "
        "stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.\n"
        "You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; "
        f"branches start with `{cfg.governance['branch_prefix']}`; every commit carries the trailer "
        f"`{cfg.governance['trailer']}: run={run_id} stage={stage} agent=devin model={model}`; PRs carry the "
        f"`{cfg.governance['pr_label']}` label.\n"
    )
    if evidence_only:
        parts.append("## Access\nYou have **no codebase access**. Judge only the evidence package below. If the "
                     "evidence is insufficient, say so (INSUFFICIENT_EVIDENCE) and list exactly what is missing.\n")
    else:
        parts.append(
            "## Access and boundaries\n"
            f"Target repository: `{cfg.repo}` (default branch `{cfg.default_branch}`). Safety classification: "
            f"**{cfg.safety_classification}**.\n"
            f"Files you may change: {boundary.allowed or ['(none)']}. Files you must not change: "
            f"{boundary.forbidden or ['(none)']}.\n"
            f"Commands — build: `{cfg.commands['build']}`; test: `{cfg.commands['test']}`; lint: `{cfg.commands['lint']}`.\n"
            f"Requirement ids match `{cfg.requirement_id_pattern}`; reference them verbatim.\n"
            + (f"Protected paths (two human reviewers): {[p.pattern for p in cfg.protected_paths]}.\n"
               if cfg.protected_paths else "")
            + (f"Repo instruction files to read first: {cfg.instructions}.\n" if cfg.instructions else "")
            + (f"Layer visibility: {json.dumps(cfg.layers)}.\n" if cfg.layers else "")
        )
    parts.append("## Governing standards (loaded at runtime — confirm each id in `standards_loaded`)\n")
    for s in standards:
        parts.append(f"### {s.id} — {s.title}\n\n{s.body.strip()}\n")
    parts.append("## Source requirement\n\n" + requirement.strip() + "\n")
    if unit:
        parts.append("## Your unit\n\n```json\n" + json.dumps(unit, indent=2) + "\n```\n")
    if answers:
        parts.append("## Human answers to earlier questions (recorded gate actions)\n")
        for a in answers:
            parts.append(f"- **{a['id']}** ({a.get('by', 'human')}): {a['answer']}")
        parts.append("")
    for name, art in artifacts.items():
        if art in (None, "", [], {}):
            continue
        body = art if isinstance(art, str) else json.dumps(art, indent=2)
        parts.append(f"## Prior artifact: {name}\n\n{body}\n")
    if feedback:
        parts.append("## Feedback from the previous iteration (resolve every item or explain why not)\n")
        parts.append("```json\n" + json.dumps(feedback, indent=2) + "\n```\n")
    parts.append("## Stage skill\n\n" + skill_text.strip() + "\n")
    parts.append(
        "## Deliver\n"
        "Finish by calling provide_structured_output with an object matching the schema you were given: "
        "`verdict`, `summary`, `evidence[]`, and where relevant `questions[]`, `trace[]` (requirement_id/kind/ref), "
        "`files_touched[]`, `branch`, `pr_url`, `standards_loaded[]`, `artifacts{}` (your stage's named outputs "
        "as markdown or JSON strings), `model`.\n"
    )
    return "\n".join(parts)


def write_brief(run_dir: str | Path, stage_key: str, text: str) -> Path:
    p = Path(run_dir) / "briefs" / f"{stage_key.replace(':', '_')}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p
