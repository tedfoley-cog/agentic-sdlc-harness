---
name: decompose
description: Splits an approved specification into independent, dependency-ordered delivery units with explicit file scopes so the orchestrator can run them in parallel waves. Used after the after-specify gate is approved.
---

# Decompose

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Group requirements into units that can be implemented and verified alone. Prefer units aligned to one module and one test file.
2. For each unit: `id` (`U1`, `U2`…), `title`, `requirement_ids`, `depends_on` (unit ids), `files` (glob list of files the unit may touch — this becomes Coding's write boundary), `oracle` (how QA verifies independently).
3. Units touching protected paths inherit the two-reviewer rule; say so in the unit.

## Verify
No cycle in `depends_on`; every requirement id appears in exactly one unit; file globs do not overlap between units in the same wave.

## Deliver
`artifacts.units` — JSON array of units. Verdict `PASS`, or `BLOCKED` with `Q-DECOMP-n` if the specification cannot be partitioned without an assumption.
