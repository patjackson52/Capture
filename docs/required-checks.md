# Required checks for branch protection (`main`)

Configure branch protection to enforce Android CD readiness.

## Required status checks

Use these check contexts (exact names from PR Checks UI):

- `Android CI / build-and-test`
- `Docs Link Check / check-doc-links` (guards runbook/evidence doc references and CD readiness consistency checks)

Recommended additional gate for release-focused PRs:

- `Android Play Internal CD / internal-release` (from manual dry-run run linked in PR)

> Note: the Play CD workflow is tag/manual-triggered, so it may not appear automatically on every PR commit. For release PRs, attach a successful dry-run workflow URL as evidence.

## Required branch protection settings

- Require pull request before merging
- Require at least 1 approval
- Dismiss stale approvals when new commits are pushed
- Require status checks to pass before merging
- Require branches to be up to date
- Include administrators (recommended)

## Optional but recommended

- Require conversation resolution before merge
- Restrict who can push to `main`
- Require signed commits (if org policy requires)
