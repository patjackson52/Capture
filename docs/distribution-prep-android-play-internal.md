# Android Play Internal distribution prep (Phase 2 scaffold)

This document defines the non-secret scaffolding and validation path for Play Internal uploads.

## Required secrets (fail-fast enforced in workflow)

- `PLAY_SERVICE_ACCOUNT_JSON` - raw JSON for the Play Console service account with minimal rights
- `PLAY_PACKAGE_NAME` - application ID/package name (for example `com.example.capture`)

> Workflow: `.github/workflows/android-play-internal.yml`

## Trigger paths

- Manual: **Android Play Internal (scaffold)** via `workflow_dispatch`
- Tag push: `v*` (upload will execute on tag runs)

## Validation behavior

The workflow fails immediately when:

- `VERSION` is empty
- tag version and `VERSION` do not match
- required distribution secrets are missing
- no release `.aab` is produced

## Safe scaffold mode (default)

`upload_enabled` defaults to `false` for manual runs.

In scaffold mode, the workflow:

1. validates configuration/secrets
2. builds release AAB (`bundleRelease`)
3. writes run summary guidance
4. skips actual Play upload

## Enabling real upload

For manual run, set:

- `upload_enabled=true`
- optional `release_status` (`draft`, `inProgress`, `completed`)

For tag push (`v*`), upload executes automatically after validation/build.

## Operator validation checklist

- [ ] Secrets exist in repo/environment scope with least privilege
- [ ] Service account has Internal track upload permission only as needed
- [ ] `PLAY_PACKAGE_NAME` matches app package exactly
- [ ] Dry-run/scaffold run succeeded from `workflow_dispatch`
- [ ] First upload performed to Internal track as `draft`
- [ ] QA install + smoke test completed from Play Internal artifact
