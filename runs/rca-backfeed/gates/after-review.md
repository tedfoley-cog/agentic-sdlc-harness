# [rca-backfeed] Gate: after-review

Run `rca-backfeed` — workflow **rca** on `tedfoley-cog/adms-test-automation-demo`.

Requirement: examples/targets/adms/defects/DEF-FLISR-7.md

Apply **gate:approved** or **gate:rejected** (comment first if rejecting). Only a human account may apply these labels; bot labels are ignored.

## Root cause

{
  "hypothesis": "build_plan (backend/app/flisr.py) never treats a tie switch as a boundary of the faulted section: _isolation_switches skips ties (flisr.py:42) and the restoration loop (flisr.py:91-122, via _nodes_restored_by flisr.py:136-151) never removes the faulted section's nodes from a tie's pick-up set, so when the faulted section's downstream end is a tie (SEC-1201-04 / TIE-1201-1405) that section is itself the tie's restoration candidate and the tie is closed whenever tie capacity >= the faulted section's load (1490 kW).",
  "evaluation": "# DEF-FLISR-7 \u2014 Evaluate (run rca-backfeed, attempt 1)\n\n## Prepare\nStandards loaded from the brief: STD-GOV v1.1, STD-RCA v1.2, STD-SAFETY v3.1. All three present and readable.\nRepo contract: not included in the brief and the brief forbids codebase access, so it was not read. The verdict below does not depend on it (noted, not blocking).\n\n## Verdict: CONFIRMED\n\nHypothesis under test: `build_plan` never treats a tie switch as a boundary of the faulted section \u2014 (a) `_isolation_switches` skips ties (flisr.py:42), and (b) the restoration loop (flisr.py:91-122 via `_nodes_restored_by` flisr.py:136-151) never removes the faulted section's nodes from a tie's pick-up set \u2014 so when the faulted section's downstream end is a tie, the tie is closed onto it whenever tie capacity >= that section's load.\n\n### Does the evidence show the mechanism, not just the symptom?\nYes. Three observed numbers in the failing output are only explainable by the faulted section itself being the tie's pick-up set:\n- `customers_restored` == `customers_remaining` == 341 (SEC-1201-04's own customer count, counted both as lost and as restored);\n- `transferred_load_kw` == 1490.0 == SEC-1201-04's load (network.py:90-91 `load_on_nodes`, to_node N-1201-4 in the candidate set);\n- \"back-feed 3 nodes\" == the island {N-1201-4, N-1201-3A, ALT-1405} = both ends of SEC-1201-04 plus the alternate source, exactly what `_nodes_restored_by` returns with REC-1201-2 open and the tie closed.\nThe sweep A threshold (1489 kW -> no close, 1490 kW -> close) shows capacity is the only gate and that the gated quantity is the faulted section's load.\n\n### Does it rule out alternatives?\nYes, with data rather than argument:\n- Mislocation: faulted_section is SEC-1201-04 in every run.\n- CB-1201 reclose as the back-feed path: at 0/1489 kW the plan still closes CB-1201 and SEC-1201-04 stays dead (REC-1201-2 holds it).\n- Capacity check defect: 1489/1490 behaves exactly as written.\n- Tie restoration wrong in general: the same tie closed for SEC-1201-02/03 faults never back-feeds (sweep A, 0 cases).\n- Tie-skip at line 42 alone: the monkeypatched counterfactual (tie added to isolation) still yields TIE close + back_fed=True because flisr.py:145-146 re-closes the tie in the what-if and 91-122 never exclude faulted nodes. This establishes that both halves of the hypothesis are necessary \u2014 important for Fix.\n- Sweep C (500 seeded feeders): back-feed in 150/150 cases where faulted section ends at the tie and the tie is closed; 0/350 otherwise. A single-cause hypothesis predicts exactly this partition.\n\n### Would the hypothesis predict the failing test's observed value?\nYes. Predicted plan for SEC-1201-04 fault with 2000 kW tie capacity: isolation [REC-1201-2], restoration [CB-1201 close, TIE-1201-1405 close], SEC-1201-04 nodes {N-1201-3A, N-1201-4} energised. That is the recorded assertion failure, both direct and via POST /flisr/plan.\n\n### Falsifiability\nThree concrete predictions are stated with the counterexample condition; predictions 1-3 are each exercised by sweep A or C.\n\n## Checks against standards\n- STD-RCA-1: single hypothesis, reproduction steps, failing tests (2) with output, observed-vs-expected table, file:line excerpts, alternative-ruling data \u2014 all present.\n- STD-RCA-2: judged from the package only; no repository used.\n- STD-SAFETY-3: defect reproduced by failing tests before any fix; no production code changed in Explore.\n- STD-GOV-7: no customer identifiers, personal names or credentials in the package.\n\n## Non-blocking notes for the next stages\n1. Code excerpts: only flisr.py:42 is quoted verbatim; lines 44-59, 91-122, 141-151 and network.py:90-91 are paraphrased with file:line. The behavioural evidence (341/341, 1490 kW, 1489/1490 threshold, counterfactual B) independently establishes the mechanism, so this does not weaken the verdict, but Review should spot-check those ranges when it has codebase access.\n2. For Fix (STD-SAFETY-4): counterfactual B shows that adding ties to isolation is not sufficient; the restoration candidate set must exclude the faulted section's nodes (or the tie whose from_node/to_node is on the faulted section must be refused). The fail-safe direction is \"refuse the tie close\", not \"best-effort re-route\".\n3. The \"Expected\" column's \"TIE-1201-1405 kept open\" is a fix design choice, not evidence; it was not used in the judgement.\n4. `backend/app/flisr.py` is a protected, safety-critical path: two human reviewers (STD-GOV-6, STD-SAFETY-1).\n5. Invariant for STD-SAFETY-5 is already stated in the package: \"a de-energised fault section is never back-fed during restoration\"; the sweep C generator (random.Random(7), 500 cases) can be reused.\n"
}

