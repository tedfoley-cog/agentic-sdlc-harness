# Implementation plan — agentic-sdlc-harness

Status: written before any code; kept current as the build proceeds.

## 1. What this repository is

A repo-agnostic **mechanism** for an agentic SDLC: a requirement goes in, a reviewed,
traced, merge-ready **draft** PR comes out, and humans act only at approval gates
(after Specify, after Architect, before merge). Agents never merge, approve, or move
work past ready-for-review. Devin is the orchestrator, the main agent and every stage
subagent.

The product repositories (e.g. the public ADMS fixture
`tedfoley-cog/adms-test-automation-demo`) stay untouched "before-state" targets; this
repository is the finished harness that is pointed at them.

## 2. Research inputs

| Source | Used for |
| --- | --- |
| Programme overview (PoC) | stage list, feedback loops, BLOCKED semantics, gate minimum, KPI list, cost method |
| Pilot 1 (busbar differential, ANSI 87B) | independent-oracle QA, two-reviewer rule for safety-critical paths, three known failure modes, acceptance criteria |
| Fit/gap report on the ADMS repo | confirms the ADMS repo is a fixture not the mechanism; lists the gaps this repo closes |
| IEC 60255-1 / -187-1 (measuring relays, differential), IEC 61508-3 (software lifecycle, tool classification T1-T3), IEC 61850-7-4 (logical nodes), IEEE C37.118 (synchrophasor), IEEE C37.2 (device numbers) | wording of the governing standards store; the T2/T3 "tool classification argument" finding; requirement-ID vocabulary |
| Devin REST API v3 (`POST /v3/organizations/{org}/sessions`, `GET .../sessions/{id}`, `POST .../messages`) | child-session transport; `devin_mode` enum (normal, fast, fusion, lite, ultra, swe-2-*) for the Coding-vs-QA mode split |
| GitHub REST (issues, labels, events, PR reviews) | human gate recording |

## 3. Layout

```
agentic-sdlc-harness/
  harness/                 Python package `agentic_sdlc` (stdlib + pyyaml only)
    config.py              harness.yaml contract + validation
    standards.py           StandardsStore (markdown dir | Confluence REST) — stop if absent
    brief.py               compiles stage brief: skill + standards + config + prior artifacts
    sessions/              SessionBackend: rest_v3 | devin_tool (parent session relays) | fake
    orchestrator.py        state machine: stages, loops, gates, parallel units, resume
    gates.py               GitHub-native gates (gate issue + labels, PR reviews); Jira/Linear adapters as stubs
    checks/                deterministic: model_logic_separation, removed_error_handling, missing_input_as_zero, scope, governance
    runlog.py              append-only hash-chained JSONL + replay
    trace.py               incremental trace matrix REQ -> design -> code -> test -> PR
    kpis.py                per-run KPIs + history
    cli.py                 `harness run|resume|gate|status|replay|report|check`
  plugin/skills/<stage>/SKILL.md   14 stage skills (prepare/execute/verify/deliver) + CONTRACT.md
  standards/               governing standards store (Confluence stand-in)
  console/                 Vite + React run viewer (reads runs/*.json), static-build friendly
  tests/                   pytest (orchestrator w/ fake backend, checks, runlog, trace, kpis)
  tests/ui/                Playwright gauntlet (>=5 complex scenarios) + UI_TEST_PLAN.md
  runs/                    worked examples from the dry run (runlog, trace, kpis, screenshots)
  examples/targets/adms/   harness.yaml overlay + requirement for the fixture
  docs/                    this plan, flowchart.html/.png, architecture, gates, conventions
  .github/workflows/ci.yml python tests + console build + Playwright on every push
  README.md, DEMO_NOTES.md
```

## 4. Mechanism design

### Stage machine
New feature: Specify → [GATE 1] → Decompose → Design ⇄ Architect (loop, max N) → [GATE 2] →
Coding ⇄ Verify(deterministic) ⇄ QA (loop, max N) → Integrate → Document → Trace →
[GATE 3: PR reviews] → (human merges) → optional Release.
RCA: Explore ⇄ Evaluate (≤2 rounds, else RETRACTION) → Review → Fix → QA → Document → Trace → [GATE 3].

Independent units from Decompose run in parallel (`parallel` fan-out) when their
dependency list is satisfied; a `BLOCKED` unit does not stop its siblings.

### Verdicts
`PASS | FAIL | BLOCKED | CONFIRMED | VIOLATION | NEEDS-HUMAN | REFUTED |
INSUFFICIENT_EVIDENCE`, always with `evidence[]` (artifact refs). Stage skills say which
subset they may emit. Every verdict is validated against a JSON schema before it is
accepted into the run log.

### Human gates (GitHub-native)
A gate issue is opened in the **harness** repo per gate; the human applies
`gate:approved` or `gate:rejected`. The orchestrator reads the *labeled* event, records
the actor login, and rejects bot actors. Gate 3 is the PR's own reviews (count against
`protected_paths.reviewers`). Jira/Linear are adapters behind the same interface,
not dependencies. Agents never infer a decision: a missing label = waiting.

### Repo contract (`harness.yaml`, overlay allowed)
build/test/lint commands, requirement-ID pattern, protected paths + reviewer count,
safety classification, standards locations, instruction files, write boundaries per
stage (allowed/forbidden globs), layer visibility, loop limits, models per stage.

### Deterministic checks (run after Coding, results fed back automatically)
1. `model_logic_separation` — data-model files (dataclass/pydantic/struct) must not grow
   control flow; logic files must not define new models.
2. `removed_error_handling` — diff must not net-remove `raise`/`except`/`throw`/guard
   clauses without a replacement in the same hunk.
3. `missing_input_as_zero` — flags `.get(x, 0)`, `or 0`, `?? 0`, `try…except: x = 0`,
   `optional → 0` patterns introduced by the change.
Plus scope (files touched ⊆ brief), governance (trailer, `ai-generated` label, draft).

### Governance
Branch `agent/<run-id>/<unit>`, draft PR only, commit trailer
`AI-Governance: run=<id> stage=<stage> agent=devin model=<mode>`, label `ai-generated`,
PR body carries trace + evidence. No merge path exists in the code.

### Trace & audit
Trace rows are appended by each stage (REQ → design item → file → test → PR), not by a
final pass. `runlog.jsonl` is append-only with a hash chain; `harness replay` rebuilds
state from it; the console renders it.

### KPIs
autonomy, first-pass approval per stage, loop iterations, loop resolution rate,
requirement test coverage, human review hours (from gate open→decision + manual entry),
cycle time, inference cost per story point (ACUs from session metadata × rate).

## 5. Dry run (against the ADMS fixture)
* Feature: a small FLISR requirement with one deliberate gap → Specify returns BLOCKED
  question; human answers at Gate 1; proceed to a draft PR.
* RCA: known FLISR defect (isolation ignores tie switches) → Explore/Evaluate/Review/Fix
  → draft PR. At least one QA or Architect loop resolved by agents.
* Humans = this session's operator. Fixture `main` is never modified.
* Both run logs + trace reports stored under `runs/` as worked examples.

## 6. Verification
pytest; ruff; console `tsc --noEmit` + build; Playwright gauntlet headless; flowchart
render check; live click-through recorded by the Devin testing agent.

## 7. Known constraints found so far
* The Devin API keys available in this session are expired → the dry run uses the
  `devin_tool` transport (the parent Devin session relays `create session` calls); the
  REST v3 backend is implemented and unit-tested against recorded responses but not
  exercised live. Raised as an open question.
