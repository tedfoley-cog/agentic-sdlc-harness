# Agentic SDLC stage brief — DESIGN (run feature-tie-capacity, attempt 6)

Role: Designer. Produce the design for the specification within the repo's architecture.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: PASS, BLOCKED. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=feature-tie-capacity stage=design agent=devin model=normal`; PRs carry the `ai-generated` label.

## Access and boundaries
Target repository: `tedfoley-cog/adms-test-automation-demo` (default branch `main`). Safety classification: **safety-critical**.
Files you may change: ['**']. Files you must not change: ['(none)'].
Commands — build: `npm --prefix console ci --no-audit --no-fund && npm --prefix console run build`; test: `pytest backend -q`; lint: `ruff check backend`.
Requirement ids match `(?:REQ|DEF)-[A-Z]+-\d{1,3}`; reference them verbatim.
Protected paths (two human reviewers): ['backend/app/flisr.py', 'firmware/src/**'].
Repo instruction files to read first: ['.agents/skills/safety-critical-change/SKILL.md', 'DEMO_NOTES.md'].
Layer visibility: {"models": ["backend/app/models.py"], "logic": ["backend/app/flisr.py", "backend/app/state_estimator.py", "backend/app/agc.py", "backend/app/network.py", "backend/app/savecase.py"], "api": ["backend/app/api.py"], "ui": ["console/**"], "visibility": {"api": ["logic", "models"], "logic": ["models"], "ui": ["api"]}}.

## Governing standards (loaded at runtime — confirm each id in `standards_loaded`)

### STD-ARCH — STD-ARCH — Architecture and design standard

# STD-ARCH — Architecture and design standard
Version: 2.0

- **STD-ARCH-1**: Data models, settings and scaling constants live in a dedicated module and carry no control flow. Logic modules import models; they do not define them.
- **STD-ARCH-2**: One shared implementation of any numerically sensitive function (e.g. a slope/threshold characteristic) is used by every consumer (firmware, setting tool, test oracle). Duplicated characteristics are a VIOLATION.
- **STD-ARCH-3**: Layer visibility is declared in the repo contract; a lower layer never imports an upper layer. Cross-layer access goes through the declared interface.
- **STD-ARCH-4**: Every public function states its behaviour for absent, stale and out-of-range inputs. Fail-safe is the default: refuse or hold rather than operate on a guessed value.
- **STD-ARCH-5**: Error handling is part of the design. A refactor that removes a guard, exception path or quality flag must show the equivalent handling elsewhere in the same change.
- **STD-ARCH-6**: Designs map every requirement id to at least one component and one test strategy; unmapped requirements are a design defect, not a documentation gap.
- **STD-ARCH-7**: The architect's review is independent: the reviewer does not edit the design, only returns CONFIRMED or VIOLATION with clause references.
- **STD-ARCH-8**: IEC 61850 model exposure (logical nodes, data objects) is added only for settled behaviour; provisional behaviour is kept internal.

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

# Change request: respect tie-switch capacity during FLISR restoration

Restoration plans produced by `backend/app/flisr.py::locate_fault` / the restoration planner must
not transfer more load onto a tie switch than its rated capacity. When the tie capacity is not
known the plan must say so instead of restoring. Telemetry for tie capacity arrives from the SCADA
scan every 10 s.

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


## Prior artifact: units

