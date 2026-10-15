---
name: evaluate
description: Judges a root-cause hypothesis strictly from the evidence package, with no codebase access, and returns CONFIRMED, REFUTED with a specific objection, or INSUFFICIENT_EVIDENCE with the exact missing item. Used after every Explore round.
---

# Evaluate

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: CONFIRMED, REFUTED, INSUFFICIENT_EVIDENCE.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Read only the evidence package in the brief. You have no repository and must not clone one.
2. Ask: does the evidence show the mechanism, not just the symptom? Does it rule out alternatives? Would the hypothesis predict the failing test's observed value?
3. Each objection is one `evidence[]` entry of kind `note` with the gap stated precisely so Explore can act on it (STD-RCA-2).

## Deliver
`artifacts.evaluation` (markdown). `CONFIRMED` / `REFUTED` / `INSUFFICIENT_EVIDENCE`.
