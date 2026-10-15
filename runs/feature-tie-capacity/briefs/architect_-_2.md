# Agentic SDLC stage brief — ARCHITECT (run feature-tie-capacity, attempt 2)

Role: Architecture reviewer. Independently check the design against the governing standards.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: CONFIRMED, VIOLATION, BLOCKED, NEEDS-HUMAN. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=feature-tie-capacity stage=architect agent=devin model=normal`; PRs carry the `ai-generated` label.

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

## Prior artifact: design

# Design — FLISR restoration respects tie-switch capacity

Run: `feature-tie-capacity` · Stage: DESIGN · Attempt: 4 · Inputs: `specification.md` (attempt 4, complete; REQ-TIECAP-9/11/21/22 amended per Q-DESIGN-3, §9), `units.json` (U1–U4), `architecture-review.md` (Architect attempt 1, VIOLATION, on `agent/feature-tie-capacity/architect` @ 0584fbb), Q-DESIGN-1..3 answers (principal-engineer-standin)
Safety classification: **safety-critical** (STD-SAFETY-1). Protected path `backend/app/flisr.py`: two human reviewers (STD-GOV-6).
Status: **complete, no open questions** (§9). A-1 (STD-ARCH-4) is resolved for every input, including the negative-section-load case that attempt 3 left open. The design composes on top of the DEF-FLISR-7 hold-open guard (draft PR #13), which is kept unchanged.

Changes from attempt 3:
- **Q-DESIGN-2 (A-1 residual).** `build_plan` refuses the whole plan (`FlisrError`, HTTP 409, no plan, lockout stays open) when **any** candidate section's `load_kw` is NaN, ±inf or < 0, even if L is still ≥ 0. Otherwise L is the plain sum (REQ-TIECAP-3 unchanged). §3, §4, §6.1, §6.2, §7.
- **Q-DESIGN-3 (O-2).** PR #13 lands first and its guard is kept, unchanged and in its place. A new reason `FAULTED_SECTION` reports each tie the guard holds open: one `blocked_ties` entry plus a note naming the tie. Precedence is **FAULTED_SECTION > CAPACITY_INVALID > CAPACITY_UNKNOWN > CAPACITY_STALE > CAPACITY_EXCEEDED**. The guard runs before load and capacity are evaluated. REQ-TIECAP-21 is amended, and so are REQ-TIECAP-9/11/22, which the answer forces (§9). §2, §4, §6, §7.
- **Existing DEF-FLISR-7 tests (measured).** A prototype of this design on top of PR #13's branch (`agent/rca-backfeed/fix` @ 20d2a30) fails 19 of the 38 tests on that branch. Every failure comes from the new plan fields (`as_of`, `blocked_ties`, `deprecations`) or from the REQ-TIECAP-12 note text. None changes a switching step or a count. U3 therefore has to edit those three PR #13 test files under the narrow rule in §6.1.

Baseline re-measured on `main` @ 5f6b471: `pytest backend -q` → 2 passed; on `agent/rca-backfeed/integration`, which carries PR #13: 38 passed, 1 warning; `ruff check backend tools` → 1 pre-existing error in `tools/` (UP017), unrelated to this change.

## 1. Components and layers

Layer map (repo contract): `ui → api → logic → models`. No lower layer imports an upper one (STD-ARCH-3).

| Layer | Module | Change | Imports (allowed) |
|---|---|---|---|
| models | `backend/app/models.py` | New: constants, `IsoAwareDatetime`, `TieCapacity`, `TieBlockReason`, `BlockedTie`. Extended: `RestorationPlan`. | pydantic, stdlib only |
| logic | `backend/app/flisr.py` | New: `tie_capacity_verdict()` (the single capacity characteristic), `_not_finite_nonneg()` (the one finite-and-non-negative predicate, used for C, for L and by the notes), `_legacy_to_tie_capacity()`, `_blocked_note()`. Changed: `build_plan()` signature and tie loop. `locate_fault`, `_isolation_switches`, `_nodes_restored_by` unchanged. | `.models`, `.network` (same layer, as today) |
| logic | `backend/app/network.py` | Unchanged (`load_on_nodes` keeps computing L). | `.models` |
| api | `backend/app/api.py` | Changed: `FlisrRequest`, `flisr_plan` route; new `server_now()` dependency, `_check_as_of_bound()`. | `.flisr`, `.models`, `.network` |
| ui | `console/**` | Unchanged (does not call `/flisr/plan`). | — |

Data flow (HTTP): JSON body → FastAPI/Pydantic request validation (`FlisrRequest`, `TieCapacity`) → `_check_as_of_bound(as_of, server_now)` → `flisr.build_plan(..., tie_capacity | tie_capacity_kw, as_of=resolved)` → per candidate tie `tie_capacity_verdict(entry, L, as_of)` → `RestorationPlan` (with `blocked_ties`, `as_of`, `deprecations`) → HTTP 200. Any validation failure → HTTP 422 and `build_plan` is never called.

## 2. Data models — `backend/app/models.py` (U2, extended in U3)

U2 adds the characteristic constants, `IsoAwareDatetime`, `TieCapacity`, `TieBlockReason`, `BlockedTie` and `RestorationPlan.blocked_ties`, all additive. U3 adds only `RestorationPlan.as_of` and `RestorationPlan.deprecations` (units.json U3 scope note).

Models and constants only; no plant decision logic (STD-ARCH-1). The one validator function is a type parser (it decides whether an input *is* an ISO-8601 string), not a plant decision.

```python
# Tie-capacity characteristic parameters: the ONE production source (STD-ARCH-1/2, Q-DESIGN-1).
# Imported by flisr.tie_capacity_verdict, flisr._blocked_note, api._check_as_of_bound and the
# /flisr/plan OpenAPI description. No production module restates these values (spec Q-SPEC-1/2/4/10/12).
TIE_CAPACITY_TOLERANCE_KW: Final = 0.5
TIE_CAPACITY_MAX_AGE = timedelta(seconds=20)        # age > 20 s  -> CAPACITY_STALE
TIE_CAPACITY_MAX_LEAD = timedelta(seconds=2)        # age < -2 s  -> CAPACITY_INVALID
AS_OF_MAX_LAG = timedelta(seconds=60)               # server_now - as_of > 60 s -> 422
AS_OF_MAX_LEAD = timedelta(seconds=2)               # as_of - server_now > 2 s  -> 422
TIE_CAPACITY_GOOD_QUALITY: Final = "GOOD"

def _require_iso_string(value):          # BeforeValidator
    datetime -> pass through (Python callers);
    str      -> datetime.fromisoformat(value)  (rejects "yesterday", "1790000000")
    other    -> ValueError  (JSON numbers, bool, null)
IsoAwareDatetime = Annotated[AwareDatetime, BeforeValidator(_require_iso_string)]

class TieCapacity(BaseModel):            # REQ-TIECAP-1
    model_config = ConfigDict(extra="forbid")
    kw: StrictFloat                      # JSON number only; NaN/±inf/negative pass (flagged by the planner)
    timestamp: IsoAwareDatetime          # aware ISO-8601 only; no clock comparison here
    quality: StrictStr

class TieBlockReason(StrEnum):           # REQ-TIECAP-11 (amended); declaration order == precedence (REQ-TIECAP-9 amended)
    FAULTED_SECTION, CAPACITY_INVALID, CAPACITY_UNKNOWN, CAPACITY_STALE, CAPACITY_EXCEEDED
    # FAULTED_SECTION is set only by build_plan's DEF-FLISR-7 guard, never by tie_capacity_verdict (Q-DESIGN-3)

class BlockedTie(BaseModel):
    tie_id: str
    reason: TieBlockReason

class RestorationPlan(BaseModel):        # existing fields unchanged
    ...
    as_of: AwareDatetime                 # U3, REQ-TIECAP-14: required, always UTC
    blocked_ties: list[BlockedTie] = []  # U2, REQ-TIECAP-11
    deprecations: list[str] = []         # U3, REQ-TIECAP-16
```

Why per-field strictness, not `ConfigDict(strict=True)`: measured on pydantic 2.14.1 / fastapi 0.143.1 (this stage, prototype outside the repo), FastAPI validates the body in Python mode, so model-wide strict rejects valid ISO strings (`datetime_type`), and lax `AwareDatetime` alone accepts the numeric string `"1790000000"` as a Unix time. `IsoAwareDatetime` measured: `"yesterday"`, `1790000000`, `"1790000000"`, `null`, naive and date-only → rejected; `Z`, `+02:00`, basic `20261015T220000Z` → accepted. `StrictFloat` measured: JSON `2000` → 2000.0 accepted; `"2000"`, `true`, `null` → rejected; JSON `NaN`/`-Infinity` reach the model. `extra="forbid"` → `extra_forbidden` 422.

`RestorationPlan.as_of` is required because REQ-TIECAP-14 says *always*; `flisr.build_plan` is the only constructor (grep: `flisr.py:76`). Characterization (U1) pins fields individually, so it is unaffected.

## 3. Shared characteristic — `flisr.tie_capacity_verdict` (STD-ARCH-2)

There is one implementation of the capacity decision. Its parameters come only from the `models.py` constants in §2. Production consumers (Q-DESIGN-1):

| Consumer | Uses |
|---|---|
| `flisr.build_plan` tie loop (planner) | calls `tie_capacity_verdict`; no comparison of its own |
| `flisr._blocked_note` (operator notes) | formats `TIE_CAPACITY_TOLERANCE_KW`, `TIE_CAPACITY_MAX_AGE`, `TIE_CAPACITY_MAX_LEAD`; never re-derives the reason, only formats the reason the verdict returned |
| `api._check_as_of_bound` (endpoint) | `AS_OF_MAX_LAG`, `AS_OF_MAX_LEAD` |
| `api` route `description` (OpenAPI) | formats the same constants into the deprecation note |

No production module other than `models.py` contains the literals 0.5, 20, 2 or 60 for these purposes. A test enforces this (§6.3, check P2).

```python
def _not_finite_nonneg(x) -> bool:
    """True when x is not a real number (bool excluded), or is NaN, ±inf or < 0. -0.0 and 0.0 pass."""
    return not (isinstance(x, (int, float)) and not isinstance(x, bool)
                and math.isfinite(x) and x >= 0.0)

def tie_capacity_verdict(
    entry: TieCapacity | None, transferred_kw: float, as_of: datetime
) -> TieBlockReason | None:
    """None = the tie may close. Otherwise the first applicable reason (REQ-TIECAP-9).

    Preconditions (STD-ARCH-4). Each one is checked before any comparison. A violation raises
    ValueError and returns no verdict, so the caller cannot treat it as "may close":
      - transferred_kw is finite and >= 0 (spec §0: L range L >= 0). NaN, +inf, -inf and
        negative values raise; build_plan converts this into FlisrError (no plan), see §4.
      - as_of is a timezone-aware datetime. Naive or non-datetime raises.
      - entry is None or a TieCapacity whose timestamp is timezone-aware. Any other type, or a
        naive timestamp (reachable only through model_construct, which skips validation),
        raises.
    Decisions on valid inputs:
      absent entry -> CAPACITY_UNKNOWN; kw not finite or < 0, or timestamp more than 2 s ahead of
      as_of -> CAPACITY_INVALID; quality != GOOD -> CAPACITY_UNKNOWN; older than 20 s ->
      CAPACITY_STALE; L <= C + 0.5 kW -> None (close); otherwise CAPACITY_EXCEEDED.
    Never substitutes, clamps or defaults a value."""
    if _not_finite_nonneg(transferred_kw):                       -> raise ValueError
    if not _is_aware_datetime(as_of):                            -> raise ValueError
    if entry is None:                                            -> CAPACITY_UNKNOWN
    if not isinstance(entry, TieCapacity) or not _is_aware_datetime(entry.timestamp):
                                                                 -> raise ValueError
    age = as_of - entry.timestamp                                # timedelta, exact µs
    if _not_finite_nonneg(entry.kw) or age < -TIE_CAPACITY_MAX_LEAD:
                                                                 -> CAPACITY_INVALID
    if entry.quality != TIE_CAPACITY_GOOD_QUALITY:               -> CAPACITY_UNKNOWN
    if age > TIE_CAPACITY_MAX_AGE:                               -> CAPACITY_STALE
    if transferred_kw <= entry.kw + TIE_CAPACITY_TOLERANCE_KW:   -> None (close)
    return CAPACITY_EXCEEDED
```

`_is_aware_datetime(x)` is `isinstance(x, datetime) and x.utcoffset() is not None`. It is a type check, not a threshold.

Design decisions:
- **Out-of-range L is refused. It is never blocked or closed (A-1).** The specification defines L ≥ 0 (§0 Definitions), so L outside that range means the network model is wrong, not that the capacity is. No `BlockedTie` reason fits: the four reasons describe C, not L. Adding a fifth reason would change REQ-TIECAP-11 and Q-SPEC-5. The repo safety skill (step 4: "refuse (raise the module's error type …)") and STD-ARCH-4 ("refuse or hold") make refusal the default, so the verdict raises. Measured on `main` @ 5f6b471 with the shipped model (`CB-1201` open, C = 0.0): `SEC-1201-04.load_kw` = NaN, −inf or −120.0 each **closes** `TIE-1201-1405` today. The attempt-2 design still closed on −inf and −120.0. Attempt 3 closes on none of them.
- **Why the precondition comes before the absent-entry check.** If the entry check came first, a NaN L with no capacity entry would return CAPACITY_UNKNOWN and hide a corrupt network model. Network-model faults therefore take priority over capacity reasons. REQ-TIECAP-9 orders capacity reasons only and is unaffected.
- **Positive close condition is kept.** It is now defence in depth: with the L precondition in place no NaN can reach `L <= C + τ`, but if it did, the comparison would be False and the tie would block.
- **Ages compared as `timedelta`**, never as float seconds, so the 20.000 s / 20.001 s and −2.000 s / −2.001 s boundaries are exact at microsecond resolution (measured: `20.001 s > 20 s` True, `20 s > 20 s` False). A naive operand is rejected by the precondition rather than left to raise `TypeError` from the subtraction (measured: `can't subtract offset-naive and offset-aware datetimes`).
- `kw = -0.0` and `L = -0.0` pass `>= 0.0` (valid, as the spec requires for kw; L = −0.0 is the sum of zero-load sections).
- A `kw` that is not a real number (reachable only through `model_construct`) is CAPACITY_INVALID ("not a finite number", Q-SPEC-9), not a crash.
- Precedence is the order of the `if` statements; a missing entry can only be UNKNOWN.
- **Negative section load inside a non-negative L (Q-DESIGN-2).** This case cannot reach the verdict. `build_plan` checks every candidate section's `load_kw` first (§4) and refuses the plan for any NaN, ±inf or negative value. An L that passes the verdict's precondition is therefore always the sum of finite non-negative loads. The verdict's own L precondition stays, as defence in depth, and also catches a sum that overflows to +inf.
- **`FAULTED_SECTION` is not a verdict output.** It is a topology reason, decided by the DEF-FLISR-7 guard before L exists. The verdict returns only the four capacity reasons. So the single capacity characteristic (STD-ARCH-2) is unchanged and the guard is not re-implemented.

## 4. Planner — `flisr.build_plan` (U3)

```python
def build_plan(
    feeder: Feeder,
    lockout_switch_mrid: str,
    tie_capacity_kw: dict[str, float] | None = None,     # legacy, deprecated (kept positional for callers)
    *,
    tie_capacity: dict[str, TieCapacity] | None = None,
    as_of: datetime | None = None,
) -> RestorationPlan:
```

Behaviour for absent / stale / out-of-range inputs (STD-ARCH-4), in docstring form:

| Input | Behaviour |
|---|---|
| both `tie_capacity` and `tie_capacity_kw` not None (incl. both `{}`) | `ValueError`; no plan (REQ-TIECAP-15) |
| `as_of` None | `datetime.now(UTC)` read **once** at entry (REQ-TIECAP-2, REQ-TIECAP-20) |
| `as_of` naive | `ValueError`; no plan (REQ-TIECAP-2) |
| `as_of` aware, any offset | `as_of.astimezone(UTC)`; same instant; stored in `plan.as_of` |
| `tie_capacity_kw` given (legacy) | each entry → `TieCapacity.model_construct(kw=v, timestamp=as_of, quality=TIE_CAPACITY_GOOD_QUALITY)` (O-3) (no re-validation, so NaN/±inf/negative survive and become CAPACITY_INVALID); `plan.deprecations = ["tie_capacity_kw"]` (REQ-TIECAP-16) |
| both None, or `{}` | every candidate tie CAPACITY_UNKNOWN (REQ-TIECAP-5) |
| entry for a non-candidate tie | ignored, as today (spec §3) |
| any candidate section (`to_node` ∈ candidate set, after the guard has not held the tie) with `load_kw` NaN, +inf, −inf or < 0, **including a negative section inside an L ≥ 0** | `FlisrError("{section.name}: load_kw {v} kW is not a finite non-negative number; network model invalid, no plan")`. No plan; HTTP 409; lockout stays open (Q-DESIGN-2). Example: a −600 kW spur under C = 1000 kW, which closes the tie today with L = 890 kW → no plan. |
| candidate tie with L NaN, +inf, −inf or < 0 after the section check (only a sum that overflows to +inf) | `FlisrError("{name}: transferred load {L} kW is not a finite non-negative number; network model invalid, no plan")`. No plan; HTTP 409 (A-1). `CB-1201` stays in lockout, so the faulted section stays de-energised and customers wait for manual switching. This is the fail-safe state. |
| candidate tie whose pick-up set contains an endpoint (`from_node` or `to_node`) of the faulted section (DEF-FLISR-7 guard, PR #13) | held open by the guard, unchanged; `blocked_ties` entry `FAULTED_SECTION`; the guard's note (names the tie and the faulted section); its pick-up customers are counted once in `customers_remaining`, as PR #13 counts them (measured 341 for a fault on `SEC-1201-04`). Section loads in a held tie's pick-up set are not evaluated, so an invalid load there does not refuse the plan; the tie is already held open, which is the fail-safe outcome. Load and capacity are not evaluated, so a missing, NaN, stale or short capacity on that tie is never reported instead (Q-DESIGN-3). |
| a `tie_capacity` / `tie_capacity_kw` value of the wrong Python type (direct callers only; HTTP rejects it with 422) | `TieCapacity` slot holding a non-`TieCapacity` value → `ValueError`, no plan. Legacy value not a real number → CAPACITY_INVALID |
| lockout not open / no isolating switch | `FlisrError`, unchanged |
| no fault indication | unchanged early return; `blocked_ties` stays `[]` (REQ-TIECAP-19) |

Why `ValueError` and not `FlisrError`: `FlisrError` means "the network state does not allow a defensible plan" and maps to HTTP 409. Naive `as_of` and both-maps are caller contract violations that HTTP validation already rejects with 422, so they never reach `build_plan` from `api.py`; a direct Python caller gets an exception and no plan either way.

Tie loop (replaces `flisr.py:92-121`; isolation, lockout re-close and `_nodes_restored_by` untouched, REQ-TIECAP-10):

```text
for switch in feeder.switches:                 # order => blocked_ties order (REQ-TIECAP-11)
    skip silently if not tie / not SCADA / empty candidate set     # as today
    if candidate_nodes & {faulted.from_node, faulted.to_node}:     # DEF-FLISR-7 guard, PR #13, kept as is
        notes.append(<PR #13 hold-open note>)                         # unchanged text
        blocked_ties.append(BlockedTie(tie_id=switch.mrid, reason=FAULTED_SECTION))   # added (Q-DESIGN-3)
        continue                                                      # before any load or capacity evaluation
    for sec in sections with to_node ∈ candidate_nodes:
        if _not_finite_nonneg(sec.load_kw): raise FlisrError(...)    # Q-DESIGN-2: whole plan refused
    L = load_on_nodes(feeder, candidate_nodes)                        # plain sum (REQ-TIECAP-3)
    if _not_finite_nonneg(L): raise FlisrError(...)               # A-1: overflow only, defence in depth
    customers = Σ customers of sections whose to_node ∈ candidate_nodes
    entry = capacities.get(switch.mrid)       # no default value — removes `.get(..., 0.0)` at flisr.py:98
    reason = tie_capacity_verdict(entry, L, as_of)
    if reason is None:
        append close step; transferred_load_kw += L; customers_restored += customers   # unchanged
    else:
        blocked_ties.append(BlockedTie(tie_id=switch.mrid, reason=reason))
        notes.append(_blocked_note(switch, reason, entry, L, as_of))
        customers_remaining += customers                                        # REQ-TIECAP-18
```

Operator notes (`_blocked_note`, REQ-TIECAP-12), one per blocked tie, naming `Switch.name` and the reason code:

| Reason | Note |
|---|---|
| FAULTED_SECTION | the PR #13 guard note, unchanged (it names the tie and the faulted section). The machine-readable code is in `blocked_ties` and the human-readable reason in the note, so REQ-TIECAP-12 is met without changing the DEF-FLISR-7 text. |
| CAPACITY_EXCEEDED | `"{name} blocked (CAPACITY_EXCEEDED): {L:.1f} kW to transfer exceeds {C:.1f} kW available capacity (+{TIE_CAPACITY_TOLERANCE_KW:g} kW tolerance)"` |
| CAPACITY_STALE | `"{name} blocked (CAPACITY_STALE): capacity value is {age_s:.3f} s old (limit {TIE_CAPACITY_MAX_AGE.total_seconds():g} s)"` |
| CAPACITY_UNKNOWN | `"{name} blocked (CAPACITY_UNKNOWN): no capacity value"` or `"...: capacity quality {quality!r} is not GOOD"` |
| CAPACITY_INVALID | `"{name} blocked (CAPACITY_INVALID): capacity {kw} kW is not a finite non-negative number"` or `"...: capacity timestamp is {lead_s:.3f} s ahead of as_of (limit {TIE_CAPACITY_MAX_LEAD.total_seconds():g} s)"` |

Rendered on the shipped model these read, for example, `+0.5 kW tolerance`, `limit 20 s`, `limit 2 s`. The limit text comes from the same constants the verdict uses, so a note can never state a limit different from the one applied. `_blocked_note` receives the reason from `tie_capacity_verdict` and does not compare anything itself. For UNKNOWN and INVALID it chooses between the two message variants with presence and type checks only (entry is None or not; which INVALID sub-condition holds). Those sub-condition checks reuse the verdict's predicate `_not_finite_nonneg` in `flisr.py`; they are not re-implemented.

Error handling removed and its replacement in the same change (STD-ARCH-5):

| Removed | Replacement |
|---|---|
| `tie_capacity_kw = tie_capacity_kw or {}` + `.get(mrid, 0.0)` (implicit zero) | explicit `entry = None` → CAPACITY_UNKNOWN, machine-readable |
| `transferred > available` skip guard | `tie_capacity_verdict` positive close condition (blocks NaN that the old guard let through) |
| free-text-only skip note | `blocked_ties` entry + note |
| (none today: a NaN / ±inf / negative L is compared numerically and closes the tie) | new `FlisrError` precondition on every candidate section load and on L (A-1, Q-DESIGN-2); verdict `ValueError` preconditions |
| DEF-FLISR-7 guard (PR #13) | **not removed**. Kept byte-for-byte; one `blocked_ties.append` added in its branch (Q-DESIGN-3) |

Integration with DEF-FLISR-7 (O-2, STD-ARCH-5, Q-DESIGN-3). PR #13 (`agent/rca-backfeed/fix`) lands first, and this change is built on top of it. U1 characterization is therefore pinned on `main` with PR #13 merged. The required order in the tie loop is: empty-candidate skip → **DEF-FLISR-7 guard (→ FAULTED_SECTION, continue)** → section-load precondition → L → `tie_capacity_verdict`. That ordering is what implements the amended precedence FAULTED_SECTION > CAPACITY_INVALID > CAPACITY_UNKNOWN > CAPACITY_STALE > CAPACITY_EXCEEDED. Moving the guard after any later step, dropping it, or changing its decision, note or customer accounting violates STD-ARCH-5 and the spec's "neither fix nor mask DEF-FLISR-7". Measured with a prototype of this ordering (shipped model, `CB-1201` open, fault on `SEC-1201-04`): `TIE-1201-1405` gets `FAULTED_SECTION` and stays open for capacity GOOD 2000 kW, NaN, `"BAD"`, 30 s stale, 10 kW and missing alike, with `customers_remaining` = 341 as PR #13 has it. Plan-level preconditions come before every per-tie reason: lockout, isolation, and the Q-DESIGN-2 section-load check (applied to ties the guard has not held). A raise returns no plan, so where it sits in the loop cannot change any plan that is returned.

## 5. Endpoint — `POST /flisr/plan` in `backend/app/api.py` (U3)

`FlisrRequest` stays in `api.py` (existing convention for HTTP request schemas: `EstimationRequest`, `AgcRequest`). It is an API-layer DTO, not a domain model; it reuses `TieCapacity` and `IsoAwareDatetime` from `models.py`.

```python
class FlisrRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")                    # unknown body field -> 422
    feeder_mrid: StrictStr
    lockout_switch_mrid: StrictStr
    tie_capacity: dict[str, TieCapacity] | None = None
    tie_capacity_kw: dict[str, StrictFloat] | None = None        # deprecated
    as_of: IsoAwareDatetime | None = None

    @field_validator("tie_capacity", "tie_capacity_kw", "as_of", mode="before")
    def _no_null(v): None -> ValueError("omit the field instead of sending null")   # defaults are not validated, so "absent" still works
    @model_validator(mode="after")
    def _mutually_exclusive(self): both not None -> ValueError   # REQ-TIECAP-15 (both {} included)

def server_now() -> datetime:          # FastAPI dependency; tests override via app.dependency_overrides
    return datetime.now(UTC)

def _check_as_of_bound(as_of, now):    # REQ-TIECAP-23; raises RequestValidationError(loc=("body","as_of")) -> 422
    now - as_of > AS_OF_MAX_LAG  or  as_of - now > AS_OF_MAX_LEAD  -> reject   (exactly 60 s / 2 s accepted)

@router.post("/flisr/plan", response_model=RestorationPlan, description=<deprecation + mutual-exclusion note>)
def flisr_plan(request: FlisrRequest, now: datetime = Depends(server_now)) -> RestorationPlan:
    as_of = request.as_of if request.as_of is not None else now     # server clock read once per request
    _check_as_of_bound(as_of, now)                                  # before load_network / build_plan
    ... flisr.build_plan(feeder, lockout, request.tie_capacity_kw,
                         tie_capacity=request.tie_capacity, as_of=as_of)
    KeyError -> 404, FlisrError -> 409   (unchanged; now also out-of-range L, A-1); blocked ties -> 200 (REQ-TIECAP-13)
```

Prototype measurements (pydantic 2.14.1 / fastapi 0.143.1, outside the repo): `"kw":"2000"`, `true`, `null` → 422 `float_type`; timestamp `"yesterday"`, `1790000000` → 422; naive → 422 `timezone_aware`; extra field at body and `TieCapacity` level → 422 `extra_forbidden`; `"tie_capacity": null` and `"as_of": null` → 422; both maps `{}` → 422; JSON `NaN` / `-Infinity` → reaches handler (planner then CAPACITY_INVALID); `RequestValidationError` raised in the handler → standard 422 body; the response serialises a UTC `as_of` as `...Z`.

OpenAPI `description` (REQ-TIECAP-17), a module-level string in `api.py` built from the `models.py` constants (for example the 0.5 kW tolerance and the 20 s / 2 s limits) so it cannot drift from them: "`tie_capacity_kw` is deprecated and will be removed one release after this one. It is mutually exclusive with `tie_capacity`; sending both returns 422. Legacy values are treated as quality GOOD with timestamp = as_of." Not `Field(deprecated=True)`: in pydantic 2.14 that emits a `DeprecationWarning` whenever the handler reads the attribute.

## 6. Test strategy

### 6.1 Files and order (from `units.json`; safety skill steps 1–5)

| Unit | File | Content |
|---|---|---|
| U1 | `test_flisr_tie_capacity_characterization.py` | `@pytest.mark.characterization` on `main` **with PR #13 merged** (Q-DESIGN-3), via legacy `tie_capacity_kw`; pins isolation, restoration steps and their order, customer counts and `transferred_load_kw`. Excludes C ∈ (L, L+0.5], missing, non-finite or negative values, negative section loads, and ties held by the DEF-FLISR-7 guard (PR #13's own tests pin those). Includes the no-fault plan with `model_dump().get("blocked_ties", []) == []` |
| U1 | `test_flisr_tie_capacity_repro.py` | `xfail(strict=True)`: (a) no entry → expects `blocked_ties` CAPACITY_UNKNOWN; (b) legacy NaN and +inf → expects no close step for `TIE-1201-1405` |
| U2 | `test_flisr_tie_capacity_models.py` | accept/reject classes via `model_validate_json` **and** a FastAPI `TestClient` echo route defined in the test (Python-mode path) |
| U3 | `test_flisr_tie_capacity_planner.py` | `build_plan` with injected `as_of`; boundaries; precedence; per-tie; accounting; notes; legacy parity; ValueError cases; A-1 preconditions: `tie_capacity_verdict` called directly with L ∈ {NaN, +inf, −inf, −120.0, −1e-9} → `ValueError`, L ∈ {0.0, −0.0} accepted; naive `as_of`, non-datetime `as_of`, naive `entry.timestamp` via `model_construct`, entry of the wrong type → `ValueError`; non-real `kw` via `model_construct` → CAPACITY_INVALID; `build_plan` on a deep copy of the shipped model with `SEC-1201-04.load_kw` ∈ {NaN, +inf, −inf, −120.0} and each capacity state (missing, GOOD 0.0, GOOD 2000.0) → `FlisrError`, no plan | **Q-DESIGN-2 rows:** a 10-customer spur after `SEC-1201-04` with `load_kw` −600.0 and C ∈ {1000.0, 2000.0}: `FlisrError`, no plan (today it closes with L = 890); one section at −1e-9, and −120.0 with every other load positive: `FlisrError`. **Q-DESIGN-3 rows:** fault on `SEC-1201-04` × capacity {GOOD 2000, NaN, `"BAD"`, 30 s stale, 10 kW, missing, no map} → exactly one `blocked_ties` entry (`TIE-1201-1405`, `FAULTED_SECTION`), no close step for the tie, the PR #13 note present once, `customers_remaining` equal to the PR #13 value; held tie with a NaN load in its pick-up set → plan returned, `FAULTED_SECTION`, no `FlisrError`; a two-tie topology with one held tie and one capacity-blocked tie → both listed, in `feeder.switches` order |
| U3 | `test_flisr_tie_capacity_api.py` | `TestClient`; `app.dependency_overrides[server_now]` fixed clock; `monkeypatch` of `app.api.load_network` with a model whose candidate L is NaN → 409, body carries no plan; `monkeypatch` of `app.api.flisr.build_plan` with a recorder to assert "not called" on every 422; OpenAPI text |
| U4 | `test_flisr_tie_capacity_invariant.py` | ≥ 500 seeded cases (seed + count printed). At least 5 % of the cases inject an out-of-range L (NaN, ±inf, negative total). For those the invariant is "`FlisrError`, no plan", checked against an oracle predicate on the oracle's own L. At least 5 % of the cases inject one negative section load inside a positive total (→ `FlisrError`). At least 5 % mark a fault whose section touches a tie's pick-up set (→ that tie is `FAULTED_SECTION`, not closed, whatever its capacity, and its loads are not checked) |

**Existing DEF-FLISR-7 tests (U3 file-list delta).** `test_flisr_characterization.py`, `test_flisr_def_flisr_7.py` and `test_flisr_def_flisr_7_qa.py` come from PR #13. With this design applied, 19 of them fail. Each failure is an exact `model_dump()` or note comparison that now meets `as_of`, `blocked_ties` or `deprecations`, or a REQ-TIECAP-12 note that replaced `"skipped: … exceeds 0 kW"` (measured on a prototype). U3 adds these three files to its file list. The only edits allowed in them are: (1) leave every existing expected value as it is and compare with `model_dump(exclude={"as_of", "blocked_ties", "deprecations"})`, or pass a fixed `as_of`; (2) add assertions on `blocked_ties` (`FAULTED_SECTION` where the guard holds a tie, `[]` otherwise); (3) replace the old skip-note text only in tests that pin the implicit-zero or skip note, which REQ-TIECAP-5/12 remove on purpose. No expected switching step, order, customer count or `transferred_load_kw` may change. Following safety skill step 2, the PR lists each edited test with its before/after assertion and explains it. Any other edit is a STOP.

`backend/tests/test_flisr.py` passes unchanged throughout. All tests that need the shipped model set `CB-1201.open = True` (otherwise 409).

### 6.2 Boundary values (shipped model, `CB-1201` open, L = 1490.0 kW, customers 341)

C = 1490.0 close · 1489.5 close · 1489.4 EXCEEDED · age 19.999 / 20.000 s fresh, 20.001 s STALE · age −1.999 / −2.000 s fresh, −2.001 s INVALID · server clock fixed: as_of −60.000 s / +2.000 s accepted, −60.001 s / +2.001 s 422 · `SEC-1201-04.load_kw` NaN / +inf / −inf / −120.0 → `FlisrError` (today: NaN, −inf and −120.0 close the tie; +inf blocks, measured), 0.0 → valid L · spur −600.0 under C = 1000.0 → `FlisrError` (today: closes, L = 890.0) · fault on `SEC-1201-04` → `FAULTED_SECTION` for every capacity state (prototype, measured).

### 6.3 Oracle and the scoped STD-ARCH-2 waiver (Q-DESIGN-1)

**Waiver (explicit and scoped).** STD-ARCH-2 says one shared implementation of a numerically sensitive characteristic is used by every consumer, test oracle included, and calls duplicates a VIOLATION. STD-SAFETY-6 requires operate boundaries to be checked against an *independent* closed-form oracle. Per Q-DESIGN-1 (principal-engineer-standin), **STD-SAFETY-6 governs the test oracle** and **STD-ARCH-2 applies to production consumers only** (planner, endpoint, notes; §3). Scope of the waiver:

- Covers only the QA oracle functions in `backend/tests/test_flisr_tie_capacity_planner.py`, `test_flisr_tie_capacity_api.py` and `test_flisr_tie_capacity_invariant.py`, which restate the closed forms below.
- Does not cover any module under `backend/app/`. A second production implementation of the characteristic, or a restated production literal, is still a STD-ARCH-2 VIOLATION.
- The U3 and U4 oracles are separate restatements: units.json says U4's oracle is "implemented in the test file". Both use the literals from the specification. Under the waiver this is intended: more diversity, no shared defect.

**Oracle content.** The oracle lives under `backend/tests`. It does not import `app.flisr` or `app.network` and does not use the `models.py` threshold constants (Q-DESIGN-1: "must not import app.flisr or share its threshold code"). It may read `app.models` data types (`Feeder`, `Section`, `Switch`, `TieCapacity`) as plain data. Functions are named `oracle_*`:

| Oracle function | Closed form (literals from the specification) |
|---|---|
| `oracle_candidate_nodes(feeder, tie_mrid, opened)` | its own BFS over the test topology: nodes reachable from the tie's `from_node` with isolation switches open and the tie closed, minus nodes reachable from `source_node` (spec "Candidate tie" definition) |
| `oracle_load_kw(feeder, nodes)` / `oracle_customers(...)` | Σ `load_kw` / `customers` of sections whose `to_node` ∈ nodes |
| `oracle_held(feeder, nodes, faulted_mrid)` | `nodes & {faulted.from_node, faulted.to_node}` is non-empty (restates the DEF-FLISR-7 rule from the spec, not PR #13's code); True ⇒ expect `FAULTED_SECTION` before anything else |
| `oracle_sections_ok(feeder, nodes)` | every section with `to_node` ∈ nodes has `isfinite(load_kw) and load_kw >= 0`; False (for a tie that is not held) ⇒ expect `FlisrError` |
| `oracle_l_in_range(L)` | `isfinite(L) and L >= 0` (spec §0 range); False ⇒ expect `FlisrError` |
| `oracle_reason(entry, L, as_of)` | `None` → UNKNOWN; `not (isfinite(kw) and kw >= 0) or age < timedelta(seconds=-2)` → INVALID; `quality != "GOOD"` → UNKNOWN; `age > timedelta(seconds=20)` → STALE; `L <= kw + 0.5` → close; else EXCEEDED. Called only after `oracle_held` is False (REQ-TIECAP-9 amended precedence) |
| `oracle_as_of_ok(as_of, now)` (API test) | `now - as_of <= timedelta(seconds=60) and as_of - now <= timedelta(seconds=2)` |

Tolerance: 0.5 kW in engineering units. Per-unit statement waived by Q-SPEC-4; the PR records this waiver against STD-SAFETY-6.

**Checks that keep the oracle independent and the production source single** (all in the U2/U3/U4 files already listed in units.json; no new files):

- **O1 — oracle independence** (planner, API and invariant test files): an `ast` check of the test module asserts that no `oracle_*` function refers to a name bound by `from app.flisr …`, `from app.network …`, `import app.flisr` / `app.network`, or to a `TIE_CAPACITY_*` / `AS_OF_*` constant, reached either through attribute access on any alias of `app.models` (`models.X`, `m.X` after `import app.models as m`, `from app import models as mm`) or as a bare name bound by `from app.models import TIE_CAPACITY_* / AS_OF_*` (O-4). The check walks every `Import` / `ImportFrom` in the module to collect the aliases and bound names, then walks each `oracle_*` body for `Name` and `Attribute` nodes. The module may import `build_plan` / the app as the subject under test; only the oracle functions are constrained.
- **P1 — constant pin** (U2, `test_flisr_tie_capacity_models.py`): asserts `TIE_CAPACITY_TOLERANCE_KW == 0.5`, `TIE_CAPACITY_MAX_AGE == timedelta(seconds=20)`, `TIE_CAPACITY_MAX_LEAD == timedelta(seconds=2)`, `AS_OF_MAX_LAG == timedelta(seconds=60)`, `AS_OF_MAX_LEAD == timedelta(seconds=2)`, `TIE_CAPACITY_GOOD_QUALITY == "GOOD"`, using spec literals. A wrong constant then fails a test; the oracle does not move with it.
- **P2 — no restated production literal** (U3, planner test): an `ast` check of `tie_capacity_verdict`, `_not_finite_nonneg`, `_blocked_note`, `_legacy_to_tie_capacity` (from `app/flisr.py` source) and `_check_as_of_bound` plus the route description builder (from `app/api.py` source) asserts no numeric constant other than `0` / `0.0`, no `timedelta(...)` call, and no string constant `"GOOD"` (O-3). This mechanically enforces §3's single production source.
- **Oracle self-check** (planner test): the oracle reproduces the §6.2 hand-computed shipped-model values (L = 1490.0 kW, 341 customers, the boundary verdicts) before it is used against `build_plan`.

## 7. Requirement → component → test (STD-ARCH-6)

| Requirement | Component | Test strategy |
|---|---|---|
| REQ-TIECAP-1 | `models.TieCapacity`, `IsoAwareDatetime` | U2 models test, both JSON and TestClient paths |
| REQ-TIECAP-2 | `flisr.build_plan` signature, `as_of` resolution; `tie_capacity_verdict` as_of precondition | planner test: UTC vs `+02:00` identical plan; naive → `ValueError`; None → UTC now; verdict direct with naive / non-datetime `as_of` → `ValueError` (A-1) |
| REQ-TIECAP-3 | `flisr.tie_capacity_verdict` (close branch, L precondition); `build_plan` section-load and L checks → `FlisrError` (Q-DESIGN-2); constant `models.TIE_CAPACITY_TOLERANCE_KW` | planner boundaries §6.2 vs the independent `oracle_reason` / `oracle_candidate_nodes` / `oracle_load_kw` (§6.3); out-of-range-L rows and the negative-section rows (spur −600, −1e-9, −120.0) vs `oracle_sections_ok` / `oracle_l_in_range`; O1, P1, P2 |
| REQ-TIECAP-4 | `tie_capacity_verdict` → EXCEEDED; tie loop | planner test 1489.4; oracle |
| REQ-TIECAP-5 | `tie_capacity_verdict` (None / non-GOOD); loop with no default | planner: missing key, None, `{}`, `"BAD"`, `"SUSPECT"`, `"good"`, `""`; inspection of `flisr.py` (no `0.0` default); U1 repro (a) |
| REQ-TIECAP-6 | `tie_capacity_verdict` (`age > TIE_CAPACITY_MAX_AGE`) | planner ages 19.999 / 20.000 / 20.001 s vs `oracle_reason`; P1 |
| REQ-TIECAP-7 | `tie_capacity_verdict` (`age < -TIE_CAPACITY_MAX_LEAD`) | planner ages −1.999 / −2.000 / −2.001 s vs `oracle_reason`; P1 |
| REQ-TIECAP-8 | `tie_capacity_verdict` (finite, ≥ 0) | planner NaN, ±inf, −1.0, 0.0, −0.0; API raw JSON `NaN`/`Infinity`/`-Infinity`/`-1` → 200 INVALID; U1 repro (b) |
| REQ-TIECAP-9 (amended, Q-DESIGN-3) | loop order: guard → section check → `tie_capacity_verdict` statement order; `TieBlockReason` declaration order | planner: every combination of {held by guard, invalid kw, future > 2 s, non-GOOD, stale, exceeded} vs `oracle_held` + `oracle_reason`; held + any capacity state → FAULTED_SECTION |
| REQ-TIECAP-10 | tie loop (per-tie, isolation untouched) | planner two-tie generated topology |
| REQ-TIECAP-11 (amended, Q-DESIGN-3) | `models.BlockedTie`, `TieBlockReason` (5 members), `RestorationPlan.blocked_ties`; guard branch appends FAULTED_SECTION | U2 schema test (enum = 5 values in order); planner content and order, two-tie mixed topology |
| REQ-TIECAP-12 | `flisr._blocked_note` (limits formatted from `models.py` constants); PR #13 guard note for FAULTED_SECTION | planner: one note per reason, L/C to 0.1 kW, age; held tie: the PR #13 note exactly once; P2 (no literal limits in the note code) |
| REQ-TIECAP-13 | `api.FlisrRequest`, `flisr_plan` | API: 422 list in spec, each asserting planner not called; blocked tie → 200 |
| REQ-TIECAP-14 | `RestorationPlan.as_of`; `build_plan` UTC normalisation; `flisr_plan` as_of resolution | API: `+01:00` echoed as `22:00:00Z`; absent → instant within send/receive window (parsed comparison) |
| REQ-TIECAP-15 | `FlisrRequest._mutually_exclusive`; `build_plan` ValueError | API both present (incl. `{}`) → 422; planner both → ValueError |
| REQ-TIECAP-16 | `flisr._legacy_to_tie_capacity`; `RestorationPlan.deprecations` | planner + API legacy-only parity with GOOD/as_of; `deprecations` asserted both ways |
| REQ-TIECAP-17 | `flisr_plan` route `description` | API: inspect `app.openapi()["paths"]["/flisr/plan"]["post"]["description"]` |
| REQ-TIECAP-18 | tie loop accounting; guard branch accounting from PR #13, unchanged | planner vs oracle sums; held tie `customers_remaining` equals the PR #13 value |
| REQ-TIECAP-19 | `build_plan` no-fault early return | U1 characterization (unchanged after U2/U3) |
| REQ-TIECAP-20 | `build_plan` reads clock once at entry | planner: monkeypatched clock counts one read; inspection |
| REQ-TIECAP-21 (amended, Q-DESIGN-3) | DEF-FLISR-7 guard + section check + `tie_capacity_verdict` + tie loop + L precondition | U4 invariant over ≥ 500 seeded cases: no close step unless the tie is not held, every candidate section load is valid, capacity is usable and L ≤ C + 0.5 kW. Every candidate tie that is not closed appears exactly once in `blocked_ties` with the amended-precedence reason (FAULTED_SECTION first). Out-of-range-L and negative-section cases produce no plan. The generator places ties and faults at any node; oracle restated in the invariant file (§6.3 waiver); O1 |
| REQ-TIECAP-22 (amended, Q-DESIGN-3) | unchanged isolation/restoration code paths | U1 characterization pinned on `main` with PR #13 merged; DEF-FLISR-7 guard ties are excluded (pinned by PR #13's tests, edited only as §6.1 allows) |
| REQ-TIECAP-23 | `api.server_now`, `_check_as_of_bound` (`models.AS_OF_MAX_LAG` / `AS_OF_MAX_LEAD`), `IsoAwareDatetime` | API with overridden clock: §6.2 bounds vs `oracle_as_of_ok`, naive, `"yesterday"`, `1790000000` → 422, planner not called; O1, P1, P2 |

No requirement is unmapped.

## 8. Standards check (verify)

- STD-ARCH-1: constants and types in `models.py`; decision logic in `flisr.py`; request DTO in `api.py` (API layer).
- STD-ARCH-2: one production capacity characteristic (`tie_capacity_verdict`); parameters single-sourced in `models.py` and imported by every production consumer (planner, notes, endpoint, OpenAPI text; §3), enforced by P2. Test oracle: scoped waiver per Q-DESIGN-1 (§6.3).
- STD-ARCH-3: `models` imports nothing from the app; `flisr` imports `models`/`network`; `api` imports `flisr`/`models`/`network`. No upward import.
- STD-ARCH-4: the §3 docstring states the preconditions and decisions of `tie_capacity_verdict` for every input: `entry` absent, wrong type, naive timestamp, non-finite, negative or non-real `kw`, stale, future-dated, non-GOOD; `transferred_kw` NaN, ±inf or negative; `as_of` naive or non-datetime. The §4 table does the same for `build_plan`: both maps, naive or absent `as_of`, legacy, wrong-type values, out-of-range L, non-candidate entries, lockout, no fault. §5 does the same for the endpoint. Fail-safe in every row: refuse the plan (raise), or block the tie. Nothing is closed on a guessed or out-of-range value. A negative section load inside a non-negative L refuses the plan (Q-DESIGN-2). A tie the DEF-FLISR-7 guard holds is reported as FAULTED_SECTION (Q-DESIGN-3). No input is left undecided.
- STD-ARCH-5: §4 removed-guard table. The DEF-FLISR-7 guard from PR #13 is kept unchanged and runs first in the loop (§4); the only edit in its branch adds the `blocked_ties` entry. PR #13 tests are edited only under the §6.1 rule.
- STD-ARCH-6: §7.
- STD-ARCH-7: this design is handed to the Architect unchanged; Architect does not edit it.
- STD-ARCH-8: no IEC 61850 logical nodes or data objects are added; `blocked_ties` is internal to the planner API.
- STD-SAFETY-2/3/4/5: U1 (pinned on main + PR #13) before any production edit, repro xfail, smallest fail-safe change (§4), invariant ≥ 500 (U4) covering held ties and negative section loads.
- STD-SAFETY-6: independent closed-form oracle under `backend/tests`, not importing `app.flisr` / `app.network` or the threshold constants (O1); boundaries §6.2; tolerance 0.5 kW engineering units; per-unit waived by Q-SPEC-4 (record against STD-SAFETY-6 in the PR).
- STD-SAFETY-7: no tool-certification credit claimed; tool-classification argument as a finding in §8.1.
- STD-SAFETY-8: no production systems, secrets or field devices used; prototype ran locally against synthetic bodies.
- STD-GOV-1/2: branch `agent/feature-tie-capacity/design`, trailer on the commit. STD-GOV-7: the platform appends a `Co-Authored-By` trailer carrying a personal name to agent commits; the agent cannot change the commit identity, so this is reported as a compliance note.

### 8.1 Tool-classification argument (STD-SAFETY-7, finding for the assessor; no credit claimed)

- **The design agent (this stage) and the Coding agent.** Their output becomes executable code, so they can introduce faults directly. The argument treats them as **T3**-like. Mitigation: no output is trusted on the agent's word. Two human reviewers check the protected path (STD-GOV-6), the Architect review is independent (STD-ARCH-7), the QA oracle is independent (§6.3), and the invariant runs over ≥ 500 seeded cases (STD-SAFETY-5).
- **pytest, ruff, and the `ast` checks O1/P1/P2.** These are verification tools. They can fail to detect a fault but cannot insert one, so they are **T2**. Their failure mode (a missed defect) is covered by the diversity of oracle versus implementation and by human review.
- **pydantic 2.14.1 and FastAPI 0.143.1.** These are runtime libraries that ship in the executable, not tools. They fall under the IEC 61508-3 pre-existing software arguments (7.4.4 / 7.4.2.12). The validation behaviour the design relies on is measured, not assumed: §2 and §5 list the measurements, and U2/U3 tests pin them so that a library upgrade that changes it fails CI.
- **The assessor decides.** This is an argument for the assessor, not a classification decision.

## 9. Open questions

None. Q-DESIGN-1..3 are answered (principal-engineer-standin) and folded in:

- **Q-DESIGN-1** → §3, §6.3, §7, §8. STD-SAFETY-6 governs the test oracle. It is independent, lives under `backend/tests`, and imports neither `app.flisr` nor `app.network` nor the threshold constants. STD-ARCH-2 governs production consumers only: tolerance, max age, max lead and the as_of bounds live in `models.py`, and the planner, notes and endpoint import them from there. The waiver is scoped and recorded in §6.3.
- **Q-DESIGN-2** → §3, §4, §6.1, §6.2, §6.3, §7. A NaN, ±inf or negative `Section.load_kw` is invalid model data. If any candidate section of a tie the guard has not held has one, `build_plan` raises `FlisrError` (HTTP 409, no plan, lockout stays open). This applies even when L ≥ 0. Otherwise L is the plain sum. REQ-TIECAP-3 is unchanged.
- **Q-DESIGN-3** → §2, §4, §6, §7, and specification amendments. PR #13 lands first, and its guard is kept unchanged. Each tie it holds open gets one `blocked_ties` entry `FAULTED_SECTION` and the PR #13 note, which names the tie. The guard runs before load and capacity evaluation. Specification amendments, recorded in `specification.md` with this citation:
  - **REQ-TIECAP-21 (directed by the answer):** "…every candidate tie not closed shall appear exactly once in `blocked_ties` with the reason the amended precedence gives: FAULTED_SECTION > CAPACITY_INVALID > CAPACITY_UNKNOWN > CAPACITY_STALE > CAPACITY_EXCEEDED. A tie whose pick-up set contains an endpoint of the faulted section is FAULTED_SECTION and is never closed. A candidate section load that is not finite and non-negative refuses the plan."
  - **REQ-TIECAP-9 and REQ-TIECAP-11 (forced by the answer):** the precedence list gains FAULTED_SECTION first, and the closed reason enum gains FAULTED_SECTION.
  - **REQ-TIECAP-22 (forced by "PR #13 lands first and is kept"):** the parity reference becomes `main` with PR #13 merged, and DEF-FLISR-7 guard ties are excluded. Parity with 5f6b471 on those inputs would need the guard removed.
  - **Spec §3, "neither fix nor mask DEF-FLISR-7":** still met. The guard's decision is unchanged, and FAULTED_SECTION reports the held tie rather than hiding it.

## 10. Architect feedback (iteration 1, VIOLATION) — resolution by item

| Item | Clause | Resolution (attempt 3, completed in attempt 4) |
|---|---|---|
| A-1 | STD-ARCH-4, STD-SAFETY-4 | **Resolved for every input.** §3: `tie_capacity_verdict` states and enforces its preconditions (`ValueError`) for L NaN / ±inf / < 0, a naive or non-datetime `as_of`, a naive `entry.timestamp`, and a wrong-type entry. §4: `build_plan` refuses the plan (`FlisrError`, 409) for any NaN / ±inf / negative candidate-section load, including a negative section inside L ≥ 0 (Q-DESIGN-2), and for an out-of-range L; both checks run before the verdict. Tests: §6.1 planner/API rows, the §6.2 spur and boundary rows, U4 out-of-range and negative-section cases, §7 REQ-TIECAP-2/3/21. |
| O-1 | STD-ARCH-1 | Accepted; `_require_iso_string` stays in `models.py` as a type parser. No change. |
| O-2 | STD-ARCH-5 | The DEF-FLISR-7 guard is kept unchanged, first in the loop and ahead of load and capacity evaluation. It reports `FAULTED_SECTION` (Q-DESIGN-3). PR #13 test edits are limited by the §6.1 rule. |
| O-3 | STD-ARCH-2 | Legacy conversion uses `TIE_CAPACITY_GOOD_QUALITY` (§4); P2 covers `_legacy_to_tie_capacity` and rejects `"GOOD"` literals (§6.3). |
| O-4 | STD-SAFETY-6 | O1 extended to bare `from app.models import …` names and any module alias (§6.3). |
| O-5 | STD-GOV-7 | Compliance note carried forward: the platform appends a `Co-Authored-By` trailer with a personal name to agent commits. The agent cannot change the commit identity. |
| (noted) | STD-SAFETY-7 | Tool-classification argument added (§8.1). |


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
name: architect
description: Independently reviews a design against the architecture and safety standards and returns CONFIRMED or VIOLATION with clause references; never edits the design. Used after every Design iteration until CONFIRMED, bounded by the repo contract's loop limit.
---

# Architect

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: CONFIRMED, VIOLATION, BLOCKED, NEEDS-HUMAN.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Check each STD-ARCH clause against the design; check STD-SAFETY-1/4 where the change touches protection, control or isolation logic.
2. Check layer visibility against the repo contract; check that every requirement id is mapped.
3. Write findings as `evidence[]` entries of kind `standard` (ref = clause id, detail = what violates it and where).

## Verify
Every finding cites a clause; no finding asks for anything outside the specification's scope.

## Deliver
`artifacts.review` (markdown). `CONFIRMED` when there are no violations; `VIOLATION` otherwise; `NEEDS-HUMAN` when the design is acceptable only under a trade-off the standards do not settle.

## Deliver
Finish by calling provide_structured_output with an object matching the schema you were given: `verdict`, `summary`, `evidence[]`, and where relevant `questions[]`, `trace[]` (requirement_id/kind/ref), `files_touched[]`, `branch`, `pr_url`, `standards_loaded[]`, `artifacts{}` (your stage's named outputs as markdown or JSON strings), `model`.
