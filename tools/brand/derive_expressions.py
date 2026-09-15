#!/usr/bin/env python3
r"""Turn the chosen ComfyUI otter expression renders (happy, idle, alert) into
transparent HoltOS brand files without redrawing anything: cut the flat dark
background out, crop to a square and resize, with derive_logo.py's matte.

  C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe tools/brand/derive_expressions.py --root archiso/airootfs --preview <png>

The renders live in docs/design-references/ (Liam's picks, 2026-09-15). Design
comes only from ComfyUI renders (Liam, 2026-09-14); this script only processes them.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_logo import crop_square, load_rgb, matte, to_image  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
RENDERS = {
    "happy": "docs/design-references/holtos-otter-happy-seed6101-2.png",
    "idle": "docs/design-references/holtos-otter-idle-seed6201-1.png",
    "alert": "docs/design-references/holtos-otter-alert-seed6301-2.png",
}
SIZES = (1024, 512)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Derive the HoltOS otter expression files.")
    parser.add_argument("--root", required=True, help="Root of archiso/airootfs")
    parser.add_argument("--preview", required=True, help="Output path for the preview PNG")
    args = parser.parse_args()

    out_dir = Path(args.root) / "usr" / "share" / "holtos" / "brand"
    out_dir.mkdir(parents=True, exist_ok=True)
    cutouts = []
    for name, rel in RENDERS.items():
        img = to_image(crop_square(matte(load_rgb(REPO / rel))))
        for size in SIZES:
            path = out_dir / f"holtos-otter-{name}-{size}.png"
            img.resize((size, size), Image.LANCZOS).save(str(path))
            print(f"Wrote {path}")
        cutouts.append(img)

    cell = 280
    canvas = Image.new("RGB", (cell * len(cutouts), cell * 2), (30, 30, 30))
    for row, bg in enumerate(((0x0D, 0x0B, 0x12), (0xF4, 0xEB, 0xFF))):
        for i, img in enumerate(cutouts):
            tile = Image.new("RGB", (cell - 16, cell - 16), bg)
            small = img.resize((cell - 40, cell - 40), Image.LANCZOS)
            tile.paste(small, (12, 12), small)
            canvas.paste(tile, (i * cell + 8, row * cell + 8))
    preview = Path(args.preview)
    preview.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(preview))
    print(f"Wrote preview {preview}")


if __name__ == "__main__":
    main()
