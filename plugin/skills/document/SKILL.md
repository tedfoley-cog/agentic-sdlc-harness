---
name: document
description: Updates user and operator documentation for what actually changed, generating settings tables from the models module and citing requirement ids. Used after Integrate.
---

# Document

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Diff the integrated PR; list behaviours added or changed, including invalid/missing/boundary input behaviour (STD-DOC-1).
2. Update docs in the files the brief allows; settings/ranges/defaults come from the models module (STD-DOC-2); cite requirement ids (STD-DOC-3); state exclusions (STD-DOC-4).
3. Commit to the integration branch with the trailer.

## Deliver
`trace[]` doc rows, `files_touched`, `artifacts.document`. `PASS` / `BLOCKED`.