[
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
  },
  {
    "id": "U2",
    "wave": 2,
    "title": "Domain types: TieCapacity, BlockedTie and RestorationPlan.blocked_ties",
    "requirement_ids": [
      "REQ-TIECAP-1",
      "REQ-TIECAP-11"
    ],
    "depends_on": [
      "U1"
    ],
    "files": [
      "backend/app/models.py",
      "backend/tests/test_flisr_tie_capacity_models.py"
    ],
    "safety": "safety-critical (inherited, STD-REQ-6). models.py is not a protected path, but the types gate which ties FLISR closes and ship in the protected-path change set: two human reviewers (STD-GOV-6, STD-SAFETY-1).",
    "scope_notes": [
      "Additive only: TieCapacity{kw, timestamp, quality} with extra fields forbidden; BlockedTie{tie_id, reason}; reason enum {CAPACITY_UNKNOWN, CAPACITY_STALE, CAPACITY_INVALID, CAPACITY_EXCEEDED}; RestorationPlan.blocked_ties default [].",
      "Strictness per field, not model-wide ConfigDict(strict=True): measured on pydantic 2.14.1 / fastapi 0.143.1, model-wide strict makes FastAPI reject valid ISO-8601 datetime strings (spec section 4 design note). kw strict JSON number (string/bool/null rejected), NaN/+-inf/negative accepted; timestamp ISO-8601 string only, timezone-aware, JSON number and naive rejected; quality strict str; no clock comparison in the model.",
      "No change to build_plan or api.py in this unit; U1 characterization must stay green."
    ],
    "oracle": "Model unit tests per accept/reject class listed in REQ-TIECAP-1 ('yesterday', 1790000000, naive '2026-10-15T22:00:00', '2000', true, extra field -> reject; NaN, -1.0, +02:00 offset -> accept) validated both via model_validate_json and via a FastAPI TestClient echo route defined inside the test, so the HTTP (Python-mode) validation path is exercised; inspection of models.py; U1 suite re-run green."
  },
  {
    "id": "U3",
    "wave": 3,
    "title": "Planner and endpoint: build_plan tie-capacity evaluation, legacy compatibility and POST /flisr/plan validation",
    "requirement_ids": [
      "REQ-TIECAP-2",
      "REQ-TIECAP-3",
      "REQ-TIECAP-4",
      "REQ-TIECAP-5",
      "REQ-TIECAP-6",
      "REQ-TIECAP-7",
      "REQ-TIECAP-8",
      "REQ-TIECAP-9",
      "REQ-TIECAP-10",
      "REQ-TIECAP-12",
      "REQ-TIECAP-13",
      "REQ-TIECAP-14",
      "REQ-TIECAP-15",
      "REQ-TIECAP-16",
      "REQ-TIECAP-17",
      "REQ-TIECAP-18",
      "REQ-TIECAP-20",
      "REQ-TIECAP-23"
    ],
    "depends_on": [
      "U2"
    ],
    "files": [
      "backend/app/flisr.py",
      "backend/app/api.py",
      "backend/app/models.py",
      "backend/tests/test_flisr_tie_capacity_planner.py",
      "backend/tests/test_flisr_tie_capacity_api.py",
      "backend/tests/test_flisr_tie_capacity_repro.py"
    ],
    "safety": "safety-critical (inherited, STD-REQ-6). Touches protected path backend/app/flisr.py: two human reviewers required irrespective of agent confidence (STD-GOV-6, STD-SAFETY-1).",
    "scope_notes": [
      "Why one unit for two modules: REQ-TIECAP-15 and REQ-TIECAP-16 each state a build_plan clause and an HTTP clause, and the legacy tie_capacity_kw path (REQ-TIECAP-16) must be migrated in the same step as the new tie_capacity path or the U1 characterization (which uses the legacy interface) breaks or REQ-TIECAP-5's inspection of flisr.py:98 fails in an intermediate state. Splitting would require a transiently non-conforming unit.",
      "Smallest fail-safe change (STD-SAFETY-4): remove the 0.0 default at flisr.py:98; per-tie usability with precedence INVALID > UNKNOWN > STALE > EXCEEDED; close iff L <= C + 0.5 kW; as_of read once per call (REQ-TIECAP-20); blocked ties add only to customers_remaining (REQ-TIECAP-18); one note per blocked tie (REQ-TIECAP-12).",
      "models.py is in scope only for response fields the Design stage places on RestorationPlan (as_of, deprecations, REQ-TIECAP-14/16) and for request types; the TieCapacity/BlockedTie definitions from U2 are not to be changed.",
      "api.py: injectable server clock (spec section 4) for REQ-TIECAP-23 boundary tests; 422 before the planner runs for every malformed body (each 422 test asserts build_plan was not called); 200 with blocked_ties, never 409, for a blocked tie; OpenAPI description carries the deprecation and mutual-exclusion note (REQ-TIECAP-17).",
      "Remove only the xfail markers in test_flisr_tie_capacity_repro.py; the repro tests must then pass unmodified otherwise.",
      "Out of scope (spec section 3): DEF-FLISR-7 / _isolation_switches, locate_fault, SCADA adapter, shared alternate-feeder capacity, partial pick-up, console/**, state_estimator.py, agc.py, savecase.py, firmware/**, legacy/**."
    ],
    "oracle": "Independent closed-form checks in the QA tests, not importing app.network or app.flisr helpers: QA-owned BFS over the test topology for the candidate node set and L (spec definitions), L <= C + 0.5 kW, age > 20 s, age < -2 s, quality == 'GOOD', math.isfinite(kw) and kw >= 0, the REQ-TIECAP-9 precedence function, and the as_of bound [server_now - 60 s, server_now + 2 s]. Shipped-model boundaries (L = 1490 kW): C = 1490.0 and 1489.5 close, 1489.4 CAPACITY_EXCEEDED; ages 19.999/20.000 fresh, 20.001 stale; -1.999/-2.000 fresh, -2.001 invalid; as_of -60.000/+2.000 accepted, -60.001/+2.001 -> 422. Tolerance 0.5 kW engineering units; per-unit waived by Q-SPEC-4 (record against STD-SAFETY-6). U1 characterization and backend/tests/test_flisr.py green unchanged."
  },
  {
    "id": "U4",
    "wave": 4,
    "title": "Safety invariant: no tie closed without usable capacity and L <= C + 0.5 kW, over >= 500 seeded cases",
    "requirement_ids": [
      "REQ-TIECAP-21"
    ],
    "depends_on": [
      "U3"
    ],
    "files": [
      "backend/tests/test_flisr_tie_capacity_invariant.py"
    ],
    "safety": "safety-critical (inherited, STD-REQ-6). Test-only; ships in the protected-path change set: two human reviewers (STD-GOV-6, STD-SAFETY-1).",
    "scope_notes": [
      "STD-SAFETY-5: at least 500 seeded random cases over radial and branched feeders with one or more SCADA ties; capacity maps covering missing, non-GOOD, stale, boundary age, future-dated, NaN/+-inf, negative, below/at/above L + 0.5 kW; injected as_of.",
      "The seeded generator in backend/tests/rca_def_flisr_7_sweep.py (branch agent/rca-backfeed/explore, not on main) may be copied into this one file; it only places ties at the feeder tail, so the generator must also place ties elsewhere to exercise multi-tie per-tie blocking.",
      "The invariant is about capacity gating only; it must neither assert nor exclude DEF-FLISR-7 back-feed (spec section 3). The oracle reproduces the specification's candidate-set definition, including today's pick-up semantics."
    ],
    "oracle": "QA-owned BFS of REQ-TIECAP-3 plus closed-form usability and REQ-TIECAP-9 precedence, implemented in the test file without importing app.network or app.flisr helpers; seed and case count printed in the test output for the PR evidence."
  }
]

