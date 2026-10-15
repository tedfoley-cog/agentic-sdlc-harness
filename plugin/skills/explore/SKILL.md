---
name: explore
description: Reproduces a reported defect, gathers evidence and states one falsifiable root-cause hypothesis with an evidence package the Evaluate stage can judge without code access. Used first in the RCA workflow and again with the evaluator's objections as constraints.
---

# Explore

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED, INSUFFICIENT_EVIDENCE.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Reproduce: write the smallest failing test that demonstrates the defect (STD-SAFETY-3). If it cannot be reproduced, return INSUFFICIENT_EVIDENCE with what you tried.
2. Localise: code excerpts with file:line, the data path, and what rules out the main alternatives (STD-RCA-1).
3. State one hypothesis in one sentence. If feedback from Evaluate is present, each objection is a constraint — address it explicitly.
4. Do not fix anything. Commit the failing test on `agent/<run-id>/explore` only if the brief allows test files.

## Deliver
`artifacts.hypothesis` (string) and `artifacts.evidence_package` (markdown: reproduction, failing test output, excerpts, alternatives ruled out). `PASS` / `BLOCKED` / `INSUFFICIENT_EVIDENCE`.
