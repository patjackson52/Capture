# Android Internal release + rollback runbook

Use this runbook to execute and operate Internal track releases.

For first rollout operators, start with `docs/android-internal-release-drill-pack.md` (dry-run rehearsal + evidence prefill), then use `docs/android-first-internal-rollout-execution-pack.md` (single-source quickstart + evidence + rollback decision tree), then this runbook for detailed procedures.

## Preconditions

- All setup in `docs/distribution-prep-android-play-internal.md` is complete
- Release PR merged with required checks green
- `VERSION` and `versionName` aligned
- Decision recorded for `release_status` (`draft` recommended for first rollout)
- `docs/release-governance-checklist.md` approval gates reviewed and satisfied
- Evidence record opened from `docs/release-verification-evidence-template.md`

## Release procedure (Internal track)

1. **Prepare candidate**
   - Confirm target commit is on `main` and PR checks are green.
   - Confirm `VERSION` equals `versionName`.
   - Confirm `versionCode` increment is intentional and higher than the last shipped tag.

2. **Preflight dry run (required)**
   - Open GitHub Actions → **Android Play Internal CD**.
   - Run `workflow_dispatch` on `main` with:
     - `upload_enabled=false`
     - `release_status=draft`
   - Wait for green run and save:
     - run URL
     - commit SHA
     - artifact checksum (`release-metadata.txt`)

3. **Create release tag (promotes to upload mode)**
   - `git checkout main && git pull --ff-only`
   - `git tag v<VERSION>`
   - `git push origin v<VERSION>`

4. **Monitor upload run**
   - Workflow: **Android Play Internal CD** (tag-triggered run)
   - Verify summary includes:
     - expected `version` / `versionName` / `versionCode`
     - previous tag + previous `versionCode`
     - `release_status`
     - upload requested = `true`

5. **Verify in Play Console**
   - Internal track contains the new release
   - Status matches selected `release_status`
   - Build is tied to expected `versionCode`

6. **QA validation**
   - Install from Play Internal
   - Run smoke suite on target device matrix
   - Confirm crash-free startup and critical user path

## Manual release alternative

For controlled rehearsals, use `workflow_dispatch`:
- `upload_enabled=false` for dry run
- `upload_enabled=true` for actual upload

## Rollback / halt procedure

Trigger rollback on high crash rate, major regression, or security issue.

1. **Immediate containment**
   - Halt promotions beyond Internal
   - Mark incident in release channel

2. **Play Console action** (choose one)
   - Deactivate problematic internal release, or
   - Replace with previous known-good AAB

3. **Code-level remediation**
   - Revert offending commit(s) on `main`
   - Cut new patch release with incremented `versionCode`

4. **Verification**
   - Re-run CD workflow
   - Confirm updated build in Internal track
   - Re-run smoke tests

5. **Post-incident**
   - Capture timeline + root cause
   - Add prevention action items to backlog and checklist docs

## Evidence to retain per release

- Workflow run URL + commit SHA
- Generated metadata artifact (`release-metadata.*`)
- QA sign-off record
- Rollback decision log (if applicable)

Use `docs/release-verification-evidence-template.md` as the release record skeleton, and link it from the release PR/issue.
