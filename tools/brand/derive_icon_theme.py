#!/usr/bin/env python3
r"""Build the HoltOS icon theme from chosen ComfyUI icon renders without redrawing anything: cut each rounded glass tile out of its render's black background (derive_app_icon.cut_tile), resize, and write a freedesktop icon theme that falls back to Breeze for every icon HoltOS does not draw.

  C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe tools/brand/derive_icon_theme.py --renders <dir> --root archiso/airootfs --preview <png>

<dir> holds one chosen render per icon, named <render-name>.png (see ICONS). Design comes only from ComfyUI renders (Liam, 2026-09-14); this script only processes them.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_app_icon import cut_tile  # noqa: E402


THEME = "HoltOS"
SIZES = [16, 22, 24, 32, 48, 64, 96, 128, 256]

# icon name -> (context directory, render name). Several names share a render.
ICONS: dict[str, tuple[str, str]] = {
    "folder": ("places", "folder"),
    "inode-directory": ("mimetypes", "folder"),
    "user-home": ("places", "user-home"),
    "folder-home": ("places", "user-home"),
    "user-desktop": ("places", "user-desktop"),
    "folder-desktop": ("places", "user-desktop"),
    "folder-documents": ("places", "folder-documents"),
    "folder-download": ("places", "folder-download"),
    "folder-downloads": ("places", "folder-download"),
    "folder-music": ("places", "folder-music"),
    "folder-pictures": ("places", "folder-pictures"),
    "folder-images": ("places", "folder-pictures"),
    "folder-videos": ("places", "folder-videos"),
    "folder-video": ("places", "folder-videos"),
    "user-trash": ("places", "user-trash"),
    "user-trash-full": ("places", "user-trash"),
    "folder-network": ("places", "folder-network"),
    "network-workgroup": ("places", "folder-network"),
    "text-x-generic": ("mimetypes", "folder-documents"),
    "audio-x-generic": ("mimetypes", "folder-music"),
    "image-x-generic": ("mimetypes", "folder-pictures"),
    "video-x-generic": ("mimetypes", "folder-videos"),
    "org.kde.dolphin": ("apps", "org.kde.dolphin"),
    "system-file-manager": ("apps", "org.kde.dolphin"),
    "org.kde.konsole": ("apps", "org.kde.konsole"),
    "utilities-terminal": ("apps", "org.kde.konsole"),
    "systemsettings": ("apps", "systemsettings"),
    "preferences-system": ("apps", "systemsettings"),
}

CONTEXTS: dict[str, str] = {"places": "Places", "mimetypes": "MimeTypes", "apps": "Applications"}


def index_theme() -> str:
    """Return the full text of a freedesktop index.theme for HoltOS."""
    lines: list[str] = [
        "[Icon Theme]",
        "Name=HoltOS",
        "Comment=HoltOS glass icons, falling back to Breeze",
        "Inherits=breeze-dark,breeze_cursors,hicolor",
        "Example=folder",
    ]

    dirs: list[str] = []
    for size in SIZES:
        for context in sorted(CONTEXTS):
            dirs.append(f"{size}x{size}/{context}")
    lines.append("Directories=" + ",".join(dirs))

    for d in dirs:
        parts = d.split("/")
        size_str, ctx = parts[0], parts[1]
        size_int = int(size_str.replace("x", ""))
        lines.append("")
        lines.append(f"[{d}]")
        lines.append(f"Size={size_int}")
        lines.append(f"Context={CONTEXTS[ctx]}")
        lines.append("Type=Fixed")

    return "\n".join(lines) + "\n"


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Derive a freedesktop icon theme from ComfyUI tile renders."
    )
    parser.add_argument("--renders", required=True, help="Directory of chosen render PNGs")
    parser.add_argument("--root", required=True, help="Root of archiso/airootfs")
    parser.add_argument("--preview", required=True, help="Output path for the preview PNG")
    parser.add_argument(
        "--radius", type=float, default=0.22, help="Corner radius as a share of the side"
    )
    args = parser.parse_args()

    renders_dir: Path = Path(args.renders)
    root: Path = Path(args.root)
    base: Path = root / "usr/share/icons" / THEME

    # Build cache: render name -> cut tile Image (skip missing renders)
    cache: dict[str, Image.Image] = {}
    skipped_renders: set[str] = set()
    for _name, (_context, render) in ICONS.items():
        if render not in cache and render not in skipped_renders:
            render_path = renders_dir / f"{render}.png"
            if not render_path.exists():
                print(f"missing render: {render_path}")
                skipped_renders.add(render)
                continue
            cache[render] = cut_tile(str(render_path), args.radius)

    # Write icon files
    written_names: set[str] = set()
    for name, (context, render) in ICONS.items():
        if render not in cache:
            continue
        tile = cache[render]
        for size in SIZES:
            out = base / f"{size}x{size}" / context / f"{name}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            tile.resize((size, size), Image.LANCZOS).save(str(out))
        written_names.add(name)
        print(f"{name}: {len(SIZES)} sizes from {render}")

    # Write index.theme
    (base / "index.theme").write_text(index_theme(), encoding="utf-8", newline="\n")

    # Preview: one row per distinct render (in ICONS order, deduplicated)
    seen_renders: list[str] = []
    for _name, (_context, render) in ICONS.items():
        if render not in seen_renders and render in cache:
            seen_renders.append(render)

    preview_sizes = [256, 64, 48, 32, 16]
    cell = 272
    cols = len(preview_sizes) + 1  # +1 for the render column
    rows = len(seen_renders)
    canvas_w = cell * cols
    canvas_h = cell * rows
    canvas_bg = (30, 30, 30)
    canvas: Image.Image = Image.new("RGB", (canvas_w, canvas_h), canvas_bg)

    for row_idx, render in enumerate(seen_renders):
        tile = cache[render]
        # First cell: the full render at 256 on holt-night
        src_tile = Image.new("RGB", (cell - 16, cell - 16), (0x0D, 0x0B, 0x12))
        render_img = tile.resize((256, 256), Image.LANCZOS)
        src_tile.paste(render_img, (8, 8), render_img)
        canvas.paste(src_tile, (0, row_idx * cell))

        # Remaining cells: sizes on holt-night
        for col_idx, size in enumerate(preview_sizes):
            bg = Image.new("RGB", (cell - 16, cell - 16), (0x0D, 0x0B, 0x12))
            small = tile.resize((size, size), Image.LANCZOS)
            offset_x = (256 - size) // 2
            offset_y = (256 - size) // 2
            bg.paste(small, (offset_x + 8, offset_y + 8), small)
            canvas.paste(bg, ((col_idx + 1) * cell, row_idx * cell))

    preview_path: Path = Path(args.preview)
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(preview_path))
    print(f"Wrote preview {preview_path}")

    print(f"{len(written_names)} icon names written, {len(cache)} renders used")


if __name__ == "__main__":
    main()
