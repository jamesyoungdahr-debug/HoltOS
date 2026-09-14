"""Preview packaged wallpapers behind HoltOS Glass, without booting the VM.

    python preview.py                 every packaged HoltOS-Neon-* wallpaper
    python preview.py --ids Rain Den  just these (the name after HoltOS-Neon-)

Mocks a translucent, blurred window and the bottom panel over the 1080p image,
roughly as KWin's blur and the Kvantum HoltOSGlass fills draw them, so a
wallpaper that leaves the glass flat or muddy shows up in seconds.
Writes qa/preview-<Name>.png and qa/preview-sheet.png.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
WALLS = REPO / "archiso" / "airootfs" / "usr" / "share" / "wallpapers"
OUT = HERE / "qa"
INK = (23, 20, 35)
WINDOW_ALPHA = 0.40
PANEL_ALPHA = 0.55
BLUR_RADIUS = 18
RADIUS = 10
TEXT = (244, 235, 255, 110)


def find_wallpapers(ids: list[str] | None) -> list[tuple[str, Path]]:
    """Find packaged HoltOS-Neon wallpapers."""
    results: list[tuple[str, Path]] = []
    for d in sorted(WALLS.glob("HoltOS-Neon-*")):
        name = d.name[len("HoltOS-Neon-"):]
        if ids and name not in ids:
            continue
        image = d / "contents" / "images" / "1920x1080.jpg"
        if not image.exists():
            image = image.with_suffix(".png")
        if not image.exists():
            print(f"skip {name}: no 1920x1080 image")
            continue
        results.append((name, image))
    return results


def glass(canvas: Image.Image, box: tuple[int, int, int, int], alpha: float, radius: int) -> None:
    """Draw a translucent blurred glass region on canvas (RGBA, in-place)."""
    x0, y0, x1, y1 = box
    region = canvas.crop(box).convert("RGB").filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    region = Image.blend(region, Image.new("RGB", region.size, INK), alpha)
    mask = Image.new("L", region.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, region.size[0] - 1, region.size[1] - 1), radius=radius, fill=255
    )
    canvas.paste(region, (x0, y0), mask)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        box, radius=radius, outline=(255, 255, 255, 20), width=1
    )
    canvas.alpha_composite(overlay)


def bars(canvas: Image.Image, x: int, y: int, widths: list[int], step: int = 30) -> None:
    """Draw rounded-rectangle content bars on the canvas."""
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i, w in enumerate(widths):
        d.rounded_rectangle(
            (x, y + i * step, x + w, y + i * step + 14), radius=7, fill=TEXT
        )
    canvas.alpha_composite(overlay)


def mock(image: Path) -> Image.Image:
    """Build a mocked preview image with glass windows and panel."""
    canvas = Image.open(image).convert("RGBA").resize((1920, 1080))
    glass(canvas, (190, 130, 1070, 750), WINDOW_ALPHA, RADIUS)  # main window
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.line((190, 170, 1070, 170), fill=(255, 255, 255, 25), width=1)  # title bar line
    for i in range(3):
        cx = 1040 - i * 22
        d.ellipse((cx - 6, 144, cx + 6, 156), fill=(244, 235, 255, 160))
    canvas.alpha_composite(overlay)
    bars(canvas, 230, 210, [520, 610, 440, 580, 360, 500])
    glass(canvas, (1180, 420, 1700, 780), WINDOW_ALPHA, RADIUS)  # second window
    bars(canvas, 1220, 480, [360, 420, 300])
    glass(canvas, (0, 1036, 1920, 1080), PANEL_ALPHA, 0)  # bottom panel
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(5):
        x = 16 + i * 40
        d.rounded_rectangle((x, 1045, x + 26, 1071), radius=6, fill=(244, 235, 255, 150))
    d.rounded_rectangle((1820, 1052, 1890, 1064), radius=6, fill=(244, 235, 255, 150))
    canvas.alpha_composite(overlay)
    return canvas.convert("RGB")


def sheet(previews: list[tuple[str, Image.Image]]) -> Image.Image:
    """Compose a grid preview sheet from individual previews."""
    cols = min(2, len(previews))
    rows = -(-len(previews) // 2)
    cell_w, cell_h = 960 + 12, 540 + 28 + 12
    out = Image.new("RGB", (12 + cols * cell_w, 12 + rows * cell_h), (13, 11, 18))
    d = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    for i, (name, img) in enumerate(previews):
        x, y = 12 + (i % 2) * cell_w, 12 + (i // 2) * cell_h
        out.paste(img.resize((960, 540), Image.LANCZOS), (x, y))
        d.text((x + 4, y + 548), name, fill=(244, 235, 255), font=font)
    return out


def main() -> None:
    """Entry point for the preview tool."""
    parser = argparse.ArgumentParser(description="Preview HoltOS wallpapers")
    parser.add_argument("--ids", nargs="+", default=None, help="Wallpaper names to preview")
    args = parser.parse_args()

    walls = find_wallpapers(args.ids)
    if not walls:
        print("no packaged wallpapers found")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    previews: list[tuple[str, Image.Image]] = []
    for name, image in walls:
        img = mock(image)
        path = OUT / f"preview-{name}.png"
        img.save(path)
        print(f"wrote {path.name}")
        previews.append((name, img))

    sheet(previews).save(OUT / "preview-sheet.png")
    print("wrote preview-sheet.png")


if __name__ == "__main__":
    main()