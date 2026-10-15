# STD-REQ — Requirements specification standard
Version: 1.2

- **STD-REQ-1**: Every requirement has a stable id matching the repo contract's `requirement_id_pattern` and is written as one testable statement (shall/shall not, measurable bound, named inputs and outputs).
- **STD-REQ-2**: A requirement that depends on a quantity (threshold, ratio, timing, CT ratio, per-unit base) states the unit, the range and the behaviour at the range limits.
- **STD-REQ-3**: Missing, late or invalid inputs are specified explicitly. "Treat as zero" is never an implicit default; the specification states refuse / hold-last-value / flag-quality for each input.
- **STD-REQ-4**: Ambiguities, contradictions and missing acceptance criteria in the source are recorded as questions with stable ids (`Q-SPEC-n`). The specifier does not resolve them by assumption; work that does not depend on the open question continues.
- **STD-REQ-5**: Each requirement names its verification method (test, analysis, inspection, demonstration) and, for protection or control functions, the independent oracle QA will use.
- **STD-REQ-6**: Safety classification (IEC 61508-3 context: none / safety-related / safety-critical) is stated for the change and inherited by every unit derived from it.
- **STD-REQ-7**: Scope exclusions are listed so that later stages can reject scope creep rather than absorb it.
