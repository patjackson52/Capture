#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from assets_manifest_lib import MANIFEST, load_manifest, rel, validate_files_and_dimensions, validate_schema


def fail(msg: str):
    print(f"::error::{msg}")


def warn(msg: str):
    print(f"::warning::{msg}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Play Store assets manifest + scaffold files")
    parser.add_argument("--json", action="store_true", help="print machine-readable summary")
    args = parser.parse_args()

    try:
        manifest = load_manifest(MANIFEST)
    except FileNotFoundError:
        fail(f"Missing manifest: {rel(MANIFEST)}")
        return 1
    except Exception as ex:  # noqa: BLE001
        fail(f"Unable to load manifest: {ex}")
        return 1

    schema_errors = validate_schema(manifest)
    errors, warnings, rows = validate_files_and_dimensions(manifest)
    all_errors = [*schema_errors, *errors]

    for issue in schema_errors:
        fail(issue)
    for issue in errors:
        fail(issue)
    for note in warnings:
        warn(note)

    summary = {
        "manifest": rel(MANIFEST),
        "asset_count": len(rows),
        "errors": len(all_errors),
        "warnings": len(warnings),
        "ok": len(all_errors) == 0,
    }

    if args.json:
        print(json.dumps({"summary": summary, "assets": rows}, indent=2))

    if all_errors:
        print(f"Asset manifest check failed ({len(all_errors)} issue(s)).")
        return 1

    print("Asset manifest check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
