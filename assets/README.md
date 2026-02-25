# Assets scaffolding (Android / Play Store)

This directory tracks **store assets readiness** without committing final artwork.

## Layout

- `source/play-store/` — editable source files from design tools (SVG, Figma exports, layered files)
- `exports/play-store/` — final deliverable exports used for submission
- `manifest.json` — required asset inventory with expected dimensions/formats

## Workflow

1. Keep design source files under `source/play-store/`.
2. Export submission-ready files to the paths in `manifest.json`.
3. Run `scripts/check-assets-manifest.py` to validate placeholders and exported dimensions.

## Notes

- Placeholder markdown files are committed now so CI can confirm structure is intact.
- Replace placeholders with real images as launch assets are produced.
