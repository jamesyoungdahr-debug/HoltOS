r"""Trace the HoltOS otter mark (the chosen ComfyUI render, already cut out) into an SVG without redrawing it: split the image into its flat colour layers, trace each layer's outline with marching squares, simplify the outlines and write them as SVG paths, then render the SVG back to PNG so the trace can be compared with the render.

  C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe tools/brand/trace_mark.py --mark archiso/airootfs/usr/share/holtos/brand/holtos-mark-1024.png --out archiso/airootfs/usr/share/holtos/brand/holtos-mark.svg --preview <png>

Design comes only from ComfyUI renders (Liam, 2026-09-14); this script only processes them.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


# ---------------------------------------------------------------------------
# Brand tokens – ordered bottom → top (draw order)
# ---------------------------------------------------------------------------
LAYERS = [
    ("rim-magenta", (1.00, 0.31, 0.85)),   # #FF4FD8
    ("rim-blue", (0.31, 0.48, 1.00)),      # #4F7BFF
    ("head", (0.55, 0.20, 0.95)),          # main purple face
    ("face-light", (0.72, 0.55, 0.98)),    # lighter lower face
    ("lilac", (0.92, 0.88, 1.00)),         # whisker pad #F4EBFF-ish
    ("dark", (0.20, 0.06, 0.40)),          # nose, eyes, mouth
    ("white", (1.00, 1.00, 1.00)),         # whiskers
    ("lime", (0.78, 1.00, 0.24)),          # sparks #C6FF3D
]

RIM_NAMES = {"rim-magenta", "rim-blue"}


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------
def load(path: str | Path) -> np.ndarray:
    """Load *path* as a float32 RGBA image in [0, 1]."""
    img = Image.open(str(path)).convert("RGBA")
    arr = np.array(img, dtype=np.float32) / 255.0
    return arr


# ---------------------------------------------------------------------------
# Palette assignment & mask building
# ---------------------------------------------------------------------------
def assign_layers(rgba: np.ndarray):
    """Return list of (name, mean_rgb, reference_rgb, pixel_mask)."""
    h, w = rgba.shape[:2]
    refs = [(name, ref) for name, ref in LAYERS]

    # Only consider pixels with alpha > 0.5
    rgb = rgba[:, :, :3]

    # Precompute distances to every reference (HWC × C → HWL)
    dists: list[np.ndarray] = []
    for _, ref in refs:
        d = np.sqrt(((rgb - ref) ** 2).sum(axis=2))
        dists.append(d)

    # Assign each opaque pixel to the nearest reference layer
    stacked = np.stack(dists, axis=-1)  # (H, W, L)
    assignment = np.argmin(stacked, axis=-1)  # (H, W) – index into refs

    # The transparent background is black RGB: without this check it all went
    # to the "dark" layer, and every layer below it covered the whole image.
    opaque = rgba[:, :, 3] > 0.5

    layers: list[tuple[str, tuple[float, float, float], tuple[float, float, float], np.ndarray]] = []
    for i, (name, ref) in enumerate(refs):
        mask = (assignment == i) & opaque
        n_pixels = int(mask.sum())
        if n_pixels < 50:
            mean_rgb = ref
        else:
            mean_rgb = tuple(float(x) for x in rgb[mask].mean(axis=0))
        layers.append((name, mean_rgb, ref, mask))

    return layers


def build_layer_masks(layers: list[tuple[str, ...]]) -> list[np.ndarray]:
    """Build composite masks so shapes don't leave gaps.

    For layer i (bottom→top): include pixels of layer i AND every layer above it (j > i),
    except the two rim layers which only include their own pixels plus each other.
    Then apply a 3×3 majority filter (2 passes).
    """
    n = len(layers)
    masks: list[np.ndarray] = []

    for i in range(n):
        name_i = layers[i][0]
        if name_i in RIM_NAMES:
            # Rim layers: own pixels + the other rim layer
            combined = np.zeros_like(layers[0][3], dtype=bool)
            for j in range(n):
                if layers[j][0] in RIM_NAMES:
                    combined |= layers[j][3]
        else:
            # Include self and all layers above (j > i)
            combined = np.zeros_like(layers[0][3], dtype=bool)
            for j in range(i, n):
                combined |= layers[j][3]

        cleaned = majority_filter(combined, passes=2)
        masks.append(cleaned)

    return masks


def majority_filter(mask: np.ndarray, passes: int = 1) -> np.ndarray:
    """Binary 3×3 majority filter via padded slicing."""
    m = mask.astype(np.uint8)
    for _ in range(passes):
        # Pad with False (0)
        p = np.pad(m, 1, mode="constant", constant_values=0)
        # Sum of all 9-neighbourhoods using slicing
        s = (p[0:-2, 0:-2] + p[0:-2, 1:-1] + p[0:-2, 2:] +
             p[1:-1, 0:-2] + p[1:-1, 1:-1] + p[1:-1, 2:] +
             p[2:, 0:-2]  + p[2:, 1:-1]   + p[2:, 2:])
        m = (s >= 5).astype(np.uint8)
    return m.astype(bool)


# ---------------------------------------------------------------------------
# Marching squares
# ---------------------------------------------------------------------------
def marching_squares(mask: np.ndarray) -> list[list[tuple[float, float]]]:
    """Closed outlines of a boolean mask, following pixel edges.

    Every edge between an inside and an outside pixel becomes a unit segment,
    oriented clockwise around the inside (screen coordinates, y down), so the
    segments chain into closed loops: outer outlines one way, holes the other,
    which suits fill-rule evenodd. Straight runs are merged here; rdp() then
    smooths the pixel staircase. Returns loops in image pixels.
    """
    m = np.pad(mask.astype(bool), 1, mode="constant", constant_values=False)
    inside = m[1:-1, 1:-1]
    rows, cols = inside.shape
    starts: dict[tuple[int, int], list[tuple[int, int]]] = {}

    def add(edge_mask: np.ndarray, sx: int, sy: int, ex: int, ey: int) -> None:
        for r, c in zip(*np.nonzero(edge_mask)):
            starts.setdefault((int(c) + sx, int(r) + sy), []).append((int(c) + ex, int(r) + ey))

    add(inside & ~m[:-2, 1:-1], 0, 0, 1, 0)   # outside above: top edge, left to right
    add(inside & ~m[1:-1, 2:], 1, 0, 1, 1)    # outside right: right edge, top to bottom
    add(inside & ~m[2:, 1:-1], 1, 1, 0, 1)    # outside below: bottom edge, right to left
    add(inside & ~m[1:-1, :-2], 0, 1, 0, 0)   # outside left: left edge, bottom to top

    loops: list[list[tuple[float, float]]] = []
    while starts:
        first = next(iter(starts))
        loop = [first]
        point = first
        while True:
            ends = starts.get(point)
            if not ends:
                break
            nxt = ends.pop()
            if not ends:
                del starts[point]
            point = nxt
            if point == first:
                break
            loop.append(point)
        # Merge collinear runs: keep only the corners.
        corners = []
        n = len(loop)
        for i in range(n):
            px, py = loop[i - 1]
            cx, cy = loop[i]
            qx, qy = loop[(i + 1) % n]
            if (cx - px) * (qy - cy) - (cy - py) * (qx - cx) != 0:
                corners.append((float(cx), float(cy)))
        if len(corners) >= 3:
            loops.append(corners)
    return loops


# ---------------------------------------------------------------------------
# Ramer-Douglas-Peucker simplification (closed-loop variant)
# ---------------------------------------------------------------------------
def _perpendicular_dist(pt: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    """Perpendicular distance from *pt* to line segment *a-b*."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    if dx == 0 and dy == 0:
        return math.hypot(pt[0] - a[0], pt[1] - a[1])
    num = abs(dy * pt[0] - dx * pt[1] + b[0] * a[1] - b[1] * a[0])
    den = math.hypot(dx, dy)
    return num / den


