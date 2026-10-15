# STD-RCA — Root-cause analysis standard
Version: 1.2

- **STD-RCA-1**: Explore produces a single falsifiable hypothesis and an evidence package: reproduction steps, failing test, observed vs expected, relevant code excerpts with file:line, and the data that rules out the main alternatives.
- **STD-RCA-2**: Evaluate judges the hypothesis from the evidence package only, without codebase access. It returns CONFIRMED, REFUTED (with the specific objection) or INSUFFICIENT_EVIDENCE (with the exact missing item).
- **STD-RCA-3**: A refutation in round one starts a new exploration round with the objections as constraints. At most two rounds; an unconfirmed hypothesis after round two is published as a RETRACTION, never as a weak finding.
- **STD-RCA-4**: Review decides whether the confirmed root cause is safe to act on: blast radius, affected requirement ids, whether a fail-safe fix exists, and whether the change is safety-critical (two reviewers).
- **STD-RCA-5**: Fix follows STD-SAFETY-3/4: failing test first, smallest fail-safe fix, invariant demonstrated.
- **STD-RCA-6**: The PR body contains Defect, Root cause, Fix, Evidence and Blast radius sections.
