#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

failures=0

check_exists() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "::error file=${path}::Missing referenced file: ${path}"
    failures=$((failures + 1))
  fi
}

# Enforce anchor docs for first rollout pack.
required_docs=(
  "docs/android-first-internal-rollout-execution-pack.md"
  "docs/release-runbook-basics.md"
  "docs/release-governance-checklist.md"
  "docs/release-verification-evidence-template.md"
  "docs/android-internal-release-run-now-checklist.md"
  "docs/android-internal-release-drill-pack.md"
  "docs/required-checks.md"
)

for d in "${required_docs[@]}"; do
  check_exists "$d"
done

# Validate docs/*.md references found in key docs and workflows.
sources=(
  "docs/android-first-internal-rollout-execution-pack.md"
  "docs/release-runbook-basics.md"
  "docs/release-governance-checklist.md"
  "docs/required-checks.md"
  "docs/android-internal-release-run-now-checklist.md"
  "docs/android-internal-release-drill-pack.md"
  ".github/workflows/android-play-internal.yml"
  ".github/workflows/capture-release-baseline.yml"
  ".github/workflows/docs-link-check.yml"
)

for src in "${sources[@]}"; do
  while IFS= read -r ref; do
    check_exists "$ref"
  done < <(grep -Eo 'docs/[A-Za-z0-9._/-]+\.md' "$src" | sort -u)
done

if [[ "$failures" -gt 0 ]]; then
  echo "Found ${failures} missing docs reference(s)."
  exit 1
fi

echo "Docs link check passed."
