# Play Store asset production workflow (Android)

This workflow defines **who does what** and what "done" means for listing assets.

## Roles

- **Product owner / release manager**
  - Confirms release scope, locales, and listing claims.
  - Owns handoff deadline and final Play Console upload checkpoint.
- **Design owner**
  - Produces icon/feature graphic/screenshot creative source files.
  - Ensures copy and visual hierarchy align with brand standards.
- **Capture operator (QA or release engineer)**
  - Captures raw screenshots from release-candidate build.
  - Sanitizes status bar/notifications and verifies UI correctness.
- **Localization reviewer**
  - Reviews locale-specific text overlays and listing copy fit.
- **Release reviewer (independent check)**
  - Runs validation scripts and signs off on ready-to-upload package.

## Source-of-truth artifacts

- `assets/manifest.json` — per-asset inventory + `slotKey` linkage.
- `assets/requirements/play-listing-required-asset-matrix.json` — machine-readable required slot matrix by locale/device type.
- `scripts/check-assets-manifest.py` — schema + file/dimension checks.
- `scripts/assets-preflight-report.py` — release preflight markdown/JSON outputs.
- `scripts/generate-play-asset-handoff-bundle.py` — handoff skeleton directory/zip generator.

## Workflow stages

1. **Plan scope**
   - Confirm release locales and targeted device classes.
   - Update matrix + manifest if slot requirements changed.
2. **Produce assets**
   - Design creates/updates source files under `assets/source/play-store/`.
   - Capture operator exports final PNG/JPG files into paths defined in `assets/manifest.json`.
3. **Validate package**
   - Run `scripts/check-assets-manifest.py`.
   - Run `scripts/assets-preflight-report.py` and review blocking issues.
4. **Prepare handoff**
   - Run `scripts/generate-play-asset-handoff-bundle.py --release <label> --zip`.
   - Attach checklist, evidence, and approvals in generated bundle.
5. **Final sign-off**
   - Release reviewer confirms done criteria (below).
   - Release manager marks assets ready for Play Console upload.

## Done criteria (release-blocking)

An asset pack is **done** only when all are true:

- [ ] Manifest schema validation passes with zero errors.
- [ ] Every required slot in the matrix has matching required assets in manifest (`slotKey` mapped).
- [ ] Every required manifest asset has a committed placeholder or final export at declared path.
- [ ] Any present export file matches declared dimensions + format.
- [ ] Preflight report generated and attached to release evidence (`build/assets-preflight-report.*`).
- [ ] Handoff bundle generated for the release and includes checklist + approvals.
- [ ] Independent reviewer sign-off recorded.

## Optional quality upgrades (non-blocking)

- Additional locale variants beyond baseline `en-US`.
- Tablet/large-screen screenshots when UX is intentionally supported.
- A/B creative variants tracked in a separate experiment brief.
