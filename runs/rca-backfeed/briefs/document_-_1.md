# Agentic SDLC stage brief — DOCUMENT (run rca-backfeed, attempt 1)

Role: Technical writer. Update user/operator documentation for what actually changed.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: PASS, BLOCKED. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=rca-backfeed stage=document agent=devin model=normal`; PRs carry the `ai-generated` label.

## Access and boundaries
Target repository: `tedfoley-cog/adms-test-automation-demo` (default branch `main`). Safety classification: **safety-critical**.
Files you may change: ['docs/**', 'README.md']. Files you must not change: ['(none)'].
Commands — build: `npm --prefix console ci --no-audit --no-fund && npm --prefix console run build`; test: `pytest backend -q`; lint: `ruff check backend`.
Requirement ids match `(?:REQ|DEF)-[A-Z]+-\d{1,3}`; reference them verbatim.
Protected paths (two human reviewers): ['backend/app/flisr.py', 'firmware/src/**'].
Repo instruction files to read first: ['.agents/skills/safety-critical-change/SKILL.md', 'DEMO_NOTES.md'].
Layer visibility: {"models": ["backend/app/models.py"], "logic": ["backend/app/flisr.py", "backend/app/state_estimator.py", "backend/app/agc.py", "backend/app/network.py", "backend/app/savecase.py"], "api": ["backend/app/api.py"], "ui": ["console/**"], "visibility": {"api": ["logic", "models"], "logic": ["models"], "ui": ["api"]}}.

## Governing standards (loaded at runtime — confirm each id in `standards_loaded`)

### STD-DOC — STD-DOC — Documentation standard

# STD-DOC — Documentation standard
Version: 1.0

- **STD-DOC-1**: Documentation describes what the change does and the behaviour for invalid, missing and boundary inputs — the same cases the tests cover.
- **STD-DOC-2**: Settings, units, ranges and defaults are documented from the models module, not re-typed; discrepancies are a FAIL in the Document stage.
- **STD-DOC-3**: Each documented behaviour cites the requirement id it implements.
- **STD-DOC-4**: Operator-facing documentation states what the function does *not* do (scope exclusions from STD-REQ-7).

### STD-GOV — STD-GOV — AI governance and delivery standard

# STD-GOV — AI governance and delivery standard
Version: 1.1

- **STD-GOV-1**: Agents work on branches prefixed `agent/` and open draft pull requests only. Marking ready-for-review is the last agent action; approving, merging and moving tickets past ready-for-review are human actions.
- **STD-GOV-2**: Every commit carries `AI-Governance: run=<run-id> stage=<stage> agent=<agent> model=<mode>`; every PR carries the `ai-generated` label and a body with requirement ids, evidence and the trace table.
- **STD-GOV-3**: Human gate decisions are taken in a system of record where only a human account can act (GitHub label event / PR review). Decisions by bot accounts are ignored. Agents never infer a decision from silence.
- **STD-GOV-4**: The audit log is append-only and hash-chained; it records agent, run id, stage, brief, model, timestamps, artifacts read and produced, verdicts, gate decisions and the human decision-maker.
- **STD-GOV-5**: Feedback loops are bounded by the repo contract; on reaching the limit the run escalates to NEEDS-HUMAN with the full loop history.
- **STD-GOV-6**: Protected paths require the configured number of human reviewers irrespective of agent confidence; safety-critical classification implies at least two.
- **STD-GOV-7**: Customer identifiers, personal names and credentials never appear in briefs, logs or PRs.

### STD-SAFETY — STD-SAFETY — Safety-related change standard

# STD-SAFETY — Safety-related change standard
Version: 3.1

- **STD-SAFETY-1**: A change touching protection, control or isolation logic is safety-critical regardless of size and requires two human reviewers before merge (IEC 61508-3 independence of verification).
- **STD-SAFETY-2**: Current behaviour is pinned with characterization tests before any change so regressions are visible as test failures, not as field events.
- **STD-SAFETY-3**: A defect is reproduced with a failing test before it is fixed. If it cannot be reproduced, the stage stops with INSUFFICIENT_EVIDENCE rather than applying a speculative fix.
- **STD-SAFETY-4**: The fix is the smallest change that makes the failing test pass while keeping the characterization tests green; fail-safe (refuse / block / hold) is preferred over "best effort".
- **STD-SAFETY-5**: A safety invariant is stated and demonstrated over seeded inputs (at least 500 where a generator exists) — for example "a de-energised fault section is never back-fed during restoration" or "the differential element never operates below the restraint characteristic".
- **STD-SAFETY-6**: Operate boundaries are compared against an independent closed-form oracle, with tolerance stated in per-unit and in engineering units (IEC 60255-187-1 accuracy classes).
- **STD-SAFETY-7**: The harness does not claim tool certification credit. Each run produces a tool-classification argument (IEC 61508-3 T1/T2/T3) as a finding for the assessor.
- **STD-SAFETY-8**: Agents never access production systems, production secrets or field devices.

## Source requirement

# DEF-FLISR-7 — restoration back-fed a de-energised section

During drill 14 the restoration plan closed a tie switch that re-energised the faulted section.
Expected: the faulted section stays isolated. Observed: `plan_restoration` returned a close action
on the tie adjacent to the faulted section. Reproduce with the drill-14 savecase in `backend/tests/data`.

## Human answers to earlier questions (recorded gate actions)

- **Q-EXPLORE-1** (protection-reviewer-standin): Confirmed in writing: the drill-14 savecase was not retained. The shipped FDR-1201 scenario (fault on SEC-1201-04, lockout CB-1201, tie TIE-1201-1405) stands in for drill 14 for this investigation; the defect report has been corrected to say so.
- **Q-EXPLORE-2** (protection-reviewer-standin): Confirmed: app.flisr.build_plan (backend/app/flisr.py) called from POST /flisr/plan is the function under investigation. The defect report's 'plan_restoration' was a naming error and has been corrected.
- **Q-EXPLORE-3** (protection-reviewer-standin): Yes, corrected: the repo contract layer map now lists backend/app/state_estimator.py and backend/app/api.py.
- **Q-EXPLORE-4** (protection-reviewer-standin): Existing exception. Later stages lint the files they touch (ruff check backend) and must not fix tools/build_coverage_report.py in this change; it goes in a separate change.
- **Q-REVIEW-1** (protection-reviewer-standin): Yes: a separate defect will be filed for build_plan not checking that the alternate-feeder side of a tie is healthy before closing. Out of scope for DEF-FLISR-7; Fix must not address it.
- **Q-REVIEW-2** (protection-reviewer-standin): Confirmed accounting for a refused tie: the faulted section's customers count once in customers_remaining and are excluded from customers_restored and transferred_load_kw (DEF-FLISR-7 scenario: 0 restored / 341 remaining / 0 kW). The refusal is recorded in the plan's notes naming the tie and the faulted section.

## Prior artifact: root_cause

{
  "hypothesis": "build_plan (backend/app/flisr.py) never treats a tie switch as a boundary of the faulted section: _isolation_switches skips ties (flisr.py:42) and the restoration loop (flisr.py:91-122, via _nodes_restored_by flisr.py:136-151) never removes the faulted section's nodes from a tie's pick-up set, so when the faulted section's downstream end is a tie (SEC-1201-04 / TIE-1201-1405) that section is itself the tie's restoration candidate and the tie is closed whenever tie capacity >= the faulted section's load (1490 kW).",
  "evaluation": "# DEF-FLISR-7 \u2014 Evaluate (run rca-backfeed, attempt 1)\n\n## Prepare\nStandards loaded from the brief: STD-GOV v1.1, STD-RCA v1.2, STD-SAFETY v3.1. All three present and readable.\nRepo contract: not included in the brief and the brief forbids codebase access, so it was not read. The verdict below does not depend on it (noted, not blocking).\n\n## Verdict: CONFIRMED\n\nHypothesis under test: `build_plan` never treats a tie switch as a boundary of the faulted section \u2014 (a) `_isolation_switches` skips ties (flisr.py:42), and (b) the restoration loop (flisr.py:91-122 via `_nodes_restored_by` flisr.py:136-151) never removes the faulted section's nodes from a tie's pick-up set \u2014 so when the faulted section's downstream end is a tie, the tie is closed onto it whenever tie capacity >= that section's load.\n\n### Does the evidence show the mechanism, not just the symptom?\nYes. Three observed numbers in the failing output are only explainable by the faulted section itself being the tie's pick-up set:\n- `customers_restored` == `customers_remaining` == 341 (SEC-1201-04's own customer count, counted both as lost and as restored);\n- `transferred_load_kw` == 1490.0 == SEC-1201-04's load (network.py:90-91 `load_on_nodes`, to_node N-1201-4 in the candidate set);\n- \"back-feed 3 nodes\" == the island {N-1201-4, N-1201-3A, ALT-1405} = both ends of SEC-1201-04 plus the alternate source, exactly what `_nodes_restored_by` returns with REC-1201-2 open and the tie closed.\nThe sweep A threshold (1489 kW -> no close, 1490 kW -> close) shows capacity is the only gate and that the gated quantity is the faulted section's load.\n\n### Does it rule out alternatives?\nYes, with data rather than argument:\n- Mislocation: faulted_section is SEC-1201-04 in every run.\n- CB-1201 reclose as the back-feed path: at 0/1489 kW the plan still closes CB-1201 and SEC-1201-04 stays dead (REC-1201-2 holds it).\n- Capacity check defect: 1489/1490 behaves exactly as written.\n- Tie restoration wrong in general: the same tie closed for SEC-1201-02/03 faults never back-feeds (sweep A, 0 cases).\n- Tie-skip at line 42 alone: the monkeypatched counterfactual (tie added to isolation) still yields TIE close + back_fed=True because flisr.py:145-146 re-closes the tie in the what-if and 91-122 never exclude faulted nodes. This establishes that both halves of the hypothesis are necessary \u2014 important for Fix.\n- Sweep C (500 seeded feeders): back-feed in 150/150 cases where faulted section ends at the tie and the tie is closed; 0/350 otherwise. A single-cause hypothesis predicts exactly this partition.\n\n### Would the hypothesis predict the failing test's observed value?\nYes. Predicted plan for SEC-1201-04 fault with 2000 kW tie capacity: isolation [REC-1201-2], restoration [CB-1201 close, TIE-1201-1405 close], SEC-1201-04 nodes {N-1201-3A, N-1201-4} energised. That is the recorded assertion failure, both direct and via POST /flisr/plan.\n\n### Falsifiability\nThree concrete predictions are stated with the counterexample condition; predictions 1-3 are each exercised by sweep A or C.\n\n## Checks against standards\n- STD-RCA-1: single hypothesis, reproduction steps, failing tests (2) with output, observed-vs-expected table, file:line excerpts, alternative-ruling data \u2014 all present.\n- STD-RCA-2: judged from the package only; no repository used.\n- STD-SAFETY-3: defect reproduced by failing tests before any fix; no production code changed in Explore.\n- STD-GOV-7: no customer identifiers, personal names or credentials in the package.\n\n## Non-blocking notes for the next stages\n1. Code excerpts: only flisr.py:42 is quoted verbatim; lines 44-59, 91-122, 141-151 and network.py:90-91 are paraphrased with file:line. The behavioural evidence (341/341, 1490 kW, 1489/1490 threshold, counterfactual B) independently establishes the mechanism, so this does not weaken the verdict, but Review should spot-check those ranges when it has codebase access.\n2. For Fix (STD-SAFETY-4): counterfactual B shows that adding ties to isolation is not sufficient; the restoration candidate set must exclude the faulted section's nodes (or the tie whose from_node/to_node is on the faulted section must be refused). The fail-safe direction is \"refuse the tie close\", not \"best-effort re-route\".\n3. The \"Expected\" column's \"TIE-1201-1405 kept open\" is a fix design choice, not evidence; it was not used in the judgement.\n4. `backend/app/flisr.py` is a protected, safety-critical path: two human reviewers (STD-GOV-6, STD-SAFETY-1).\n5. Invariant for STD-SAFETY-5 is already stated in the package: \"a de-energised fault section is never back-fed during restoration\"; the sweep C generator (random.Random(7), 500 cases) can be reused.\n"
}

## Prior artifact: evidence_package

{
  "hypothesis": "build_plan (backend/app/flisr.py) never treats a tie switch as a boundary of the faulted section: _isolation_switches skips ties (flisr.py:42) and the restoration loop (flisr.py:91-122, via _nodes_restored_by flisr.py:136-151) never removes the faulted section's nodes from a tie's pick-up set, so when the faulted section's downstream end is a tie (SEC-1201-04 / TIE-1201-1405) that section is itself the tie's restoration candidate and the tie is closed whenever tie capacity >= the faulted section's load (1490 kW).",
  "evidence_package": "# DEF-FLISR-7 evidence package (run rca-backfeed, explore, attempt 2)\n\nBranch `agent/rca-backfeed/explore` @ c43f8c42a2142b0043a5da5bf125e59258866547 (parent a6c2139 from attempt 1). No production code changed.\n\n## Inputs (from recorded human answers)\n- Q-EXPLORE-1: FDR-1201 scenario stands in for drill 14 (fault SEC-1201-04, lockout CB-1201, tie TIE-1201-1405).\n- Q-EXPLORE-2: function under test is `app.flisr.build_plan`, called from `POST /flisr/plan` (backend/app/api.py:40-49).\n- Q-EXPLORE-4: `ruff check backend tools` fails on main in tools/build_coverage_report.py (UP017), an existing exception; touched files linted with `ruff check backend` (clean).\n\n## FDR-1201 topology (backend/data/feeder_model.json)\n```\nSRC-1201 -[CB-1201 breaker]- BUS-1201 -(SEC-1201-01)- N-1201-1 -[REC-1201-1]- N-1201-1A -(SEC-1201-02)- N-1201-2\n -[SEC-SW-1201-1]- N-1201-2A -(SEC-1201-03)- N-1201-3 -[REC-1201-2]- N-1201-3A -(SEC-1201-04)- N-1201-4 -[TIE-1201-1405 tie, NO]- ALT-1405\n```\nSEC-1201-04: 341 customers, 1490 kW. Only tie on the feeder is TIE-1201-1405 and it is directly on SEC-1201-04's downstream node N-1201-4.\n\n## Reproduction\n1. Load FDR-1201; set fault_indicator True on SEC-1201-01..03, False on SEC-1201-04 (locate_fault -> SEC-1201-04); set CB-1201.open = True (lockout). The shipped model has CB-1201 closed, so the API returns 409 unless lockout is set.\n2. `build_plan(feeder, \"CB-1201\", {\"TIE-1201-1405\": 2000.0})`, directly and through `POST /flisr/plan` (TestClient, `api.load_network` monkeypatched to return the modified model).\n3. Apply the plan's isolation + restoration steps and compute energised nodes from SRC-1201 and ALT-1405.\n\nCommand: `pytest backend -q` -> `2 failed, 2 passed`. Both failures are the new DEF-FLISR-7 tests; the 2 existing tests in backend/tests/test_flisr.py still pass.\n\n### Failing test output\n```\nbackend/tests/test_flisr_def_flisr_7.py:22: AssertionError: plan re-energises SEC-1201-04: restoration=[('CB-1201', 'close'), ('TIE-1201-1405', 'close')]\n  assert not ({'N-1201-3A', 'N-1201-4'} & {'ALT-1405', 'BUS-1201', 'N-1201-1', 'N-1201-1A', 'N-1201-2', 'N-1201-2A', ...})\nbackend/tests/test_flisr_def_flisr_7.py:52: AssertionError: POST /flisr/plan closes TIE-1201-1405 onto SEC-1201-04: {... 'restoration': [CB-1201 close, TIE-1201-1405 close 'back-feed 3 nodes from alternate source'], 'customers_restored': 341, 'customers_remaining': 341, 'transferred_load_kw': 1490.0}\n```\n\n### Observed vs expected\n| | Observed | Expected |\n|---|---|---|\n| faulted_section | SEC-1201-04 | SEC-1201-04 |\n| isolation | REC-1201-2 open (upstream only) | SEC-1201-04 bounded on both ends: REC-1201-2 open and TIE-1201-1405 kept open |\n| restoration | CB-1201 close, **TIE-1201-1405 close** | CB-1201 close only (nothing healthy downstream of SEC-1201-04 to restore) |\n| SEC-1201-04 after plan | energised from ALT-1405 | de-energised |\n| customers_restored / remaining | 341 / 341 (the same 341 customers counted both ways) | 0 / 341 |\n| transferred_load_kw | 1490 (the faulted section's own load) | 0 |\n\n## Code excerpts\n- flisr.py:41-43 \u2014 ties are dropped before isolation is considered:\n  `for switch in feeder.switches:` / `if not switch.scada_controllable or switch.kind.value == \"tie\": continue`\n- flisr.py:44-59 \u2014 isolation only looks for a switch whose to_node == section.from_node (upstream) or from_node == section.to_node (downstream). For SEC-1201-04 the only downstream match is TIE-1201-1405 (from_node N-1201-4), which was skipped at line 42, so isolation = [REC-1201-2]. No error is raised because `steps` is non-empty (line 60).\n- flisr.py:91-122 \u2014 every SCADA tie is a restoration candidate; the only gate is `transferred > available` (line 99). Nothing compares candidate_nodes with the faulted section.\n- flisr.py:141-151 `_nodes_restored_by` \u2014 opens isolated switches, closes the tie, returns `energised_nodes(from tie.from_node) - energised_nodes(from source)`. With REC-1201-2 open, the tie's island is {N-1201-4, N-1201-3A, ALT-1405} = both ends of SEC-1201-04. The faulted section is not subtracted.\n- flisr.py:145-146 \u2014 the tie is forced closed after the isolated switches are opened, so even a tie listed in isolation would be re-closed in the what-if.\n- network.py:90-91 `load_on_nodes` \u2014 the 1490 kW \"transferred\" is SEC-1201-04's own load (to_node N-1201-4 in the candidate set).\n\n## Alternatives ruled out (diagnostic: `PYTHONPATH=backend python backend/tests/rca_def_flisr_7_sweep.py`)\nA. FDR-1201, every locatable faulted section x tie capacity:\n```\nfaulted     | cap_kw | isolation                      | restoration                      | tie_candidates                          | back_fed\nSEC-1201-02 | 0/1489/1490 | REC-1201-1, SEC-SW-1201-1 | CB close                         | ALT, N-2A, N-3, N-3A, N-4               | False\nSEC-1201-02 | 2000   | REC-1201-1, SEC-SW-1201-1      | CB close, TIE close              | ALT, N-2A, N-3, N-3A, N-4               | False\nSEC-1201-03 | 0/1489 | REC-1201-2, SEC-SW-1201-1      | CB close                         | ALT, N-3A, N-4                          | False\nSEC-1201-03 | 1490/2000 | REC-1201-2, SEC-SW-1201-1   | CB close, TIE close              | ALT, N-3A, N-4                          | False\nSEC-1201-04 | 0/1489 | REC-1201-2                     | CB close                         | ALT, N-3A, N-4                          | False\nSEC-1201-04 | 1490/2000 | REC-1201-2                  | CB close, TIE close              | ALT, N-3A, N-4                          | True\n```\n- **Fault mislocation (locate_fault)** \u2014 ruled out: faulted_section is SEC-1201-04 as the stand-in scenario specifies; the bad step is the tie close, not the location.\n- **Lockout re-close (CB-1201) back-feeds** \u2014 ruled out: with tie capacity 0/1489 the plan still closes CB-1201 and SEC-1201-04 stays dead (REC-1201-2 holds it).\n- **Capacity check wrong** \u2014 ruled out as cause: 1490 vs 1489 is the exact threshold of SEC-1201-04's load, so the check works as written; capacity is the *only* gate, which is the defect.\n- **Tie restoration is wrong in general** \u2014 ruled out: closing the same tie for faults on SEC-1201-02/03 never back-feeds, because a non-tie switch bounds those sections downstream.\n- **Only the tie skip at flisr.py:42** \u2014 ruled out as a sufficient explanation (part B counterfactual, monkeypatched in the script, no production edit): adding TIE-1201-1405 to isolation gives isolation [REC-1201-2 open, TIE-1201-1405 open] but restoration still contains TIE-1201-1405 close and back_fed = True, because flisr.py:145-146 re-closes it and lines 91-122 never exclude faulted nodes. Both halves are in the hypothesis.\n\nC. Seeded radial feeders with a tail tie (random.Random(7), 500 cases, 2-8 sections, capacity 0-6000 kW):\n```\nfaulted_adjacent_to_tie | tie_closed | back_fed | cases\nFalse | False | False | 131\nFalse | True  | False | 177\nTrue  | False | False | 42\nTrue  | True  | True  | 150\n```\nBack-feed happens in exactly the cases where the faulted section's downstream node is the tie and the tie is closed (150/150), and never otherwise (0/350). That fits the hypothesis and nothing broader.\n\n## Falsifiable predictions\n1. Any feeder whose faulted section ends at a SCADA tie with capacity >= that section's load gets a plan that closes the tie onto it (sweep C: 150/150).\n2. A fault on a section with a non-tie downstream switch is never back-fed by build_plan (sweep A and C: 0/350).\n3. Setting the tie capacity below the faulted section's load suppresses the close (sweep A, 1489 kW).\nAny counterexample to 1 or 2 refutes the hypothesis.\n\n## Out of scope / for later stages\n- Not fixed (explore stage). Fix stage per STD-SAFETY-3/4: both tests above must pass, existing tests unchanged, and a safety invariant over at least 500 seeded inputs (the sweep generator can be reused).\n- Blast radius hint for Review: only plans whose faulted section is next to a tie change; the shipped default (fault SEC-1201-03) is unaffected.\n- `backend/app/flisr.py` is a protected path (two human reviewers, STD-GOV-6 / STD-SAFETY-1).\n"
}

