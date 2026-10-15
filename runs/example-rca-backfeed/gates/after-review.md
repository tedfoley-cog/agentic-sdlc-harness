# [example-rca-backfeed] Gate: after-review

Run `example-rca-backfeed` — workflow **rca** on `tedfoley-cog/adms-test-automation-demo`.

Requirement: examples/targets/adms/defects/DEF-FLISR-7.md

Apply **gate:approved** or **gate:rejected** (comment first if rejecting). Only a human account may apply these labels; bot labels are ignored.

## Root cause

{
  "hypothesis": "snapshot ordering",
  "evaluation": "Ordering trace demonstrates the mechanism and excludes telemetry lag."
}

## Review

...

Reviewers required: 2

## Trace so far

| Requirement | Design | Code | Test | PR |
|---|---|---|---|---|
| DEF-FLISR-7 | — | — | — | — |

Requirement test coverage: **0%** (0/1); orphans: ['DEF-FLISR-7']
