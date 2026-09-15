"""Builds panel-background.svg for the HoltOS Plasma styles."""

SURFACE = "#171423"
FLARE = "#FF4FD8"
CURRENT = "#B14DFF"
PULSE = "#4F7BFF"
WHITE = "#FFFFFF"
NAMES = ["topleft", "top", "topright", "left", "center", "right",
         "bottomleft", "bottom", "bottomright"]


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def box(w, h):
    w = fmt(w)
    h = fmt(h)
    return f'<rect x="0" y="0" width="{w}" height="{h}" fill="#000000" fill-opacity="0"/>'


def part(id_, x, y, w, h, body):
    x = fmt(x); y = fmt(y)
    return f'<g id="{id_}" transform="translate({x},{y})">{box(w,h)}{body}</g>'


def rect(x, y, w, h, fill, op=1):
    x = fmt(x); y = fmt(y); w = fmt(w); h = fmt(h)
    o = fmt(op) if op != 1 else "1"
    # crispEdges: antialiased edges on stretched frame parts showed as seams.
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" fill-opacity="{o}" shape-rendering="crispEdges"/>'


def quarter_d(corner, r, inset=0):
    r = fmt(r)
    if corner == "topleft":
        return f"M {r},{r} H 0 A {r},{r} 0 0 1 {r},0 Z"
    elif corner == "topright":
        return f"M 0,{r} V 0 A {r},{r} 0 0 1 {r},{r} Z"
    elif corner == "bottomleft":
        return f"M {r},0 V {r} A {r},{r} 0 0 1 0,0 Z"
    else:
        return f"M 0,0 H {r} A {r},{r} 0 0 1 0,{r} Z"


def arc_d(corner, r, inset):
    q = r - inset
    i = fmt(inset); r = fmt(r); q = fmt(q)
    if corner == "topleft":
        return f"M {i},{r} A {q},{q} 0 0 1 {r},{i}"
    elif corner == "topright":
        return f"M 0,{i} A {q},{q} 0 0 1 {q},{r}"
    elif corner == "bottomleft":
        return f"M {i},0 A {q},{q} 0 0 0 {r},{q}"
    else:
        return f"M 0,{q} A {q},{q} 0 0 0 {q},0"


def layout(prefix, ox, oy, c, m, bodies):
    positions = [
        ("topleft", ox, oy), ("top", ox + c, oy), ("topright", ox + c + m, oy),
        ("left", ox, oy + c), ("center", ox + c, oy + c), ("right", ox + c + m, oy + c),
        ("bottomleft", ox, oy + c + m), ("bottom", ox + c, oy + c + m),
        ("bottomright", ox + c + m, oy + c + m),
    ]
    sizes = [
        (c, c), (m, c), (c, c), (c, m), (m, m), (c, m), (c, c), (m, c), (c, c)
    ]
    out = ""
    for (name, px, py), (pw, ph) in zip(positions, sizes):
        pid = prefix + name
        body = bodies.get(name, "")
        out += part(pid, px, py, pw, ph, body)
    return out


def size(name, c, m):
    idx = NAMES.index(name)
    if idx in (0, 2, 6, 8):
        return c, c
    elif idx in (1, 7):
        return m, c
    elif idx == 4:
        # The centre tile is m by m. It used to get c by m, so only part of a
        # stretched centre was filled: popups showed an untinted, unblurred
        # right half (seen in the VM, 2026-09-15).
        return m, m
    else:
        return c, m


def fills(c, m, colour, op, radius):
    result = {}
    for name in NAMES:
        w, h = size(name, c, m)
        if radius > 0 and name in ("topleft", "topright", "bottomleft", "bottomright"):
            d = quarter_d(name, radius)
            result[name] = f'<path d="{d}" fill="{colour}" fill-opacity="{fmt(op)}"/>'
        else:
            result[name] = rect(0, 0, w, h, colour, op)
    return result


