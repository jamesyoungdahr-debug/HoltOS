#!/usr/bin/env python3
r"""Turn chosen ComfyUI renders into the HoltOS boot, login and splash images without redrawing anything: cut the dark background out, crop, fit and resize. The lockups pair the rendered mark with the name "HoltOS" set in the brand font (Nunito ExtraBold). Design comes only from ComfyUI renders (Liam, 2026-09-14). Example:
  C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe tools/brand/derive_splash_art.py --otter <png> --glow <png> --font <Nunito-ExtraBold.ttf> --root archiso/airootfs --preview <png>
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_logo import load_rgb, matte, to_image  # noqa: E402

MARK = "usr/share/holtos/brand/holtos-mark-1024.png"
INK = (255, 255, 255, 255)


def bbox_crop(img: Image.Image) -> Image.Image:
    """Crop an RGBA image to the bounding box of alpha > 5."""
    mask = img.getchannel("A").point(lambda a: 255 if a > 5 else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return img
    return img.crop(bbox)


def fit(img: Image.Image, width: int, height: int, pad: float = 0.04, anchor: str = "center") -> Image.Image:
    """Bbox-crop, scale with LANCZOS to fit inside padded area, paste onto transparent canvas."""
    cropped = bbox_crop(img)
    max_w = width * (1 - 2 * pad)
    max_h = height * (1 - 2 * pad)
    ratio = min(max_w / cropped.width, max_h / cropped.height)
    new_size = (int(cropped.width * ratio), int(cropped.height * ratio))
    scaled = cropped.resize(new_size, Image.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    if anchor == "bottom":
        x = (width - new_size[0]) // 2
        y = height - new_size[1] - int(pad * height)
    else:
        x = (width - new_size[0]) // 2
        y = (height - new_size[1]) // 2
    canvas.paste(scaled, (x, y), scaled)
    return canvas


def soft_matte(path: str) -> Image.Image:
    """Turn a glow render's light into alpha: brightness becomes opacity, colour stays pure."""
    # matte() un-premultiplied faint edge pixels into a pale grey ring around the glow.
    rgb = load_rgb(path)
    a = np.clip(rgb.max(axis=2), 0, 1)
    c = np.clip(rgb / np.maximum(a, 1e-4)[:, :, None], 0, 1)
    return to_image(np.concatenate([c, a[:, :, None]], axis=2))


def lockup(mark: Image.Image, font_path: str, width: int = 360, height: int = 104) -> Image.Image:
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
    draw.text((text_x, ty), text, fill=INK, font=font)
    return canvas


def save(img: Image.Image, root: Path, rel: str) -> Path:
    """Create parent dirs, save PNG at root/rel, print info and return the path."""
    out = root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out), "PNG")
    print(f"Wrote {out} {img.width}x{img.height}")
    return out


def preview(images: list[tuple[str, Image.Image]], path: Path) -> None:
    """Render one row per image on a dark background with labels and save."""
    scaled = []
    for label, img in images:
        if img.width > 700:
            ratio = 700 / img.width
            new_size = (700, int(img.height * ratio))
            s = img.resize(new_size, Image.LANCZOS)
        else:
            s = img.copy()
        scaled.append((label, s))
    max_w = max(p[1].width for p in scaled) + 24
    row_h = max(p[1].height for p in scaled) + 36
    total_w = sum(p[1].width + 24 for p in scaled) - 24
    total_h = row_h
    canvas = Image.new("RGBA", (total_w, total_h), (0x0D, 0x0B, 0x12, 255))
    draw = ImageDraw.Draw(canvas)
    cx = 0
    for label, s in scaled:
        cy = 18
        draw.text((cx + 6, 4), label, fill=(200, 200, 200, 255))
        canvas.paste(s, (cx + 12, cy), s)
        cx += s.width + 24
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(path), "PNG")


def main() -> None:
    """Parse args and derive all splash art from ComfyUI renders."""
    parser = argparse.ArgumentParser(description="Derive HoltOS splash art.")
    parser.add_argument("--otter", required=True)
    parser.add_argument("--glow", required=True)
    parser.add_argument("--font", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--preview", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    mark = Image.open(str(root / MARK)).convert("RGBA")
    otter = to_image(matte(load_rgb(args.otter)))
    glow = soft_matte(args.glow)
    lock = lockup(mark, args.font)

    login_otter = fit(otter, 400, 600, anchor="bottom")
    save(login_otter, root, "usr/share/sddm/themes/holtos/otter.png")

    glow_resized = glow.resize((700, 420), Image.LANCZOS)
    save(glow_resized, root, "usr/share/sddm/themes/holtos/glow.png")
    save(glow_resized, root, "usr/share/plymouth/themes/holtos/glow.png")

    save(lock, root, "usr/share/sddm/themes/holtos/lockup.png")
    save(lock, root, "usr/share/plymouth/themes/holtos/lockup.png")
    save(lock, root, "usr/share/plasma/look-and-feel/org.holtos.desktop/contents/splash/images/lockup.png")

    watermark = fit(mark, 400, 333)
    save(watermark, root, "usr/share/plymouth/themes/holtos/watermark.png")

    splash_mark = fit(mark, 220, 220)
    save(splash_mark, root, "usr/share/plasma/look-and-feel/org.holtos.desktop/contents/splash/images/otter.png")

    installer_logo = fit(mark, 256, 256)
    save(installer_logo, root, "etc/calamares/branding/holtos/logo-icon.png")

    preview(
        [
            ("login otter 400x600", login_otter),
            ("glow 700x420", glow_resized),
            ("lockup 360x104", lock),
            ("boot watermark 400x333", watermark),
            ("splash mark 220", splash_mark),
            ("installer logo 256", installer_logo),
        ],
        Path(args.preview),
    )


if __name__ == "__main__":
    main()
