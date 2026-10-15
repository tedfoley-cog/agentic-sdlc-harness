---
name: qa
description: Independently verifies a coded unit on a different agent mode: re-runs every check, writes its own oracle and test vectors, checks the three known failure modes and requirement coverage. Used after deterministic verification passes; a FAIL returns to Coding with actionable findings.
---

# Qa

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, FAIL, BLOCKED, INSUFFICIENT_EVIDENCE.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Check out the unit's branch. Run build, lint and the full test suite yourself (STD-QA-2). Treat Coding's report as hypotheses (STD-QA-1).
2. Build an independent oracle for the behaviour (closed-form, table or reference model) and your own vectors: nominal, boundary, missing input, invalid input (STD-QA-3). Add them as a separate test file under the unit's file scope if the brief allows; otherwise run them ad hoc and attach the output.
3. Check model/logic mixing, deleted error handling, missing-as-zero in the diff (STD-QA-4).
4. Verify each requirement id in scope has a passing test referencing it (STD-QA-6).

## Verify
Every FAIL item has requirement id, vector/test, observed vs expected, file:line (STD-QA-5).

## Deliver
`artifacts.qa_report` (markdown), `trace[]` test rows for your own tests, `evidence[]` command outputs. `PASS` / `FAIL` / `INSUFFICIENT_EVIDENCE` (could not run) / `BLOCKED`.