def rdp(points: list[tuple[float, float]], epsilon: float = 0.8) -> list[tuple[float, float]]:
    """Iterative RDP on a closed loop (split at the two farthest points first)."""
    if len(points) <= 4:
        return points

    n = len(points)

    # Find the two farthest points to split the loop into an open chain
    max_d2 = -1.0
    best_i, best_j = 0, 0
    for i in range(n):
        for j in range(i + 1, n):
            d2 = (points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2
            if d2 > max_d2:
                max_d2 = d2
                best_i, best_j = i, j

    def unroll(start: int, stop: int) -> list[tuple[float, float]]:
        """Points from start to stop (both included), walking forward around the loop."""
        chain = []
        idx = start
        while True:
            chain.append(points[idx])
            if idx == stop:
                return chain
            idx = (idx + 1) % n

    def simplify_open(chain: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Standard RDP on an open chain, keeping both ends."""
        keep: set[int] = {0, len(chain) - 1}
        stack = [(0, len(chain) - 1)]
        while stack:
            start, end = stack.pop()
            if end - start <= 1:
                continue
            max_dist = 0.0
            farthest = start + 1
            for k in range(start + 1, end):
                d = _perpendicular_dist(chain[k], chain[start], chain[end])
                if d > max_dist:
                    max_dist = d
                    farthest = k
            if max_dist > epsilon:
                keep.add(farthest)
                stack.append((start, farthest))
                stack.append((farthest, end))
        return [chain[i] for i in sorted(keep)]

    # Both halves of the loop, each simplified on its own, then joined: the
    # earlier version kept only the best_i -> best_j half, so every shape lost
    # half its outline and closed with a long straight edge.
    first_half = simplify_open(unroll(best_i, best_j))
    second_half = simplify_open(unroll(best_j, best_i))
    return first_half[:-1] + second_half[:-1]


# ---------------------------------------------------------------------------
# Loop filtering & SVG path generation
# ---------------------------------------------------------------------------
def _loop_area(loop: list[tuple[float, float]]) -> float:
    """Signed area via the shoelace formula."""
    n = len(loop)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        j = (i + 1) % n
        s += loop[i][0] * loop[j][1]
        s -= loop[j][0] * loop[i][1]
    return abs(s) / 2.0


def filter_loops(loops: list[list[tuple[float, float]]], min_area: float = 12.0) -> list[list[tuple[float, float]]]:
    """Drop loops with < 4 points or area below *min_area* px²."""
    return [l for l in loops if len(l) >= 4 and _loop_area(l) >= min_area]


def path_d(loops: list[list[tuple[float, float]]]) -> str:
    """One SVG path string with fill-rule='evenodd' semantics.

    Each loop is 'M x,y L x,y ... Z' with coordinates rounded to 1 decimal.
    """
    parts: list[str] = []
    for loop in loops:
        segs: list[str] = []
        if not loop:
            continue
        first_x, first_y = loop[0]
        segs.append(f"M {first_x:.1f},{first_y:.1f}")
        for x, y in loop[1:]:
            segs.append(f"L {x:.1f},{y:.1f}")
        segs.append("Z")
        parts.append(" ".join(segs))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# SVG assembly
# ---------------------------------------------------------------------------
def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    """Convert [0,1] RGB to '#rrggbb'."""
    r = max(0, min(255, int(round(rgb[0] * 255))))
    g = max(0, min(255, int(round(rgb[1] * 255))))
    b = max(0, min(255, int(round(rgb[2] * 255))))
    return f"#{r:02X}{g:02X}{b:02X}"


def build_svg(w: int, h: int, layers_data: list[tuple[str, tuple[float, float, float], str]]) -> str:
    """Build the full SVG string.

    *layers_data* is [(name, mean_rgb, path_d_string), ...] in draw order.
    The two rim layers are merged into one gradient-filled path.
    """
    # Merge rim paths
    rim_paths: list[str] = []
    other_layers: list[tuple[str, tuple[float, float, float], str]] = []

    for name, mean_rgb, d in layers_data:
        if not d.strip():
            continue
        if name in RIM_NAMES:
            rim_paths.append(d)
        else:
            other_layers.append((name, mean_rgb, d))

    rim_d = " ".join(rim_paths) if rim_paths else ""

    lines: list[str] = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    lines.append('  <title>HoltOS otter mark</title>')
    lines.append('  <!-- Traced from holtos-mark-1024.png by tools/brand/trace_mark.py -->')

    # Gradient definition
    lines.append('  <defs>')
    lines.append('    <linearGradient id="rim" x1="0" y1="0" x2="1" y2="0">')
    lines.append('      <stop offset="0" stop-color="#FF4FD8"/>')
    lines.append('      <stop offset="1" stop-color="#4F7BFF"/>')
    lines.append('    </linearGradient>')
    lines.append('  </defs>')

    # Rim path (merged)
    if rim_d:
        lines.append(f'  <path fill="url(#rim)" fill-rule="evenodd" d="{rim_d}"/>')

    # Other layers
    for name, mean_rgb, d in other_layers:
        hex_color = rgb_to_hex(mean_rgb)
        lines.append(f'  <path fill="{hex_color}" fill-rule="evenodd" d="{d}"/>')

    lines.append('</svg>')
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Preview rendering (Pillow-only, no cairo)
# ---------------------------------------------------------------------------
def _parse_svg_paths(d: str) -> list[list[tuple[float, float]]]:
    """Parse an SVG path string back into loops of (x, y)."""
    loops: list[list[tuple[float, float]]] = []
    if not d.strip():
        return loops

    current_loop: list[tuple[float, float]] = []
    tokens = d.replace(",", " ").replace("Z", " Z").split()
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd in ("M", "L"):
            x = float(tokens[i + 1])
            y = float(tokens[i + 2])
            current_loop.append((x, y))
            i += 3
        elif cmd == "Z":
            if len(current_loop) >= 3:
                loops.append(current_loop)
            current_loop = []
            i += 1
        else:
            i += 1

    return loops


def render_trace(w: int, h: int, layers_data: list[tuple[str, tuple[float, float, float], str]]) -> Image.Image:
    """Rasterise the SVG paths back to a PNG-sized image using Pillow.

    Each layer's loops are XOR'd (even-odd) into an "L" mask, then composited
    bottom-to-top. The rim gradient is drawn as a horizontal gradient masked by
    the rim layer.
    """
    bg = Image.new("RGBA", (w, h), (0x0D, 0x0B, 0x12, 255))

    # Collect per-layer masks (even-odd via XOR)
    layer_masks: list[tuple[str, np.ndarray]] = []

    for name, mean_rgb, d in layers_data:
        loops = _parse_svg_paths(d)
        if not loops:
            continue

        mask_arr = np.zeros((h, w), dtype=np.uint8)
        for loop in loops:
            # Draw each loop into a temporary "L" image
            tmp = Image.new("L", (w, h), 0)
            draw = ImageDraw.Draw(tmp)
            pts = [(int(round(x)), int(round(y))) for x, y in loop]
            if len(pts) >= 3:
                draw.polygon(pts, fill=255)

            tmp_arr = np.array(tmp, dtype=np.uint8)
            # XOR with accumulated mask (even-odd rule)
            mask_arr ^= tmp_arr

        layer_masks.append((name, mask_arr.astype(bool)))

    # Composite layers bottom-to-top
    result = bg.copy()
    for name, mask in layer_masks:
        if not np.any(mask):
            continue
        # Find the mean_rgb for this layer
        if name in RIM_NAMES:
            # Rim gradient – draw horizontal gradient masked by rim
            grad_img = Image.new("RGB", (w, h))
            for x in range(w):
                t = x / max(1, w - 1)
                r = int(round((1.0 - t) * 255 + t * 79))   # FF → 4F
                g = int(round((1.0 - t) * 79 + t * 123))    # 4F → 7B
                b = int(round((1.0 - t) * 216 + t * 255))   # D8 → FF
                draw_grad = ImageDraw.Draw(grad_img)
                draw_grad.line([(x, 0), (x, h - 1)], fill=(r, g, b))
            grad_arr = np.array(grad_img).astype(np.float32) / 255.0

            # Current result as float
            res_arr = np.array(result.convert("RGB")).astype(np.float32) / 255.0
            alpha = mask.astype(np.float32)[:, :, np.newaxis]
            blended = grad_arr * alpha + res_arr * (1 - alpha)
            result = Image.fromarray((blended * 255).astype(np.uint8), "RGB").convert("RGBA")
        else:
            # Find mean_rgb from layers_data
            rgb_val = None
            for ln, lr, ld in layers_data:
                if ln == name:
                    rgb_val = lr
                    break
            if rgb_val is None:
                continue

            r = int(round(rgb_val[0] * 255))
            g = int(round(rgb_val[1] * 255))
            b = int(round(rgb_val[2] * 255))

            res_arr = np.array(result.convert("RGB")).astype(np.float32) / 255.0
            solid = np.array([r, g, b], dtype=np.float32) / 255.0
            alpha = mask.astype(np.float32)[:, :, np.newaxis]
            blended = solid * alpha + res_arr * (1 - alpha)
            result = Image.fromarray((blended * 255).astype(np.uint8), "RGB").convert("RGBA")

    return result


def make_preview(original: np.ndarray, rendered: Image.Image, out_path: str | Path) -> None:
    """Side-by-side preview: original | trace render | difference (×3)."""
    orig_img = Image.fromarray((original * 255).astype(np.uint8), "RGBA")

    # Resize both panels to 512 px wide, maintaining aspect ratio
    def resize_to_512(img: Image.Image) -> tuple[Image.Image, int]:
        w, h = img.size
        scale = 512.0 / w
        new_w = 512
        new_h = max(1, int(round(h * scale)))
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        return resized, new_h

    orig_panel, panel_h = resize_to_512(orig_img)
    rend_panel, _ = resize_to_512(rendered.convert("RGBA"))

    # Difference panel (amplified ×3)
    orig_arr = np.array(orig_panel.convert("RGB")).astype(np.float32) / 255.0
    rend_arr = np.array(rend_panel.convert("RGB")).astype(np.float32) / 255.0

    # Mean absolute difference over opaque pixels (original alpha > 0.5)
    orig_alpha = np.array(orig_panel).astype(np.float32)[..., 3] / 255.0
    opaque_mask = orig_alpha > 0.5
    if opaque_mask.sum() > 0:
        mad = float(np.abs(orig_arr - rend_arr)[opaque_mask].mean())
    else:
        mad = 0.0

    diff = np.clip(np.abs(orig_arr - rend_arr) * 3, 0, 1)
    # Put difference on holt-night background
    bg_color = np.array([0x0D / 255, 0x0B / 255, 0x12 / 255])
    diff_img_arr = diff * opaque_mask[:, :, np.newaxis] + bg_color[np.newaxis, np.newaxis, :] * (1 - opaque_mask[:, :, np.newaxis])
    diff_panel = Image.fromarray((diff_img_arr * 255).astype(np.uint8), "RGB")

    # Composite: original | render | difference on holt-night background
    total_w = 3 * 512 + 4  # 2 px gap between panels
    canvas = Image.new("RGBA", (total_w, panel_h), (0x0D, 0x0B, 0x12, 255))
    canvas.paste(orig_panel, (0, 0))
    canvas.paste(rend_panel, (514, 0))
    canvas.paste(diff_panel.convert("RGBA"), (1028, 0))

    canvas.save(str(out_path), "PNG")
    print(f"Mean absolute difference (opaque pixels): {mad:.6f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Trace HoltOS otter mark to SVG.")
    parser.add_argument("--mark", required=True, help="Path to the ComfyUI render PNG")
    parser.add_argument("--out", required=True, help="Output SVG path")
    parser.add_argument("--preview", required=True, help="Preview PNG output path")
    parser.add_argument("--epsilon", type=float, default=0.8, help="RDP simplification epsilon (px)")
    args = parser.parse_args()

    # Load image
    rgba = load(args.mark)
    h, w = rgba.shape[:2]
    print(f"Loaded {w}×{h} image")

    # Assign palette layers
    layers = assign_layers(rgba)

    # Build composite masks (bottom→top, gap-free)
    masks = build_layer_masks(layers)

    # Trace each layer
    layers_data: list[tuple[str, tuple[float, float, float], str]] = []
    for i, (name, mean_rgb, ref_rgb, _) in enumerate(layers):
        mask = masks[i]
        n_pixels = int(mask.sum())

        if n_pixels == 0:
            print(f"  {name}: 0 pixels – skipped")
            layers_data.append((name, mean_rgb, ""))
            continue

        # Marching squares → loops
        raw_loops = marching_squares(mask)

        # Simplify with RDP
        simplified = [rdp(loop, epsilon=args.epsilon) for loop in raw_loops]

        # Filter small/insignificant loops
        filtered = filter_loops(simplified)

        n_loops = len(filtered)
        n_points = sum(len(l) for l in filtered)
        print(f"  {name}: {n_pixels} pixels, {n_loops} loops, {n_points} points")

        d = path_d(filtered) if filtered else ""
        layers_data.append((name, mean_rgb, d))

    # Build SVG
    svg_str = build_svg(w, h, layers_data)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="\n") as f:
        f.write(svg_str)

    svg_bytes = len(svg_str.encode("utf-8"))
    print(f"SVG written to {out_path} ({svg_bytes} bytes)")

    # Render preview
    rendered = render_trace(w, h, layers_data)
    make_preview(rgba, rendered, args.preview)


if __name__ == "__main__":
    main()
