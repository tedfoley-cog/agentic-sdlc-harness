---
name: trace
description: Audits the traceability matrix built incrementally by earlier stages: every requirement id must map to design, code, test and PR. The orchestrator runs this deterministically from trace.json; this skill is used when an agent must repair or explain gaps.
---

# Trace

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, FAIL.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Load `trace.json` from the run. For each requirement id check design/code/test/pr rows exist.
2. For each gap, find the artifact that should carry the reference and report it (file, test name, PR) — do not fabricate rows.

## Deliver
`artifacts.trace_report` (markdown matrix + gaps). `PASS` when coverage is complete, `FAIL` otherwise.