## Review

# DEF-FLISR-7 — Review (run rca-backfeed, attempt 1)

## Prepare
- Standards loaded: STD-GOV v1.1, STD-RCA v1.2, STD-SAFETY v3.1 (all present in the brief).
- Instruction files read: `.agents/skills/safety-critical-change/SKILL.md`, `DEMO_NOTES.md`.
- Inputs: confirmed hypothesis + evaluation, explore branch `agent/rca-backfeed/explore` @ c43f8c4, human answers Q-EXPLORE-1..4.

## Verdict: CONFIRMED (fit to act on, with a scope correction)

## Defect
DEF-FLISR-7: for a lockout on CB-1201 with the fault on SEC-1201-04 (the FDR-1201 stand-in for drill 14, per Q-EXPLORE-1), `app.flisr.build_plan` (per Q-EXPLORE-2) returns a restoration step that closes TIE-1201-1405 and re-energises the faulted section from the alternate source. Reproduced on the explore branch: `pytest backend -q` gives `2 failed, 2 passed`. The 2 failures are the DEF-FLISR-7 tests; the 2 tests already in `test_flisr.py` pass.
Severity: **Sev 0**, because the control output re-energises a faulted section (a hazard to people and equipment), and `api.py:1` says the SCADA adapter consumes the plan. The rubric has no step-down, since the defect is in the shipped plan logic and reproduces every time.

## Root cause (checked against the code on `main`)
The cited lines match `origin/main` exactly, which closes the evaluation's spot-check note 1.
- `flisr.py:42` drops ties before isolation (`switch.kind.value == "tie": continue`). Lines 44-59 only match upstream and downstream boundary switches.
- `flisr.py:91-122`: each SCADA tie is a restoration candidate, and capacity (`transferred > available`, line 99) is the **only** gate. Nothing compares the tie's pick-up set with the faulted section.
- `flisr.py:141-151` `_nodes_restored_by`: opens the isolation switches, forces the tie closed (145-146), and returns `energised(from tie.from_node) - energised(from source)`. Faulted-section nodes are not subtracted.
- `network.py:90-91` `load_on_nodes` counts the faulted section's own 1490 kW as "transferred".

