---
name: review
description: Independently decides whether a confirmed root cause is safe to act on: blast radius, affected requirement ids, availability of a fail-safe fix, and safety classification. Used after Evaluate confirms; its output is what the human approves at the after-review gate.
---

# Review

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: CONFIRMED, REFUTED, NEEDS-HUMAN, RETRACTION.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. From the confirmed hypothesis and the repository, list affected requirement ids, callers and operational scenarios (STD-RCA-4).
2. Propose the fail-safe fix shape (not the code) and the invariant Fix must demonstrate (STD-SAFETY-5). State whether the change touches protected paths.
3. If the root cause is confirmed but acting on it needs a product decision, return NEEDS-HUMAN with the decision stated.

## Deliver
`artifacts.review` (markdown: Defect, Root cause, Blast radius, Proposed fix, Invariant, Reviewers required). `CONFIRMED` / `REFUTED` / `NEEDS-HUMAN`.
