# Agentic SDLC stage brief — QA (run example-rca-backfeed, attempt 1)

Role: Independent QA. Re-run every check yourself with your own oracle/test vectors; trust nothing from Coding.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: PASS, FAIL, BLOCKED, INSUFFICIENT_EVIDENCE. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=example-rca-backfeed stage=qa agent=devin model=ultra`; PRs carry the `ai-generated` label.

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

DEF-FLISR-7 Restoration back-fed a de-energised section during drill 14.

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

## Prior artifact: root_cause

{
  "hypothesis": "snapshot ordering",
  "evaluation": "Ordering trace demonstrates the mechanism and excludes telemetry lag."
}

## Prior artifact: review

...

## Prior artifact: coding_report

{
  "verdict": "PASS",
  "summary": "Failing repro committed first; snapshot re-taken after isolation; invariant over 500 seeds.",
  "evidence": [
    {
      "kind": "note",
      "ref": "scripted example"
    }
  ],
  "trace": [
    {
      "requirement_id": "DEF-FLISR-7",
      "kind": "code",
      "ref": "backend/app/flisr.py::plan_restoration"
    },
    {
      "requirement_id": "DEF-FLISR-7",
      "kind": "test",
      "ref": "test_flisr.py::test_def_flisr_7_no_backfeed"
    }
  ],
  "files_touched": [
    "backend/app/flisr.py",
    "backend/tests/test_flisr.py"
  ],
  "branch": "agent/example/fix",
  "pr_url": "https://github.com/example-org/product-repo/pull/102",
  "session_url": "fake://sessions/fake-0006",
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
  "commands": {},
  "branch": "agent/example/fix",
  "files_in_diff": []
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
