# Required checks for branch protection (main)

This repository uses GitHub Actions for CI.

Enforce these required status checks on `main`:

- `build-and-test` (job from workflow **Android CI**)

Notes:
- GitHub may display the context as `Android CI / build-and-test` in some UIs.
- Protect against API merges bypassing checks by requiring status checks before merge.