## Prior artifact: prs

[
  "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13",
  "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/14"
]

## Prior artifact: branches

[
  "agent/rca-backfeed/explore",
  "agent/rca-backfeed/review",
  "agent/rca-backfeed/fix",
  "agent/rca-backfeed/qa",
  "agent/rca-backfeed/integration"
]

## Prior artifact: trace_matrix

| Requirement | Design | Code | Test | PR |
|---|---|---|---|---|
| DEF-FLISR-7 | `artifacts.review#proposed-fix-shape` | `backend/app/flisr.py:42`<br>`backend/app/flisr.py:91-151`<br>`backend/app/flisr.py:91-122`<br>`backend/app/flisr.py:136-151`<br>`backend/app/api.py:40-49`<br>`backend/app/flisr.py:91-122`<br>`backend/app/flisr.py:136-151`<br>`backend/app/flisr.py:42`<br>`backend/app/api.py:40-49`<br>`backend/app/flisr.py (build_plan restoration loop guard, commit 20d2a30)`<br>`backend/app/flisr.py:97-107 (commit 20d2a30)` | `backend/tests/test_flisr_def_flisr_7.py`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_tie_does_not_back_feed_faulted_tail_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_closes_tie_onto_faulted_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_tie_does_not_back_feed_faulted_tail_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_closes_tie_onto_faulted_section`<br>`backend/tests/rca_def_flisr_7_review_probe.py`<br>`backend/tests/test_flisr_characterization.py`<br>`backend/tests/test_flisr_def_flisr_7.py`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_nominal_drill_14_stand_in`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_refusal_is_independent_of_tie_capacity`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_healthy_tail_capacity_boundary_unchanged`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_missing_capacity_still_refuses_with_named_note`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_invalid_capacity_cannot_bypass_the_guard`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_error_paths_retained`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_tie_on_any_faulted_endpoint_is_refused`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_pick_up_through_non_scada_downstream_switch_is_refused`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_api_plan_matches_direct_plan`<br>`backend/tests/test_flisr_def_flisr_7_qa.py::test_qa_def_flisr_7_seeded_plans_agree_with_oracle_and_never_back_feed` | `https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13`<br>`https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13`<br>`https://github.com/tedfoley-cog/adms-test-automation-demo/pull/14` |

