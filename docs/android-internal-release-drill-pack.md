# Android Internal Release Drill Pack (dry-run rehearsal)

Lightweight, one-pass rehearsal pack operators can execute before a tagged Internal upload.

Use this to validate process readiness and prefill release evidence in a single session.

## When to use

Run this drill when:
- onboarding a new release operator,
- process/docs changed since the last release,
- preparing for first rollout in a cycle.

## Inputs you need up front

- Candidate commit SHA on `main`
- Current `VERSION`, `versionName`, `versionCode`
- Previous shipped tag + `versionCode`
- A release issue/PR where evidence will be recorded

## One-pass drill steps (30–45 min)

1. **Open all operator docs once**
   - `docs/android-internal-release-run-now-checklist.md`
   - `docs/release-governance-checklist.md`
   - `docs/release-verification-evidence-template.md`

2. **Run local preflight checks**

   ```bash
   git checkout main
   git pull --ff-only

   VERSION_FILE="$(tr -d '[:space:]' < VERSION)"
   VERSION_NAME="$(grep -E 'versionName\s*=\s*"' app/build.gradle.kts | head -n1 | sed -E 's/.*"([^"]+)".*/\1/')"
   VERSION_CODE="$(grep -E 'versionCode\s*=\s*[0-9]+' app/build.gradle.kts | head -n1 | sed -E 's/.*=\s*([0-9]+).*/\1/')"

   echo "VERSION=${VERSION_FILE} versionName=${VERSION_NAME} versionCode=${VERSION_CODE}"
   test "${VERSION_FILE}" = "${VERSION_NAME}"
   ```

3. **Execute required CD dry run**
   - GitHub Actions → **Android Play Internal CD**
   - Branch: `main`
   - Inputs:
     - `upload_enabled=false`
     - `release_status=draft`
   - Wait for green completion.

4. **Capture evidence immediately (same sitting)**
   - Open the evidence template and fill:
     - Release identity block
     - Dry-run evidence block
     - Rehearsal evidence block
     - Operator checklist completion block
   - Attach run URL + metadata (`release-metadata.*`).

5. **Gate handoff (no tag in drill mode)**
   - Confirm governance checklist owners and approvers are identified.
   - Record GO/NO-GO recommendation for real release execution.

## Drill success criteria

- Dry run completed successfully (`upload_enabled=false`)
- Evidence template prefilled with required fields
- No missing approver/owner assignments
- Operator can proceed to live checklist without clarification

## Outputs to attach to release issue/PR

- Dry-run run URL
- `aab_sha256`, `version`, `versionCode`, `run_attempt`
- Candidate commit SHA
- Named owners for Engineering, QA, Product approvals
- Any blocker list (if present)

## Related docs

- Execution pack (first rollout): `docs/android-first-internal-rollout-execution-pack.md`
- Live checklist: `docs/android-internal-release-run-now-checklist.md`
- Governance checklist: `docs/release-governance-checklist.md`
- Evidence template: `docs/release-verification-evidence-template.md`
- Detailed runbook: `docs/release-runbook-basics.md`
