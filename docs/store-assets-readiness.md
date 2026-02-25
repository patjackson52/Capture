# Android Play Store assets readiness

This checklist tracks required Play listing art and screenshots before release.

## Required assets (baseline)

- App icon: `512x512 PNG`
- Feature graphic: `1024x500 PNG`
- Phone screenshots: at least 2 (current scaffold uses `1080x1920 PNG`)

## Repository scaffold

- Manifest: `assets/manifest.json`
- Required-asset matrix: `assets/requirements/play-listing-required-asset-matrix.json`
- Schema details: `assets/README.md`
- Source working files: `assets/source/play-store/`
- Submission exports: `assets/exports/play-store/`
- Validation script: `scripts/check-assets-manifest.py`
- Preflight checklist report: `scripts/assets-preflight-report.py`
- Handoff bundle generator: `scripts/generate-play-asset-handoff-bundle.py`
- Screenshot automation + fallback plan: `docs/play-store-screenshot-generation-plan.md`
- Asset production workflow: `docs/asset-production-workflow.md`

## Validate locally

```bash
scripts/check-assets-manifest.py
scripts/assets-preflight-report.py
scripts/generate-play-asset-handoff-bundle.py --release <label> --zip
```

Current CI behavior:
- Fails when required schema fields/placeholders are missing
- Warns when required final exports are not yet added
- Verifies image dimensions when exports are present

Preflight report outputs:
- Markdown checklist for release operators: `build/assets-preflight-report.md`
- JSON summary for automation/pipelines: `build/assets-preflight-report.json`

## Human/design-owned items

- Final artwork and branding decisions
- Screenshot capture curation and copy polish
- Play listing localized creatives (if/when needed)
