# Android Internal Release — Run-Now Checklist (first rollout)

Use this as the **live operator checklist** during execution.

Related docs:
- Execution pack: `docs/android-first-internal-rollout-execution-pack.md`
- Rehearsal drill: `docs/android-internal-release-drill-pack.md`
- Governance gates: `docs/release-governance-checklist.md`
- Detailed runbook: `docs/release-runbook-basics.md`
- Evidence template: `docs/release-verification-evidence-template.md`

## 0) Preconditions (must be YES before action)

- [ ] Candidate commit is merged on `main`
- [ ] Required checks green on candidate PR
- [ ] `VERSION` == `versionName`
- [ ] `versionCode` incremented vs previous shipped tag
- [ ] Release evidence record opened

Quick verify:

```bash
VERSION_FILE="$(tr -d '[:space:]' < VERSION)"
VERSION_NAME="$(grep -E 'versionName\s*=\s*"' app/build.gradle.kts | head -n1 | sed -E 's/.*"([^"]+)".*/\1/')"
VERSION_CODE="$(grep -E 'versionCode\s*=\s*[0-9]+' app/build.gradle.kts | head -n1 | sed -E 's/.*=\s*([0-9]+).*/\1/')"
echo "VERSION=${VERSION_FILE} versionName=${VERSION_NAME} versionCode=${VERSION_CODE}"
test "${VERSION_FILE}" = "${VERSION_NAME}"
```

## 1) Dry-run (required)

- [ ] Trigger workflow **Android Play Internal CD** on `main`
- [ ] Inputs: `upload_enabled=false`, `release_status=draft`
- [ ] Run passes
- [ ] Capture run URL + metadata artifact (`release-metadata.*`)
- [ ] Record `aab_sha256`, `version`, `versionCode`, `previous_tag`, `previous_versionCode`, `run_url` in evidence record

## 2) Approval gate (explicit go/no-go to tag)

- [ ] Engineering owner approval
- [ ] QA approval
- [ ] Product/release owner approval
- [ ] Security/privacy review complete (if sensitive)
- [ ] Governance checklist fully complete

Decision:
- [ ] **GO** (tag release)
- [ ] **NO-GO** (stop and remediate)

## 3) Tag and upload

```bash
git checkout main
git pull --ff-only
git tag v$(tr -d '[:space:]' < VERSION)
git push origin v$(tr -d '[:space:]' < VERSION)
```

- [ ] Tag-triggered workflow run passes
- [ ] Summary shows `Upload requested: true`
- [ ] Play Internal has expected `versionCode`

## 4) Post-upload validation

- [ ] Install from Play Internal
- [ ] Smoke tests pass on target device matrix
- [ ] Evidence template completed (including QA sign-off + final GO/NO-GO)

## 5) Rollback decision support (if issue appears)

Immediate rollback if any are true:
- [ ] P0/P1 regression in critical flow
- [ ] Crash/ANR materially above baseline
- [ ] Security/privacy incident
- [ ] Major install/update failure spike

If rollback needed:
- [ ] Stop promotion immediately
- [ ] Deactivate/replace bad Internal release in Play
- [ ] Revert/fix on `main`, bump `versionCode`, rerun CD
- [ ] Capture incident timeline in evidence record
