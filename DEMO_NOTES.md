# Demo notes — Agentic SDLC harness

## What to show, in order

1. **The contract** — `examples/targets/adms/harness.yaml`: everything the harness knows about a product repo on one page. Swap the file, swap the repo.
2. **The requirement goes in** — `harness run --workflow feature ...` with `examples/targets/adms/requirements/REQ-tie-capacity.md`. Specify stops with `Q-SPEC-1` instead of guessing what "unavailable capacity" means for a safety-critical restoration. `harness answer` records who answered.
3. **The console** — `npm --prefix console run dev`. Runs → Run view (timeline, gate chips with the human login, feedback loops) → Trace → Audit (chain re-verified in the browser) → KPIs → Gate form.
4. **A loop that resolved itself** — the Coding ⇄ QA loop in `runs/*`: deterministic check fails on `missing-input-as-zero`, Coding fixes, QA passes on a different Devin mode with its own oracle.
5. **The three gates** — after-specify, after-architect, before-merge: each a recorded human decision, each with actor; bot actors are ignored (`tests/test_orchestrator.py::test_gate_rejects_bot_actor`).
6. **RCA chain** — `runs/*rca*`: Explore → Evaluate REFUTED (evidence-only, `repos=[]`) → second Explore → CONFIRMED → Review → human gate → Fix → QA → draft PR.
7. **Replay** — `harness replay <run>` rebuilds the state from the audit log and proves the chain.

## Dry-run results

See `runs/` — `example-*` are the deterministic scripted runs (CI replays them); `feature-tie-capacity` and `rca-backfeed` are the live runs whose stage sessions were real Devin child sessions (session URLs in each `sessions/*.result.json` and in the audit log). Humans at the gates were stand-ins (recorded as such in `gates/*.decision.json`) because the only GitHub account available to the dry run was a bot — which the GitHub gate provider correctly ignores.

### Live feature run — `runs/feature-tie-capacity` (status `ready-to-merge`)

