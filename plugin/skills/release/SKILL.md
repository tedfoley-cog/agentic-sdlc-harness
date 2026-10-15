---
name: release
description: Prepares release notes and a tagged release candidate on the integration branch once the merge gate is approved; never publishes or merges. Optional stage enabled by `release.enabled` in the repo contract.
---

# Release

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED, NEEDS-HUMAN.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Draft release notes from the PR body and trace table: requirement ids, behaviour changes, safety classification, reviewers.
2. Create an annotated candidate tag on the branch head (`rc/<run-id>`) and push the tag. Do not create a GitHub release, do not merge.

## Deliver
`artifacts.release` (notes), `evidence[]` with the tag. `PASS` / `BLOCKED` / `NEEDS-HUMAN`.