The mechanism is the real root cause: **the restoration loop never excludes a tie whose pick-up set contains a faulted-section node.** Part B of the explore sweep (re-run here, same output) shows that the tie skip at line 42 alone is not sufficient.

### Scope correction (new evidence from this review)
The hypothesis frames the trigger as "the faulted section's downstream end is a tie". That is one instance of the mechanism, not the whole condition. Evidence-package prediction 2 ("a fault on a section with a non-tie downstream switch is never back-fed") **does not hold** outside the explore generator, which only places ties at the tail. Probe `backend/tests/rca_def_flisr_7_review_probe.py` (branch `agent/rca-backfeed/review` @ 614061d) found:

| Case (shipped FDR-1201 + one extra SCADA tie, 5000 kW) | Faulted | Isolation | Restoration | Back-fed |
|---|---|---|---|---|
| A1 tie on upstream end N-1201-3A | SEC-1201-04 | REC-1201-2 | CB-1201, TIE-1201-1405, TIE-X | **True** |
| A2 tie on downstream end N-1201-3, REC-1201-2 also bounds it | SEC-1201-03 | SEC-SW-1201-1, REC-1201-2 | CB-1201, TIE-1201-1405, TIE-X | **True** |
| A3 tie on upstream end N-1201-2A, both ends bounded by non-ties | SEC-1201-03 | SEC-SW-1201-1, REC-1201-2 | CB-1201, TIE-1201-1405, TIE-X | **True** |
| A4 tie on a healthy node N-1201-1 (control) | SEC-1201-03 | SEC-SW-1201-1, REC-1201-2 | CB-1201, TIE-1201-1405, TIE-X | False |

Seeded sweep: `random.Random(11)`, 500 radial feeders with 2-8 sections and 1-3 SCADA ties on random nodes, unpatched code.

| tail_tie_case | closed tie on a faulted-section node | back_fed | cases |
|---|---|---|---|
| False | False | False | 301 |
| False | True | True | **130** |
| True | False | False | 5 |
| True | True | True | 64 |

Back-feed happens in exactly the 194/194 plans that close a tie sitting on a faulted-section node, and in 0/306 others. 130 of those 194 are cases the "downstream-tail tie" framing would miss. This strengthens the mechanism and widens the trigger. It does not refute the root cause, because the mechanism as stated predicts these cases too.

## Blast radius
- **Affected requirement ids:** DEF-FLISR-7. No `REQ-*` ids exist in the repo (`git grep -E "(REQ|DEF)-[A-Z]+-[0-9]{1,3}" origin/main` returns nothing), so no other requirement is affected or traceable.
- **Callers:** `POST /flisr/plan` (`backend/app/api.py:40-49`) is the only production caller (`git grep build_plan`). The console does not call it; its only FLISR reference is in `coverage.json`. No firmware path is involved.
- **Behaviour that changes with the fix:** any plan in which a SCADA tie with enough capacity sits on a node of the faulted section (either end, whatever other switch bounds it). For the shipped model, that is only a fault on SEC-1201-04 with TIE-1201-1405 capacity ≥ 1490 kW.
- **Behaviour that provably stays the same:** faults whose faulted-section nodes are not in any tie's pick-up set. That covers the shipped default fault SEC-1201-03 (`test_build_plan_isolates_and_restores_tail`: isolation {SEC-SW-1201-1, REC-1201-2}, CB-1201 + TIE-1201-1405 close, 341 restored) and SEC-1201-02 (sweep A).
- **Accounting side effect:** today the faulted section's customers are counted in `customers_restored` and its load in `transferred_load_kw` (341/341, 1490 kW). With the guard in place the plan reports 0 restored, 341 remaining, 0 kW.
- **Adjacent, out of scope (not verified, needs its own ticket):** `build_plan` gets only one feeder. It never checks that the alternate side of a tie is healthy (FDR-1405 SEC-1405-02 ends at ALT-1405). `_nodes_restored_by` walks from `tie.from_node`, so the "N nodes" in the step reason includes the alternate-source node (Sev 3, cosmetic).

