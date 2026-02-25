# Assets scaffolding (Android / Play Store)

This directory tracks **store assets readiness** without committing final artwork.

## Layout

- `source/play-store/` — editable source files from design tools (SVG, Figma exports, layered files)
- `exports/play-store/` — final deliverable exports used for submission
- `manifest.json` — asset inventory + schema metadata (required/recommended, dimensions, locale, acceptance criteria)
- `requirements/play-listing-required-asset-matrix.json` — required slot matrix (locale/device type/min/max) linked from the manifest

## Manifest schema highlights

Top-level fields:

- `schemaVersion` — manifest schema revision
- `platform` — currently `android-play-store`
- `defaultLocale` + `locales` — listing locale strategy
- `acceptanceCriteria` — global quality gate for all assets
- `requiredAssetMatrix.path` + `requiredAssetMatrix.version` — binds manifest entries to a machine-readable slot matrix file
- `playListingMetadataTemplates.path` + `playListingMetadataTemplates.version` — locale-ready short/full description + screenshot caption templates
- `assets[]` — per-file requirements

Per-asset required fields:

- `id`, `slotKey`, `export`, `placeholder`, `format`
- `dimensions.width`, `dimensions.height`
- `required`, `recommended`, `locale`
- `acceptanceCriteria[]`

Optional-but-useful fields:

- `type`, `group`, `notes`

## Workflow

1. Keep design source files under `source/play-store/`.
2. Export submission-ready files to the paths in `manifest.json`.
3. Run `scripts/check-assets-manifest.py` to validate schema, placeholders, and dimensions.
4. Run `scripts/check-play-localization-completeness.py` to verify required locales are fully scaffolded.
5. Run `scripts/assets-preflight-report.py` to generate checklist artifacts:
   - `build/assets-preflight-report.md`
   - `build/assets-preflight-report.json`

## Notes

- Placeholder markdown files are committed now so CI can confirm structure is intact.
- Replace placeholders with real images as launch assets are produced.
