#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os

from assets_manifest_lib import MANIFEST, load_manifest, load_required_asset_matrix, rel


def _required_slots(matrix: dict) -> list[dict]:
    slots = matrix.get("slots", [])
    if not isinstance(slots, list):
        return []
    out = [slot for slot in slots if isinstance(slot, dict) and bool(slot.get("required", False))]
    out.sort(key=lambda s: (str(s.get("locale", "")), str(s.get("slotKey", ""))))
    return out


def _assets_by_slot(manifest: dict) -> dict[str, list[dict]]:
    mapping: dict[str, list[dict]] = {}
    assets = manifest.get("assets", [])
    if not isinstance(assets, list):
        return mapping
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        key = asset.get("slotKey")
        if not isinstance(key, str):
            continue
        mapping.setdefault(key, []).append(asset)
    return mapping


def build_markdown(release_label: str, manifest: dict, matrix: dict) -> str:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    lines: list[str] = []
    lines.append(f"# Release candidate assets checklist — {release_label}")
    lines.append("")
    lines.append(f"Generated (UTC): {now}")
    lines.append(f"Manifest: `{rel(MANIFEST)}`")
    matrix_path = (manifest.get("requiredAssetMatrix") or {}).get("path", "<missing>")
    lines.append(f"Required matrix: `{matrix_path}`")
    lines.append("")

    lines.append("## Global gates")
    lines.append("")
    lines.append("- [ ] `scripts/check-assets-manifest.py` passes")
    lines.append("- [ ] `scripts/check-play-localization-completeness.py` passes")
    lines.append("- [ ] `scripts/assets-preflight-report.py` generated and attached")
    lines.append("- [ ] Brand/legal approvals attached for this release candidate")
    lines.append("")

    by_slot = _assets_by_slot(manifest)
    required_slots = _required_slots(matrix)

    lines.append("## Required slot checklist")
    lines.append("")
    for slot in required_slots:
        slot_key = slot.get("slotKey", "<missing-slot>")
        display_name = slot.get("displayName", "<unnamed>")
        locale = slot.get("locale", "default")
        min_count = slot.get("minCount", "?")
        max_count = slot.get("maxCount", "?")
        lines.append(
            f"- [ ] **{display_name}** (`{slot_key}`) — locale `{locale}`, required count `{min_count}..{max_count}`"
        )
        for asset in by_slot.get(slot_key, []):
            asset_id = asset.get("id", "<missing-id>")
            export_path = asset.get("export", "<missing-export>")
            placeholder_path = asset.get("placeholder", "<missing-placeholder>")
            lines.append(f"  - [ ] `{asset_id}` export ready: `{export_path}`")
            lines.append(f"  - [ ] `{asset_id}` placeholder retained/audited: `{placeholder_path}`")
    lines.append("")

    lines.append("## Localization handoff")
    lines.append("")
    for locale in manifest.get("locales", []):
        if isinstance(locale, str):
            lines.append(f"- [ ] Locale `{locale}` short/full descriptions finalized")
            lines.append(f"- [ ] Locale `{locale}` screenshot captions reviewed")
    lines.append("")

    lines.append("## Sign-off")
    lines.append("")
    lines.append("- [ ] Product owner approval")
    lines.append("- [ ] QA approval")
    lines.append("- [ ] Release manager approval")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate RC assets checklist markdown from manifest + required matrix")
    parser.add_argument("--release", default="rc", help="release label used in checklist title")
    parser.add_argument(
        "--out",
        default="build/release-candidate-assets-checklist.md",
        help="output markdown path",
    )
    args = parser.parse_args()

    manifest = load_manifest(MANIFEST)
    matrix = load_required_asset_matrix(manifest)

    markdown = build_markdown(args.release, manifest, matrix)

    out_path = args.out
    out_parent = os.path.dirname(out_path)
    if out_parent:
        os.makedirs(out_parent, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
