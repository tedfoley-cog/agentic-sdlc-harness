---
name: coding
description: Implements one delivery unit test-first on an agent branch, touching only the files in the brief, and opens a draft PR with the governance trailer and label. Used for each unit after the after-architect gate, and again with verification/QA findings when a loop iteration fails.
---

# Coding

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, FAIL, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. `git checkout -b agent/<run-id>/<unit-id>` from the default branch. Baseline: run the repo's test and lint commands.
2. Pin current behaviour with characterization tests where the unit changes existing logic (STD-SAFETY-2).
3. Write the failing test(s) for the unit's requirement ids first — test names or markers include the id (STD-CODE-1, STD-CODE-7). Commit.
4. Make the smallest change that passes. Never coerce missing/invalid input to zero (STD-CODE-3); never drop a guard without replacing it (STD-CODE-4); models stay in the models module (STD-ARCH-1).
5. If feedback is present (deterministic checks, QA report), resolve every item and reference it in the commit body.
6. Commit with the `AI-Governance:` trailer. Push. Open a **draft** PR with the `ai-generated` label; body: requirement ids, what changed, how to verify.

## Verify
Run build, lint and test; paste the tail as `evidence[]` of kind `command`. Confirm `files_touched` ⊆ brief files.

## Deliver
`branch`, `pr_url`, `files_touched[]`, `trace[]` rows of kind `code` and `test`. `PASS`; `FAIL` if you could not make the tests pass; `BLOCKED` with `Q-CODE-n` if the brief is wrong or incomplete.
