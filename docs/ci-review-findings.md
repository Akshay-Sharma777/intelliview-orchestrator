# CI Workflow Review — Issue #32

## Scope

Reviewed `.github/workflows/ci.yml` to verify the existing CI workflow,
confirm whether Ruff lint and pytest run for pull requests, and document
observed gaps or potential reliability concerns.

No workflow, lint, or test configuration changes were made as part of this
review.

---

## Pull Request Triggers

The CI workflow runs for pull requests targeting:

- `main`
- `Stabilized-version`
- `issue-22-dataset-validation`

Pull requests targeting other branches do not trigger this workflow.

Therefore, CI coverage is limited to the configured target branches rather
than applying repository-wide to every possible pull request.

---

## Ruff Verification

The Python Tests job installs Ruff version `0.9.10` and runs:

```text
ruff check orchestrator workers monitoring database tests scripts routers retrieval