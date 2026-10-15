# Agentic SDLC stage brief — CODING (run example-feature-tie-capacity, attempt 2)

Role: Implementer. Write a failing test first, then the smallest change that makes it pass.

## Contract
Work in four phases and report each in your final output: **prepare** (load the governing standards listed below and confirm each by id; if one is missing, stop with BLOCKED), **execute**, **verify** (re-check your own output against the standards and the repo contract), **deliver** (structured verdict with evidence).

Allowed verdicts for this stage: PASS, FAIL, BLOCKED. Every verdict needs `evidence[]` entries that point at files, tests, commands, commits, PRs or standard clauses you actually used or produced.
Gaps, contradictions or missing acceptance criteria in your inputs are reported as `questions[]` with stable ids (`Q-<STAGE>-<n>`) and verdict BLOCKED. Never fill a gap with an assumption.
You never merge, approve, close a gate, or move a ticket past ready-for-review. Draft PRs only; branches start with `agent/`; every commit carries the trailer `AI-Governance: run=example-feature-tie-capacity stage=coding agent=devin model=normal`; PRs carry the `ai-generated` label.

## Access and boundaries
Target repository: `tedfoley-cog/adms-test-automation-demo` (default branch `main`). Safety classification: **safety-critical**.
Files you may change: ['backend/app/flisr.py', 'backend/tests/**']. Files you must not change: ['backend/app/models.py', 'firmware/**', 'legacy/**'].
Commands — build: `npm --prefix console run build`; test: `pytest backend -q`; lint: `ruff check backend tools`.
Requirement ids match `(?:REQ|DEF)-[A-Z]+-\d{1,3}`; reference them verbatim.
Protected paths (two human reviewers): ['backend/app/flisr.py', 'firmware/src/**'].
Repo instruction files to read first: ['.agents/skills/safety-critical-change/SKILL.md', 'DEMO_NOTES.md'].
Layer visibility: {"models": ["backend/app/models.py"], "logic": ["backend/app/flisr.py", "backend/app/state_estimation.py", "backend/app/agc.py"], "api": ["backend/app/main.py"], "ui": ["console/**"], "visibility": {"api": ["logic", "models"], "logic": ["models"], "ui": ["api"]}}.

## Governing standards (loaded at runtime — confirm each id in `standards_loaded`)

### STD-CODE — STD-CODE — Implementation standard

# STD-CODE — Implementation standard
Version: 1.4

- **STD-CODE-1**: Test first. The failing test that demonstrates the requirement (or the defect) is committed before the production change that satisfies it.
- **STD-CODE-2**: Change only the files named in the brief. If the brief is wrong, stop with BLOCKED and say which file is missing and why.
- **STD-CODE-3**: Missing or invalid input is never coerced to zero (`.get(k, 0)`, `or 0`, `?? 0`, exception handlers assigning 0). Raise, return an explicit unavailable value, or set a quality flag. A documented exception needs `# harness: zero-ok <standard clause>`.
- **STD-CODE-4**: Never delete error handling during a refactor without replacing it in the same change; the deterministic check `removed_error_handling` enforces this.
- **STD-CODE-5**: Every commit carries the `AI-Governance:` trailer; every branch starts with the configured agent prefix; pull requests are opened as drafts with the `ai-generated` label and are never merged by an agent.
- **STD-CODE-6**: The repo's build, lint and test commands pass locally before delivery; the output is attached as evidence.
- **STD-CODE-7**: Each test references the requirement id it verifies (test name or marker) so traceability is built as the code is written.
- **STD-CODE-8**: Numerical code uses the shared characteristic function and explicit units; magic constants require a named setting with a source reference.

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

REQ-FLISR-101 ...
REQ-FLISR-102 ...
REQ-FLISR-103 ...

## Your unit

```json
{
  "id": "U1",
  "title": "Capacity model + guard",
  "depends_on": [],
  "files": [
    "backend/app/flisr.py",
    "backend/tests/test_flisr_capacity.py"
  ],
  "requirement_ids": [
    "REQ-FLISR-101",
    "REQ-FLISR-102"
  ]
}
```

## Human answers to earlier questions (recorded gate actions)

- **Q-SPEC-1** (ops-lead): Refuse restoration and raise an operator alarm; never hold last value.

## Prior artifact: specification

REQ-FLISR-101 ...
REQ-FLISR-102 ...
REQ-FLISR-103 ...

## Prior artifact: design

v2

## Prior artifact: architecture_review

ok

## Feedback from the previous iteration (resolve every item or explain why not)

```json
[
  {
    "from": "qa",
    "iteration": 1,
    "summary": "Vector 7 (capacity exactly at load) restores; spec says refuse at equality.",
    "evidence": [
      {
        "kind": "test",
        "ref": "oracle vector 7",
        "detail": "observed restore, expected refuse"
      }
    ],
    "report": "..."
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
name: coding
description: Implements one delivery unit test-first on an agent branch, touching only the files in the brief, and opens a draft PR with the governance trailer and label. Used for each unit after the after-architect gate, and again with verification/QA findings when a loop iteration fails.
---

# Coding

Follows the four-phase contract in `CONTRACT.md`. Allowed verdicts: PASS, FAIL, BLOCKED.

## Prepare
Load the governing standards named in the brief (ids in `standards_loaded`); stop with `BLOCKED` if any is missing. Read the repo contract and its instruction files.

## Execute
1. `git checkout -b agent/<run-id>/<unit-id>` from the default branch. Baseline: run the repo's test and lint commands.
2. Pin current behaviour with characterization tests where the unit changes existing logic (STD-SAFETY-2).
3. Write the failing test(s) for the unit's requirement ids first — test names or markers include the id (STD-CODE-1, STD-CODE-7). Commit.
4. Make the smallest change that passes. Never coerce missing/invalid input to zero (STD-CODE-3); never drop a guard without replacing it (STD-CODE-4); models stay in the models module (STD-ARCH-1).
5. If feedback is present (deterministic checks, QA report), resolve every item and reference it in the commit body.
6. Commit with the `AI-Governance:` trailer. Push. Open a **draft** PR with the `ai-generated` label; body: requirement ids, what changed, how to verify.

## Verify
Run build, lint and test; paste the tail as `evidence[]` of kind `command`. Confirm `files_touched` ⊆ brief files.

## Deliver
`branch`, `pr_url`, `files_touched[]`, `trace[]` rows of kind `code` and `test`. `PASS`; `FAIL` if you could not make the tests pass; `BLOCKED` with `Q-CODE-n` if the brief is wrong or incomplete.

## Deliver
Finish by calling provide_structured_output with an object matching the schema you were given: `verdict`, `summary`, `evidence[]`, and where relevant `questions[]`, `trace[]` (requirement_id/kind/ref), `files_touched[]`, `branch`, `pr_url`, `standards_loaded[]`, `artifacts{}` (your stage's named outputs as markdown or JSON strings), `model`.
