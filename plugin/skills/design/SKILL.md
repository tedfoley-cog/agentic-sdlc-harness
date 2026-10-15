---
name: design
description: Produces the design for the approved specification inside the repository's existing architecture — components, data flow, model/logic separation, error handling and the test strategy per requirement. Used before the Architect review and again when the Architect returns VIOLATION.
---

# Design

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Read the instruction files and the layer map from the brief; locate the existing modules the change touches.
2. For each unit: components changed, interfaces, where data models live versus logic (STD-ARCH-1), the single shared implementation of any numerically sensitive function (STD-ARCH-2), behaviour for absent/stale/out-of-range input (STD-ARCH-4), error-handling design (STD-ARCH-5).
3. Map every requirement id to a component and a test strategy (STD-ARCH-6); emit the mapping as `trace[]` rows of kind `design`.
4. When feedback from the Architect is present, address every finding by clause id and say what changed.

## Verify
No requirement unmapped; no model/logic mixing; no guessed defaults.

## Deliver
`artifacts.design` (markdown), `trace[]` design rows. `PASS` or `BLOCKED` with `Q-DESIGN-n`.
