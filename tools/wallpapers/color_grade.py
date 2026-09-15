"""Deterministic colour-grade for neon wallpaper recolours.

Rebalances an already-rendered wallpaper so all five brand neon colours are
present, preserving composition and luminance.

    python color_grade.py input.png output.png

Brand palette (hex → HSV hue in degrees):
  purple #B14DFF → 274   magenta #FF4FD8 → 313   electric blue #4F7BFF → 225
  teal #28E0C8 → 172     lime #C6FF3D → 78       ground #0D0B12 (near-black)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


# ── HSV helpers (pure numpy, no external deps) ───────────────────────────────


def rgb_to_hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert RGB [0,1] float32 array of shape (H,W,3) to (H,S,V).

    Hue is returned in [0, 1] where 1.0 == 360 degrees.
    """
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    # Value
    v = cmax

    # Saturation
    s = np.where(cmax == 0.0, 0.0, delta / cmax)

    # Hue (in [0,1])
    h = np.zeros_like(delta)
    mask_r = (cmax == r) & (delta > 0)
    mask_g = (cmax == g) & (delta > 0)
    mask_b = (cmax == b) & (delta > 0)

    h[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6.0
    h[mask_g] = ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2.0
    h[mask_b] = ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4.0

    h = (h / 6.0) % 1.0
    return h, s, v


def hsv_to_rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Convert H,S,V arrays to RGB [0,1] float32 array of shape (H,W,3).

    Hue must be in [0, 1] where 1.0 == 360 degrees.
    """
    c = v * s
    h6 = h * 6.0
    x = c * (1.0 - np.abs((h6 % 2.0) - 1.0))

    r = np.zeros_like(h)
    g = np.zeros_like(h)
    b = np.zeros_like(h)

    m0 = (h6 >= 0.0) & (h6 < 1.0)
    m1 = (h6 >= 1.0) & (h6 < 2.0)
    m2 = (h6 >= 2.0) & (h6 < 3.0)
    m3 = (h6 >= 3.0) & (h6 < 4.0)
    m4 = (h6 >= 4.0) & (h6 < 5.0)
    m5 = (h6 >= 5.0) & (h6 < 6.0)

    r[m0] = c[m0]; g[m0] = x[m0]
    r[m1] = x[m1]; g[m1] = c[m1]
    g[m2] = c[m2]; b[m2] = x[m2]
    g[m3] = x[m3]; b[m3] = c[m3]
    r[m4] = x[m4]; b[m4] = c[m4]
    r[m5] = c[m5]; b[m5] = x[m5]

    m = v - c
    return np.stack([r + m, g + m, b + m], axis=-1)


# ── Grade pipeline ───────────────────────────────────────────────────────────


def grade(input_path: str | Path, output_path: str | Path) -> None:
    """Colour-grade a single wallpaper PNG in-place."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    img = Image.open(input_path)
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)

    # Normalise to [0,1] based on original bit depth
    if img.mode == "I;16" or (hasattr(img, "bitdepth") and img.bitdepth == 16):
        arr = arr / 65535.0
    else:
        # Check the raw dtype before convert("RGB") by re-opening
        raw = Image.open(input_path)
        if np.asarray(raw).dtype == np.uint16:
            arr = arr / 65535.0
        else:
            arr = arr / 255.0

    h, s, v = rgb_to_hsv(arr)

    # Glow mask
    glow = (s >= 0.20) & (v >= 0.25)

    # ── Glow pixels ────────────────────────────────────────────────────────

    # 1. Hue remap (monotonic interpolation)
    hdeg = np.copy(h) * 360.0
    xp = np.array([0, 150, 195, 245, 260, 285, 340, 360], dtype=np.float64)
    fp = np.array([150, 150, 195, 245, 260, 315, 318, 360], dtype=np.float64)
    hdeg[glow] = np.interp(hdeg[glow], xp, fp)
    hdeg = np.mod(hdeg, 360.0)
    h = hdeg / 360.0

    # 2. Lime spark – scattered subset of very bright glow pixels
    bright_glow = glow & (v >= np.percentile(v[glow], 95.0))
    ys, xs = np.indices(bright_glow.shape)
    spark_mask = bright_glow & ((ys + xs) % 2 == 0)
    h[spark_mask] = 78.0 / 360.0
    s[spark_mask] = np.maximum(s[spark_mask], 0.90)

    # 3. Saturation boost for glow
    s[glow] = np.clip(s[glow] * 1.18, 0.0, 1.0)

    # ── Non-glow pixels ────────────────────────────────────────────────────
    s[~glow] = s[~glow] * 0.85

    # V is preserved everywhere (no changes made to v).

    rgb_out = hsv_to_rgb(h, s, v)
    rgb_out = np.clip(rgb_out, 0.0, 1.0)
    out_img = Image.fromarray(np.rint(rgb_out * 255.0).astype(np.uint8))
    out_img.save(str(output_path), "PNG")


# ── CLI entry point ──────────────────────────────────────────────────────────


def main() -> None:
    """Parse arguments and run the colour-grade."""
    parser = argparse.ArgumentParser(
        description="Deterministic neon colour-grade for HoltOS wallpapers"
    )
    parser.add_argument("input", help="Input wallpaper PNG")
    parser.add_argument("output", help="Output graded PNG")
    args = parser.parse_args()

    grade(args.input, args.output)


if __name__ == "__main__":
    main()
