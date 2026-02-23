#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

failures=0

err() {
  local msg="$1"
  echo "::error::${msg}"
  failures=$((failures + 1))
}

check_contains() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if ! grep -Fq "$pattern" "$file"; then
    err "Missing ${label} in ${file}: ${pattern}"
  fi
}

# Required checks doc must stay aligned with workflow + job contexts.
check_contains "docs/required-checks.md" "Android CI / build-and-test" "required check context"
check_contains "docs/required-checks.md" "Docs Link Check / check-doc-links" "required check context"
check_contains "docs/required-checks.md" "Android Play Internal CD / internal-release" "recommended release check context"

# Verify workflow and job identifiers exist for the contexts above.
check_contains ".github/workflows/android-ci.yml" "name: Android CI" "workflow name"
check_contains ".github/workflows/android-ci.yml" "build-and-test:" "job id"

check_contains ".github/workflows/docs-link-check.yml" "name: Docs Link Check" "workflow name"
check_contains ".github/workflows/docs-link-check.yml" "check-doc-links:" "job id"

check_contains ".github/workflows/android-play-internal.yml" "name: Android Play Internal CD" "workflow name"
check_contains ".github/workflows/android-play-internal.yml" "internal-release:" "job id"

# Evidence template should preserve operator-critical fields referenced by runbooks.
for field in \
  "## Release identity" \
  "## Dry-run evidence (required)" \
  "## Upload run evidence" \
  "## Play Console verification" \
  "## QA sign-off" \
  "## Go/No-go" \
  "## Rollback readiness"; do
  check_contains "docs/release-verification-evidence-template.md" "$field" "evidence template section"
done

# First rollout execution pack must continue to point at governance + runbook + evidence docs.
for doc in \
  "docs/release-governance-checklist.md" \
  "docs/release-runbook-basics.md" \
  "docs/release-verification-evidence-template.md" \
  "docs/android-internal-release-run-now-checklist.md"; do
  check_contains "docs/android-first-internal-rollout-execution-pack.md" "$doc" "execution pack reference"
done

# Play CD workflow must continue to emit evidence-friendly metadata.
for field in \
  "run_url=" \
  "build/evidence-prefill.md" \
  "run_attempt="; do
  check_contains ".github/workflows/android-play-internal.yml" "$field" "workflow evidence field"
done

if [[ "$failures" -gt 0 ]]; then
  echo "Release readiness consistency check failed (${failures} issue(s))."
  exit 1
fi

echo "Release readiness consistency check passed."
