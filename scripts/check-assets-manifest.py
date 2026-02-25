#!/usr/bin/env python3
import json
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MANIFEST = os.path.join(ROOT, "assets", "manifest.json")


def png_size(path: str):
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


def jpeg_size(path: str):
    with open(path, "rb") as f:
        if f.read(2) != b"\xff\xd8":
            raise ValueError("invalid JPEG signature")
        while True:
            marker_start = f.read(1)
            if not marker_start:
                raise ValueError("unexpected EOF")
            if marker_start != b"\xff":
                continue
            marker = f.read(1)
            while marker == b"\xff":
                marker = f.read(1)
            if marker in [bytes([m]) for m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF)]:
                _len = struct.unpack(">H", f.read(2))[0]
                _precision = f.read(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            seg_len = struct.unpack(">H", f.read(2))[0]
            f.seek(seg_len - 2, os.SEEK_CUR)


def image_size(path: str, fmt: str):
    fmt = fmt.lower()
    if fmt == "png":
        return png_size(path)
    if fmt in ("jpg", "jpeg"):
        return jpeg_size(path)
    raise ValueError(f"unsupported format for dimension check: {fmt}")


def fail(msg: str):
    print(f"::error::{msg}")


def main():
    if not os.path.isfile(MANIFEST):
        fail(f"Missing manifest: {os.path.relpath(MANIFEST, ROOT)}")
        return 1

    with open(MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)

    failures = 0
    assets = data.get("assets", [])

    for item in assets:
        asset_id = item.get("id", "<unknown>")
        export_rel = item.get("export")
        placeholder_rel = item.get("placeholder")
        required = bool(item.get("required", True))

        if not export_rel or not placeholder_rel:
            fail(f"{asset_id}: manifest entry missing export/placeholder")
            failures += 1
            continue

        export_path = os.path.join(ROOT, export_rel)
        placeholder_path = os.path.join(ROOT, placeholder_rel)

        if not os.path.isfile(placeholder_path):
            fail(f"{asset_id}: missing placeholder {placeholder_rel}")
            failures += 1

        if os.path.isfile(export_path):
            fmt = item.get("format", "").lower()
            w_req = item.get("width")
            h_req = item.get("height")
            if fmt and w_req and h_req:
                try:
                    w_act, h_act = image_size(export_path, fmt)
                    if (w_act, h_act) != (w_req, h_req):
                        fail(f"{asset_id}: wrong dimensions for {export_rel} (got {w_act}x{h_act}, expected {w_req}x{h_req})")
                        failures += 1
                except Exception as e:
                    fail(f"{asset_id}: unable to validate {export_rel}: {e}")
                    failures += 1
        elif required:
            print(f"::warning::{asset_id}: export not present yet ({export_rel}); placeholder is present")

    if failures:
        print(f"Asset manifest check failed ({failures} issue(s)).")
        return 1

    print("Asset manifest check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
