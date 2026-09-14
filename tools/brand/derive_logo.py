#!/usr/bin/env python3
"""Turn chosen ComfyUI logo renders into HoltOS icon files without redrawing anything.

Cut the flat dark background out into transparency, crop, square and resize.
Run with ComfyUI's bundled Python (numpy + Pillow):
  C:\\ComfyUI\\ComfyUI_windows_portable\\python_embeded\\python.exe tools/brand/derive_logo.py \\
      --mark <png> --appicon <png> --symbolic <png> --root archiso/airootfs --preview <png>

Design comes only from ComfyUI renders (Liam, 2026-09-14); this script only processes them.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def load_rgb(path: str | Path) -> np.ndarray:
    """Load an image and return HxWx3 float32 in 0..1."""
    img = Image.open(str(path)).convert("RGB")
    return np.array(img, dtype=np.float32) / 255.0


def background_color(rgb: np.ndarray) -> np.ndarray:
    """Return the median colour of a border strip 16 px wide on all four sides."""
    h, w = rgb.shape[:2]
    strip = np.concatenate([
        rgb[:16, :].reshape(-1, 3),
        rgb[-16:, :].reshape(-1, 3),
        rgb[:, :16].reshape(-1, 3),
        rgb[:, -16:].reshape(-1, 3),
    ], axis=0)
    return np.median(strip, axis=0)


def matte(rgb: np.ndarray, low: float = 0.035, high: float = 0.22) -> np.ndarray:
    """Return HxWx4 float32 with the flat background removed to transparency."""
    bg = background_color(rgb)
    d = np.max(np.abs(rgb - bg), axis=2)
    a = np.clip((d - low) / (high - low), 0, 1)
    # Smooth step
    a = a * a * (3 - 2 * a)

    c = np.zeros_like(rgb)
    mask = a > 0.001
    # Un-premultiply: the stored colour is bg + (fg - bg) * alpha, so fg = bg + (stored - bg)/alpha
    c[mask] = (rgb[mask] - bg[None, None, :] * (1 - a[mask, None])) / a[mask, None]
    c = np.clip(c, 0, 1)

    return np.concatenate([c, a[:, :, None]], axis=2)


def crop_square(rgba: np.ndarray, margin: float = 0.04) -> np.ndarray:
    """Crop to bounding box of alpha > 0.02, expand, square and pad with transparent."""
    h, w = rgba.shape[:2]
    ys, xs = np.where(rgba[..., 3] > 0.02)
    if len(xs) == 0:
        return rgba

    x0, x1 = int(np.min(xs)), int(np.max(xs))
    y0, y1 = int(np.min(ys)), int(np.max(ys))

    box_w = x1 - x0 + 1
    box_h = y1 - y0 + 1
    expand = int(margin * max(box_w, box_h))

    x0 = max(x0 - expand, 0)
    y0 = max(y0 - expand, 0)
    x1 = min(x1 + expand, w - 1)
    y1 = min(y1 + expand, h - 1)

    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    side = max(x1 - x0 + 1, y1 - y0 + 1)
    half = int(np.ceil(side / 2))

    sx = int(cx - half)
    sy = int(cy - half)
    ex = sx + side
    ey = sy + side

    # Pad the source with transparent if needed
    pad_top = max(-sy, 0)
    pad_left = max(-sx, 0)
    pad_bottom = max(ey - h, 0)
    pad_right = max(ex - w, 0)

    if any(p > 0 for p in [pad_top, pad_left, pad_bottom, pad_right]):
        rgba = np.pad(rgba, ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)),
                       mode="constant", constant_values=0)
        sx += pad_left
        sy += pad_top

    return rgba[sy:ey, sx:ex]


def white_glyph(rgb: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Return HxWx4 RGBA with pure-white glyph and transparent cut-outs."""
    L = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    a = np.clip((L - (threshold - 0.08)) / 0.16, 0, 1)
    c = np.ones_like(rgb)
    return np.concatenate([c, a[:, :, None]], axis=2)


