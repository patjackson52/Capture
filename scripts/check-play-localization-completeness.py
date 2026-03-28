#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from assets_manifest_lib import MANIFEST, load_manifest, load_required_asset_matrix, rel


def fail(msg: str) -> None:
    print(f"::error::{msg}")


def warn(msg: str) -> None:
    print(f"::warning::{msg}")


def required_locales(manifest: dict[str, Any], matrix: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    locales = manifest.get("locales", [])
    if isinstance(locales, list):
        out.update(locale for locale in locales if isinstance(locale, str) and locale.strip())

    default_locale = manifest.get("defaultLocale")
    if isinstance(default_locale, str) and default_locale.strip():
        out.add(default_locale)

    slots = matrix.get("slots", [])
    if isinstance(slots, list):
        for slot in slots:
            if not isinstance(slot, dict):
                continue
            locale = slot.get("locale")
            if isinstance(locale, str) and locale not in {"all", "default"}:
                out.add(locale)
    return out


def required_screenshot_slot_keys(matrix: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    slots = matrix.get("slots", [])
    if not isinstance(slots, list):
        return out
    for slot in slots:
        if not isinstance(slot, dict):
            continue
        slot_key = slot.get("slotKey")
        required = bool(slot.get("required", False))
        if isinstance(slot_key, str) and "screenshot" in slot_key and required:
            out.add(slot_key)
    return out


def load_templates(manifest: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None, str | None]:
    ref = manifest.get("playListingMetadataTemplates")
    if not isinstance(ref, dict):
        return None, None, "manifest.playListingMetadataTemplates is missing"

    path = ref.get("path")
    if not isinstance(path, str) or not path.strip():
        return None, None, "manifest.playListingMetadataTemplates.path is missing"

    abs_path = os.path.join(os.path.dirname(os.path.dirname(MANIFEST)), path)
    if not os.path.isfile(abs_path):
        return path, None, f"metadata templates file not found: {path}"

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as ex:  # noqa: BLE001
        return path, None, f"failed to parse metadata templates JSON ({path}): {ex}"

    if not isinstance(payload, dict):
        return path, None, f"metadata templates root must be object: {path}"

    return path, payload, None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Play listing localization completeness against manifest + required matrix"
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable report")
    args = parser.parse_args()

    try:
        manifest = load_manifest(MANIFEST)
        matrix = load_required_asset_matrix(manifest)
    except Exception as ex:  # noqa: BLE001
        fail(f"Unable to load manifest/matrix: {ex}")
        return 1

    template_path, templates, load_err = load_templates(manifest)
    if load_err:
        fail(load_err)
        return 1

    assert templates is not None
    locales_obj = templates.get("locales")
    if not isinstance(locales_obj, dict):
        fail("play listing metadata templates: 'locales' must be an object")
        return 1

    required = required_locales(manifest, matrix)
    required_slots = required_screenshot_slot_keys(matrix)

    errors: list[str] = []
    warnings: list[str] = []

    coverage: dict[str, Any] = {}

    for locale in sorted(required):
        entry = locales_obj.get(locale)
        coverage[locale] = {
            "present": isinstance(entry, dict),
            "shortDescription": False,
            "fullDescription": False,
            "requiredScreenshotSlots": sorted(required_slots),
            "captionSlotsPresent": [],
        }
        if not isinstance(entry, dict):
            errors.append(f"missing metadata template locale: {locale}")
            continue

        short_desc = entry.get("shortDescription")
        full_desc = entry.get("fullDescription")
        captions = entry.get("screenshotCaptions")

        if isinstance(short_desc, str) and short_desc.strip():
            coverage[locale]["shortDescription"] = True
        else:
            errors.append(f"{locale}: shortDescription is missing/empty")

        if isinstance(full_desc, str) and full_desc.strip():
            coverage[locale]["fullDescription"] = True
        else:
            errors.append(f"{locale}: fullDescription is missing/empty")

        if not isinstance(captions, dict):
            errors.append(f"{locale}: screenshotCaptions must be an object")
            continue

        for slot_key in sorted(required_slots):
            values = captions.get(slot_key)
            if not isinstance(values, list) or len(values) == 0:
                errors.append(f"{locale}: screenshotCaptions.{slot_key} must include at least 1 caption")
                continue
            non_empty = [v for v in values if isinstance(v, str) and v.strip()]
            if not non_empty:
                errors.append(f"{locale}: screenshotCaptions.{slot_key} has no non-empty captions")
                continue
            coverage[locale]["captionSlotsPresent"].append(slot_key)

    for locale in locales_obj.keys():
        if locale not in required:
            warnings.append(f"metadata locale '{locale}' is present but not currently required")

    for issue in errors:
        fail(issue)
    for note in warnings:
        warn(note)

    summary = {
        "manifest": rel(MANIFEST),
        "metadataTemplates": template_path,
        "requiredLocales": sorted(required),
        "requiredScreenshotSlots": sorted(required_slots),
        "errors": len(errors),
        "warnings": len(warnings),
        "ok": len(errors) == 0,
    }

    if args.json:
        print(json.dumps({"summary": summary, "coverage": coverage}, indent=2))

    if errors:
        print(f"Localization completeness check failed ({len(errors)} issue(s)).")
        return 1

    print("Localization completeness check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