## Proposed fix shape (for Fix, not code)
Fail-safe means **refuse the tie** (STD-SAFETY-4). Do not re-route on a best-effort basis.
1. In the `build_plan` restoration loop, compute the tie's pick-up set as today. If it contains `faulted_section.from_node` or `faulted_section.to_node`, do not close the tie. Append a note ("<tie> held open: would energise faulted <section>") and do not add the faulted section's customers to `customers_remaining` a second time.
2. On its own, adding ties to `_isolation_switches` (line 42) is **not** a fix (part B). It is optional only as a presentation choice and must not be the only guard.
3. No change to `locate_fault`, the capacity check, the lockout reclose, or `network.py`.
4. Feasibility shown (part C of the probe, in-process patch only): over the same 500 inputs the guard gives **0 back-fed plans**. The DEF-FLISR-7 scenario becomes CB-1201 close only, 0 restored / 341 remaining / 0 kW. The shipped-default inputs give an unchanged plan (341 restored, 96 remaining).

## Invariant Fix must demonstrate (STD-SAFETY-5)
"A de-energised fault section is never back-fed during restoration": after applying isolation and restoration, neither endpoint of the faulted section is reachable from the feeder source or from any closed tie's alternate side. Check it over ≥ 500 seeded inputs. **The generator must place ties on arbitrary nodes (as in the review probe), not only at the tail.** The explore sweep C generator would also pass a narrow "downstream-tail tie" fix. Also required: the 2 DEF-FLISR-7 tests pass, the existing `test_flisr.py` tests pass unchanged, characterization tests for the shipped SEC-1201-02/03 plans are added before the edit (STD-SAFETY-2), and `ruff check backend` is clean. Do not touch `tools/` (Q-EXPLORE-4).

## Reviewers required
`backend/app/flisr.py` is a protected path and the change is safety-critical, so **two human reviewers** are required (STD-GOV-6, STD-SAFETY-1). Use a draft PR only, with the `ai-generated` label. The repo has no such label today, so a human has to create it.

## Compliance notes
- The review commit 614061d carries the `AI-Governance` trailer. The platform also added a `Co-Authored-By` trailer that contains a personal name, which conflicts with STD-GOV-7. The explore commits a6c2139 and c43f8c4 have the same trailer. The agent cannot change its git identity, so this needs a human or platform fix.
- Tool classification (STD-SAFETY-7): the probe and sweep scripts are diagnostic. They only exercise `build_plan`, and their output is checked against the independent reachability check (`back_fed`). That makes them T2 (verification tools whose errors could hide a defect but cannot introduce one). No certification credit is claimed.
- No production system, secret or field device was accessed (STD-SAFETY-8). No production code was changed.


Reviewers required: 2

## Trace so far

| Requirement | Design | Code | Test | PR |
|---|---|---|---|---|
| DEF-FLISR-7 | `artifacts.review#proposed-fix-shape` | `backend/app/flisr.py:42`<br>`backend/app/flisr.py:91-151`<br>`backend/app/flisr.py:91-122`<br>`backend/app/flisr.py:136-151`<br>`backend/app/api.py:40-49`<br>`backend/app/flisr.py:91-122`<br>`backend/app/flisr.py:136-151`<br>`backend/app/flisr.py:42`<br>`backend/app/api.py:40-49` | `backend/tests/test_flisr_def_flisr_7.py`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_tie_does_not_back_feed_faulted_tail_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_closes_tie_onto_faulted_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_tie_does_not_back_feed_faulted_tail_section`<br>`backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_closes_tie_onto_faulted_section`<br>`backend/tests/rca_def_flisr_7_review_probe.py` | — |

Requirement test coverage: **100%** (1/1); orphans: none
