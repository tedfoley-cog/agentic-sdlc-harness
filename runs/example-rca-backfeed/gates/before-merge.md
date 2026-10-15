# [example-rca-backfeed] Gate: before-merge

Run `example-rca-backfeed` — workflow **rca** on `tedfoley-cog/adms-test-automation-demo`.

Requirement: examples/targets/adms/defects/DEF-FLISR-7.md

Apply **gate:approved** or **gate:rejected** (comment first if rejecting). Only a human account may apply these labels; bot labels are ignored.


Reviewers required: 2

## Trace so far

| Requirement | Design | Code | Test | PR |
|---|---|---|---|---|
| DEF-FLISR-7 | — | `backend/app/flisr.py::plan_restoration` | `test_flisr.py::test_def_flisr_7_no_backfeed` | `https://github.com/example-org/product-repo/pull/102` |

Requirement test coverage: **100%** (1/1); orphans: none
