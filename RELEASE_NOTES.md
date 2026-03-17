# Capture v0.1.0-alpha.1 Release Notes

**Release date:** February 2026
**Package:** `dev.patrickjackson.capture`
**Min SDK:** 26 (Android 8.0) | **Target SDK:** 35 (Android 15)

---

## What is Capture?

Capture is a fast, privacy-first Android utility for saving notes, images, and files to a local directory on your device. No accounts, no cloud sync, no data collection — everything stays on your phone.

---

## Highlights

### Core features

- **Quick note capture** — Open the app and start typing. Notes are saved instantly to your chosen directory.
- **Share sheet integration** — Share text, images, or files from any app directly into Capture.
- **Text selection capture** — Select text anywhere on your device and send it to Capture via the text-selection menu.
- **Folder picker** — Choose any local directory as your save destination.
- **Obsidian-style embeds** — Attachments are embedded in note bodies using `![[filename]]` syntax, compatible with Obsidian and similar tools.

### Developer & quality

- **In-app debug log viewer** — Built-in log screen for troubleshooting.
- **Modern stack** — Built with Jetpack Compose, Material 3, and edge-to-edge display support.
- **CI/CD pipeline** — GitHub Actions for automated builds, unit tests, and Play Store internal track deployment.
- **Release governance** — Signing prerequisites, release checklists, and evidence templates for auditable releases.

---

## Known limitations

- This is an **alpha** release — expect rough edges.
- No cloud sync or backup (by design for this version).
- Unsigned release builds unless signing secrets are configured in CI.

---

## Privacy

Capture does not collect, transmit, or share any personal data. All content is stored locally on your device. No analytics or advertising SDKs are included. See [Privacy Policy](docs/privacy-policy.md) for details.
