#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f VERSION ]] || [[ ! -f app/build.gradle.kts ]]; then
  echo "Run from Capture repo root (VERSION + app/build.gradle.kts required)." >&2
  exit 1
fi

VERSION_FILE="$(tr -d '[:space:]' < VERSION)"
VERSION_NAME="$(grep -E 'versionName\s*=\s*"' app/build.gradle.kts | head -n1 | sed -E 's/.*"([^"]+)".*/\1/')"
VERSION_CODE="$(grep -E 'versionCode\s*=\s*[0-9]+' app/build.gradle.kts | head -n1 | sed -E 's/.*=\s*([0-9]+).*/\1/')"

if [[ -z "$VERSION_FILE" || -z "$VERSION_NAME" || -z "$VERSION_CODE" ]]; then
  echo "Failed to parse VERSION/versionName/versionCode." >&2
  exit 1
fi

version_match="yes"
if [[ "$VERSION_FILE" != "$VERSION_NAME" ]]; then
  version_match="no"
fi

PREVIOUS_TAG="$(git tag -l 'v*' --sort=-version:refname | head -n1 || true)"
PREVIOUS_VERSION_CODE="unknown"
if [[ -n "$PREVIOUS_TAG" ]]; then
  PREVIOUS_VERSION_CODE="$(git show "$PREVIOUS_TAG":app/build.gradle.kts 2>/dev/null | grep -E 'versionCode\s*=\s*[0-9]+' | head -n1 | sed -E 's/.*=\s*([0-9]+).*/\1/' || true)"
  PREVIOUS_VERSION_CODE="${PREVIOUS_VERSION_CODE:-unknown}"
fi

printf "release_version=%s\n" "$VERSION_FILE"
printf "version_name=%s\n" "$VERSION_NAME"
printf "version_code=%s\n" "$VERSION_CODE"
printf "previous_tag=%s\n" "${PREVIOUS_TAG:-none}"
printf "previous_version_code=%s\n" "$PREVIOUS_VERSION_CODE"
printf "target_commit_sha=%s\n" "$(git rev-parse HEAD)"
printf "suggested_tag=v%s\n" "$VERSION_FILE"
printf "version_match=%s\n" "$version_match"

if [[ "$version_match" != "yes" ]]; then
  echo "warning=VERSION/versionName mismatch (VERSION=$VERSION_FILE versionName=$VERSION_NAME)"
fi

echo ""
echo "Run-now quick checklist"
if [[ "$version_match" = "yes" ]]; then
  echo "- [x] VERSION == versionName ($VERSION_FILE)"
else
  echo "- [ ] VERSION == versionName (fix before release)"
fi
echo "- [ ] Dry-run dispatch: upload_enabled=false release_status=draft"
echo "- [ ] Governance approvals collected (Eng + QA + Product)"
echo "- [ ] Tag and monitor upload run"
echo "- [ ] Complete evidence template + QA + GO/NO-GO"
