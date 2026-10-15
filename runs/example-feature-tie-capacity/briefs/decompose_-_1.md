# Agentic SDLC stage brief — DECOMPOSE (run example-feature-tie-capacity, attempt 1)

Role: Delivery planner. Split the approved specification into independent, dependency-ordered units.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: PASS, BLOCKED. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=example-feature-tie-capacity stage=decompose agent=devin model=normal`; PRs carry the `ai-generated` label.

## Access and boundaries
Target repository: `tedfoley-cog/adms-test-automation-demo` (default branch `main`). Safety classification: **safety-critical**.
Files you may change: ['**']. Files you must not change: ['(none)'].
Commands — build: `npm --prefix console run build`; test: `pytest backend -q`; lint: `ruff check backend tools`.
Requirement ids match `(?:REQ|DEF)-[A-Z]+-\d{1,3}`; reference them verbatim.
Protected paths (two human reviewers): ['backend/app/flisr.py', 'firmware/src/**'].
Repo instruction files to read first: ['.agents/skills/safety-critical-change/SKILL.md', 'DEMO_NOTES.md'].
Layer visibility: {"models": ["backend/app/models.py"], "logic": ["backend/app/flisr.py", "backend/app/state_estimation.py", "backend/app/agc.py"], "api": ["backend/app/main.py"], "ui": ["console/**"], "visibility": {"api": ["logic", "models"], "logic": ["models"], "ui": ["api"]}}.

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

### STD-REQ — STD-REQ — Requirements specification standard

# STD-REQ — Requirements specification standard
Version: 1.2

- **STD-REQ-1**: Every requirement has a stable id matching the repo contract's `requirement_id_pattern` and is written as one testable statement (shall/shall not, measurable bound, named inputs and outputs).
- **STD-REQ-2**: A requirement that depends on a quantity (threshold, ratio, timing, CT ratio, per-unit base) states the unit, the range and the behaviour at the range limits.
- **STD-REQ-3**: Missing, late or invalid inputs are specified explicitly. "Treat as zero" is never an implicit default; the specification states refuse / hold-last-value / flag-quality for each input.
- **STD-REQ-4**: Ambiguities, contradictions and missing acceptance criteria in the source are recorded as questions with stable ids (`Q-SPEC-n`). The specifier does not resolve them by assumption; work that does not depend on the open question continues.
- **STD-REQ-5**: Each requirement names its verification method (test, analysis, inspection, demonstration) and, for protection or control functions, the independent oracle QA will use.
- **STD-REQ-6**: Safety classification (IEC 61508-3 context: none / safety-related / safety-critical) is stated for the change and inherited by every unit derived from it.
- **STD-REQ-7**: Scope exclusions are listed so that later stages can reject scope creep rather than absorb it.

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

REQ-FLISR-101 ...
REQ-FLISR-102 ...
REQ-FLISR-103 ...

## Human answers to earlier questions (recorded gate actions)

- **Q-SPEC-1** (ops-lead): Refuse restoration and raise an operator alarm; never hold last value.

## Prior artifact: specification

REQ-FLISR-101 ...
REQ-FLISR-102 ...
REQ-FLISR-103 ...

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
name: decompose
description: Splits an approved specification into independent, dependency-ordered delivery units with explicit file scopes so the orchestrator can run them in parallel waves. Used after the after-specify gate is approved.
---

# Decompose

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. Group requirements into units that can be implemented and verified alone. Prefer units aligned to one module and one test file.
2. For each unit: `id` (`U1`, `U2`…), `title`, `requirement_ids`, `depends_on` (unit ids), `files` (glob list of files the unit may touch — this becomes Coding's write boundary), `oracle` (how QA verifies independently).
3. Units touching protected paths inherit the two-reviewer rule; say so in the unit.

## Verify
No cycle in `depends_on`; every requirement id appears in exactly one unit; file globs do not overlap between units in the same wave.

## Deliver
`artifacts.units` — JSON array of units. Verdict `PASS`, or `BLOCKED` with `Q-DECOMP-n` if the specification cannot be partitioned without an assumption.

## Deliver
Finish by calling provide_structured_output with an object matching the schema you were given: `verdict`, `summary`, `evidence[]`, and where relevant `questions[]`, `trace[]` (requirement_id/kind/ref), `files_touched[]`, `branch`, `pr_url`, `standards_loaded[]`, `artifacts{}` (your stage's named outputs as markdown or JSON strings), `model`.
