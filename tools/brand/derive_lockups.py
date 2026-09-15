#!/usr/bin/env python3
r"""Derive the HoltOS logo lockups from the rendered mark: horizontal (mark beside the name) and stacked (mark above the name), each for dark backgrounds (white name) and light backgrounds (holt-night name). Nothing is redrawn: the mark is the ComfyUI render already cut out in usr/share/holtos/brand/holtos-mark-1024.png, the name is set in Nunito ExtraBold (Liam, 2026-09-14: design comes only from ComfyUI renders). Example:
  C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe tools/brand/derive_lockups.py --font <Nunito-ExtraBold.ttf> --root archiso/airootfs --preview <png>
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_splash_art import bbox_crop, save  # noqa: E402


MARK = "usr/share/holtos/brand/holtos-mark-1024.png"
OUT = "usr/share/holtos/brand"
WHITE = (255, 255, 255, 255)
NIGHT = (0x0D, 0x0B, 0x12, 255)
PAPER = (0xF4, 0xEB, 0xFF, 255)


def horizontal(mark: Image.Image, font_path: str, ink: tuple[int, int, int, int], width: int = 1080, height: int = 312) -> Image.Image:
    """Create a transparent canvas with the mark and 'HoltOS' text side by side."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cropped_mark = bbox_crop(mark)
    mark_h = int(height * 0.80)
    ratio = mark_h / cropped_mark.height
    mark_w = int(cropped_mark.width * ratio)
    scaled_mark = cropped_mark.resize((mark_w, mark_h), Image.LANCZOS)
    mx = int(height * 0.08)
    my = (height - mark_h) // 2
    canvas.paste(scaled_mark, (mx, my), scaled_mark)
    text_x = mx + mark_w + int(height * 0.16)
    text = "HoltOS"
    size = int(height * 0.52)
    max_text_w = width - text_x - int(height * 0.08)
    while size > 4:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        if tw <= max_text_w:
            break
        size -= 1
    font = ImageFont.truetype(font_path, size)
    tbbox = draw.textbbox((text_x, 0), text, font=font)
    ty = (height - (tbbox[3] - tbbox[1])) // 2 - tbbox[1]
    draw.text((text_x, ty), text, fill=ink, font=font)
    return canvas


def stacked(mark: Image.Image, font_path: str, ink: tuple[int, int, int, int], width: int = 640, height: int = 760) -> Image.Image:
    """Create a transparent canvas with the mark above 'HoltOS' text."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cropped_mark = bbox_crop(mark)
    mark_h = int(height * 0.62)
    mark_w = int(cropped_mark.width * mark_h / cropped_mark.height)
    if mark_w > int(width * 0.90):
        mark_w = int(width * 0.90)
        mark_h = int(cropped_mark.height * mark_w / cropped_mark.width)
    scaled_mark = cropped_mark.resize((mark_w, mark_h), Image.LANCZOS)
    mx = (width - mark_w) // 2
    my = int(height * 0.05)
    canvas.paste(scaled_mark, (mx, my), scaled_mark)
    text = "HoltOS"
    size = int(height * 0.20)
    max_text_w = width - int(width * 0.10)
    while size > 4:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        if tw <= max_text_w:
            break
        size -= 1
    font = ImageFont.truetype(font_path, size)
    tbbox = draw.textbbox((0, 0), text, font=font)
    # textbbox offsets: place the visible glyphs, not the font's line box.
    tx = (width - (tbbox[2] - tbbox[0])) // 2 - tbbox[0]
    ty = my + mark_h + int(height * 0.04) - tbbox[1]
    draw.text((tx, ty), text, fill=ink, font=font)
    return canvas


def preview(items: list[tuple[str, Image.Image, tuple[int, int, int, int]]], path: Path) -> None:
    """Render the lockups side by side, each on its own dark or light panel, with labels, and save."""
    gap = 16
    label_h = 18
    panels = []
    for label, img, bg in items:
        if img.width > 360:
            s = img.resize((360, int(img.height * 360 / img.width)), Image.LANCZOS)
        else:
            s = img.copy()
        panel = Image.new("RGBA", (s.width + 24, s.height + 24), bg)
        panel.paste(s, (12, 12), s)
        panels.append((label, panel))
    width = sum(p.width for _, p in panels) + gap * (len(panels) - 1)
    height = label_h + max(p.height for _, p in panels)
    canvas = Image.new("RGBA", (width, height), (0x26, 0x20, 0x33, 255))
    draw = ImageDraw.Draw(canvas)
    cx = 0
    for label, panel in panels:
        draw.text((cx + 2, 2), label, fill=(150, 150, 150, 255))
        canvas.paste(panel, (cx, label_h))
        cx += panel.width + gap
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(path), "PNG")


def main() -> None:
    """Parse args and derive all lockups from the mark."""
    parser = argparse.ArgumentParser(description="Derive HoltOS logo lockups.")
    parser.add_argument("--font", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--preview", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    mark = Image.open(str(root / MARK)).convert("RGBA")
    font = args.font

    holtos_lockup_horizontal = horizontal(mark, font, WHITE)
    save(holtos_lockup_horizontal, root, f"{OUT}/holtos-lockup-horizontal.png")

    holtos_lockup_horizontal_light = horizontal(mark, font, NIGHT)
    save(holtos_lockup_horizontal_light, root, f"{OUT}/holtos-lockup-horizontal-light.png")

    holtos_lockup_stacked = stacked(mark, font, WHITE)
    save(holtos_lockup_stacked, root, f"{OUT}/holtos-lockup-stacked.png")

    holtos_lockup_stacked_light = stacked(mark, font, NIGHT)
    save(holtos_lockup_stacked_light, root, f"{OUT}/holtos-lockup-stacked-light.png")

    preview(
        [
            ("horizontal, dark", holtos_lockup_horizontal, NIGHT),
            ("horizontal, light", holtos_lockup_horizontal_light, PAPER),
            ("stacked, dark", holtos_lockup_stacked, NIGHT),
            ("stacked, light", holtos_lockup_stacked_light, PAPER),
        ],
        Path(args.preview),
    )


if __name__ == "__main__":
    main()
