#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "assets" / "manifest.json"
DEFAULT_OUT_ROOT = ROOT / "build" / "play-asset-handoff"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def safe_release_name(value: str) -> str:
    return "".join(c for c in value if c.isalnum() or c in {"-", "_", "."})


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def checklist_markdown(release_name: str, manifest: dict, bundle_rel: str) -> str:
    assets = manifest.get("assets", [])
    required_assets = [a for a in assets if isinstance(a, dict) and a.get("required")]

    lines: list[str] = []
    lines.append(f"# Play asset handoff checklist — {release_name}")
    lines.append("")
    lines.append(f"Generated (UTC): {dt.datetime.now(dt.timezone.utc).isoformat()}")
    lines.append(f"Bundle root: `{bundle_rel}`")
    lines.append("")
    lines.append("## Producer checklist")
    lines.append("")
    lines.append("- [ ] Confirm release tag/version and locale scope")
    lines.append("- [ ] Replace placeholder files with final exports")
    lines.append("- [ ] Run `scripts/check-assets-manifest.py`")
    lines.append("- [ ] Run `scripts/check-play-localization-completeness.py`")
    lines.append("- [ ] Run `scripts/assets-preflight-report.py`")
    lines.append("- [ ] Attach reviewer sign-off and legal/brand approval evidence")
    lines.append("")
    lines.append("## Required assets to hand off")
    lines.append("")

    for asset in required_assets:
        asset_id = asset.get("id", "<missing-id>")
        slot_key = asset.get("slotKey", "<missing-slot>")
        export_path = asset.get("export", "<missing-export>")
        lines.append(f"- [ ] `{asset_id}` ({slot_key}) → `{export_path}`")

    lines.append("")
    lines.append("## Reviewer acceptance")
    lines.append("")
    lines.append("- [ ] Dimensions/format validated")
    lines.append("- [ ] Copy + localization reviewed")
    lines.append("- [ ] Compliance (privacy/safety/branding) approved")
    lines.append("- [ ] Final package uploaded to release ticket")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Play Store asset handoff bundle skeleton")
    parser.add_argument("--release", help="release label (default: UTC timestamp)")
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT), help="root output directory")
    parser.add_argument("--zip", action="store_true", help="also create a zip archive")
    args = parser.parse_args()

    manifest = load_manifest()

    default_release = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    release_name = safe_release_name(args.release or f"release-{default_release}")
    if not release_name:
        raise SystemExit("invalid release label")

    out_root = Path(args.out_root)
    bundle_dir = out_root / release_name

    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)

    # Skeleton directories expected by handoff process.
    for rel_dir in [
        "assets/exports/play-store/icons",
        "assets/exports/play-store/graphics",
        "assets/exports/play-store/screenshots/phone",
        "assets/exports/play-store/screenshots/tablet",
        "evidence",
        "approvals",
        "notes",
    ]:
        ensure_dir(bundle_dir / rel_dir)

    # Include source-of-truth metadata.
    write_file(bundle_dir / "assets/manifest.json", json.dumps(manifest, indent=2) + "\n")

    matrix_ref = (manifest.get("requiredAssetMatrix") or {}).get("path")
    if isinstance(matrix_ref, str) and matrix_ref.strip():
        matrix_src = ROOT / matrix_ref
        if matrix_src.exists():
            write_file(bundle_dir / matrix_ref, matrix_src.read_text(encoding="utf-8"))

    metadata_ref = (manifest.get("playListingMetadataTemplates") or {}).get("path")
    if isinstance(metadata_ref, str) and metadata_ref.strip():
        metadata_src = ROOT / metadata_ref
        if metadata_src.exists():
            write_file(bundle_dir / metadata_ref, metadata_src.read_text(encoding="utf-8"))

    write_file(
        bundle_dir / "CHECKLIST.md",
        checklist_markdown(release_name, manifest, str(bundle_dir.relative_to(ROOT))),
    )

    write_file(
        bundle_dir / "README.md",
        "\n".join(
            [
                f"# Play asset handoff bundle ({release_name})",
                "",
                "This directory is generated as a release handoff skeleton.",
                "Populate exported images, evidence, and approvals before final upload.",
                "",
                "Run before handoff:",
                "- scripts/check-assets-manifest.py",
                "- scripts/assets-preflight-report.py",
                "",
            ]
        ),
    )

    zip_path = None
    if args.zip:
        ensure_dir(out_root)
        zip_base = out_root / release_name
        zip_path = shutil.make_archive(str(zip_base), "zip", root_dir=bundle_dir)

    print(f"Generated bundle skeleton: {bundle_dir}")
    if zip_path:
        print(f"Generated zip: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