def hints(prefix, x, y, top, bottom, left, right):
    t = fmt(top); b = fmt(bottom); l = fmt(left); r = fmt(right)
    x1 = fmt(x + 12); x2 = fmt(x + 24); x3 = fmt(x + 24 + int(l) + 8)
    yf = fmt(y)
    out = f'<rect id="{prefix}hint-top-margin" width="4" height="{t}" x="{fmt(x)}" y="{yf}" fill="#ff00ff"/>'
    out += f'<rect id="{prefix}hint-bottom-margin" width="4" height="{b}" x="{x1}" y="{yf}" fill="#ff00ff"/>'
    out += f'<rect id="{prefix}hint-left-margin" width="{l}" height="4" x="{x2}" y="{yf}" fill="#ff00ff"/>'
    out += f'<rect id="{prefix}hint-right-margin" width="{r}" height="4" x="{x3}" y="{yf}" fill="#ff00ff"/>'
    return out


def plain_frame(prefix, ox, oy, alpha, radius, outline):
    c = max(radius, 6)
    m = 20
    b = fills(c, m, SURFACE, alpha, radius)
    if outline == "bottom":
        for name in ("bottomleft", "bottom", "bottomright"):
            w, _ = size(name, c, m)
            b[name] += rect(0, c - 1, w, 1, WHITE, 0.10)
    elif outline == "all":
        b["top"] += rect(0, 0, m, 1, WHITE, 0.12)
        b["bottom"] += rect(0, c - 1, m, 1, WHITE, 0.12)
        b["left"] += rect(0, 0, 1, m, WHITE, 0.12)
        b["right"] += rect(c - 1, 0, 1, m, WHITE, 0.12)
        for name in NAMES:
            if name in ("topleft", "topright", "bottomleft", "bottomright"):
                d = arc_d(name, c, 0.5)
                b[name] += f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="1"/>'
    body = layout(prefix, ox, oy, c, m, b)
    mask = fills(c, m, "#000000", 1, radius)
    body += layout("mask-" + prefix, ox + 60, oy, c, m, mask)
    return body


def neon_frame(prefix, ox, oy, alpha):
    c = 24
    m = 20
    b = fills(c, m, SURFACE, alpha, c)
    # Rim only: inner glow bands on the edges left visible seams at the corners.
    b["top"] += rect(0, 0, m, 1.5, "url(#rimH)")
    b["bottom"] += rect(0, c - 1.5, m, 1.5, "url(#rimH)")
    b["left"] += rect(0, 0, 1.5, m, FLARE)
    b["right"] += rect(c - 1.5, 0, 1.5, m, PULSE)
    for name in ("topleft", "bottomleft"):
        d = arc_d(name, c, 0.75)
        b[name] += f'<path d="{d}" fill="none" stroke="{FLARE}" stroke-width="1.5"/>'
    for name in ("topright", "bottomright"):
        d = arc_d(name, c, 0.75)
        b[name] += f'<path d="{d}" fill="none" stroke="{PULSE}" stroke-width="1.5"/>'
    body = layout(prefix, ox, oy, c, m, b)
    mask = fills(c, m, "#000000", 1, c)
    body += layout("mask-" + prefix, ox + 90, oy, c, m, mask)
    return body


def defs():
    s = '<defs>'
    s += f'<linearGradient id="rimH" x1="0" y1="0" x2="1" y2="0">'
    s += f'<stop offset="0" stop-color="{FLARE}"/>'
    s += f'<stop offset="0.5" stop-color="{CURRENT}"/>'
    s += f'<stop offset="1" stop-color="{PULSE}"/>'
    s += '</linearGradient>'
    s += '</defs>'
    return s


def panel_background_svg(variant, alpha):
    if variant == "dock":
        body = plain_frame("", 0, 0, alpha, 0, "bottom")
        body += hints("", 0, 60, 2, 2, 6, 6)
        body += neon_frame("south-", 0, 100, alpha)
        body += hints("south-", 0, 190, 6, 6, 18, 18)
    elif variant == "classic":
        body = plain_frame("", 0, 0, alpha, 10, "all")
        body += hints("", 0, 60, 4, 4, 8, 8)
    else:
        raise ValueError(f"Unknown variant: {variant}")
    body += '<rect id="hint-stretch-borders" x="300" y="0" width="4" height="4" fill="#ff00ff"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">{defs()}{body}</svg>'


if __name__ == "__main__":
    print(len(panel_background_svg("dock", 0.30)))
