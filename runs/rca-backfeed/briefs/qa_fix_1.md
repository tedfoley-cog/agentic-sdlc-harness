# Agentic SDLC stage brief — QA (run rca-backfeed, attempt 1)

Role: Independent QA. Re-run every check yourself with your own oracle/test vectors; trust nothing from Coding.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: PASS, FAIL, BLOCKED, INSUFFICIENT_EVIDENCE. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=rca-backfeed stage=qa agent=devin model=ultra`; PRs carry the `ai-generated` label.

## Access and boundaries
Target repository: `tedfoley-cog/adms-test-automation-demo` (default branch `main`). Safety classification: **safety-critical**.
Files you may change: ['**']. Files you must not change: ['(none)'].
Commands — build: `npm --prefix console ci --no-audit --no-fund && npm --prefix console run build`; test: `pytest backend -q`; lint: `ruff check backend`.
Requirement ids match `(?:REQ|DEF)-[A-Z]+-\d{1,3}`; reference them verbatim.
Protected paths (two human reviewers): ['backend/app/flisr.py', 'firmware/src/**'].
Repo instruction files to read first: ['.agents/skills/safety-critical-change/SKILL.md', 'DEMO_NOTES.md'].
Layer visibility: {"models": ["backend/app/models.py"], "logic": ["backend/app/flisr.py", "backend/app/state_estimator.py", "backend/app/agc.py", "backend/app/network.py", "backend/app/savecase.py"], "api": ["backend/app/api.py"], "ui": ["console/**"], "visibility": {"api": ["logic", "models"], "logic": ["models"], "ui": ["api"]}}.

## Governing standards (loaded at runtime — confirm each id in `standards_loaded`)

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

### STD-QA — STD-QA — Independent verification standard

# STD-QA — Independent verification standard
Version: 1.3

- **STD-QA-1**: QA runs on a different model or agent mode from Coding and starts from the brief and the repository, not from Coding's report. Coding's claims are hypotheses to be re-tested.
- **STD-QA-2**: QA re-runs build, lint and the full test suite itself and attaches the output; it does not accept a pasted log.
- **STD-QA-3**: For protection/control functions QA writes or uses an independent oracle (closed-form or reference model) and its own test vectors, including boundary and invalid-input vectors, and reports agreement with tolerance.
- **STD-QA-4**: QA checks the three known failure modes explicitly: model/logic mixing, deleted error handling, missing input treated as zero — in addition to the deterministic checks the harness already ran.
- **STD-QA-5**: Every FAIL names the requirement id, the failing vector or test, the observed and expected values and the file/line; Coding must be able to act on it without a conversation.
- **STD-QA-6**: QA verifies each requirement id in scope has at least one passing test that references it; missing coverage is a FAIL even when all tests pass.
- **STD-QA-7**: QA may return INSUFFICIENT_EVIDENCE when it cannot run the checks (environment, missing fixtures); it never passes on trust.

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

## Your unit

```json
{
  "id": "fix",
  "title": "Apply the reviewed root-cause fix",
  "files": [
    "backend/app/flisr.py",
    "backend/tests/**"
  ],
  "depends_on": []
}
```

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

## Prior artifact: review

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


## Prior artifact: coding_report

{
  "verdict": "PASS",
  "summary": "prepare: STD-CODE v1.4, STD-GOV v1.1 and STD-SAFETY v3.1 loaded; .agents/skills/safety-critical-change/SKILL.md and DEMO_NOTES.md read. execute: on agent/rca-backfeed/fix, characterization tests were committed first (932ccfb), then a failing DEF-FLISR-7 reproduction plus a 500-case seeded invariant with ties on any node (9863be7; 282/500 failed before the fix), then the smallest fail-safe fix (20d2a30): in build_plan's restoration loop, any SCADA tie whose pick-up set contains an endpoint of the faulted section is held open and a note names the tie and the section. DEF-FLISR-7 scenario: 0 restored / 341 remaining / 0 kW (Q-REVIEW-2). verify: pytest backend -q gives 13 passed; ruff check backend is clean; console build and make -C firmware test pass. ruff check backend tools fails only on the UP017 error in tools/build_coverage_report.py:183 that is already on main, an existing exception per Q-EXPLORE-4, so tools/ was not touched. In CI the backend job fails at that same lint step and never reaches pytest, so the pytest evidence is from local runs; native and ui pass. deliver: draft PR #13 with the ai-generated label; two human reviewers required. Follow-ups, not fixed here: a separate unisolated-fault-via-lockout-reclose defect when the upstream boundary switch is non-SCADA (55/412 seeded plans); and the platform-added Co-Authored-By trailer contains a personal name, which conflicts with STD-GOV-7.",
  "evidence": [
    {
      "kind": "commit",
      "ref": "932ccfb",
      "detail": "Characterization tests pinning build_plan on FDR-1201 before the fix (STD-SAFETY-2); green before and after"
    },
    {
      "kind": "commit",
      "ref": "9863be7",
      "detail": "Failing reproduction + invariant committed before the production change (STD-CODE-1, STD-SAFETY-3): 6 failed / 7 passed, invariant 282/500 back-fed"
    },
    {
      "kind": "commit",
      "ref": "20d2a30",
      "detail": "Smallest fail-safe fix: refuse the tie close, no re-routing (STD-SAFETY-4); all commits carry AI-Governance: run=rca-backfeed stage=fix agent=devin model=normal (STD-CODE-5, STD-GOV-2)"
    },
    {
      "kind": "test",
      "ref": "backend/tests/test_flisr_def_flisr_7.py::test_def_flisr_7_invariant_faulted_section_never_back_fed_over_seeded_feeders",
      "detail": "Seed 20261015, 500 radial/branched feeders, 1-3 ties on arbitrary nodes, independent BFS oracle: 0 back-fed after the fix (STD-SAFETY-5)"
    },
    {
      "kind": "command",
      "ref": "pytest backend -q",
      "detail": "13 passed (local)"
    },
    {
      "kind": "command",
      "ref": "ruff check backend",
      "detail": "All checks passed"
    },
    {
      "kind": "command",
      "ref": "ruff check backend tools",
      "detail": "1 error: UP017 in tools/build_coverage_report.py:183, already on main; existing exception per Q-EXPLORE-4, not fixed here"
    },
    {
      "kind": "command",
      "ref": "npm --prefix console run build",
      "detail": "built"
    },
    {
      "kind": "command",
      "ref": "make -C firmware test",
      "detail": "fault_detect: 2 cases, 0 failed"
    },
    {
      "kind": "pr",
      "ref": "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13",
      "detail": "Draft, label ai-generated, sections Defect/Root cause/Fix/Evidence/Blast radius/trace. CI: native and ui pass; backend fails at the pre-existing tools/ UP017 lint step before pytest"
    },
    {
      "kind": "standard",
      "ref": "STD-GOV-6",
      "detail": "Protected safety-critical path backend/app/flisr.py: two human reviewers required (also STD-SAFETY-1); no approval or merge by the agent"
    },
    {
      "kind": "standard",
      "ref": "STD-CODE-2",
      "detail": "Only backend/app/flisr.py and backend/tests/** changed; models.py, firmware/**, legacy/** and tools/** untouched"
    },
    {
      "kind": "standard",
      "ref": "STD-CODE-7",
      "detail": "All new tests carry pytest.mark.requirement('DEF-FLISR-7')"
    },
    {
      "kind": "standard",
      "ref": "STD-SAFETY-7",
      "detail": "Seeded invariant and probes are T2 verification tools (could hide a defect, cannot introduce one); no certification credit claimed"
    },
    {
      "kind": "note",
      "ref": "STD-GOV-7",
      "detail": "The platform-added Co-Authored-By trailer contains a personal name; needs a human or platform fix"
    },
    {
      "kind": "note",
      "ref": "follow-up",
      "detail": "Separate defect, not fixed: when the upstream boundary switch is non-SCADA, the lockout reclose energises the fault from the feeder source (55/412 seeded plans); documented in the PR"
    }
  ],
  "artifacts": {
    "pr_body": "/home/ubuntu/evidence/pr_body.md"
  },
  "trace": [
    {
      "requirement_id": "DEF-FLISR-7",
      "kind": "code",
      "ref": "backend/app/flisr.py (build_plan restoration loop guard, commit 20d2a30)"
    },
    {
      "requirement_id": "DEF-FLISR-7",
      "kind": "test",
      "ref": "backend/tests/test_flisr_characterization.py"
    },
    {
      "requirement_id": "DEF-FLISR-7",
      "kind": "test",
      "ref": "backend/tests/test_flisr_def_flisr_7.py"
    },
    {
      "requirement_id": "DEF-FLISR-7",
      "kind": "pr",
      "ref": "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13"
    }
  ],
  "standards_loaded": [
    "STD-CODE",
    "STD-GOV",
    "STD-SAFETY"
  ],
  "files_touched": [
    "backend/app/flisr.py",
    "backend/tests/conftest.py",
    "backend/tests/test_flisr_characterization.py",
    "backend/tests/test_flisr_def_flisr_7.py"
  ],
  "branch": "agent/rca-backfeed/fix",
  "pr_url": "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13",
  "session_url": "https://devin-gtm.devinenterprise.com/sessions/28223982d72d4bceaeefeab801fc7e74",
  "model": "normal"
}

## Prior artifact: deterministic_checks

{
  "verdict": "PASS",
  "checks": [
    {
      "name": "model_logic_separation",
      "verdict": "PASS",
      "findings": [],
      "detail": "no findings"
    },
    {
      "name": "removed_error_handling",
      "verdict": "PASS",
      "findings": [],
      "detail": "no findings"
    },
    {
      "name": "missing_input_as_zero",
      "verdict": "PASS",
      "findings": [],
      "detail": "no findings"
    },
    {
      "name": "scope",
      "verdict": "PASS",
      "findings": [],
      "detail": "no findings"
    },
    {
      "name": "governance",
      "verdict": "PASS",
      "findings": [],
      "detail": "no findings"
    }
  ],
  "commands": {
    "build": {
      "cmd": "npm --prefix console ci --no-audit --no-fund && npm --prefix console run build",
      "returncode": 0,
      "tail": "\nadded 68 packages in 592ms\n\n> qa-coverage-console@0.1.0 build\n> tsc -b && vite build\n\nvite v5.4.11 building for production...\ntransforming...\n\u2713 37 modules transformed.\nrendering chunks...\ncomputing gzip size...\ndist/index.html                   0.43 kB \u2502 gzip:  0.29 kB\ndist/assets/index-BhRQqo7Z.css    5.29 kB \u2502 gzip:  1.63 kB\ndist/assets/index-DvMiGgeB.js   159.79 kB \u2502 gzip: 50.27 kB\n\u2713 built in 418ms\n"
    },
    "lint": {
      "cmd": "ruff check backend",
      "returncode": 0,
      "tail": "All checks passed!\n"
    },
    "test": {
      "cmd": "pytest backend -q",
      "returncode": 0,
      "tail": ".............                                                            [100%]\n=============================== warnings summary ===============================\ntests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_does_not_close_tie_onto_faulted_section\n  /home/ubuntu/.pyenv/versions/3.12.13/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.\n    from starlette.testclient import TestClient as TestClient  # noqa\n\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n13 passed, 1 warning in 0.46s\n"
    }
  },
  "branch": "agent/rca-backfeed/fix",
  "files_in_diff": [
    "backend/app/flisr.py",
    "backend/tests/conftest.py",
    "backend/tests/test_flisr_characterization.py",
    "backend/tests/test_flisr_def_flisr_7.py"
  ]
}

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
name: qa
description: Independently verifies a coded unit on a different agent mode: re-runs every check, writes its own oracle and test vectors, checks the three known failure modes and requirement coverage. Used after deterministic verification passes; a FAIL returns to Coding with actionable findings.
---

# Qa

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, FAIL, BLOCKED, INSUFFICIENT_EVIDENCE.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Check out the unit's branch. Run build, lint and the full test suite yourself (STD-QA-2). Treat Coding's report as hypotheses (STD-QA-1).
2. Build an independent oracle for the behaviour (closed-form, table or reference model) and your own vectors: nominal, boundary, missing input, invalid input (STD-QA-3). Add them as a separate test file under the unit's file scope if the brief allows; otherwise run them ad hoc and attach the output.
3. Check model/logic mixing, deleted error handling, missing-as-zero in the diff (STD-QA-4).
4. Verify each requirement id in scope has a passing test referencing it (STD-QA-6).

## Verify
Every FAIL item has requirement id, vector/test, observed vs expected, file:line (STD-QA-5).

## Deliver
`artifacts.qa_report` (markdown), `trace[]` test rows for your own tests, `evidence[]` command outputs. `PASS` / `FAIL` / `INSUFFICIENT_EVIDENCE` (could not run) / `BLOCKED`.

## Deliver
Finish by calling provide_structured_output with an object matching the schema you were given: `verdict`, `summary`, `evidence[]`, and where relevant `questions[]`, `trace[]` (requirement_id/kind/ref), `files_touched[]`, `branch`, `pr_url`, `standards_loaded[]`, `artifacts{}` (your stage's named outputs as markdown or JSON strings), `model`.
