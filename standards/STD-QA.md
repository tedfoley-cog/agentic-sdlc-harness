# STD-QA — Independent verification standard
Version: 1.3

- **STD-QA-1**: QA runs on a different model or agent mode from Coding and starts from the brief and the repository, not from Coding's report. Coding's claims are hypotheses to be re-tested.
- **STD-QA-2**: QA re-runs build, lint and the full test suite itself and attaches the output; it does not accept a pasted log.
- **STD-QA-3**: For protection/control functions QA writes or uses an independent oracle (closed-form or reference model) and its own test vectors, including boundary and invalid-input vectors, and reports agreement with tolerance.
- **STD-QA-4**: QA checks the three known failure modes explicitly: model/logic mixing, deleted error handling, missing input treated as zero — in addition to the deterministic checks the harness already ran.
- **STD-QA-5**: Every FAIL names the requirement id, the failing vector or test, the observed and expected values and the file/line; Coding must be able to act on it without a conversation.
- **STD-QA-6**: QA verifies each requirement id in scope has at least one passing test that references it; missing coverage is a FAIL even when all tests pass.
- **STD-QA-7**: QA may return INSUFFICIENT_EVIDENCE when it cannot run the checks (environment, missing fixtures); it never passes on trust.
