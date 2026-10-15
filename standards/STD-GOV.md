# STD-GOV — AI governance and delivery standard
Version: 1.1

- **STD-GOV-1**: Agents work on branches prefixed `agent/` and open draft pull requests only. Marking ready-for-review is the last agent action; approving, merging and moving tickets past ready-for-review are human actions.
- **STD-GOV-2**: Every commit carries `AI-Governance: run=<run-id> stage=<stage> agent=<agent> model=<mode>`; every PR carries the `ai-generated` label and a body with requirement ids, evidence and the trace table.
- **STD-GOV-3**: Human gate decisions are taken in a system of record where only a human account can act (GitHub label event / PR review). Decisions by bot accounts are ignored. Agents never infer a decision from silence.
- **STD-GOV-4**: The audit log is append-only and hash-chained; it records agent, run id, stage, brief, model, timestamps, artifacts read and produced, verdicts, gate decisions and the human decision-maker.
- **STD-GOV-5**: Feedback loops are bounded by the repo contract; on reaching the limit the run escalates to NEEDS-HUMAN with the full loop history.
- **STD-GOV-6**: Protected paths require the configured number of human reviewers irrespective of agent confidence; safety-critical classification implies at least two.
- **STD-GOV-7**: Customer identifiers, personal names and credentials never appear in briefs, logs or PRs.
