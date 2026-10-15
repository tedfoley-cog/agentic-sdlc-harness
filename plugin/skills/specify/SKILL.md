---
name: specify
description: Turns a source requirement into a numbered, testable specification with stable requirement ids, explicit invalid-input behaviour and a verification method per requirement. Used first in the new-feature workflow and whenever a gate rejection sends the specification back.
---

# Specify

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED, NEEDS-HUMAN.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Extract every behaviour the source asks for. Assign ids that match the repo contract's `requirement_id_pattern`, one testable statement each (STD-REQ-1).
2. For each quantity: unit, range, behaviour at the limits (STD-REQ-2). For each input: behaviour when missing, late or invalid — refuse / hold / flag, never implicit zero (STD-REQ-3).
3. Name the verification method and, for protection/control behaviour, the independent oracle QA will use (STD-REQ-5). State the safety classification (STD-REQ-6) and scope exclusions (STD-REQ-7).
4. Anything the source leaves open — a missing value, a contradiction, an undefined edge — becomes `questions[]` with id `Q-SPEC-n` and `blocking_units` naming which requirements depend on it. Verdict `BLOCKED` while any question is open; do not guess (STD-REQ-4).

## Verify
Each requirement is testable, has a verification method, has invalid-input behaviour, and quotes no customer identifiers.

## Deliver
`artifacts.specification` — the full specification as markdown. `trace[]` is empty here; requirements are registered by the orchestrator from the ids in the specification. Verdict `PASS` only when there are no open questions.
