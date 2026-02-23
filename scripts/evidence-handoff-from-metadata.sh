#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <release-metadata.txt> [run_url_override]" >&2
  exit 1
fi

META_FILE="$1"
RUN_URL_OVERRIDE="${2:-}"

if [[ ! -f "$META_FILE" ]]; then
  echo "Metadata file not found: $META_FILE" >&2
  exit 1
fi

value() {
  local key="$1"
  grep -E "^${key}=" "$META_FILE" | head -n1 | cut -d'=' -f2-
}

version="$(value version)"
version_code="$(value versionCode)"
previous_tag="$(value previous_tag)"
previous_version_code="$(value previous_versionCode)"
sha="$(value sha)"
aab_sha256="$(value aab_sha256)"
release_status="$(value release_status)"
upload_requested="$(value upload_requested)"
operator="$(value actor)"
run_attempt="$(value run_attempt)"
run_url="${RUN_URL_OVERRIDE:-$(value run_url)}"

cat <<EOF
## Release identity
- Date/UTC: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- Operator: ${operator}
- Target commit SHA: ${sha}
- Version (\`VERSION\`/\`versionName\`): ${version}
- \`versionCode\`: ${version_code}
- Previous tag: ${previous_tag}
- Previous \`versionCode\`: ${previous_version_code}

## Dry-run evidence (required)
- Workflow URL (dispatch, \`upload_enabled=false\`): ${run_url}
- Result: pass/fail
- \`aab_sha256\` from metadata: ${aab_sha256}
- \`run_attempt\`: ${run_attempt}

## Upload run evidence
- Workflow URL (tag-triggered): ${run_url}
- Result: pass/fail
- \`release_status\` used: ${release_status}
- Upload requested = true (yes/no): ${upload_requested}
EOF
