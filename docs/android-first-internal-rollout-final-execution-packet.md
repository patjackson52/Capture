# Android first internal rollout — final execution packet

Use this as the **single operator sheet** for first internal rollout execution.

It is intentionally condensed into one checklist with copy/paste commands and evidence handoff references.

Related detail docs (deep dive):
- `docs/android-first-internal-rollout-execution-pack.md`
- `docs/android-internal-release-run-now-checklist.md`
- `docs/android-internal-release-drill-pack.md`
- `docs/release-governance-checklist.md`
- `docs/release-verification-evidence-template.md`

---

## A) One-pass operator checklist (GO path)

- [ ] Candidate changes are merged on `main`
- [ ] Required checks green for release PR (`Android CI`, `Docs Link Check`)
- [ ] Local version alignment verified (`VERSION == versionName`)
- [ ] `versionCode` greater than previous shipped tag
- [ ] Dry-run completed (`upload_enabled=false`, `release_status=draft`)
- [ ] Dry-run evidence attached (run URL + metadata + `aab_sha256`)
- [ ] Engineering + QA + Product approvals captured
- [ ] GO decision recorded
- [ ] Tag pushed (`v<version>`)
- [ ] Tag-triggered upload run passed
- [ ] Play Internal confirms expected `versionCode`
- [ ] QA smoke pass recorded
- [ ] Final GO/NO-GO + rollback readiness recorded in evidence template

---

## B) Commands (copy/paste)

### 1) Sync + version context

```bash
git checkout main
git pull --ff-only
./scripts/release-day-context.sh
```

Expected signals:
- `version_match=yes`
- `previous_tag` and `previous_version_code` populated (or `none/unknown` for first tag)

### 2) Manual dry-run in GitHub Actions UI (required)

Workflow: **Android Play Internal CD**

Inputs:
- `upload_enabled=false`
- `release_status=draft`

### 3) Evidence handoff from dry-run artifact metadata

If artifact `capture-android-play-internal-<version>` is downloaded locally:

```bash
./scripts/evidence-handoff-from-metadata.sh /path/to/release-metadata.txt
```

Paste output into release PR/issue evidence section.

### 4) Tag + trigger live upload (after approvals)

```bash
git checkout main
git pull --ff-only
git tag v$(tr -d '[:space:]' < VERSION)
git push origin v$(tr -d '[:space:]' < VERSION)
```

### 5) Optional rollback starter (if GO revoked)

```bash
git checkout main
git pull --ff-only
git revert <bad_commit_sha>
# bump VERSION/versionName/versionCode
git commit -am "revert: rollback internal release and bump versionCode"
git tag v$(tr -d '[:space:]' < VERSION)
git push origin main --follow-tags
```

---

## C) Evidence handoff references (source of truth)

Attach all of the following to the release PR/issue:

1. Dry-run workflow run URL (dispatch)
2. Tag-triggered workflow run URL (upload)
3. Artifact files:
   - `release-metadata.txt`
   - `release-metadata.json`
   - `build/evidence-handoff.md` (if present in artifact)
4. `aab_sha256` from metadata
5. Play Console verification screenshot/link
6. QA sign-off notes
7. Final GO/NO-GO decision
8. Rollback readiness statement

Canonical schema for evidence fields:
- `docs/release-verification-evidence-template.md`

---

## D) Human-only minimal steps (cannot be automated here)

- Trigger dry-run and tag-upload workflows in GitHub Actions UI
- Approve release gate (Engineering/QA/Product)
- Verify Play Console Internal track result
- Execute QA smoke and sign-off
- Make final GO/NO-GO call
