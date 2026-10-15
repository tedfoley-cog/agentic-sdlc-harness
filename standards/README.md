# Governing standards store

This directory stands in for the Confluence space that holds the organisation's governing
standards. Stage skills load the standards they need **at runtime** (`standards.required`
and `standards.by_stage` in `harness.yaml`) and stop with `BLOCKED` when one is missing.
Swap the provider to `confluence` in `harness.yaml` to read the same page titles from
Confluence Cloud (credentials from environment variables only).

Clauses are written as `- **STD-X-n**: text` so skills can cite them by id in evidence.
Standards referenced: IEC 60255-1 / -187-1, IEC 61508-3, IEC 61850-7-4, IEEE C37.118,
IEEE C37.2. Nothing here claims certification credit; the harness produces a tool
classification argument as a finding for the assessor.
