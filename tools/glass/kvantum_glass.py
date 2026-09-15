"""Restyle the HoltOS Glass Kvantum SVG so every window surface is one even pane of glass.

Liam's reference (docs/design-references/glass-dolphin-reference.jpg) shows the title
bar, toolbar, sidebar, tabs and file view sharing one tint. This script sets the alpha of
the window and dialog fills, clears the dock (Places sidebar) and toolbar layers and
their edges, recolours item selection, press and hover to translucent HoltOS purple, and
adds translucent tab elements. It edits the raw SVG text (ElementTree would rename the
xlink prefix Kvantum relies on) and can be run again with new values.

Run by hand from the repo root:
    python tools/glass/kvantum_glass.py --svg archiso/airootfs/usr/share/Kvantum/HoltOSGlass/HoltOSGlass.svg
"""

import argparse
import re
import sys

SIDES = ["left", "right", "top", "bottom", "topleft", "topright", "bottomleft", "bottomright"]
REQUIRED = ["window-normal", "dialog-normal", "dock-normal", "menubar-normal", "itemview-toggled"]
GROUP_TAG = re.compile(r"<g[\s>]|</g>")


def fmt(value):
    """Format an alpha as a short SVG number: 0.4, 0.22, 0, 1."""
    return f"{value:.2f}".rstrip("0").rstrip(".") or "0"


def find_tag(text, eid):
    """Return the match for the opening tag with id=eid, or None."""
    return re.search(r'<(path|rect|g|use|circle)\b[^>]*\bid="' + re.escape(eid) + r'"[^>]*>', text)


def style_of(tag):
    """Return the style attribute of an opening tag ("" when absent)."""
    m = re.search(r'\bstyle="([^"]*)"', tag)
    return m.group(1) if m else ""


def set_style(tag, props):
    """Return the opening tag with the given style properties set or replaced."""
    pairs = {}
    for part in style_of(tag).split(";"):
        key, _, value = part.partition(":")
        if key.strip():
            pairs[key.strip()] = value.strip()
    pairs.update(props)
    style = ";".join(f"{k}:{v}" for k, v in pairs.items())
    m = re.search(r'\bstyle="([^"]*)"', tag)
    if m:
        return tag[:m.start(1)] + style + tag[m.end(1):]
    if tag.endswith("/>"):
        return tag[:-2] + f' style="{style}"/>'
    return tag[:-1] + f' style="{style}">'


def group_end(text, pos):
    """Return the index just after the </g> that closes the <g> opened before pos."""
    depth = 1
    for m in GROUP_TAG.finditer(text, pos):
        if m.group(0) == "</g>":
            depth -= 1
            if depth == 0:
                return m.end()
        elif text[text.index(">", m.start()) - 1] != "/":
            depth += 1
    raise ValueError("unclosed <g> at offset %d" % pos)


def recolour_children(chunk, accent):
    """Fill every child with the accent and drop child opacity (the group carries it)."""
    chunk = re.sub(r"fill:(url\(#[^)]*\)|#[0-9a-fA-F]{3,6})", "fill:" + accent, chunk)
    chunk = re.sub(r'\bfill="[^"]*"', f'fill="{accent}"', chunk)

    def strip_opacity(m):
        style = re.sub(r"(^|;)\s*opacity:[0-9.]+", "", m.group(1)).lstrip(";")
        return f'style="{style}"'

    return re.sub(r'style="([^"]*)"', strip_opacity, chunk)


