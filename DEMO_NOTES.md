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