## Feedback from the previous iteration (resolve every item or explain why not)

```json
[
  {
    "from": "architect",
    "iteration": 3,
    "verdict": "VIOLATION",
    "summary": "Architecture review attempt 3 of design attempt 5 (1238178): VIOLATION. A-2 and A-4 are resolved, and A-3 is resolved in the prose and units. Still open, A-5 (STD-ARCH-4, STD-GOV-3, STD-ARCH-6): the normative tie-loop pseudocode in design \u00a74 (lines 183-188), the \u00a77 REQ-TIECAP-9 row, \u00a79 Q-DESIGN-3 and \u00a710.1 O-2 put the DEF-FLISR-7 guard before the Q-DESIGN-2 section-load check. The \u00a74 table, the line-224 prose and units.json U3 say the opposite. Measured on base 20d2a30: a held tie with NaN or -120 load on SEC-1201-04 returns a plan instead of FlisrError. Also, the unamended scope notes in units.json U4 (neither assert nor exclude back-feed) and U3 (precedence without FAULTED_SECTION) contradict the amendments. The fix is a Design-stage change that keeps the design consistent with itself; no new question is needed. The design was not edited.",
    "findings": [
      {
        "kind": "file",
        "ref": "docs/specs/feature-tie-capacity/design.md@1238178#L183-188",
        "detail": "Pseudocode: the guard branch ends with 'continue  # before any load or capacity evaluation'; the section-load FlisrError check comes after it"
      },
      {
        "kind": "file",
        "ref": "docs/specs/feature-tie-capacity/design.md@1238178#L169,L224",
        "detail": "Table and prose: the section-load check covers every candidate tie, held or not, before the guard"
      },
      {
        "kind": "file",
        "ref": "docs/specs/feature-tie-capacity/design.md@1238178#L327,L374,L389",
        "detail": "\u00a77 REQ-TIECAP-9 'guard \u2192 section check \u2192 verdict'; \u00a79 and \u00a710.1 O-2 'guard ahead of load evaluation'"
      },
      {
        "kind": "file",
        "ref": "docs/specs/feature-tie-capacity/units.json@1238178 U4,U3",
        "detail": "U4 'must neither assert nor exclude DEF-FLISR-7 back-feed' vs the amendment 'Held ties: FAULTED_SECTION'; U3 precedence INVALID>UNKNOWN>STALE>EXCEEDED vs the amended REQ-TIECAP-9"
      },
      {
        "kind": "command",
        "ref": "build_plan on 20d2a30, FDR-1201, CB-1201 open, fault SEC-1201-04, SEC-1201-04.load_kw in {NaN,-120}",
        "detail": "Plan returned: restoration [CB-1201 close], customers_remaining 341, held-open note; no FlisrError"
      },
      {
        "kind": "command",
        "ref": "pytest backend -q (20d2a30)",
        "detail": "13 passed, 1 warning"
      },
      {
        "kind": "command",
        "ref": "ruff check backend (20d2a30)",
        "detail": "All checks passed!"
      },
      {
        "kind": "command",
        "ref": "prototype adding as_of/blocked_ties/deprecations to RestorationPlan on 20d2a30, reverted",
        "detail": "Exactly 5 of 13 base tests fail, as design \u00a76.1 states"
      },
      {
        "kind": "commit",
        "ref": "e2339d5",
        "detail": "architecture-review.md on agent/feature-tie-capacity/architect, AI-Governance trailer"
      },
      {
        "kind": "standard",
        "ref": "STD-ARCH-4",
        "detail": "Same input stated with two behaviours"
      },
      {
        "kind": "standard",
        "ref": "STD-GOV-3",
        "detail": "Pseudocode departs from the recorded Q-DESIGN-2 answer"
      },
      {
        "kind": "standard",
        "ref": "STD-ARCH-6",
        "detail": "REQ-TIECAP-9 component mapping and U3/U4 unit scope notes are inconsistent"
      }
    ],
    "review": "# Architecture review \u2014 FLISR restoration respects tie-switch capacity\n\nRun: `feature-tie-capacity` \u00b7 Stage: ARCHITECT \u00b7 Attempt: 3 \u00b7 Reviewed: `docs/specs/feature-tie-capacity/design.md`, `specification.md` amendments and `units.json` amendments @ `1238178` (design attempt 5, draft PR #15), against the declared base `agent/rca-backfeed/fix` @ `20d2a30` (PR #13) and `main` @ `5f6b471`\nStandards: STD-ARCH v2.0, STD-SAFETY v3.1, STD-GOV v1.1 \u00b7 Safety classification: **safety-critical**\nVerdict: **VIOLATION** (1 finding with two parts: A-5 STD-ARCH-4 / STD-GOV-3 / STD-ARCH-6). Attempt-2 findings A-2 and A-4 are resolved. A-3 is resolved in the prose and the units, but the normative loop pseudocode still has the carve-out (A-5). The design was not edited (STD-ARCH-7).\n\n## Prepare\n\n- Standards loaded from the brief: STD-ARCH (v2.0), STD-SAFETY (v3.1), STD-GOV (v1.1).\n- Repo instructions read: `.agents/skills/safety-critical-change/SKILL.md`, `DEMO_NOTES.md`.\n- Layer map (brief): `ui \u2192 api \u2192 logic \u2192 models`. logic = `flisr.py`, `state_estimator.py`, `agc.py`, `network.py`, `savecase.py`; models = `models.py`; api = `api.py`.\n- Baseline re-run this attempt on a worktree of `20d2a30`: `pytest backend -q` \u2192 **13 passed**, `ruff check backend` \u2192 all checks passed.\n\n## Attempt-2 items\n\n| Item | Status | Evidence |\n|---|---|---|\n| A-2 (STD-ARCH-6) | **Resolved** | REQ-TIECAP-18 amended in `specification.md` @ 1238178 (capacity-blocked: all candidate sections; FAULTED_SECTION: candidate sections other than the faulted one). This matches `flisr.py` @ 20d2a30 guard accounting (`section.mrid != faulted_section.mrid`). Measured: fault on `SEC-1201-04`, `customers_remaining` = 341. Design \u00a74 row, \u00a77 row and U3/U4 notes are consistent with it. |\n| A-3 (STD-GOV-3, STD-ARCH-4) | **Partly resolved, see A-5** | The header, the \u00a74 input table (line 169), the \u00a74 \"Integration with DEF-FLISR-7\" paragraph (line 224), \u00a76.3 (`oracle_sections_ok` checked before `oracle_held`), \u00a78, \u00a79, \u00a710.2 and `units.json` U3/U4 now apply Q-DESIGN-2 to every candidate tie, before the guard. REQ-TIECAP-21 now has only the Q-DESIGN-3 amendment, as Q-DESIGN-2 directs. |\n| A-4.1 (STD-SAFETY-2) | **Resolved** | Base named by SHA `20d2a303c9548f9f7170cb3dfef1487fb7e9a009` in the design header, REQ-TIECAP-22 and U1, with a base-drift STOP. PR #14's QA file is excluded. \"5 of 13\" re-measured: adding `as_of`, `blocked_ties` and `deprecations` to `RestorationPlan` on 20d2a30 fails exactly the 5 tests the design names (\u00a76.1). |\n| A-4.2 (STD-ARCH-6) | **Resolved** except U4, see A-5(b) | `units.json` @ 1238178: U1 base, U2 enum of 5 members, U3 files +2 base test files and +REQ-TIECAP-11, U3 loop-order note, U4 held-tie note. |\n| O-B (STD-ARCH-4) | Resolved | \u00a74 row for a non-datetime `as_of`. |\n| O-C (STD-GOV-7) | Open (platform) | see Observations. |\n| O-D (REQ-TIECAP-12) | Accepted | PR #13 note text unchanged; code in `blocked_ties`. |\n\n## Finding (VIOLATION)\n\n### A-5 \u2014 STD-ARCH-4, STD-GOV-3, STD-ARCH-6: the normative tie-loop pseudocode still exempts held ties from the Q-DESIGN-2 check\n\n**(a) design.md.** Attempt 5 says the tie-loop order is \"empty-candidate skip \u2192 section-load precondition (every candidate tie) \u2192 DEF-FLISR-7 guard \u2192 L precondition \u2192 `tie_capacity_verdict`\". This appears in the \u00a74 paragraph (line 224), in the \u00a74 table (line 169, \"held or not, checked before the guard\") and in units.json U3. Other parts of the design still give the old order:\n\n- **\u00a74 \"Tie loop\" pseudocode (lines 183\u2013188).** The loop that \"replaces `flisr.py:92-121`\" runs the guard first and ends its branch with `continue  # before any load or capacity evaluation`. The `for sec in sections \u2026: raise FlisrError` check comes after that `continue`. Implemented as written, a held tie's pick-up sections are never checked, which is exactly the attempt-4 carve-out that A-3 rejected.\n- **\u00a77 row REQ-TIECAP-9 (line 327)**: \"loop order: guard \u2192 section check \u2192 `tie_capacity_verdict`\".\n- **\u00a79 Q-DESIGN-3 (line 374)**: \"The guard runs before load and capacity evaluation\". **\u00a710.1 O-2 (line 389)**: \"first in the loop and ahead of load and capacity evaluation\".\n\nMeasured on the base @ 20d2a30, where the guard runs first and no load check exists, so this is the outcome the pseudocode keeps for a held tie. Setup: shipped `FDR-1201`, `CB-1201` open, fault indications on SEC-1201-01..03, so the fault is on `SEC-1201-04`; `TIE-1201-1405` = 2000 kW. With `SEC-1201-04.load_kw` = NaN, and again with \u2212120.0, a plan **is returned**: restoration `[CB-1201 close]`, `customers_remaining` 341, the held-open note. Q-DESIGN-2 as written, and the design's own \u00a74 table, require `FlisrError` with no plan.\n\nThe design states two different behaviours for the same input, so STD-ARCH-4 is not met: the stated behaviour must be the one that governs. The pseudocode is the part Coding implements, and it departs from the recorded human answer, which STD-GOV-3 forbids. The independent oracle (\u00a76.3) uses the prose order, so QA would probably catch the difference. But the design is the contract and must not depend on QA to settle its own contradiction.\n\n**(b) units.json U4.** The original U4 scope note was not amended: \"The invariant is about capacity gating only; it must neither assert nor exclude DEF-FLISR-7 back-feed (spec section 3)\". The amendment added next to it says \"Held ties: FAULTED_SECTION whatever the capacity \u2026\", and design \u00a77 REQ-TIECAP-21 says \"no close step unless the tie is not held\". So U4 now asserts the DEF-FLISR-7 hold, and its two scope notes contradict each other. The same applies to U3's unamended note \"per-tie usability with precedence INVALID > UNKNOWN > STALE > EXCEEDED\", which conflicts with the amended REQ-TIECAP-9 (FAULTED_SECTION first). The amended note is right next to it, so this one matters less. These are the unit-boundary consistency points A-4.2 asked for (STD-ARCH-6: requirement \u2192 component \u2192 test must agree).\n\n**Resolution (Design stage; no new scope, no new question):**\n\n1. Reorder the \u00a74 pseudocode to match line 224: the section-load check for each candidate tie comes before the guard branch.\n2. Make \u00a77 REQ-TIECAP-9, \u00a79 and \u00a710.1 O-2 consistent with that order. Note that the guard still comes before L and capacity, but after the section-load check.\n3. Mark the stale U4 and U3 scope notes in `units.json` as superseded, using the same `[Design attempt N amendment]` convention.\n\n## Clause-by-clause check\n\n| Clause | Result | Evidence |\n|---|---|---|\n| STD-ARCH-1 | Conforms | Constants, `IsoAwareDatetime`, `TieCapacity`, `TieBlockReason` (5), `BlockedTie` and the `RestorationPlan` fields are in `models.py` (\u00a72). Decisions are in `flisr.py` (\u00a73\u20134). `_require_iso_string` is a type parser (O-1). `FlisrRequest` is an API DTO (O-A). |\n| STD-ARCH-2 | Conforms under the scoped waiver | One production characteristic, `tie_capacity_verdict`, and one predicate, `_not_finite_nonneg`. Parameters come only from `models.py`, enforced by P1/P2. The oracle restatement is waived per Q-DESIGN-1 and limited to three `backend/tests` files (\u00a76.3). FAULTED_SECTION is not a verdict output. |\n| STD-ARCH-3 | Conforms | `models` imports pydantic/stdlib only, `flisr` imports `.models` and `.network`, `api` imports `.flisr`, `.models` and `.network`. This matches the imports in `flisr.py`/`api.py` @ 20d2a30. No upward import. |\n| STD-ARCH-4 | **VIOLATION (A-5a)** | The same input (a held tie with an invalid pick-up load) is stated two ways: \u00a74 table/line 224 say `FlisrError`, the \u00a74 pseudocode says plan returned. Every other row is stated. |\n| STD-ARCH-5 | Conforms | \u00a74 removed-guard table. The PR #13 guard is kept byte-for-byte, and its branch only adds a `blocked_ties.append`. |\n| STD-ARCH-6 | **VIOLATION (A-5a \u00a77 row, A-5b units)** | All REQ-TIECAP-1..23 are mapped in \u00a77 (checked id by id). The REQ-TIECAP-9 component mapping gives the wrong order, and U4/U3 carry contradictory scope notes. |\n| STD-ARCH-7 | Conforms | Review only. `design.md`, `specification.md` and `units.json` on this branch are byte-identical to `1238178` (`git diff 1238178` empty for the three files). |\n| STD-ARCH-8 | Conforms | No IEC 61850 LN/DO exposure. |\n| STD-SAFETY-1 | Conforms | Safety-critical. Protected `backend/app/flisr.py` needs two human reviewers (header, U1\u2013U4). |\n| STD-SAFETY-2 | Conforms | The characterization base is pinned by SHA with a drift STOP. The \u00a76.1 edit rule for the 5 affected base tests keeps every step and count unchanged. |\n| STD-SAFETY-3 | Conforms | U1 reproductions re-measured on 20d2a30, shipped model, `CB-1201` open, fault on SEC-1201-03. No entry: tie skipped with no machine-readable reason. Legacy NaN and +inf: `TIE-1201-1405` **closed**, `customers_restored` 341. Both fail as `xfail(strict=True)` intends. |\n| STD-SAFETY-4 | Conforms in the prose; at risk through A-5a | Fail-safe preconditions and per-tie blocking. A held tie with an invalid load must refuse the plan, as Q-DESIGN-2 requires. |\n| STD-SAFETY-5 | Conforms | U4 has \u2265 500 seeded cases, with \u2265 5 % each of out-of-range L, a negative section inside a positive total, and held ties. Seed and count are printed. |\n| STD-SAFETY-6 | Conforms (per-unit waived by Q-SPEC-4) | Independent `oracle_*` (\u00a76.3), O1 import/constant check, boundaries in \u00a76.2, 0.5 kW in engineering units. |\n| STD-SAFETY-7 | Conforms | \u00a78.1 tool-classification argument. No credit claimed. |\n| STD-SAFETY-8 | Conforms | Local worktrees and synthetic model copies only. |\n| STD-GOV-1/2 | Conforms | `agent/feature-tie-capacity/design`, draft PR #15. Commit `1238178` has the `AI-Governance` trailer. |\n| STD-GOV-3 | **VIOLATION (A-5a)** | The pseudocode departs from the recorded Q-DESIGN-2 answer. |\n| STD-GOV-6 | Conforms | Two human reviewers for the protected path. |\n| STD-GOV-7 | Note (O-C) | |\n\n## Observations (no verdict impact)\n\n- **O-C (STD-GOV-7).** The platform appends a `Co-Authored-By` trailer with a personal name and e-mail to agent commits (design `1238178` and this review's commits). The agent cannot change the commit identity. Carried forward as a compliance note.\n- **O-E (blast radius).** Applying Q-DESIGN-2 before the guard means a fault whose held tie's pick-up set (faulted section included) has an invalid load now returns 409 and no plan, where PR #13 returns isolation steps. The design states this blast radius (\u00a74), and reviewers should confirm it. It follows from the recorded answer, so it is not a finding.\n\n## Verify\n\n- Every finding cites a clause and a measured or quoted source (line numbers in `design.md` @ 1238178, scope notes in `units.json` @ 1238178, plans measured on 20d2a30). None asks for scope outside the specification. The resolution only aligns the design with its own stated order and with Q-DESIGN-2. The Architect makes no design choice.\n- No production or test code changed. Base re-run: `pytest backend -q` 13 passed, `ruff check backend` all checks passed (20d2a30). The prototype edit used to re-measure \"5 of 13\" was reverted in a throw-away worktree.\n"
  }
]
```

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
name: design
description: Produces the design for the approved specification inside the repository's existing architecture — components, data flow, model/logic separation, error handling and the test strategy per requirement. Used before the Architect review and again when the Architect returns VIOLATION.
---

# Design

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Read the instruction files and the layer map from the brief; locate the existing modules the change touches.
2. For each unit: components changed, interfaces, where data models live versus logic (STD-ARCH-1), the single shared implementation of any numerically sensitive function (STD-ARCH-2), behaviour for absent/stale/out-of-range input (STD-ARCH-4), error-handling design (STD-ARCH-5).
3. Map every requirement id to a component and a test strategy (STD-ARCH-6); emit the mapping as `trace[]` rows of kind `design`.
4. When feedback from the Architect is present, address every finding by clause id and say what changed.

## Verify
No requirement unmapped; no model/logic mixing; no guessed defaults.

## Deliver
`artifacts.design` (markdown), `trace[]` design rows. `PASS` or `BLOCKED` with `Q-DESIGN-n`.

## Deliver
Finish by calling provide_structured_output with an object matching the schema you were given: `verdict`, `summary`, `evidence[]`, and where relevant `questions[]`, `trace[]` (requirement_id/kind/ref), `files_touched[]`, `branch`, `pr_url`, `standards_loaded[]`, `artifacts{}` (your stage's named outputs as markdown or JSON strings), `model`.
