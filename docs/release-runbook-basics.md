# Android Internal release + rollback runbook

Use this runbook to execute and operate Internal track releases.

## Preconditions

- All setup in `docs/distribution-prep-android-play-internal.md` is complete
- Release PR merged with required checks green
- `VERSION` and `versionName` aligned
- Decision recorded for `release_status` (`draft` recommended for first rollout)

## Release procedure (Internal track)

1. **Prepare candidate**
   - Confirm target commit on `main`
   - Confirm `VERSION`/`versionCode` are correct

2. **Create release tag**
   - `git tag v<VERSION>`
   - `git push origin v<VERSION>`

3. **Monitor workflow**
   - Workflow: **Android Play Internal CD**
   - Verify summary shows expected version, checksum, and upload state

4. **Verify in Play Console**
   - Internal track contains new release
   - Status matches selected `release_status`
   - Release notes/changelog populated (if required by team process)

5. **QA validation**
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
