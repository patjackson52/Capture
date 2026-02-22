# Required checks for branch protection (`main`)

This repository uses GitHub Actions for CI.

## Required status checks to enforce

Use these exact check names when configuring branch protection for `main`:

- `build-and-test` (from workflow **Android CI**)

Depending on GitHub UI/API context formatting, this may appear as:

- `Android CI / build-and-test`

## Branch protection settings (recommended)

In addition to required checks, enable:

- Require a pull request before merging
- Require approvals (at least 1)
- Dismiss stale approvals on new commits
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators (recommended for strict policy)

## GitHub click-path

1. Repo **Settings**
2. **Branches**
3. Under **Branch protection rules**, edit/add rule for `main`
4. Enable **Require status checks to pass before merging**
5. Add required check: `build-and-test`
6. Save changes

## API/CLI note

If using API/CLI, ensure the rule references the same status context that appears in checks for a PR commit. Use the exact string shown in the PR Checks tab if `build-and-test` alone does not resolve.
