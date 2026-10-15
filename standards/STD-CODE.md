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