Requirement `REQ-tie-capacity.md` (5 lines) → draft fixture PR [#24](https://github.com/tedfoley-cog/adms-test-automation-demo/pull/24) (U1–U4 + QA U1–U4 + `docs/flisr/tie-capacity.md`, 793 tests, 23/23 requirements traced to tests). 30 Devin stage sessions, 3 human gates, 0 agent merges/approvals.

- **Specify**: 4 rounds, 13 stable-ID questions (`Q-SPEC-1..13`) answered by the ops lead before anything was designed — "tie capacity" was ambiguous (nameplate vs live SCADA value, kW vs kVA).
- **Design ⇄ Architect**: 7 Design / 5 Architect rounds. The bound (2) tripped as designed → `NEEDS-HUMAN`; the principal engineer extended it three times with recorded reasons (`loop.extended`), round 5 `CONFIRMED`. Architect found a real spec contradiction (REQ-TIECAP-3/4 vs the held-tie rule) that was fixed in the spec, not papered over in code.
- **Coding**: U2 stopped itself twice with `BLOCKED` — the repo contract forbade `backend/app/models.py` but the approved design assigned it (`contract.amended`), and an existing exact-dump test pinned the file (`units.amended`). Deterministic `model_logic_separation` rejected a branching pydantic validator; Coding rewrote it declaratively on the automatic feedback, no human.
- **QA**: every unit QA'd on Ultra with an AST-enforced independent oracle (600–800 seeded feeders each, 100 % agreement); QA U4 mutation-tested the planner 18 ways. A QA finding addressed to another unit was carried into that unit's brief (`finding.carried`).
- **Trace**: stopped at `NEEDS-HUMAN` because the id scanner registered the scope exclusion `DEF-FLISR-7` as a requirement; the ops lead waived it with a reason (`harness waive`, `trace.waived`) — never inferred.
- **Harness defects the live run found** (all fixed with `harness.corrected` in the audit log): stacked PRs diffed against `main` instead of their base; stacked-unit files flagged out of scope; raw structured-output JSON rejected by the relay; `missing_input_as_zero` matched prose in a docstring; replayed loop rounds double-counted in KPIs; Integrate skill told the agent to flip draft→ready (now a human action at before-merge).
- **Carried to humans at before-merge** (in `gates/before-merge.decision.json`, not scope-expanded): landing order #13 → #14 → #24; re-pin 14 whole-plan equality tests in `test_flisr_def_flisr_7_qa.py`; Devin Review finding on #14 (closed tie back-feeding the fault) → own defect; QA-U4 shared-island accounting → own defect; pre-existing ruff `UP017` in `tools/` → human chore (fixture CI backend job is red on every agent branch because of it); platform `Co-Authored-By` trailer → governance question.

### Live RCA run — `runs/rca-backfeed` (status `ready-to-merge`)

`DEF-FLISR-7` → Explore (CONFIRMED hypothesis) → Evaluate on Ultra with `repos=[]` → **REFUTED** the first hypothesis on evidence alone → Explore #2 → CONFIRMED → Review → after-review gate → Fix (failing test first, smallest fail-safe change) → QA on Ultra (independent oracle) → Integrate → Document → Trace → before-merge gate. Draft fixture PRs [#13](https://github.com/tedfoley-cog/adms-test-automation-demo/pull/13) / [#14](https://github.com/tedfoley-cog/adms-test-automation-demo/pull/14); autonomy 0.875.

## Ask → where it lives

| Ask | Location |
|-----|----------|
| Requirement in, reviewed draft PR out; humans only at gates | `harness/agentic_sdlc/orchestrator.py` (`FEATURE_PLAN`, `RCA_PLAN`, `gate:*` steps) |
| Standards loaded at runtime, swappable store, BLOCKED when missing | `harness/agentic_sdlc/standards.py`, `standards/*.md`, `tests/test_orchestrator.py::test_missing_standard_blocks` |
| Specify asks stable-ID questions, never guesses | `plugin/skills/specify/SKILL.md`, `orchestrator.py` (`questions` → `Paused`), `harness answer` |
| QA independent of Coding (different mode, own oracle) | `config.py` (`modes.qa != modes.coding` enforced), `plugin/skills/qa/SKILL.md`, `STD-QA-1` |
| Evaluate evidence-only, no codebase access | `config.py` (`boundaries["evaluate"]` forced), `brief.py` (`repos=[]`), `STD-RCA-2` |
| Coding writes a failing test first; only files named in the brief | `plugin/skills/coding/SKILL.md`, `checks/diffs.py` scope check, `STD-CODE-1` |
| Devin child session per stage, state persisted, resume after gates | `sessions/rest_v3.py`, `sessions/relay.py`, `runs/<id>/state.json`, `harness resume` |
| Bounded feedback loops with escalation | `harness.yaml: loops.*`, `orchestrator.py` (`NEEDS-HUMAN` on bound) |
| Parallel units when dependencies allow | `orchestrator.py` coding waves (dependency-ordered) |
| Human gates after Specify / Architect / before merge, explicit human action | `gates.py` (`GitHubIssueGate`, `GitHubPRReviewGate`, bot actors ignored), `gate:approved` / `gate:rejected` |
| Jira / Linear optional, not dependencies | `gates.py::provider_from_config` (adapter stubs) |
| Per-repo config (build/test/lint, id pattern, protected paths, safety class, standards, instructions, boundaries, layers) | `examples/targets/adms/harness.yaml`, `config.py` |
| Deterministic checks: model/logic mix, deleted error handling, missing→zero | `checks/model_logic_separation.py`, `checks/removed_error_handling.py`, `checks/missing_input_as_zero.py`, `tests/test_checks.py`, `harness check` |
| Governance: agent branches, draft PRs, trailer, label, never merge/approve | `checks/governance.py`, `STD-GOV`, `plugin/skills/CONTRACT.md` |
| Incremental traceability req → design → code → test → PR | `trace.py`, `runs/<id>/trace.json`, console Trace view |
| Audit: agent, run, stage, brief, model, timestamps, artifacts, verdicts, gate decisions, decision-maker | `runlog.py` (hash-chained JSONL), `runs/<id>/runlog.jsonl`, `runs/<id>/briefs/` |
| Audit replay + run viewer | `harness replay`, `console/` (Run / Audit views, browser-side chain verification) |
| KPIs per run + trend | `kpis.py`, `runs/kpi_history.jsonl`, console KPIs view |
| Orchestrator run view (stages, verdicts, gates, trace coverage) | `console/src/views/Run.tsx` |
| Multi-view UI, validated forms, filter/sort/search, drill-down, ≥5 Playwright journeys, CI on every push | `console/src/views/*`, `console/tests/ui/*.spec.ts` (7), `.github/workflows/ci.yml` |
| Flowchart | `README.md` (native Mermaid), `docs/flowchart.html`, `docs/flowchart-*.png` |
