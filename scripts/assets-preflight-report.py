#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from assets_manifest_lib import MANIFEST, load_manifest, rel, validate_files_and_dimensions, validate_schema


def build_markdown(summary: dict, rows: list[dict], schema_errors: list[str], errors: list[str], warnings: list[str]) -> str:
    lines: list[str] = []
    lines.append("# Asset pack preflight report")
    lines.append("")
    lines.append(f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}")
    lines.append(f"Manifest: `{summary['manifest']}`")
    lines.append(f"Platform: `{summary['platform']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Assets tracked: **{summary['asset_count']}**")
    lines.append(f"- Required assets: **{summary['required_count']}**")
    lines.append(f"- Exports present: **{summary['exports_present']}**")
    lines.append(f"- Placeholders present: **{summary['placeholders_present']}**")
    lines.append(f"- Errors: **{summary['errors']}**")
    lines.append(f"- Warnings: **{summary['warnings']}**")
    lines.append("")

    if schema_errors or errors:
        lines.append("## Blocking issues")
        lines.append("")
        for issue in schema_errors + errors:
            lines.append(f"- [ ] {issue}")
        lines.append("")

    if warnings:
        lines.append("## Non-blocking warnings")
        lines.append("")
        for warning in warnings:
            lines.append(f"- [ ] {warning}")
        lines.append("")

    lines.append("## Required file checklist")
    lines.append("")
    for row in rows:
        if row["required"]:
            export_mark = "x" if row["export_exists"] else " "
            placeholder_mark = "x" if row["placeholder_exists"] else " "
            lines.append(f"- **{row['id']}**")
            lines.append(f"  - [{placeholder_mark}] Placeholder `{row['placeholder']}`")
            lines.append(f"  - [{export_mark}] Export `{row['export']}`")
    lines.append("")

    lines.append("## Full inventory")
    lines.append("")
    for row in rows:
        req = "required" if row["required"] else "optional"
        rec = "recommended" if row["recommended"] else "not-recommended"
        lines.append(f"- `{row['id']}` — {req}, {rec}, status: `{row['status']}`")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Markdown/JSON preflight report for Play Store asset pack")
    parser.add_argument("--out", default="build/assets-preflight-report.md", help="output markdown report path")
    parser.add_argument("--json-out", default="build/assets-preflight-report.json", help="output JSON report path")
    args = parser.parse_args()

    manifest = load_manifest(MANIFEST)

    schema_errors = validate_schema(manifest)
    errors, warnings, rows = validate_files_and_dimensions(manifest)

    required_rows = [r for r in rows if r["required"]]
    summary = {
        "manifest": rel(MANIFEST),
        "platform": manifest.get("platform", "unknown"),
        "asset_count": len(rows),
        "required_count": len(required_rows),
        "exports_present": sum(1 for r in rows if r["export_exists"]),
        "placeholders_present": sum(1 for r in rows if r["placeholder_exists"]),
        "errors": len(schema_errors) + len(errors),
        "warnings": len(warnings),
        "ok": len(schema_errors) + len(errors) == 0,
    }

    payload = {
        "summary": summary,
        "schema_errors": schema_errors,
        "errors": errors,
        "warnings": warnings,
        "assets": rows,
    }

    markdown = build_markdown(summary, rows, schema_errors, errors, warnings)

    for out_path, content in (
        (args.out, markdown),
        (args.json_out, json.dumps(payload, indent=2)),
    ):
        parent = "/".join(out_path.split("/")[:-1])
        if parent:
            import os

            os.makedirs(parent, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Wrote {args.out}")
    print(f"Wrote {args.json_out}")

    if summary["ok"]:
        print("Asset preflight: PASS")
        return 0

    print("Asset preflight: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
