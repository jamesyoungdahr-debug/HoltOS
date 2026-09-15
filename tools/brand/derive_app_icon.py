#!/usr/bin/env python3
r"""Turn a chosen ComfyUI app-icon render (a rounded glass tile with a neon rim on a black background) into HoltOS icon files without redrawing anything: find the tile, cut its rounded shape out of the background, keep the tile itself opaque, and resize.

derive_logo.py's background matte cannot be used here: the tile's inside is nearly as dark as the background and would turn transparent.

  C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe tools/brand/derive_app_icon.py --render <png> --name holtos-apps --root archiso/airootfs --preview <png>

Design comes only from ComfyUI renders (Liam, 2026-09-14); this script only processes them.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_logo import load_rgb, save_sizes, to_image  # noqa: E402

SIZES = [16, 22, 24, 32, 48, 64, 96, 128, 256, 512]


def tile_box(rgb: np.ndarray, threshold: float = 0.55) -> tuple[int, int, int, int]:
    """Square box (x0, y0, x1, y1) around the bright neon rim."""
    bright = rgb.max(axis=2) > threshold
    ys, xs = np.where(bright)
    if len(xs) == 0:
        raise SystemExit("no bright rim found in the render")
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    side = max(x1 - x0, y1 - y0) + 1
    pad = int(side * 0.01)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = side / 2 + pad
    h, w = rgb.shape[:2]
    return (
        max(int(round(cx - half)), 0),
        max(int(round(cy - half)), 0),
        min(int(round(cx + half)), w),
        min(int(round(cy + half)), h),
    )


def rounded_mask(size: int, radius_ratio: float = 0.22, scale: int = 4) -> Image.Image:
    """Anti-aliased rounded-square mask, drawn at 4x and scaled down."""
    big = Image.new("L", (size * scale, size * scale), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, size * scale - 1, size * scale - 1),
        radius=int(size * scale * radius_ratio),
        fill=255,
    )
    return big.resize((size, size), Image.LANCZOS)


def cut_tile(render: str, radius_ratio: float) -> Image.Image:
    """Crop the tile square and make everything outside its rounded shape transparent."""
    rgb = load_rgb(render)
    x0, y0, x1, y1 = tile_box(rgb)
    crop = rgb[y0:y1, x0:x1]
    side = min(crop.shape[0], crop.shape[1])
    crop = crop[:side, :side]
    mask = np.array(rounded_mask(side, radius_ratio), dtype=np.float32) / 255.0
    rgba = np.concatenate([crop, mask[:, :, None]], axis=2)
    return to_image(rgba)


def preview(icon: Image.Image, render: str, path: Path) -> None:
    """Render, then the icon at 256/64/48/32/16 on holt-night and on lilac."""
    sizes = [256, 64, 48, 32, 16]
    cell = 272
    canvas = Image.new("RGB", (cell * (len(sizes) + 1), cell * 2), (30, 30, 30))
    src = Image.open(render).convert("RGB").resize((256, 256), Image.LANCZOS)
    canvas.paste(src, (8, 8))
    for row, bg in enumerate(((0x0D, 0x0B, 0x12), (0xF4, 0xEB, 0xFF))):
        for i, size in enumerate(sizes):
            tile = Image.new("RGB", (256, 256), bg)
            small = icon.resize((size, size), Image.LANCZOS)
            tile.paste(small, ((256 - size) // 2, (256 - size) // 2), small)
            canvas.paste(tile, (cell * (i + 1) + 8, cell * row + 8))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(path))


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Derive a HoltOS app icon from a ComfyUI tile render.")
    parser.add_argument("--render", required=True, help="Path to the chosen render PNG")
    parser.add_argument("--name", required=True, help="Icon name, e.g. holtos-apps")
    parser.add_argument("--root", required=True, help="Root of archiso/airootfs")
    parser.add_argument("--preview", required=True, help="Output path for the preview PNG")
    parser.add_argument("--radius", type=float, default=0.22, help="Corner radius as a share of the side")
    args = parser.parse_args()

    root = Path(args.root)
    icon = cut_tile(args.render, args.radius)
    for p in save_sizes(icon, root, args.name, SIZES):
        print(f"Wrote {p}")
    brand = root / "usr" / "share" / "holtos" / "brand" / f"{args.name}-icon-1024.png"
    brand.parent.mkdir(parents=True, exist_ok=True)
    icon.resize((1024, 1024), Image.LANCZOS).save(str(brand))
    print(f"Wrote {brand}")
    preview(icon, args.render, Path(args.preview))
    print(f"Wrote preview {args.preview}")


if __name__ == "__main__":
    main()
