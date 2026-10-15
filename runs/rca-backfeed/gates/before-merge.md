# [rca-backfeed] Gate: before-merge

Run `rca-backfeed` — workflow **rca** on `tedfoley-cog/adms-test-automation-demo`.

Requirement: examples/targets/adms/defects/DEF-FLISR-7.md

Apply **gate:approved** or **gate:rejected** (comment first if rejecting). Only a human account may apply these labels; bot labels are ignored.


Reviewers required: 2

## Trace so far

| Requirement | Design | Code | Test | PR |
|---|---|---|---|---|
| DEF-FLISR-7 | `artifacts.review#proposed-fix-shape` | `backend/app/flisr.py:42`<br>`backend/app/flisr.py:91-151`<br>`backend/app/flisr.py:91-122`<br>`backend/app/flisr.py:136-151`<br>`backend/app/api.py:40-49`<br>`backend/app/flisr.py:91-122`<br>`backend/app/flisr.py:136-151`<br>`backend/app/flisr.py:42`<br>`backend/app/api.py:40-49`<br>`backend/app/flisr.py (build_plan restoration loop guard, commit 20d2a30)`<br>`backend/app/flisr.py:97-107 (commit 20d2a30)`<br>`backend/app/flisr.py:97-107` | `backend/tests/test_flisr_def_flisr_7.py`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_tie_does_not_back_feed_faulted_tail_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_closes_tie_onto_faulted_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_tie_does_not_back_feed_faulted_tail_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_closes_tie_onto_faulted_section`<br>`backend/tests/rca_def_flisr_7_review_probe.py`<br>`backend/tests/test_flisr_characterization.py`<br>`backend/tests/test_flisr_def_flisr_7.py`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_nominal_drill_14_stand_in`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_refusal_is_independent_of_tie_capacity`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_healthy_tail_capacity_boundary_unchanged`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_missing_capacity_still_refuses_with_named_note`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_invalid_capacity_cannot_bypass_the_guard`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_error_paths_retained`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_tie_on_any_faulted_endpoint_is_refused`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_pick_up_through_non_scada_downstream_switch_is_refused`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_api_plan_matches_direct_plan`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_seeded_plans_agree_with_oracle_and_never_back_feed` | `https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13`<br>`https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13`<br>`https://github.com/tedfoley-cog/adms-test-automation-demo/pull/14`<br>`https://github.com/tedfoley-cog/adms-test-automation-demo/pull/14` |

Requirement test coverage: **100%** (1/1); orphans: none
