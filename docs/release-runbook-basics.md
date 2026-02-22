# Android release runbook (baseline)

This is the minimum operator runbook for unsigned baseline releases.

## Preconditions

- `VERSION` file contains the intended release version (for example `0.1.0`)
- For tag-triggered release, git tag must be `v<VERSION>` (for example `v0.1.0`)
- Android signing material is handled separately (see `docs/signing-prerequisites-android.md`)

## Triggering releases

Two supported paths:

- Manual: GitHub Actions → **Capture Release Baseline** → **Run workflow**
- Tag push: push a tag matching `v*` (example: `v0.1.0`)

## What the workflow validates

- Fails fast if `VERSION` is empty
- Fails fast if tag/version mismatch is detected
- Runs unit tests (`testDebugUnitTest`)
- Builds unsigned release artifacts (`assembleRelease`)
- Verifies at least one APK/AAB exists

## Artifacts and metadata

Expected uploaded artifact name:

- `capture-android-release-unsigned-<VERSION>`

Metadata files included in artifact:

- `build/release-metadata.txt`
- `build/release-metadata.json`

Metadata captures version, ref, commit SHA, and workflow run identifiers.

## Retention

Release artifacts are retained for 30 days by default in baseline workflow.
