# Console UI test plan (Playwright gauntlet)

Specs live in `console/tests/ui/*.spec.ts` (they resolve `@playwright/test` from the console package). Data: the committed runs under `runs/` (two scripted example runs plus the recorded dry-run worked
examples). Each scenario is a multi-step user journey, not a smoke test.

| # | Spec | Journey |
|---|------|---------|
| 1 | `runs.spec.ts` | Filter runs by workflow and status, search by id, sort, confirm empty-state, open a run from the table |
| 2 | `run-view.spec.ts` | Timeline shows stages + gates with human actors; click a FAIL/VIOLATION chip → drawer with evidence; close; open a gate chip |
| 3 | `trace.spec.ts` | Matrix shows every requirement fully traced; filter rows by kind, search, sort ref column both directions |
| 4 | `audit.spec.ts` | Chain badge verified in browser; filter by event; search for the human actor; drill into a record; count matches |
| 5 | `gate-form.spec.ts` | Validation: missing decision, bad actor, rejection without reason; then a valid rejection produces a decision record + `gh` command |
| 6 | `kpis.spec.ts` | KPI cards present with values; trend metric + scope toggles change the table and sparkline |
| 7 | `navigation.spec.ts` | Hash routing deep-links to a specific run/tab and survives reload; run switch updates all tabs |

Run: `npx playwright test` (builds the console, serves on 4173). CI runs it on every push.
