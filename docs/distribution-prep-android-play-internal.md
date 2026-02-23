# Android Play Internal CD setup guide

This guide is the end-to-end setup for shipping Capture to **Google Play Internal** from GitHub Actions.

Workflow: `.github/workflows/android-play-internal.yml`

## 1) Required repository state

- `VERSION` file must contain the release version (example: `1.1`)
- `app/build.gradle.kts` must have:
  - `versionName` exactly matching `VERSION`
  - positive integer `versionCode`
- For tag-triggered releases, tag must be `v<VERSION>` (example: `v1.1`)

## 2) GitHub permissions + protections

Configure branch protection on `main`:

- Require pull request before merge
- Require approvals (>=1)
- Require status checks to pass
- Require branch up to date before merge
- Include administrators (recommended)

Required checks are listed in `docs/required-checks.md`.

## 3) Required secrets

### Signing secrets (for signed AAB)

- `ANDROID_KEYSTORE_BASE64` - base64 of upload keystore `.jks`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`

### Play upload secrets (for Internal track upload)

- `PLAY_SERVICE_ACCOUNT_JSON` - raw service account JSON
- `PLAY_PACKAGE_NAME` - app id (example: `com.capture.app`)

Recommended: store these in a protected **Environment** (for example `production-release`) with reviewer approval.

## 4) Service account scope (least privilege)

Use a dedicated Play service account with only the permissions needed for Internal upload and release management.

Minimum practical scope:
- View app info
- Upload/edit internal releases
- No broad financial/admin permissions

## 5) Trigger modes

### Manual dry run (default)

- GitHub Actions → **Android Play Internal CD**
- `upload_enabled=false` (default)

This mode still validates versioning and builds AAB artifacts, but skips Play upload.

### Manual upload

- Run workflow with `upload_enabled=true`
- Optional `release_status` (`draft`, `inProgress`, `completed`)

### Tag upload

- Push `v*` tag (for example `v1.1`)
- Upload is requested automatically and secrets are required

## 6) Fail-fast behavior

The workflow exits early when:

- `VERSION` missing/empty
- `versionName != VERSION`
- invalid `versionCode`
- tag/version mismatch
- invalid `release_status` (must be `draft|inProgress|completed`)
- manual upload attempted from non-`main` ref
- tag release `versionCode` is not strictly greater than previous tagged release
- upload requested while signing or Play secrets are missing
- AAB output missing

## 7) Artifacts and metadata outputs

Every run uploads:

- `capture-android-play-internal-<VERSION>` artifact containing:
  - generated `.aab`
  - `build/release-metadata.txt`
  - `build/release-metadata.json`

Metadata records commit/ref, run IDs, checksum, and whether secrets were present.

## 8) Consistency checks (docs + workflow contract)

`Docs Link Check / check-doc-links` now validates both file references and release-readiness contract consistency (required check names, workflow/job IDs, and evidence template sections).

Local preflight commands:

```bash
scripts/check-doc-links.sh
scripts/check-release-readiness-consistency.sh
```

## 9) First-time enablement checklist

Use `docs/release-governance-checklist.md` as the canonical checklist to avoid drift.

Minimum first rollout milestones:
- [ ] Dry run succeeds with `upload_enabled=false`
- [ ] Metadata confirms expected version + checksum
- [ ] First Internal upload executed with `release_status=draft`
- [ ] QA installs from Play Internal and signs off
- [ ] Evidence record completed via `docs/release-verification-evidence-template.md`
