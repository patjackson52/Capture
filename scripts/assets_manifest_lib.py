#!/usr/bin/env python3
"""Shared utilities for Play Store asset manifest validation/preflight."""

from __future__ import annotations

import json
import os
import struct
from typing import Any

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MANIFEST = os.path.join(ROOT, "assets", "manifest.json")

SUPPORTED_FORMATS = {"png", "jpg", "jpeg"}


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def load_manifest(path: str = MANIFEST) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a JSON object")
    return data


def _manifest_matrix_abs(manifest: dict[str, Any]) -> str | None:
    matrix = manifest.get("requiredAssetMatrix")
    if not isinstance(matrix, dict):
        return None
    path = matrix.get("path")
    if not isinstance(path, str) or not path.strip():
        return None
    return os.path.join(ROOT, path)


def load_required_asset_matrix(manifest: dict[str, Any]) -> dict[str, Any]:
    matrix_abs = _manifest_matrix_abs(manifest)
    if not matrix_abs:
        raise ValueError("manifest.requiredAssetMatrix.path is missing")
    with open(matrix_abs, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("required asset matrix root must be a JSON object")
    return data


def png_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        sig = f.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            raise ValueError("invalid PNG signature")
        _len = f.read(4)
        chunk = f.read(4)
        if chunk != b"IHDR":
            raise ValueError("missing IHDR")
        w, h = struct.unpack(">II", f.read(8))
        return w, h


def jpeg_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        if f.read(2) != b"\xff\xd8":
            raise ValueError("invalid JPEG signature")
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while True:
            marker_start = f.read(1)
            if not marker_start:
                raise ValueError("unexpected EOF")
            if marker_start != b"\xff":
                continue
            marker = f.read(1)
            while marker == b"\xff":
                marker = f.read(1)
            if not marker:
                raise ValueError("unexpected EOF")
            marker_value = marker[0]
            if marker_value in sof:
                _len = struct.unpack(">H", f.read(2))[0]
                _precision = f.read(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            seg_len = struct.unpack(">H", f.read(2))[0]
            f.seek(seg_len - 2, os.SEEK_CUR)


def image_size(path: str, fmt: str) -> tuple[int, int]:
    normalized = fmt.lower()
    if normalized == "png":
        return png_size(path)
    if normalized in ("jpg", "jpeg"):
        return jpeg_size(path)
    raise ValueError(f"unsupported format for dimension check: {fmt}")


def _require_type(
    out_errors: list[str],
    where: str,
    obj: dict[str, Any],
    key: str,
    expected: type,
) -> Any:
    value = obj.get(key)
    if value is None:
        out_errors.append(f"{where}: missing required field '{key}'")
        return None
    if not isinstance(value, expected):
        out_errors.append(f"{where}: field '{key}' must be {expected.__name__}")
        return None
    return value


def _validate_required_asset_matrix_schema(
    manifest: dict[str, Any], errors: list[str]
) -> tuple[set[str], set[str], dict[str, dict[str, Any]]]:
    matrix_slot_keys: set[str] = set()
    matrix_locales: set[str] = set()
    slot_rules: dict[str, dict[str, Any]] = {}

    matrix_ref = _require_type(errors, "manifest", manifest, "requiredAssetMatrix", dict)
    if not isinstance(matrix_ref, dict):
        return matrix_slot_keys, matrix_locales, slot_rules

    matrix_path = _require_type(errors, "manifest.requiredAssetMatrix", matrix_ref, "path", str)
    _require_type(errors, "manifest.requiredAssetMatrix", matrix_ref, "version", str)

    if not isinstance(matrix_path, str):
        return matrix_slot_keys, matrix_locales, slot_rules

    matrix_abs = os.path.join(ROOT, matrix_path)
    if not os.path.isfile(matrix_abs):
        errors.append(f"manifest.requiredAssetMatrix.path does not exist: {matrix_path}")
        return matrix_slot_keys, matrix_locales, slot_rules

    try:
        with open(matrix_abs, "r", encoding="utf-8") as f:
            matrix = json.load(f)
    except Exception as ex:  # noqa: BLE001
        errors.append(f"manifest.requiredAssetMatrix.path failed to parse JSON ({matrix_path}): {ex}")
        return matrix_slot_keys, matrix_locales, slot_rules

    if not isinstance(matrix, dict):
        errors.append(f"required asset matrix must be an object: {matrix_path}")
        return matrix_slot_keys, matrix_locales, slot_rules

    _require_type(errors, "requiredAssetMatrix", matrix, "schemaVersion", int)
    _require_type(errors, "requiredAssetMatrix", matrix, "platform", str)

    slots = _require_type(errors, "requiredAssetMatrix", matrix, "slots", list)
    if not isinstance(slots, list):
        return matrix_slot_keys, matrix_locales, slot_rules

    for i, slot in enumerate(slots):
        where = f"requiredAssetMatrix.slots[{i}]"
        if not isinstance(slot, dict):
            errors.append(f"{where}: entry must be an object")
            continue

        slot_key = _require_type(errors, where, slot, "slotKey", str)
        _require_type(errors, where, slot, "displayName", str)
        locale = _require_type(errors, where, slot, "locale", str)
        _require_type(errors, where, slot, "deviceType", str)
        min_count = _require_type(errors, where, slot, "minCount", int)
        max_count = _require_type(errors, where, slot, "maxCount", int)

        if isinstance(slot_key, str):
            matrix_slot_keys.add(slot_key)
            slot_rules[slot_key] = {
                "minCount": min_count if isinstance(min_count, int) else None,
                "maxCount": max_count if isinstance(max_count, int) else None,
                "required": bool(slot.get("required", False)),
            }
        if isinstance(locale, str):
            matrix_locales.add(locale)

    return matrix_slot_keys, matrix_locales, slot_rules


def validate_schema(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    _require_type(errors, "manifest", manifest, "schemaVersion", int)
    _require_type(errors, "manifest", manifest, "platform", str)
    _require_type(errors, "manifest", manifest, "defaultLocale", str)

    locales = _require_type(errors, "manifest", manifest, "locales", list)
    if isinstance(locales, list):
        for i, locale in enumerate(locales):
            if not isinstance(locale, str) or not locale.strip():
                errors.append(f"manifest.locales[{i}] must be a non-empty string")

    global_criteria = _require_type(errors, "manifest", manifest, "acceptanceCriteria", list)
    if isinstance(global_criteria, list):
        for i, entry in enumerate(global_criteria):
            if not isinstance(entry, str) or not entry.strip():
                errors.append(f"manifest.acceptanceCriteria[{i}] must be a non-empty string")

    matrix_slot_keys, matrix_locales, slot_rules = _validate_required_asset_matrix_schema(manifest, errors)

    assets = _require_type(errors, "manifest", manifest, "assets", list)
    if not isinstance(assets, list):
        return errors

    slot_counts: dict[str, int] = {}

    for i, item in enumerate(assets):
        where = f"assets[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: entry must be an object")
            continue

        _require_type(errors, where, item, "id", str)
        _require_type(errors, where, item, "slotKey", str)
        _require_type(errors, where, item, "export", str)
        _require_type(errors, where, item, "placeholder", str)

        slot_key = item.get("slotKey")
        if isinstance(slot_key, str):
            slot_counts[slot_key] = slot_counts.get(slot_key, 0) + 1
            if matrix_slot_keys and slot_key not in matrix_slot_keys:
                errors.append(f"{where}: slotKey '{slot_key}' is not present in requiredAssetMatrix.slots")

        fmt = _require_type(errors, where, item, "format", str)
        if isinstance(fmt, str) and fmt.lower() not in SUPPORTED_FORMATS:
            errors.append(f"{where}: unsupported format '{fmt}'")

        dimensions = _require_type(errors, where, item, "dimensions", dict)
        if isinstance(dimensions, dict):
            width = _require_type(errors, f"{where}.dimensions", dimensions, "width", int)
            height = _require_type(errors, f"{where}.dimensions", dimensions, "height", int)
            if isinstance(width, int) and width <= 0:
                errors.append(f"{where}.dimensions.width must be > 0")
            if isinstance(height, int) and height <= 0:
                errors.append(f"{where}.dimensions.height must be > 0")

        _require_type(errors, where, item, "required", bool)
        _require_type(errors, where, item, "recommended", bool)

        locale = _require_type(errors, where, item, "locale", str)
        if isinstance(locale, str) and locale not in {"default", "all"}:
            manifest_locales = manifest.get("locales", [])
            if isinstance(manifest_locales, list) and locale not in manifest_locales:
                errors.append(f"{where}: locale '{locale}' must be one of manifest.locales or default/all")

        if isinstance(locale, str) and matrix_locales and locale not in {"default", "all"} and locale not in matrix_locales:
            errors.append(f"{where}: locale '{locale}' missing from requiredAssetMatrix.slots locales")

        criteria = _require_type(errors, where, item, "acceptanceCriteria", list)
        if isinstance(criteria, list):
            for j, entry in enumerate(criteria):
                if not isinstance(entry, str) or not entry.strip():
                    errors.append(f"{where}.acceptanceCriteria[{j}] must be a non-empty string")

    for slot_key, rules in slot_rules.items():
        count = slot_counts.get(slot_key, 0)
        min_count = rules.get("minCount")
        max_count = rules.get("maxCount")
        if isinstance(min_count, int) and count < min_count:
            errors.append(
                f"requiredAssetMatrix slot '{slot_key}' requires at least {min_count} manifest asset(s), found {count}"
            )
        if isinstance(max_count, int) and max_count >= 0 and count > max_count:
            errors.append(
                f"requiredAssetMatrix slot '{slot_key}' allows at most {max_count} manifest asset(s), found {count}"
            )

    return errors


def validate_files_and_dimensions(manifest: dict[str, Any]) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []

    assets = manifest.get("assets", [])
    if not isinstance(assets, list):
        return ["manifest.assets must be a list"], warnings, rows

    for item in assets:
        if not isinstance(item, dict):
            continue
        asset_id = item.get("id", "<unknown>")
        export_rel = item.get("export")
        placeholder_rel = item.get("placeholder")
        required = bool(item.get("required", True))

        if not isinstance(export_rel, str) or not isinstance(placeholder_rel, str):
            errors.append(f"{asset_id}: missing export/placeholder path")
            continue

        dimensions = item.get("dimensions", {})
        width_expected = dimensions.get("width") if isinstance(dimensions, dict) else None
        height_expected = dimensions.get("height") if isinstance(dimensions, dict) else None
        fmt = str(item.get("format", "")).lower()

        export_path = os.path.join(ROOT, export_rel)
        placeholder_path = os.path.join(ROOT, placeholder_rel)

        placeholder_exists = os.path.isfile(placeholder_path)
        export_exists = os.path.isfile(export_path)
        status = "ok"

        if not placeholder_exists:
            errors.append(f"{asset_id}: missing placeholder {placeholder_rel}")
            status = "error"

        if export_exists and fmt and isinstance(width_expected, int) and isinstance(height_expected, int):
            try:
                w_act, h_act = image_size(export_path, fmt)
                if (w_act, h_act) != (width_expected, height_expected):
                    errors.append(
                        f"{asset_id}: wrong dimensions for {export_rel} (got {w_act}x{h_act}, expected {width_expected}x{height_expected})"
                    )
                    status = "error"
            except Exception as ex:  # noqa: BLE001
                errors.append(f"{asset_id}: unable to validate {export_rel}: {ex}")
                status = "error"
        elif required and not export_exists:
            warnings.append(f"{asset_id}: required export not present yet ({export_rel}); placeholder is present")
            if status != "error":
                status = "missing-required-export"

        rows.append(
            {
                "id": asset_id,
                "slotKey": item.get("slotKey"),
                "required": required,
                "recommended": bool(item.get("recommended", False)),
                "export": export_rel,
                "placeholder": placeholder_rel,
                "export_exists": export_exists,
                "placeholder_exists": placeholder_exists,
                "status": status,
            }
        )

    return errors, warnings, rows
