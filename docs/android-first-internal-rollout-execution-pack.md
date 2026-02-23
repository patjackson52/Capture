# Android first internal rollout execution pack

Single-source quickstart for the **first** Internal-track rollout.

Use this as the operator script. It links to all required evidence and provides a rollback decision tree.

## Scope

- Workflow: `.github/workflows/android-play-internal.yml` (**Android Play Internal CD**)
- Track: Google Play **Internal**
- Evidence record: `docs/release-verification-evidence-template.md`
- Governance gates: `docs/release-governance-checklist.md`
- Detailed runbook: `docs/release-runbook-basics.md`

## Quickstart (operator commands)

1. **Sync and verify target commit**

   ```bash
   git checkout main
   git pull --ff-only
   ```

2. **Confirm version alignment (`VERSION` == `versionName`)**

   ```bash
   VERSION_FILE="$(tr -d '[:space:]' < VERSION)"
   VERSION_NAME="$(grep -E 'versionName\s*=\s*"' app/build.gradle.kts | head -n1 | sed -E 's/.*"([^"]+)".*/\1/')"
   VERSION_CODE="$(grep -E 'versionCode\s*=\s*[0-9]+' app/build.gradle.kts | head -n1 | sed -E 's/.*=\s*([0-9]+).*/\1/')"
   echo "VERSION=${VERSION_FILE} versionName=${VERSION_NAME} versionCode=${VERSION_CODE}"
   test "${VERSION_FILE}" = "${VERSION_NAME}"
   ```

3. **Run required dry run** (GitHub Actions UI)
   - Workflow: **Android Play Internal CD**
   - Branch: `main`
   - Inputs:
     - `upload_enabled=false`
     - `release_status=draft`

4. **Record dry-run evidence immediately** in `docs/release-verification-evidence-template.md`
   - Required fields:
     - `Workflow URL (dispatch, upload_enabled=false)`
     - `Result`
     - `aab_sha256 from metadata`
     - `Target commit SHA`
     - `version`, `versionCode`, `previous tag`, `previous versionCode`

5. **Approval gate check**
   - Complete `docs/release-governance-checklist.md` approval gates.
   - Collect Engineering + QA + Product approvals in the release PR/issue.

6. **Create release tag after approval**

   ```bash
   git tag v$(tr -d '[:space:]' < VERSION)
   git push origin v$(tr -d '[:space:]' < VERSION)
   ```

7. **Monitor tag-triggered upload run**
   - Confirm summary shows:
     - `Upload requested: true`
     - `Release status`
     - `versionName/versionCode`
   - Confirm Play Internal release appears with expected `versionCode`.

8. **QA validation + final go/no-go**
   - Run smoke tests on target device matrix.
   - Complete `QA sign-off`, `Go/No-go`, and `Rollback readiness` sections in the evidence template.

## Evidence links (must be attached to release PR/issue)

- Dry-run workflow run URL
- Tag-triggered upload workflow run URL
- Release artifact metadata (`release-metadata.txt` / `release-metadata.json`)
- Play Console verification screenshot/link
- QA sign-off notes and final GO/NO-GO decision

Canonical evidence schema: `docs/release-verification-evidence-template.md`

## Rollback decision tree

```text
Start
  |
  |-- Is there a P0/P1 regression, crash/ANR breach, or security/privacy incident?
  |      |
  |      +-- NO --> Continue monitoring in Internal validation window
  |      |
  |      +-- YES --> Halt promotion immediately
  |                   |
  |                   |-- Is current internal release recoverable via quick fix (<24h)?
  |                   |      |
  |                   |      +-- YES --> Revert/fix on main, bump versionCode, ship patched build
  |                   |      |
  |                   |      +-- NO --> Deactivate/replace bad internal release with known-good AAB
  |                   |
  |                   --> Re-run CD + smoke tests + capture incident timeline/evidence
```

## Rollback command starter

```bash
# Example rollback prep (code-level)
git checkout main
git pull --ff-only
# revert offending commit(s)
git revert <bad_commit_sha>
# bump VERSION/versionName/versionCode, then:
git commit -am "revert: rollback bad internal release and bump versionCode"
git tag v$(tr -d '[:space:]' < VERSION)
git push origin main --follow-tags
```

For full rollback policy and triggers, see `docs/release-runbook-basics.md` and `docs/release-governance-checklist.md`.
