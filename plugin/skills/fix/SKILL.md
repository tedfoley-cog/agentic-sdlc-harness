---
name: fix
description: Applies the reviewed root-cause fix test-first on an agent branch: characterization tests, the reproducing failing test, the smallest fail-safe change, the invariant over seeded inputs, and a draft PR with Defect/Root cause/Fix/Evidence/Blast radius sections. Used after the after-review gate.
---

# Fix

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, FAIL, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. `git checkout -b agent/<run-id>/fix`. Baseline; pin behaviour with characterization tests (STD-SAFETY-2).
2. Commit the failing reproduction test first (STD-SAFETY-3), then the smallest fail-safe change (STD-SAFETY-4); never coerce missing input to zero; never drop a guard.
3. Demonstrate the invariant from the review over seeded inputs — at least 500 when a generator exists (STD-SAFETY-5).
4. Run build, lint, test. Commit with the trailer; push; open a **draft** PR with `ai-generated`, body sections Defect / Root cause / Fix / Evidence / Blast radius (STD-RCA-6).
5. With feedback present (deterministic checks, QA), resolve every item.

## Deliver
`branch`, `pr_url`, `files_touched`, `trace[]` code and test rows. `PASS` / `FAIL` / `BLOCKED`.
