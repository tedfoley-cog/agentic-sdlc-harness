# [example-feature-tie-capacity] Gate: before-merge

Run `example-feature-tie-capacity` — workflow **feature** on `tedfoley-cog/adms-test-automation-demo`.

Requirement: examples/targets/adms/requirements/REQ-tie-capacity.md

Apply **gate:approved** or **gate:rejected** (comment first if rejecting). Only a human account may apply these labels; bot labels are ignored.


Reviewers required: 2

## Trace so far

| Requirement | Design | Code | Test | PR |
|---|---|---|---|---|
| REQ-FLISR-101 | `D-FLISR-1` | `backend/app/flisr.py::tie_capacity` | `test_flisr_capacity.py::test_req_flisr_101` | `https://github.com/example-org/product-repo/pull/101` |
| REQ-FLISR-102 | `D-FLISR-1` | `backend/app/flisr.py::plan_restoration` | `test_flisr_capacity.py::test_req_flisr_102` | `https://github.com/example-org/product-repo/pull/101` |
| REQ-FLISR-103 | `D-FLISR-1` | `backend/app/flisr.py::plan_restoration` | `test_flisr_stale.py::test_req_flisr_103` | `https://github.com/example-org/product-repo/pull/101` |

Requirement test coverage: **100%** (3/3); orphans: none
