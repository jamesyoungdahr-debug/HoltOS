r"""Build the HoltOS cursor theme from chosen ComfyUI cursor renders without redrawing anything: key out each render's flat chroma-green background, crop the shape, and write Xcursor files (with a pure-Python Xcursor writer, so no xcursorgen is needed). Names it does not draw fall back to breeze_cursors.

  C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe tools/brand/derive_cursor_theme.py --renders <dir> --root archiso/airootfs --preview <png>

<dir> holds arrow.png, hand.png, text.png, busy.png, move.png, forbidden.png, resize.png, crosshair.png. Design comes only from ComfyUI renders (Liam, 2026-09-14); this script only processes them.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

import numpy as np
from PIL import Image

THEME = "HoltOS"
SIZES = [24, 32, 48, 64]


def key_green(path: Path) -> Image.Image:
    """RGBA with the chroma-green background removed and green spill cleaned, cropped to the shape."""
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    # Background colour: median of a 12 px border strip.
    border = np.concatenate(
        [
            rgb[:12].reshape(-1, 3),
            rgb[-12:].reshape(-1, 3),
            rgb[:, :12].reshape(-1, 3),
            rgb[:, -12:].reshape(-1, 3),
        ]
    )
    bg = np.median(border, axis=0)
    # "Greenness": how far green exceeds the larger of red and blue, relative to the background's.
    g = rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])
    bg_g = bg[1] - max(bg[0], bg[2])
    alpha = 1.0 - np.clip((g - 0.05) / max(bg_g - 0.05, 1e-3), 0.0, 1.0)
    # Remove green spill on edges: cap green at the max of red and blue.
    out = rgb.copy()
    out[..., 1] = np.minimum(out[..., 1], np.maximum(out[..., 0], out[..., 2]))
    rgba = np.dstack([out, alpha])
    img = Image.fromarray((rgba * 255).round().astype(np.uint8), "RGBA")
    box = img.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()
    return img.crop(box) if box else img


def square(img: Image.Image, pad: float = 0.06) -> Image.Image:
    """Centre on a transparent square canvas with a small margin."""
    side = int(max(img.size) * (1 + 2 * pad))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    return canvas


# Shapes: render name -> hotspot as a fraction of the square canvas (x, y).
# arrow and hand are not centred: their tip is the hotspot.
HOTSPOTS = {
    "arrow": None,
    "hand": None,
    "text": (0.5, 0.5),
    "busy": (0.5, 0.5),
    "move": (0.5, 0.5),
    "forbidden": (0.5, 0.5),
    "resize": (0.5, 0.5),
    "crosshair": (0.5, 0.5),
}


def tip_hotspot(img: Image.Image, which: str) -> tuple[float, float]:
    """Hotspot fraction for pointer shapes: arrow = the topmost-leftmost opaque pixel, hand = the topmost opaque pixel (fingertip)."""
    a = np.asarray(img.getchannel("A")) > 128
    ys, xs = np.nonzero(a)
    if len(xs) == 0:
        return (0.0, 0.0)
    if which == "arrow":
        i = int(np.argmin(xs + ys))
    else:
        top = ys.min()
        row = xs[ys == top]
        return (float(row.mean()) / img.width, float(top) / img.height)
    return (float(xs[i]) / img.width, float(ys[i]) / img.height)


def xcursor(frames: list[tuple[int, int, int, int, Image.Image]]) -> bytes:
    """Encode frames (nominal size, xhot, yhot, delay ms, RGBA image) as an Xcursor file."""
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, len(frames))
    toc_size = 12 * len(frames)
    offset = 16 + toc_size
    toc: bytes = b""
    chunks: bytes = b""
    for nominal, xhot, yhot, delay, img in frames:
        w, h = img.size
        px = np.asarray(img.convert("RGBA"), dtype=np.uint32)
        a = px[..., 3]
        # Xcursor stores premultiplied ARGB, little-endian 32-bit.
        r = px[..., 0] * a // 255
        gch = px[..., 1] * a // 255
        b = px[..., 2] * a // 255
        argb = (a << 24) | (r << 16) | (gch << 8) | b
        chunk = struct.pack(
            "<IIIIIIIII", 36, 0xFFFD0002, nominal, 1, w, h, xhot, yhot, delay
        ) + argb.astype("<u4").tobytes()
        toc += struct.pack("<III", 0xFFFD0002, nominal, offset + len(chunks))
        chunks += chunk
    return header + toc + chunks


def frames_for(
    img: Image.Image, hot: tuple[float, float], delay: int = 0
) -> list[tuple[int, int, int, int, Image.Image]]:
    """Return one frame per size in SIZES with the given hotspot and delay."""
    return [
        (s, min(int(hot[0] * s), s - 1), min(int(hot[1] * s), s - 1), delay, img.resize((s, s), Image.LANCZOS))
        for s in SIZES
    ]


# Xcursor name -> (shape, rotation degrees counter-clockwise). Aliases are written as copies.
NAMES = {
    "default": ("arrow", 0),
    "left_ptr": ("arrow", 0),
    "arrow": ("arrow", 0),
    "top_left_arrow": ("arrow", 0),
    "pointer": ("hand", 0),
    "hand1": ("hand", 0),
    "hand2": ("hand", 0),
    "pointing_hand": ("hand", 0),
    "text": ("text", 0),
    "xterm": ("text", 0),
    "ibeam": ("text", 0),
    "wait": ("busy", 0),
    "watch": ("busy", 0),
    "progress": ("busy", 0),
    "left_ptr_watch": ("busy", 0),
    "move": ("move", 0),
    "fleur": ("move", 0),
    "all-scroll": ("move", 0),
    "size_all": ("move", 0),
    "not-allowed": ("forbidden", 0),
    "no-drop": ("forbidden", 0),
    "crossed_circle": ("forbidden", 0),
    "forbidden": ("forbidden", 0),
    "crosshair": ("crosshair", 0),
    "cross": ("crosshair", 0),
    "tcross": ("crosshair", 0),
    "ew-resize": ("resize", 0),
    "col-resize": ("resize", 0),
    "size_hor": ("resize", 0),
    "h_double_arrow": ("resize", 0),
    "e-resize": ("resize", 0),
    "w-resize": ("resize", 0),
    "sb_h_double_arrow": ("resize", 0),
    "right_side": ("resize", 0),
    "left_side": ("resize", 0),
    "ns-resize": ("resize", 90),
    "row-resize": ("resize", 90),
    "size_ver": ("resize", 90),
    "v_double_arrow": ("resize", 90),
    "n-resize": ("resize", 90),
    "s-resize": ("resize", 90),
    "sb_v_double_arrow": ("resize", 90),
    "top_side": ("resize", 90),
    "bottom_side": ("resize", 90),
    "nesw-resize": ("resize", 45),
    "size_bdiag": ("resize", 45),
    "ne-resize": ("resize", 45),
    "sw-resize": ("resize", 45),
    "top_right_corner": ("resize", 45),
    "bottom_left_corner": ("resize", 45),
    "fd_double_arrow": ("resize", 45),
    "nwse-resize": ("resize", -45),
    "size_fdiag": ("resize", -45),
    "nw-resize": ("resize", -45),
    "se-resize": ("resize", -45),
    "top_left_corner": ("resize", -45),
    "bottom_right_corner": ("resize", -45),
    "bd_double_arrow": ("resize", -45),
}


def main() -> None:
    """CLI entry-point."""
    parser = argparse.ArgumentParser(description="Derive HoltOS cursor theme from ComfyUI renders.")
    parser.add_argument("--renders", required=True, help="Directory with render PNGs")
    parser.add_argument("--root", required=True, help="Archiso airootfs root")
    parser.add_argument("--preview", required=True, help="Output preview PNG path")
    args = parser.parse_args()

    renders = Path(args.renders)
    out = Path(args.root) / "usr/share/icons" / THEME / "cursors"
    out.mkdir(parents=True, exist_ok=True)

    # Load and key each shape render.
    shapes: dict[str, Image.Image] = {}
    for shape in HOTSPOTS:
        path = renders / f"{shape}.png"
        if not path.exists():
            print(f"missing render: {path}")
            continue
        shapes[shape] = square(key_green(path))

    # Encode and write every Xcursor name.
    encoded: dict[tuple[str, int], bytes] = {}
    shape_usage: dict[str, int] = {}

    for name, (shape, rot) in NAMES.items():
        if shape not in shapes:
            continue
        key = (shape, rot)
        if key not in encoded:
            img = shapes[shape]
            if shape == "busy":
                # Animated: 12 frames, each rotated 30 degrees clockwise, 70 ms apiece.
                frames: list[tuple[int, int, int, int, Image.Image]] = []
                for i in range(12):
                    frame = img.rotate(-30 * i, resample=Image.BICUBIC)
                    frames += frames_for(frame, (0.5, 0.5), 70)
                encoded[key] = xcursor(frames)
            else:
                if rot:
                    img = img.rotate(rot, resample=Image.BICUBIC, expand=False)
                hot = HOTSPOTS[shape] or tip_hotspot(img, shape)
                encoded[key] = xcursor(frames_for(img, hot))
        (out / name).write_bytes(encoded[key])
        shape_usage[shape] = shape_usage.get(shape, 0) + 1

    for shape, count in sorted(shape_usage.items()):
        print(f"{shape}: {count} names")

    # Write cursor.theme index.
    index = Path(args.root) / "usr/share/icons" / THEME / "cursor.theme"
    index.write_text("[Icon Theme]\nName=HoltOS\nInherits=breeze_cursors\n")

    # Do not overwrite index.theme if it already exists (from derive_icon_theme.py).
    icon_index = Path(args.root) / "usr/share/icons" / THEME / "index.theme"
    if not icon_index.exists():
        icon_index.write_text("[Icon Theme]\nName=HoltOS\nInherits=breeze-icons\n")

    # Preview: one row per shape, 64 px version on two backgrounds in 96 px cells.
    preview_shapes = [s for s in HOTSPOTS if s in shapes]
    cell_w = 96 * len(preview_shapes)
    cell_h = 96 * len(preview_shapes)
    preview = Image.new("RGB", (cell_w, cell_h), (255, 255, 255))
    for row_idx, shape in enumerate(preview_shapes):
        img_64 = shapes[shape].resize((64, 64), Image.LANCZOS)
        # Dark background cell.
        dark_cell = Image.new("RGBA", (96, 96), (0x0D, 0x0B, 0x12, 255))
        dark_cell.paste(img_64, ((96 - 64) // 2, (96 - 64) // 2), img_64)
        preview.paste(dark_cell, (row_idx * 96, 0))
        # White background cell.
        light_cell = Image.new("RGBA", (96, 96), (255, 255, 255, 255))
        light_cell.paste(img_64, ((96 - 64) // 2, (96 - 64) // 2), img_64)
        preview.paste(light_cell, (row_idx * 96, 96))
    # Actually build a proper grid: row per shape, two columns (dark / light).
    col_w = 96
    num_shapes = len(preview_shapes)
    canvas = Image.new("RGB", (col_w * 2, col_w * num_shapes), (255, 255, 255))
    for row_idx, shape in enumerate(preview_shapes):
        img_64 = shapes[shape].resize((64, 64), Image.LANCZOS)
        # Dark cell.
        dark_cell = Image.new("RGBA", (96, 96), (0x0D, 0x0B, 0x12, 255))
        dark_cell.paste(img_64, ((96 - 64) // 2, (96 - 64) // 2), img_64)
        canvas.paste(dark_cell, (0, row_idx * 96))
        # Light cell.
        light_cell = Image.new("RGBA", (96, 96), (255, 255, 255, 255))
        light_cell.paste(img_64, ((96 - 64) // 2, (96 - 64) // 2), img_64)
        canvas.paste(light_cell, (96, row_idx * 96))
    canvas.save(args.preview)

    print(f"{len(NAMES)} cursor names written")


if __name__ == "__main__":
    main()
