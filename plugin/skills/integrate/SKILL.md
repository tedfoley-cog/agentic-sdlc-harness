---
name: integrate
description: Assembles the verified unit branches into one draft PR against the default branch, rebases, re-runs the suite, and completes the governance metadata and PR body. Used once all units have passed QA.
---

# Integrate

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, FAIL, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. If there is one unit branch, use it. Otherwise create `agent/<run-id>/integration`, merge each unit branch in dependency order, resolve conflicts without changing behaviour.
2. Re-run build, lint, test on the integrated branch.
3. Ensure every commit has the trailer, the PR is a draft, has `ai-generated`, and its body has: requirement ids, summary per unit, trace table from the brief, evidence links. Mark the PR **ready for review** — this is the last agent action (STD-GOV-1). Do not request specific reviewers; the harness computes the required count.

## Verify
`gh pr view` shows draft=true… then ready-for-review, label present, no merge.

## Deliver
`pr_url`, `branch`, `trace[]` pr rows (one per requirement id), `artifacts.integrate` (markdown summary). `PASS` / `FAIL` / `BLOCKED`.