def to_image(rgba: np.ndarray) -> Image.Image:
    """Convert HxWx4 float32 (0..1) to PIL RGBA uint8."""
    arr = np.round(np.clip(rgba, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def save_sizes(img: Image.Image, root: Path, name: str, sizes: list[int]) -> list[Path]:
    """Resize to each size and save under the hicolor icon theme; return paths."""
    base = root / "usr" / "share" / "icons" / "hicolor"
    paths = []
    for size in sizes:
        out_dir = base / f"{size}x{size}" / "apps"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name}.png"
        img.resize((size, size), Image.LANCZOS).save(str(out_path))
        paths.append(out_path)
    return paths


def preview(sources: list[tuple[str, Path]], outputs: dict[str, Image.Image], path: Path) -> None:
    """Build a single PNG showing source renders and output icons on dark/light backgrounds."""
    # Row 1: sources at 256 px
    src_images = []
    for label, spath in sources:
        img = Image.open(str(spath)).convert("RGBA")
        img = img.resize((256, 256), Image.LANCZOS)
        src_images.append((label, img))

    # Rows 2-3: outputs at 256, 64, 32, 16 on dark then light
    sizes = [256, 64, 32, 16]
    bg_dark = Image.new("RGBA", (256, 256), (0x0D, 0x0B, 0x12, 255))
    bg_light = Image.new("RGBA", (256, 256), (0xF4, 0xEB, 0xFF, 255))

    out_rows: list[list[tuple[str, Image.Image]]] = [[], []]
    for idx, (label, img) in enumerate(outputs.items()):
        for i, sz in enumerate(sizes):
            resized = img.resize((sz, sz), Image.LANCZOS)
            dark_composite = bg_dark.copy()
            dark_composite.paste(resized, (0, 0), resized)
            light_composite = bg_light.copy()
            light_composite.paste(resized, (0, 0), resized)
            out_rows[0].append((f"{label} {sz}", dark_composite))
            out_rows[1].append((f"{label} {sz}", light_composite))

    # Measure label height
    draw_tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    font = draw_tmp.font
    sample_text = "X"
    _, _, tw, th = draw_tmp.textbbox((0, 0), sample_text, font=font)
    label_h = max(th - 0, 2)

    # Calculate canvas size
    cell_w = 256 + 8
    row1_count = len(src_images)
    row2_count = len(out_rows[0])
    row3_count = len(out_rows[1])
    max_cols = max(row1_count, row2_count, row3_count)
    canvas_w = max_cols * cell_w + 8
    rows_data = [src_images, out_rows[0], out_rows[1]]
    canvas_h = sum(len(r) > 0 for r in rows_data) * (256 + label_h + 4) + 8

    canvas = Image.new("RGB", (canvas_w, canvas_h), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)

    y_offset = 4
    for row in rows_data:
        if not row:
            continue
        x_offset = 4
        for label, img in row:
            canvas.paste(img.convert("RGB"), (x_offset, y_offset + label_h))
            draw.text((x_offset, y_offset), label, fill=(180, 180, 180), font=font)
            x_offset += cell_w
        y_offset += 256 + label_h + 4

    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(path))


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Derive HoltOS logo icon files from ComfyUI renders.")
    parser.add_argument("--mark", required=True, help="Path to the mark render PNG")
    parser.add_argument("--appicon", required=True, help="Path to the app-icon render PNG")
    parser.add_argument("--symbolic", required=True, help="Path to the symbolic render PNG")
    parser.add_argument("--root", required=True, help="Root of archiso/airootfs")
    parser.add_argument("--preview", required=True, help="Output path for preview PNG")
    args = parser.parse_args()

    root = Path(args.root)

    # --- Mark ---
    mark_rgba = crop_square(matte(load_rgb(args.mark)))
    mark_img = to_image(mark_rgba)
    brand_dir = root / "usr" / "share" / "holtos" / "brand"
    brand_dir.mkdir(parents=True, exist_ok=True)

    mark_1024_path = brand_dir / "holtos-mark-1024.png"
    mark_img.resize((1024, 1024), Image.LANCZOS).save(str(mark_1024_path))
    print(f"Wrote {mark_1024_path}")

    mark_512_path = brand_dir / "holtos-mark-512.png"
    mark_img.resize((512, 512), Image.LANCZOS).save(str(mark_512_path))
    print(f"Wrote {mark_512_path}")

    # --- App icon ---
    app_rgba = crop_square(matte(load_rgb(args.appicon)))
    app_img = to_image(app_rgba)
    app_paths = save_sizes(app_img, root, "holtos-logo", [16, 22, 24, 32, 48, 64, 96, 128, 256, 512])
    for p in app_paths:
        print(f"Wrote {p}")

    # --- Symbolic ---
    sym_rgba = crop_square(white_glyph(load_rgb(args.symbolic)))
    sym_img = to_image(sym_rgba)
    sym_paths = save_sizes(sym_img, root, "holtos-logo-symbolic", [16, 22, 24, 32, 48, 64])
    for p in sym_paths:
        print(f"Wrote {p}")

    # --- Alpha coverage ---
    def alpha_coverage(rgba: np.ndarray) -> float:
        return (np.sum(rgba[..., 3] > 0.5) / rgba.shape[0] / rgba.shape[1]) * 100

    print(f"Mark alpha coverage: {alpha_coverage(mark_rgba):.1f}%")
    print(f"App icon alpha coverage: {alpha_coverage(app_rgba):.1f}%")
    print(f"Symbolic alpha coverage: {alpha_coverage(sym_rgba):.1f}%")

    # --- Preview ---
    preview(
        sources=[
            ("chosen mark", Path(args.mark)),
            ("app icon", Path(args.appicon)),
            ("symbolic", Path(args.symbolic)),
        ],
        outputs={
            "mark": to_image(mark_rgba),
            "app icon": app_img,
            "symbolic": sym_img,
        },
        path=Path(args.preview),
    )
    print(f"Wrote preview {args.preview}")


if __name__ == "__main__":
    main()
