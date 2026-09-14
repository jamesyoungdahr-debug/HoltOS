"""Automatic checks on raw wallpaper renders, before a person reviews them.

    python qa.py                      every PNG in renders/
    python qa.py renders/rain-*.png   just these

Needs numpy and Pillow (ComfyUI's bundled Python has both:
C:\\ComfyUI\\ComfyUI_windows_portable\\python_embeded\\python.exe qa.py).

Flags blank renders, corners too dark for HoltOS Glass to show colour, and
near-duplicate seeds, then writes qa/report.json and one contact sheet per
wallpaper id (qa/sheet-<id>.png).

Written by Claude directly: the local-model handoff for this file failed twice.
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
RENDERS = HERE / "renders"
OUT = HERE / "qa"
NAME = re.compile(r"^(?P<id>.+)-(?P<w>\d+)x(?P<h>\d+)-s(?P<seed>\d+)\.png$")

THUMB = (640, 360)
GAP = 12
CAPTION = 28
OK_COLOUR = (244, 235, 255)
WARN_COLOUR = (255, 184, 77)


def parse_render(path: Path) -> dict[str, Any] | None:
    """Split a render file name into id, size and seed; None if it is not a render."""
    m = NAME.match(path.name)
    if m is None:
        return None
    return {"path": path, "file": path.name, "id": m.group("id"), "width": int(m.group("w")),
            "height": int(m.group("h")), "seed": int(m.group("seed"))}


def coverage(img: Image.Image) -> dict[str, float]:
    """Fraction of clearly coloured pixels in each quadrant (what the glass blur can show)."""
    hsv = np.asarray(img.convert("HSV"), dtype=np.uint8)
    coloured = (hsv[:, :, 1] >= 90) & (hsv[:, :, 2] >= 46)
    h, w = coloured.shape
    mh, mw = h // 2, w // 2
    quads = {"tl": coloured[:mh, :mw], "tr": coloured[:mh, mw:], "bl": coloured[mh:, :mw], "br": coloured[mh:, mw:]}
    return {k: round(float(q.sum()) / q.size, 3) for k, q in quads.items()}


def mean_luma(arr: np.ndarray) -> float:
    """Mean BT.709 luma, 0..1."""
    return round(float((0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]).mean()), 3)


def dhash(img: Image.Image) -> np.ndarray:
    """144-bit difference hash for near-duplicate detection."""
    px = np.asarray(img.convert("L").resize((17, 9), Image.LANCZOS), dtype=np.int16)
    return px[:, 1:] > px[:, :-1]


def crop_16_9(img: Image.Image) -> Image.Image:
    """Centre crop to 16:9."""
    w, h = img.size
    ch = round(w * 9 / 16)
    if ch <= h:
        top = (h - ch) // 2
        return img.crop((0, top, w, top + ch))
    cw = round(h * 16 / 9)
    left = (w - cw) // 2
    return img.crop((left, 0, left + cw, h))


def collect(args: list[str]) -> list[Path]:
    """Expand the command-line arguments (Windows shells do not expand globs)."""
    if not args:
        return sorted(RENDERS.glob("*.png"))
    files: list[Path] = []
    for arg in args:
        if any(c in arg for c in "*?["):
            files.extend(Path(p) for p in sorted(glob.glob(arg)))
        else:
            files.append(Path(arg))
    return files


def contact_sheet(rows: list[dict[str, Any]], images: dict[str, Image.Image]) -> Image.Image:
    """Thumbnails three per row, each captioned with its seed and flags."""
    cols = min(3, len(rows))
    lines = -(-len(rows) // 3)
    cell_w, cell_h = THUMB[0] + GAP, THUMB[1] + CAPTION + GAP
    sheet = Image.new("RGB", (GAP + cols * cell_w, GAP + lines * cell_h), (13, 11, 18))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for i, row in enumerate(rows):
        x, y = GAP + (i % 3) * cell_w, GAP + (i // 3) * cell_h
        sheet.paste(crop_16_9(images[row["file"]]).resize(THUMB, Image.LANCZOS), (x, y))
        caption = f"s{row['seed']}  " + ("; ".join(row["flags"]) if row["flags"] else "ok")
        draw.text((x + 4, y + THUMB[1] + 8), caption, fill=WARN_COLOUR if row["flags"] else OK_COLOUR, font=font)
    return sheet


def main() -> None:
    """Check the renders, print a line per image, write the report and contact sheets."""
    parser = argparse.ArgumentParser(description="QA checks on wallpaper renders")
    parser.add_argument("files", nargs="*", help="render PNGs (globs allowed); default: every file in renders/")
    renders = []
    for path in collect(parser.parse_args().files):
        info = parse_render(path)
        if info is None:
            print(f"skip {path.name} (not a render name)")
        elif not path.exists():
            print(f"skip {path.name} (not found)")
        else:
            renders.append(info)
    if not renders:
        print("no renders to check")
        return

    images: dict[str, Image.Image] = {}
    hashes: dict[str, np.ndarray] = {}
    for r in renders:
        img = Image.open(r["path"]).convert("RGB")
        arr = np.asarray(img, dtype=np.float32) / 255.0
        images[r["file"]] = img
        hashes[r["file"]] = dhash(img)
        r["mean_luma"] = mean_luma(arr)
        r["coverage"] = coverage(img)
        r["flags"] = []
        if arr.max() <= 8 / 255:
            r["flags"].append("FAIL blank")
        dark = [q for q, v in r["coverage"].items() if v < 0.03]
        if dark:
            r["flags"].append("WARN dark " + ", ".join(dark))
        if r["mean_luma"] < 0.06:
            r["flags"].append("WARN very dark")

    by_id: dict[str, list[dict[str, Any]]] = {}
    for r in renders:
        by_id.setdefault(r["id"], []).append(r)
    for group in by_id.values():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                if int((hashes[a["file"]] != hashes[b["file"]]).sum()) <= 12:
                    a["flags"].append(f"WARN near-duplicate of {b['file']}")
                    b["flags"].append(f"WARN near-duplicate of {a['file']}")

    for r in renders:
        print(f"{r['file']:<40} {'; '.join(r['flags']) if r['flags'] else 'ok'}")

    OUT.mkdir(parents=True, exist_ok=True)
    report = [{k: r[k] for k in ("file", "id", "width", "height", "seed", "mean_luma", "coverage", "flags")} for r in renders]
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for rid, group in by_id.items():
        contact_sheet(group, images).save(OUT / f"sheet-{rid}.png")
    print(f"report and {len(by_id)} contact sheet(s) in {OUT}")
    sys.exit(1 if any(f.startswith("FAIL") for r in renders for f in r["flags"]) else 0)


if __name__ == "__main__":
    main()