Requirement test coverage: **100%** (1/1); orphans: none

## Stage skill

# Stage skill contract (applies to every stage)

1. **prepare** — Load every governing standard listed in the brief and record their ids in
   `standards_loaded`. If one is missing or unreadable, stop: verdict `BLOCKED`, question
   `Q-<STAGE>-STD`, no further work. Read the repo contract and the instruction files it names.
2. **execute** — Do only this stage's work, inside the file boundaries in the brief. Anything
   outside the brief is reported, not done.
3. **verify** — Re-check your own output against each standard clause you loaded; cite the
   clause ids in `evidence[]`. Run the repo's lint/test commands yourself when you changed code.
4. **deliver** — Return the structured verdict. Allowed verdicts are listed in the brief; every
   claim has an `evidence[]` entry (file, test, command output, commit, PR, standard clause).

Rules that never bend: gaps become `questions[]` + `BLOCKED` (no assumptions); draft PRs
only; branches start with the agent prefix; the `AI-Governance:` trailer is on every commit;
the `ai-generated` label is on every PR; you never approve, merge, or move a ticket past
ready-for-review; missing input is never silently treated as zero.


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

## Deliver
Finish by calling provide_structured_output with an object matching the schema you were given: `verdict`, `summary`, `evidence[]`, and where relevant `questions[]`, `trace[]` (requirement_id/kind/ref), `files_touched[]`, `branch`, `pr_url`, `standards_loaded[]`, `artifacts{}` (your stage's named outputs as markdown or JSON strings), `model`.