def apply(text, eid, props, children_accent=None):
    """Set style props on element eid (recolouring a group's children); return (text, changed)."""
    m = find_tag(text, eid)
    if not m:
        return text, False
    old = m.group(0)
    new = set_style(old, props)
    if children_accent:
        new = re.sub(r'\bfill="[^"]*"', f'fill="{children_accent}"', new)
    if children_accent and m.group(1) == "g" and not old.endswith("/>"):
        end = group_end(text, m.end())
        result = text[:m.start()] + new + recolour_children(text[m.end():end], children_accent) + text[end:]
    else:
        result = text[:m.start()] + new + text[m.end():]
    changed = result != text
    if changed:
        print(f"{eid}: {style_of(old)} -> {style_of(new)}")
    return result, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--svg", required=True)
    # Defaults match what ships since 0.0.7a (clearer glass).
    parser.add_argument("--window-alpha", type=float, default=0.15)
    parser.add_argument("--dialog-alpha", type=float, default=0.30)
    parser.add_argument("--dock-alpha", type=float, default=0.0)
    parser.add_argument("--toolbar-alpha", type=float, default=0.0)
    parser.add_argument("--edge-alpha", type=float, default=0.0)
    parser.add_argument("--selection-alpha", type=float, default=0.22)
    parser.add_argument("--pressed-alpha", type=float, default=0.30)
    parser.add_argument("--hover-alpha", type=float, default=0.10)
    parser.add_argument("--accent", default="#b14dff")
    # Menus: holt-surface at the Plasma popups' glass depth.
    parser.add_argument("--menu-alpha", type=float, default=0.45)
    parser.add_argument("--surface", default="#171423")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with open(args.svg, encoding="utf-8", newline="") as f:
        text = f.read()
    missing = [eid for eid in REQUIRED if not find_tag(text, eid)]
    if missing:
        print("missing elements: " + ", ".join(missing), file=sys.stderr)
        return 1

    changed = 0
    edits = [
        ("window-normal", {"opacity": fmt(args.window_alpha)}, None),
        ("dialog-normal", {"opacity": fmt(args.dialog_alpha)}, None),
        ("dock-normal", {"opacity": fmt(args.dock_alpha)}, None),
        ("menubar-normal", {"opacity": fmt(args.toolbar_alpha)}, None),
    ]
    for prefix in ("dock-normal", "dock-focused", "menubar-normal"):
        edits += [(f"{prefix}-{side}", {"opacity": fmt(args.edge_alpha)}, None) for side in SIDES]
    hover_ratio = args.hover_alpha / args.selection_alpha if args.selection_alpha > 0 else 0
    for suffix in [""] + ["-" + side for side in SIDES]:
        edits.append(("itemview-toggled" + suffix, {"fill": args.accent, "opacity": fmt(args.selection_alpha)}, args.accent))
        edits.append(("itemview-pressed" + suffix, {"fill": args.accent, "opacity": fmt(args.pressed_alpha)}, args.accent))
        edits.append(("itemview-focused" + suffix, {"opacity": fmt(hover_ratio)}, None))

    # Tabs and toolbar buttons get flat translucent elements of their own:
    # nothing when idle, the accent on hover, press and toggle.
    states = [("normal", 2000, 0.0), ("focused", 2030, args.hover_alpha),
              ("pressed", 2060, args.pressed_alpha), ("toggled", 2090, args.selection_alpha)]
    for prefix, y in (("tab", 2000), ("tbutton", 2030)):
        if find_tag(text, f"{prefix}-normal") is None:
            block = f'<g id="holtos-glass-{prefix}">\n' + "".join(
                f'<rect id="{prefix}-{state}" x="{x}" y="{y}" width="20" height="20" rx="4" '
                f'style="fill:{args.accent};opacity:{fmt(alpha)}"/>\n' for state, x, alpha in states) + "</g>\n"
            at = text.rfind("</svg>")
            text = text[:at] + block + text[at:]
            print(f"{prefix}-normal, {prefix}-focused, {prefix}-pressed, {prefix}-toggled: added")
            changed += 4
        else:
            edits += [(f"{prefix}-{state}", {"fill": args.accent, "opacity": fmt(alpha)}, None)
                      for state, _, alpha in states]

    # Menus (Qt menus and Plasma's context menus) had no menu-* elements, so
    # Kvantum drew them with the opaque button element they inherit from
    # PanelButtonCommand (glass audit, 2026-09-15). They get one glass pane in
    # holt-surface at the depth of the Plasma popups; the frame matches [Menu]'s
    # 3 px frame.
    menu_parts = [("-topleft", 0, 0, 3, 3), ("-top", 3, 0, 20, 3), ("-topright", 23, 0, 3, 3),
                  ("-left", 0, 3, 3, 20), ("", 3, 3, 20, 20), ("-right", 23, 3, 3, 20),
                  ("-bottomleft", 0, 23, 3, 3), ("-bottom", 3, 23, 20, 3), ("-bottomright", 23, 23, 3, 3)]
    if find_tag(text, "menu-normal") is None:
        block = '<g id="holtos-glass-menu">\n' + "".join(
            f'<rect id="menu-normal{suffix}" x="{2200 + x}" y="{2000 + y}" width="{w}" height="{h}" '
            f'style="fill:{args.surface};opacity:{fmt(args.menu_alpha)}"/>\n'
            for suffix, x, y, w, h in menu_parts) + "</g>\n"
        at = text.rfind("</svg>")
        text = text[:at] + block + text[at:]
        print("menu-normal and its frame: added")
        changed += len(menu_parts)
    else:
        edits += [(f"menu-normal{suffix}", {"fill": args.surface, "opacity": fmt(args.menu_alpha)}, None)
                  for suffix, *_ in menu_parts]

    for eid, props, accent in edits:
        text, did = apply(text, eid, props, accent)
        changed += did

    print(f"{changed} element(s) changed" + (" (dry run)" if args.dry_run else ""))
    if not args.dry_run:
        with open(args.svg, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
