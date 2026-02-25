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

    assets = _require_type(errors, "manifest", manifest, "assets", list)
    if not isinstance(assets, list):
        return errors

    for i, item in enumerate(assets):
        where = f"assets[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: entry must be an object")
            continue

        _require_type(errors, where, item, "id", str)
        _require_type(errors, where, item, "export", str)
        _require_type(errors, where, item, "placeholder", str)

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

        criteria = _require_type(errors, where, item, "acceptanceCriteria", list)
        if isinstance(criteria, list):
            for j, entry in enumerate(criteria):
                if not isinstance(entry, str) or not entry.strip():
                    errors.append(f"{where}.acceptanceCriteria[{j}] must be a non-empty string")

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
