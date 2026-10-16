# Agentic SDLC stage brief — QA (run feature-tie-capacity, attempt 1)

Role: Independent QA. Re-run every check yourself with your own oracle/test vectors; trust nothing from Coding.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: PASS, FAIL, BLOCKED, INSUFFICIENT_EVIDENCE. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=feature-tie-capacity stage=qa agent=devin model=ultra`; PRs carry the `ai-generated` label.

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

# Change request: respect tie-switch capacity during FLISR restoration

Restoration plans produced by `backend/app/flisr.py::locate_fault` / the restoration planner must
not transfer more load onto a tie switch than its rated capacity. When the tie capacity is not
known the plan must say so instead of restoring. Telemetry for tie capacity arrives from the SCADA
scan every 10 s.

## Your unit

```json
{
  "id": "U1",
  "wave": 1,
  "title": "Baseline: pin current FLISR behaviour and record failing reproductions on unmodified main",
  "requirement_ids": [
    "REQ-TIECAP-19",
    "REQ-TIECAP-22"
  ],
  "depends_on": [],
  "files": [
    "backend/tests/test_flisr_tie_capacity_characterization.py",
    "backend/tests/test_flisr_tie_capacity_repro.py"
  ],
  "safety": "safety-critical (inherited, STD-REQ-6). Test-only, but lands in the change set that touches protected backend/app/flisr.py: two human reviewers (STD-GOV-6, STD-SAFETY-1).",
  "scope_notes": [
    "Safety skill steps 1-3 (STD-SAFETY-2, STD-SAFETY-3). No production file may change in this unit; every test is written and run against main @ 5f6b471.",
    "Characterization (REQ-TIECAP-22): @pytest.mark.characterization tests through the legacy tie_capacity_kw interface, restricted to inputs where every candidate tie has a finite, non-negative entry with L <= C or L > C + 0.5 kW. They pin isolation steps, restoration steps and their order, customers_restored, customers_remaining, transferred_load_kw. They do not pin notes text (REQ-TIECAP-12 changes it) and exclude C in (L, L + 0.5], missing entries, NaN/+-inf/negative (intended changes 1-3 of the specification).",
    "Characterization inputs exclude faults on a section with a SCADA tie at either endpoint (DEF-FLISR-7 is handled incorrectly today; pinning it would mask or block that separate defect run, spec section 3).",
    "REQ-TIECAP-19: pin the no-fault plan field-by-field (no isolation, no restoration, manual-patrol note, customers_remaining) and assert plan.model_dump().get('blocked_ties', []) == [] so the same test passes unchanged on main and after U2/U3.",
    "Reproductions (STD-SAFETY-3), kept failing output for the PR: (a) shipped model, CB-1201 open, no capacity entry: plan carries no machine-readable reason for skipping TIE-1201-1405 (expects blocked_ties CAPACITY_UNKNOWN); (b) legacy tie_capacity_kw NaN and +inf: plan closes TIE-1201-1405 (expects no close step). Committed as pytest.mark.xfail(strict=True, reason='REPRO ...') so main stays green; U3 removes only the markers.",
    "backend/tests/test_flisr.py is not in any unit: it must pass unchanged to the end of the run."
  ],
  "oracle": "Characterization: the values measured on unmodified main are the oracle (re-run must be identical before and after U2-U4). Reproductions: operational expectation from REQ-TIECAP-5 and REQ-TIECAP-8 (no close step for a tie with missing or non-finite capacity), checked by observing the failure on main."
}
```

## Human answers to earlier questions (recorded gate actions)

- **Q-SPEC-1** (ops-lead-standin): Live value. 'Tie capacity' is the alternate feeder's spare capacity as delivered by the SCADA scan every 10 s, in kW on the same basis as load_kw. No unit conversion, no p.u. base; comparison tolerance is 0.5 kW. The 'rated capacity' wording in the source is loose and does not mean nameplate.
- **Q-SPEC-2** (ops-lead-standin): A value is late when it is older than 20 s (two missed scans). Inside 20 s the planner may use the last value only if its quality is GOOD. Older than 20 s, or any quality other than GOOD, is 'unknown' and must not be used.
- **Q-SPEC-3** (ops-lead-standin): Extend build_plan with tie_capacity: dict[str, TieCapacity] where TieCapacity carries kw, timestamp and quality (a Pydantic model in backend/app/models.py). Extend the POST /flisr/plan body the same way. Keep the legacy dict[str, float] accepted for one release and treat it as quality GOOD with timestamp now, with a deprecation note. The SCADA adapter side is owned by the integration team and is out of scope for this change.
- **Q-SPEC-4** (ops-lead-standin): Equality closes: the tie may close when transferred load <= capacity. No additional safety margin; the only tolerance is the 0.5 kW comparison tolerance from Q-SPEC-1. No p.u. statement needed.
- **Q-SPEC-5** (ops-lead-standin): Per tie. Only the tie with unknown capacity is blocked; isolation and ties with a known capacity proceed. 'Capacity unknown' must be machine-readable: RestorationPlan gains blocked_ties: list[BlockedTie{tie_id, reason in CAPACITY_UNKNOWN | CAPACITY_STALE | CAPACITY_INVALID | CAPACITY_EXCEEDED}] and an operator-readable note; HTTP 200, not 409.
- **Q-SPEC-6** (ops-lead-standin): Skip the tie (today's behaviour) and record it in blocked_ties with reason CAPACITY_EXCEEDED. Partial pick-up is out of scope.
- **Q-SPEC-7** (ops-lead-standin): Per tie. Shared alternate-feeder capacity across several ties is out of scope; list it as a scope exclusion.
- **Q-SPEC-8** (ops-lead-standin): Confirmed: scope is build_plan in backend/app/flisr.py plus backend/app/api.py (and models.py for the new types). The repo contract layer map has been corrected to state_estimator.py / api.py.
- **Q-SPEC-9** (ops-lead-standin): CAPACITY_INVALID = kw is NaN, +/-inf, negative, or not a finite number, or the timestamp is unparseable/timezone-naive/future-dated (see Q-SPEC-10). A quality other than GOOD is CAPACITY_UNKNOWN (same as missing). Precedence when several apply, evaluate in this order and report the first: CAPACITY_INVALID, CAPACITY_UNKNOWN, CAPACITY_STALE, CAPACITY_EXCEEDED. Malformed HTTP input (wrong types, unknown fields) is rejected by request validation with HTTP 422 and never reaches the planner.
- **Q-SPEC-10** (ops-lead-standin): Time reference is the request's as_of field: a timezone-aware ISO-8601 UTC instant supplied by the caller; when absent the server uses UTC now and echoes the value it used in the response. Capacity timestamps must be timezone-aware; naive timestamps are CAPACITY_INVALID. A timestamp more than 2 s ahead of as_of is CAPACITY_INVALID. Age = as_of - timestamp.
- **Q-SPEC-11** (ops-lead-standin): The new body field tie_capacity (dict[str, TieCapacity]) and the legacy tie_capacity_kw are mutually exclusive; both present is HTTP 422. Legacy-only requests are treated as quality GOOD with timestamp = as_of and the response carries deprecations: ['tie_capacity_kw']. The deprecation note lives in the endpoint's OpenAPI description and in the docs page the Document stage produces; removal is a separate change after one release.
- **Q-SPEC-12** (ops-lead-standin): (a) timezone-naive as_of: HTTP 422. (b) aware non-UTC offset: accept, normalise to the same UTC instant. (c) unparseable: HTTP 422. (d) yes, bounded: an as_of more than 60 s before or 2 s after the server clock is HTTP 422, so staleness cannot be bypassed by back-dating. 422 means no plan at all, which is acceptable because the request itself is malformed; the operator retries with a valid request.
- **Q-SPEC-13** (ops-lead-standin): (b) 422. TieCapacity.timestamp is a strict timezone-aware ISO-8601 datetime field; a non-ISO string or a JSON number is a request-validation failure for the whole request. Per-tie CAPACITY_INVALID for timestamps therefore covers only well-formed values that fail the semantic rules (future-dated beyond 2 s). Q-SPEC-9 is amended to match.
- **Q-DESIGN-1** (principal-engineer-standin): STD-SAFETY-6 governs the oracle: the QA/test oracle is an independent closed form that lives under backend/tests and must not import app.flisr or share its threshold code. STD-ARCH-2's one-shared-implementation rule applies to production consumers only (planner, endpoint, notes); record this as an explicit, scoped waiver in design section 6.3 citing both clauses, and keep the production threshold characteristic (tolerance, max age, max lead) in one shared module that every production consumer imports.
- **Q-DESIGN-2** (principal-engineer-standin): A negative, NaN or infinite section load is invalid model data, not a load to net off. build_plan refuses the whole plan (FlisrError, HTTP 409, lockout stays open) when any candidate section's load_kw is not a finite non-negative number; L is otherwise the plain sum. This is covered by the out-of-range precondition and needs no change to REQ-TIECAP-3/21; record it in the design as a stated precondition and add a test vector.
- **Q-DESIGN-3** (principal-engineer-standin): Draft PR #13 (DEF-FLISR-7 hold-open guard) lands first and is kept. Design on top of it: a tie refused because its pick-up set touches the faulted section is reported in blocked_ties with a new reason FAULTED_SECTION, evaluated before every capacity reason (precedence FAULTED_SECTION > CAPACITY_INVALID > CAPACITY_UNKNOWN > CAPACITY_STALE > CAPACITY_EXCEEDED). REQ-TIECAP-21 is amended accordingly in the spec by the Design stage (note the amendment in design.md and the trace); the guard's behaviour must not change.

## Prior artifact: specification

# Specification — FLISR restoration respects tie-switch capacity

Run: `feature-tie-capacity` · Stage: SPECIFY · Attempt: 4 · Status: **COMPLETE** (no open questions; Q-SPEC-1..Q-SPEC-13 answered)

## 0. Source, inputs and classification

- Source: change request "respect tie-switch capacity during FLISR restoration", plus human answers Q-SPEC-1..Q-SPEC-13 (ops-lead-standin, recorded gate actions). Q-SPEC-13 amends Q-SPEC-9 and Q-SPEC-10: a timezone-naive or unparseable capacity timestamp is a request-validation failure, not a per-tie CAPACITY_INVALID.
- Safety classification (STD-REQ-6): **safety-critical** (IEC 61508-3 context). The change alters which tie switches FLISR commands closed. Every unit derived from this specification inherits the classification. `backend/app/flisr.py` is a protected path: two human reviewers (STD-GOV-6, STD-SAFETY-1).
- Scope (Q-SPEC-8): `build_plan` in `backend/app/flisr.py`; `POST /flisr/plan` in `backend/app/api.py`; new types in `backend/app/models.py`.

### Current behaviour (baseline, `main` @ 5f6b471, re-measured this attempt; `pytest backend -q` 2 passed)

- `build_plan(feeder, lockout_switch_mrid, tie_capacity_kw: dict[str, float] | None)`. A tie with no entry reads as `0.0` kW (`flisr.py:98`, `tie_capacity_kw.get(switch.mrid, 0.0)`): an implicit "treat as zero", forbidden by STD-REQ-3.
- A tie is skipped when `transferred > available` (strict), so equality closes; there is no tolerance.
- Shipped model, `CB-1201` open: isolation opens `SEC-SW-1201-1` and `REC-1201-2`; restoration re-closes `CB-1201`. Tie `TIE-1201-1405` has L = 1490 kW.
  - no capacity → tie skipped, note `"Hollow Creek tie to 1405 skipped: 1490 kW exceeds 0 kW available capacity"`, `customers_restored = 0`, `customers_remaining = 437`, `transferred_load_kw = 0.0`.
  - C = 1490.0 → tie closed, `customers_restored = 341`, `customers_remaining = 96`, `transferred_load_kw = 1490.0`, no notes.
  - C = 1489.5 → tie skipped (note says "1490 kW exceeds 1490 kW", rounding hides the 0.5 kW); C = 1489.4 → skipped.
  - C = NaN and C = +inf → tie **closed**, `customers_restored = 341`, no note.
- `build_plan` callers: `backend/app/api.py:45` and `backend/tests/test_flisr.py` only.
- HTTP today (`FlisrRequest`, Pydantic lax mode, extra fields ignored): a JSON `NaN` capacity is accepted, a string `"2000"` is coerced to 2000.0, and an unknown body field is silently ignored. All three reach the planner.
- No timestamp, no quality, no machine-readable reason for a skipped tie.

### Definitions

- **Candidate tie**: a `Switch` with `kind == tie` and `scada_controllable == True` for which `_nodes_restored_by` returns a non-empty node set. Other ties are skipped silently, as today (§3).
- **L (transferred load)**: sum of `Section.load_kw` over sections whose `to_node` is in the candidate node set. Unit kW; range L ≥ 0.
- **C (tie capacity)**: `TieCapacity.kw` — the alternate feeder's spare capacity as delivered by the SCADA scan every 10 s, kW on the same basis as `load_kw`. No unit conversion, no per-unit base, not nameplate (Q-SPEC-1).
- **τ (tolerance)**: 0.5 kW, the only tolerance; no additional safety margin (Q-SPEC-1, Q-SPEC-4). Per-unit statement waived by Q-SPEC-4.
- **as_of**: the evaluation instant, a timezone-aware instant. Over HTTP: the request's `as_of` (timezone-aware ISO-8601; a non-UTC offset is normalised to the same UTC instant), when absent the server's UTC now (Q-SPEC-10, Q-SPEC-12).
- **server now**: the server's UTC clock, read once when the HTTP request is handled; used only for the as_of bound (REQ-TIECAP-23) and for an absent as_of.
- **age**: `as_of − TieCapacity.timestamp`, in seconds (Q-SPEC-10). Negative when the timestamp is ahead of as_of.
- **Usable capacity**: an entry that is present, valid (REQ-TIECAP-8), `quality == "GOOD"` and `age ≤ 20 s` (Q-SPEC-2).
- **Request validation**: FastAPI/Pydantic validation of the `POST /flisr/plan` body; a failure returns HTTP 422 and the planner is not called, so no plan at all is produced (Q-SPEC-9, Q-SPEC-12).
- **Present** (HTTP body field): the key appears in the JSON body, whatever its value.

## 1. Requirements

| ID | Requirement (one testable statement) | Inputs → outputs | Missing / late / invalid behaviour | Verification (oracle) | Depends on open Q |
|---|---|---|---|---|---|
| REQ-TIECAP-1 | `backend/app/models.py` shall define a Pydantic model `TieCapacity` with required fields `kw: float` (kW, same basis as `Section.load_kw`), `timestamp` (strict timezone-aware ISO-8601 datetime) and `quality: str`, and shall reject unknown fields. Validation shall reject: `kw` that is not a JSON number (string, bool, null); `timestamp` that is a non-ISO-8601 string, a JSON number, null or timezone-naive; `quality` that is not a string. It shall **not** range-check `kw` (NaN, ±Infinity and negative numbers pass validation so the planner flags them CAPACITY_INVALID, REQ-TIECAP-8) and shall not compare `timestamp` with any clock (Q-SPEC-3, Q-SPEC-9, Q-SPEC-13). | JSON / Python values → `TieCapacity` or validation error | Missing, unknown or wrongly typed field → validation error; over HTTP → 422 for the whole request (REQ-TIECAP-13). | Test: model unit tests for each accept/reject class (`"yesterday"`, `1790000000`, `"2026-10-15T22:00:00"` naive, `"2000"`, `true`, extra field → reject; `NaN`, `-1.0`, `+02:00` offset → accept). Inspection of `models.py`. | — |
| REQ-TIECAP-2 | `flisr.build_plan` shall accept `tie_capacity: dict[str, TieCapacity] \| None` keyed by tie switch mRID, and `as_of: datetime \| None`. When `as_of` is None it shall use the UTC now read once at the start of the call. A timezone-aware `as_of` with any offset shall be used as the same instant. A timezone-naive `as_of` shall make `build_plan` raise and return no plan (Q-SPEC-12(a): a malformed time reference yields no plan at all). `build_plan` itself shall not bound `as_of` against the clock; that bound is a request-validation rule (REQ-TIECAP-23), and `api.py` is the only production caller. | feeder, lockout mRID, tie_capacity, as_of → `RestorationPlan` | `tie_capacity` None or `{}` → every candidate tie is CAPACITY_UNKNOWN (REQ-TIECAP-5). Naive `as_of` → raise, no plan. | Test with an injected `as_of` (UTC and `+02:00` give identical plans; naive raises); inspection. | — |
| REQ-TIECAP-3 | For a candidate tie with usable capacity C, `build_plan` shall emit a `close` restoration step for that tie **if and only if** `L ≤ C + 0.5 kW`. | L, C → close step present / absent | C not usable → REQ-TIECAP-5..8; never closed. | Test against an independent closed-form oracle: QA computes L with its own BFS over the test topology (not `network.load_on_nodes` or `_nodes_restored_by`) and evaluates `L_oracle ≤ C + 0.5`. Shipped-model boundary (L = 1490 kW): C = 1490.0 closes; C = 1489.5 closes (L = C + τ); C = 1489.4 blocked CAPACITY_EXCEEDED. Tolerance 0.5 kW engineering units; per-unit waived (Q-SPEC-4). | — |
| REQ-TIECAP-4 | For a candidate tie with usable capacity and `L > C + 0.5 kW`, `build_plan` shall emit no step for that tie and shall record `BlockedTie(tie_id=<mRID>, reason=CAPACITY_EXCEEDED)`. No partial pick-up (Q-SPEC-6). | L, C → blocked_ties entry | — | Test (oracle as REQ-TIECAP-3). | — |
| REQ-TIECAP-5 | For a candidate tie with no entry in `tie_capacity` (including None / `{}`), or whose entry has `quality != "GOOD"` (exact, case-sensitive match), `build_plan` shall emit no step for that tie and record `BlockedTie(reason=CAPACITY_UNKNOWN)`. A missing value shall never be read as 0 kW or any other value (Q-SPEC-2, Q-SPEC-9). | entry / quality → blocked_ties entry | Missing or non-GOOD → refuse for that tie only. | Test: missing key, `None`, `{}`, qualities `"BAD"`, `"SUSPECT"`, `"good"`, `""`. Inspection that no default capacity remains at `flisr.py:98`. | — |
| REQ-TIECAP-6 | For a candidate tie whose valid entry has `age > 20 s`, `build_plan` shall not use the value, emit no step for that tie and record `BlockedTie(reason=CAPACITY_STALE)`. `age ≤ 20 s` (exactly 20 s included) is fresh (Q-SPEC-2). | timestamp, as_of → usable / blocked | Late → refuse for that tie. | Test with injected as_of: age 19.999 s, 20.000 s (fresh), 20.001 s (stale). Oracle: closed-form `age > 20`. | — |
| REQ-TIECAP-7 | A capacity timestamp ahead of as_of by no more than 2 s (−2 s ≤ age < 0) shall be treated as fresh; ahead by more than 2 s (age < −2 s) is CAPACITY_INVALID (Q-SPEC-10, Q-SPEC-13). | timestamp, as_of → usable / invalid | Future-dated beyond 2 s → refuse for that tie. | Test: age −1.999 s, −2.000 s (fresh), −2.001 s (invalid). Oracle: closed-form `age < −2`. | — |
| REQ-TIECAP-8 | For a candidate tie whose entry has `kw` NaN, +inf, −inf or negative (any value for which `math.isfinite(kw) and kw ≥ 0` is False), or a `timestamp` more than 2 s ahead of as_of, `build_plan` shall emit no step for that tie and record `BlockedTie(reason=CAPACITY_INVALID)`. It shall never clamp or substitute a value (Q-SPEC-9 as amended by Q-SPEC-13, Q-SPEC-10). `kw = 0.0` and `kw = −0.0` are valid. Timezone-naive and unparseable timestamps never reach the planner (REQ-TIECAP-1). | kw, timestamp → usable / blocked | Invalid → refuse for that tie only. | Test: each class at `build_plan` level; JSON `NaN`, `Infinity`, `-Infinity`, `-1` through HTTP → 200 with CAPACITY_INVALID. | — |
| REQ-TIECAP-9 | When several conditions apply to one tie, `build_plan` shall record only the first in the order CAPACITY_INVALID, CAPACITY_UNKNOWN, CAPACITY_STALE, CAPACITY_EXCEEDED (Q-SPEC-9). | entry → single reason | — | Test: every pair/combination of conditions, e.g. NaN + BAD + stale → INVALID; BAD + stale → UNKNOWN; stale + exceeded → STALE. Oracle: closed-form precedence function in the QA test. | — |
| REQ-TIECAP-10 | A blocked tie shall not change the plan's isolation steps, the lockout re-close step, or how any other candidate tie is evaluated (per-tie blocking, Q-SPEC-5). | per-tie inputs → plan | — | Test: two-tie generated topology, one tie usable, one blocked; isolation and the other tie's step equal the plan built with the blocked tie's entry made usable-but-exceeded. | — |
| REQ-TIECAP-11 | `RestorationPlan` shall gain `blocked_ties: list[BlockedTie]`, `BlockedTie{tie_id: str, reason}`, reason ∈ {CAPACITY_UNKNOWN, CAPACITY_STALE, CAPACITY_INVALID, CAPACITY_EXCEEDED}, with exactly one entry per blocked candidate tie, in `feeder.switches` order, empty when none is blocked (Q-SPEC-5). | — → plan field | — | Test (schema + content); inspection of `models.py`. | — |
| REQ-TIECAP-12 | For each blocked tie, `RestorationPlan.notes` shall contain one operator-readable entry naming the tie (`Switch.name`) and the reason; for CAPACITY_EXCEEDED it shall also state L and C in kW to at least 0.1 kW resolution; for CAPACITY_STALE the age in seconds. | blocked tie → note | — | Test: content asserted per reason. | — |
| REQ-TIECAP-13 | `POST /flisr/plan` shall accept a body field `tie_capacity` (object: tie mRID → `TieCapacity`) and an optional `as_of`; it shall return HTTP 200 with the plan, including `blocked_ties`, when ties are blocked, never 409 for a blocked tie (Q-SPEC-5). Request validation shall reject with HTTP 422, before the planner runs: wrong JSON types at any level (no string→number, bool→number or number→datetime coercion; `null` for an object field), missing required fields, unknown fields at body or `TieCapacity` level, any `TieCapacity` rejection of REQ-TIECAP-1, and any `as_of` rejection of REQ-TIECAP-23 (Q-SPEC-9, Q-SPEC-12, Q-SPEC-13). Existing 404 (unknown feeder) and 409 (`FlisrError`) are unchanged. | HTTP body → status + plan | Malformed → 422, no plan. | Test (FastAPI `TestClient`): `"kw": "2000"`, `"timestamp": "yesterday"`, `"timestamp": 1790000000`, naive timestamp, extra body field, `TieCapacity` missing `quality`, `"tie_capacity": null` → 422; one blocked tie → 200. Each 422 asserts the planner was not called. | — |
| REQ-TIECAP-14 | The response body shall always carry `as_of`: the instant used, as a timezone-aware UTC value — the supplied value normalised to UTC, or the server now when absent (Q-SPEC-10, Q-SPEC-12(b)). | as_of → echoed as_of | — | Test: `2026-10-15T23:00:00+01:00` echoed as the instant `2026-10-15T22:00:00Z`; absent → a UTC instant between the request's send and receive times. Comparison on parsed instants. | — |
| REQ-TIECAP-15 | `tie_capacity` and the legacy `tie_capacity_kw` shall be mutually exclusive: both present in one body → HTTP 422 (Q-SPEC-11); both passed to `build_plan` → `build_plan` raises and returns no plan. | body → 422 / raise | — | Test: both present (including both `{}`) → 422; `build_plan` with both → raises. | — |
| REQ-TIECAP-16 | For one release, a request carrying only `tie_capacity_kw` (`dict[str, float]`) — and `build_plan` called with only `tie_capacity_kw` — shall be evaluated as `TieCapacity(kw=value, timestamp=as_of, quality="GOOD")` per entry through REQ-TIECAP-3..12, and the response shall carry `deprecations: ["tie_capacity_kw"]` (Q-SPEC-3, Q-SPEC-11). Otherwise `deprecations` is `[]`. | legacy map → same decisions + deprecations | Tie missing from the legacy map → CAPACITY_UNKNOWN. Legacy NaN / ±inf / negative → CAPACITY_INVALID. Wrong JSON type → 422. | Test: legacy-only with C = 2000.0 gives the same steps and totals as `tie_capacity` with GOOD/as_of; `deprecations` asserted. | — |
| REQ-TIECAP-17 | The `POST /flisr/plan` OpenAPI description shall state that `tie_capacity_kw` is deprecated, is removed after one release, and is mutually exclusive with `tie_capacity` (Q-SPEC-11). The Document stage's docs page carries the same note. | — → OpenAPI text | — | Inspection: `app.openapi()` text for `/flisr/plan`. | — |
| REQ-TIECAP-18 | For each blocked tie, `build_plan` shall add the customers of its candidate sections to `customers_remaining` and add nothing to `customers_restored` or `transferred_load_kw`. Closed-tie accounting is unchanged. | plan totals | — | Test; oracle: independent sums over the test topology. | — |
| REQ-TIECAP-19 | When no fault indication is present (`faulted_section is None`), the plan shall be as today (no isolation, no restoration, manual-patrol note) with `blocked_ties` empty. | — | — | Test (characterization). | — |
| REQ-TIECAP-20 | as_of shall be fixed once per `build_plan` call; every entry in one plan is aged against the same instant. | — | — | Test and inspection (no clock read inside the per-tie loop). | — |
| REQ-TIECAP-21 | Safety invariant: no plan shall contain a `close` step for a tie unless that tie's capacity is usable and `L ≤ C + 0.5 kW`; every candidate tie not closed shall appear exactly once in `blocked_ties` with the reason the REQ-TIECAP-9 precedence gives. | generated feeders + capacity maps + as_of → plans | Covers missing, non-GOOD, stale, boundary-age, future-dated, non-finite, negative, below / at / above `L + τ`. | Test (STD-SAFETY-5): ≥ 500 seeded `random` cases over radial and branched topologies with one or more ties (the seeded generator in `backend/tests/rca_def_flisr_7_sweep.py` on branch `agent/rca-backfeed/explore` may be reused). Oracle: the QA-owned BFS of REQ-TIECAP-3 plus closed-form usability and precedence checks. | — |
| REQ-TIECAP-22 | For inputs where every candidate tie has usable capacity and `L ≤ C` or `L > C + 0.5 kW`, the isolation steps, restoration steps and their order, `customers_restored`, `customers_remaining` and `transferred_load_kw` shall equal `main` @ 5f6b471. | — | — | Test: `@pytest.mark.characterization` tests pinned on unmodified code before any change (STD-SAFETY-2). | — |
| REQ-TIECAP-23 | Request validation of `POST /flisr/plan` shall reject `as_of` with HTTP 422 when it is timezone-naive, not an ISO-8601 datetime string (including JSON numbers and `null`), more than 60 s before server now (`server_now − as_of > 60 s`) or more than 2 s after server now (`as_of − server_now > 2 s`). Exactly 60 s before and exactly 2 s after are accepted. A non-UTC offset is accepted and normalised (Q-SPEC-12). | as_of, server now → accept / 422 | Invalid or out-of-bound → 422, no plan; operator retries. | Test with an injected server clock: −60.000 s, +2.000 s accepted; −60.001 s, +2.001 s, naive, `"yesterday"`, `1790000000` → 422. Oracle: closed-form bound. Analysis: with the bound, a back-dated as_of can make a capacity value at most 60 s + 20 s = 80 s older than server now look fresh. | — |

### Intended behaviour changes (blast radius)

1. A candidate tie with no capacity entry was skipped with a "0 kW available" note; it is now blocked CAPACITY_UNKNOWN. Steps and accounting are identical; note text and `blocked_ties` are new.
2. `C < L ≤ C + 0.5 kW` used to skip the tie and now closes it (Q-SPEC-1/Q-SPEC-4). This is the **only** change that makes the planner more permissive; reviewers should confirm it.
3. Legacy NaN / ±inf / negative values were compared numerically. `L > NaN` is False, so on the shipped model a NaN capacity **closes** `TIE-1201-1405` today, and so does +inf (re-measured this attempt). Both are now CAPACITY_INVALID, which removes a latent unsafe close.
4. HTTP: string→number coercion and unknown fields, accepted today, become 422. Clients that relied on them break.
5. Back-dating is bounded, not removed: an as_of up to 60 s behind server now is accepted (Q-SPEC-12(d)), so a capacity value up to 80 s older than server now can still be used. Reviewers should confirm this residual window is acceptable.
6. Response schema gains `blocked_ties`, `as_of`, `deprecations` (additive).

## 2. Open questions (STD-REQ-4)

None open. Resolved this attempt:

- **Q-SPEC-12** (invalid `as_of`) → REQ-TIECAP-2, REQ-TIECAP-13, REQ-TIECAP-14, REQ-TIECAP-23: naive or unparseable → 422; non-UTC offset normalised; bounded to [server now − 60 s, server now + 2 s].
- **Q-SPEC-13** (unparseable capacity timestamp) → REQ-TIECAP-1, REQ-TIECAP-8, REQ-TIECAP-13: strict timezone-aware ISO-8601 field; non-ISO string, JSON number or naive value → 422; per-tie CAPACITY_INVALID for timestamps covers only future-dated beyond 2 s.

## 3. Scope exclusions (STD-REQ-7)

- SCADA adapter and telemetry ingestion: scan scheduling, quality mapping, timestamping (integration team, Q-SPEC-3).
- Spare capacity of one alternate feeder shared by several ties (Q-SPEC-7); each tie is checked independently.
- Partial pick-up or load shedding to fit within capacity (Q-SPEC-6).
- Nameplate / thermal rating of the tie switch, unit conversion, per-unit bases, any safety margin beyond τ (Q-SPEC-1, Q-SPEC-4).
- Removing legacy `tie_capacity_kw` (separate change after one release, Q-SPEC-11).
- `tie_capacity` entries whose key is not a candidate tie of the feeder: ignored as today; not validated, not listed.
- `locate_fault` / fault-location logic; `_isolation_switches` and DEF-FLISR-7 (a tie that is an isolation point back-feeds the faulted section) — separate defect run. This change shall neither fix nor mask DEF-FLISR-7.
- Non-SCADA-controllable ties and ties with an empty candidate set: skipped silently as today, not in `blocked_ties`.
- `console/**` (does not call `/flisr/plan`), `state_estimator.py`, `agc.py`, `savecase.py`, `firmware/**`, `legacy/**`.

## 4. Verification notes for QA

- Independent oracle: QA-owned BFS over the test topology plus closed-form `L ≤ C + 0.5`, `age > 20`, `age < −2`, `quality == "GOOD"`, `math.isfinite(kw) and kw ≥ 0`, and the REQ-TIECAP-9 precedence. It must not import `app.network` or `app.flisr` helpers.
- Tolerance 0.5 kW engineering units; per-unit tolerance waived by Q-SPEC-4 — record the waiver against STD-SAFETY-6.
- Order of work (`.agents/skills/safety-critical-change/SKILL.md`): baseline → characterization (REQ-TIECAP-19, REQ-TIECAP-22) → failing reproductions (missing capacity read as 0 kW with no machine-readable reason; legacy NaN closes the tie) → minimal fix → invariant (REQ-TIECAP-21, ≥ 500 seeded cases).
- Design note (measured, pydantic 2.14.1 / fastapi 0.143.1): a model-wide `ConfigDict(strict=True)` makes FastAPI reject valid ISO-8601 strings for datetime fields (`datetime_type`), because the body is validated in Python mode. Strictness must be applied so REQ-TIECAP-1/13 hold: numbers and strings strict, datetimes parsed from ISO-8601 strings only.
- Tests for REQ-TIECAP-23 need an injectable server clock; boundary values cannot be hit reliably against the wall clock.
- Tool classification (STD-SAFETY-7) is the assessor's finding; this specification claims no tool-certification credit.


## Prior artifact: design

docs/specs/feature-tie-capacity/design.md

## Prior artifact: architecture_review

docs/specs/feature-tie-capacity/architecture-review.md (attempt 5 section) on agent/feature-tie-capacity/architect @ 190fe5a62f419bc62f55a88734e4f48cc1ce29c8

## Prior artifact: coding_report

{
  "verdict": "PASS",
  "summary": "U1 (test-only baseline) delivered as draft PR #16 with the ai-generated label, stacked on agent/rca-backfeed/fix @ 20d2a30 (DEF-FLISR-7, PR #13), which is the characterization base set by the design. Two new test files, no production changes. 23 characterization tests pin build_plan's isolation, restoration, ordering, customers_restored, customers_remaining and transferred_load_kw through legacy tie_capacity_kw (REQ-TIECAP-22), plus the no-fault plan with blocked_ties == [] (REQ-TIECAP-19). 4 strict-xfail reproductions cover missing capacity -> CAPACITY_UNKNOWN (REQ-TIECAP-5) and NaN/+inf -> no close (REQ-TIECAP-8); all 4 fail under --runxfail on the unmodified base and on main. pytest backend: 34 passed, 4 xfailed. ruff check backend: passes. Console build: passes. CI 'backend' job fails on a pre-existing UP017 in tools/build_coverage_report.py (ruff check backend tools). Base PR #13 fails identically, and the fix is outside this unit's allowed files.",
  "evidence": [
    {
      "kind": "pr",
      "ref": "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/16",
      "detail": "Draft, label ai-generated, base agent/rca-backfeed/fix; diff 2 files +354/-0"
    },
    {
      "kind": "commit",
      "ref": "7e6453f",
      "detail": "Characterization tests; carries AI-Governance trailer"
    },
    {
      "kind": "commit",
      "ref": "6b4c72d",
      "detail": "Strict-xfail reproductions; carries AI-Governance trailer"
    },
    {
      "kind": "command",
      "ref": "git diff 20d2a30 <branch point> -- backend/",
      "detail": "Empty: no base drift"
    },
    {
      "kind": "command",
      "ref": "pytest backend -q",
      "detail": "34 passed, 4 xfailed on base+PR (13 passed before); on main @ 5f6b471 with the same files: 23 passed, 4 xfailed"
    },
    {
      "kind": "command",
      "ref": "pytest backend/tests/test_flisr_tie_capacity_repro.py -q --runxfail",
      "detail": "4 failed, as intended: 'assert None == [{tie_id: TIE-1201-1405, reason: CAPACITY_UNKNOWN}]' and 'Left contains one more item: TIE-1201-1405 close' for nan/+inf; same on main"
    },
    {
      "kind": "command",
      "ref": "ruff check backend",
      "detail": "All checks passed"
    },
    {
      "kind": "command",
      "ref": "npm --prefix console ci --no-audit --no-fund && npm --prefix console run build",
      "detail": "Built in 439ms"
    },
    {
      "kind": "command",
      "ref": "pytest --cov=app --cov-branch",
      "detail": "app/flisr.py coverage 95% (base 94%)"
    },
    {
      "kind": "note",
      "ref": "CI backend job 116742213242",
      "detail": "Fails at 'ruff check backend tools': UP017 in tools/build_coverage_report.py:183 (ruff 0.17.1). Pre-existing; base PR #13 backend job also fails. Not fixable in U1 under STD-CODE-2. CI ui and native jobs pass."
    }
  ],
  "questions": [
    {
      "id": "Q-CODE-U1-1",
      "question": "CI 'backend' fails on a pre-existing ruff UP017 in tools/build_coverage_report.py, outside U1's allowed files, and PR #13 fails the same way. Should a separate change fix it?",
      "blocking_units": []
    },
    {
      "id": "Q-CODE-U1-2",
      "question": "PR #16 targets agent/rca-backfeed/fix (stacked on PR #13, as the design requires). Retarget it to main after #13 lands?",
      "blocking_units": []
    }
  ],
  "trace": [
    {
      "requirement_id": "REQ-TIECAP-22",
      "kind": "test",
      "ref": "backend/tests/test_flisr_tie_capacity_characterization.py::test_req_tiecap_22_char_*"
    },
    {
      "requirement_id": "REQ-TIECAP-19",
      "kind": "test",
      "ref": "backend/tests/test_flisr_tie_capacity_characterization.py::test_req_tiecap_19_char_no_fault_indication_plan"
    },
    {
      "requirement_id": "REQ-TIECAP-5",
      "kind": "test",
      "ref": "backend/tests/test_flisr_tie_capacity_repro.py::test_req_tiecap_5_repro_missing_capacity_blocks_tie_as_unknown"
    },
    {
      "requirement_id": "REQ-TIECAP-8",
      "kind": "test",
      "ref": "backend/tests/test_flisr_tie_capacity_repro.py::test_req_tiecap_8_repro_non_finite_capacity_never_closes_tie"
    },
    {
      "requirement_id": "REQ-TIECAP-22",
      "kind": "pr",
      "ref": "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/16"
    }
  ],
  "standards_loaded": [
    "STD-CODE-1",
    "STD-CODE-2",
    "STD-CODE-3",
    "STD-CODE-4",
    "STD-CODE-5",
    "STD-CODE-6",
    "STD-CODE-7",
    "STD-CODE-8",
    "STD-GOV-1",
    "STD-GOV-2",
    "STD-GOV-3",
    "STD-GOV-4",
    "STD-GOV-5",
    "STD-GOV-6",
    "STD-GOV-7",
    "STD-SAFETY-1",
    "STD-SAFETY-2",
    "STD-SAFETY-3",
    "STD-SAFETY-4",
    "STD-SAFETY-5",
    "STD-SAFETY-6",
    "STD-SAFETY-7",
    "STD-SAFETY-8",
    ".agents/skills/safety-critical-change/SKILL.md"
  ],
  "files_touched": [
    "backend/tests/test_flisr_tie_capacity_characterization.py",
    "backend/tests/test_flisr_tie_capacity_repro.py"
  ],
  "branch": "agent/feature-tie-capacity/U1",
  "pr_url": "https://github.com/tedfoley-cog/adms-test-automation-demo/pull/16",
  "session_url": "https://devin-gtm.devinenterprise.com/sessions/b66ea84b7f1a4727b8073ce4ab60cfaa",
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
      "tail": "\nadded 68 packages in 593ms\n\n> qa-coverage-console@0.1.0 build\n> tsc -b && vite build\n\nvite v5.4.11 building for production...\ntransforming...\n\u2713 37 modules transformed.\nrendering chunks...\ncomputing gzip size...\ndist/index.html                   0.43 kB \u2502 gzip:  0.29 kB\ndist/assets/index-BhRQqo7Z.css    5.29 kB \u2502 gzip:  1.63 kB\ndist/assets/index-DvMiGgeB.js   159.79 kB \u2502 gzip: 50.27 kB\n\u2713 built in 417ms\n"
    },
    "lint": {
      "cmd": "ruff check backend",
      "returncode": 0,
      "tail": "All checks passed!\n"
    },
    "test": {
      "cmd": "pytest backend -q",
      "returncode": 0,
      "tail": "..................................xxxx                                   [100%]\n=============================== warnings summary ===============================\ntests/test_flisr_def_flisr_7.py::test_def_flisr_7_post_flisr_plan_does_not_close_tie_onto_faulted_section\n  /home/ubuntu/.pyenv/versions/3.12.13/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.\n    from starlette.testclient import TestClient as TestClient  # noqa\n\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n34 passed, 4 xfailed, 1 warning in 0.50s\n"
    }
  },
  "branch": "agent/feature-tie-capacity/U1",
  "files_in_diff": [
    "backend/tests/test_flisr_tie_capacity_characterization.py",
    "backend/tests/test_flisr_tie_capacity_repro.py"
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
