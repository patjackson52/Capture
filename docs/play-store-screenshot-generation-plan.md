# Play Store screenshot generation plan (automation + manual fallback)

Goal: make screenshot production repeatable for Android release trains while preserving a clear manual path if automation breaks.

## Automation-first plan

### 1) Stable capture scenarios

Define scenario IDs and expected screens before implementation:

- `onboarding-complete`
- `capture-start`
- `capture-review`
- `library-browse`

For each scenario, pin:

- Build flavor + seed data set
- Locale (`en-US` baseline, localized variants later)
- Device profile (phone first; tablet optional)
- Orientation and status-bar normalization rules

### 2) Instrumented screenshot harness (proposed)

Implement under Android test tooling (e.g., `androidTest` + Compose test rules / UI Automator):

- Launch app with deterministic fixtures
- Navigate to each scenario state
- Capture lossless PNG screenshots to a known artifact directory
- Name files to match `assets/manifest.json` export paths

Suggested output root:

- `app/build/outputs/play-screenshots/<buildType>/...`

### 3) Post-processing and packaging

Automated step should:

- Resize/crop only if required by Play constraints (avoid quality loss)
- Copy final exports into `assets/exports/play-store/screenshots/...`
- Run `scripts/check-assets-manifest.py`
- Generate report via `scripts/assets-preflight-report.py`

### 4) CI integration (phase 2)

After local harness is stable:

- Add optional workflow job for screenshot generation on demand (manual dispatch)
- Upload raw + final screenshot artifacts
- Publish preflight markdown/json reports as workflow artifacts

## Manual fallback checklist

Use this when automation is unavailable or for final design polish passes.

### Capture setup

- [ ] Use release-candidate build (or exact SHA documented in evidence)
- [ ] Enable demo mode / clean status bar (time, battery, network)
- [ ] Disable notifications and personal data surfaces
- [ ] Confirm theme/locale configuration for targeted listing

### Capture execution

- [ ] Capture at least 2 distinct phone screenshots matching manifest dimensions
- [ ] Verify screenshots reflect real shipping flows (no debug UI)
- [ ] Save exports to manifest-declared paths in `assets/exports/play-store/`

### Validation and handoff

- [ ] Run `scripts/check-assets-manifest.py`
- [ ] Run `scripts/assets-preflight-report.py`
- [ ] Attach `build/assets-preflight-report.md` to release evidence bundle
- [ ] Record operator + date + build SHA in release notes/evidence doc

## Acceptance criteria for this plan

- Operators can produce Play-ready screenshots in <30 minutes with either automation or manual fallback.
- Validation scripts produce deterministic pass/fail output.
- Report artifact is suitable for release evidence handoff without extra formatting.
