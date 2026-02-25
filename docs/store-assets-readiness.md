# Android Play Store assets readiness

This checklist tracks required Play listing art and screenshots before release.

## Required assets (baseline)

- App icon: `512x512 PNG`
- Feature graphic: `1024x500 PNG`
- Phone screenshots: at least 2 (current scaffold uses `1080x1920 PNG`)

## Repository scaffold

- Manifest: `assets/manifest.json`
- Source working files: `assets/source/play-store/`
- Submission exports: `assets/exports/play-store/`
- Validation script: `scripts/check-assets-manifest.py`

## Validate locally

```bash
scripts/check-assets-manifest.py
```

Current CI behavior:
- Fails when required placeholders are missing
- Warns when final exports are not yet added
- Verifies image dimensions when exports are present

## Human/design-owned items

- Final artwork and branding decisions
- Screenshot capture curation and copy polish
- Play listing localized creatives (if/when needed)
