"""Builds tasks.svg for the HoltOS Plasma styles (the dock's task buttons).

Plasma draws each button state from 9-slice frame parts named "<state>-<part>";
each part is a group whose bounding box sets its size. normal-hint-*-margin rects
set icon padding. Design (Liam, 2026-09-14, chosen ComfyUI dock mockup): a glowing
magenta line under running apps, a soft purple glow behind the active app.
"""

FLARE = "#FF4FD8"
CURRENT = "#B14DFF"
PULSE = "#4F7BFF"
WARNING = "#FFB84D"
C = 10
M = 20
GAP = 20


def fmt(v):
    """Format a number, stripping trailing zeros and the decimal point if whole."""
    return f"{v:.2f}".rstrip("0").rstrip(".")


def box(w, h):
    """Return an invisible bounding-box rect of size w×h."""
    w = fmt(w)
    h = fmt(h)
    return f'<rect x="0" y="0" width="{w}" height="{h}" fill="#000000" fill-opacity="0"/>'


def part(id_, x, y, w, h, body):
    """Return a translated <g> element with the given id and bounding box."""
    x = fmt(x)
    y = fmt(y)
    return '<g id="{id_}" transform="translate({x},{y})">{box}{body}</g>'.format(
        id_=id_, x=x, y=y, box=box(w, h), body=body
    )


def rect(x, y, w, h, fill, op, rx=0):
    """Return a <rect> element with the given attributes."""
    attrs = 'x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" fill-opacity="{op}"'.format(
        x=fmt(x), y=fmt(y), w=fmt(w), h=fmt(h), fill=fill, op=fmt(op)
    )
    if rx > 0:
        attrs += ' rx="{rx}"'.format(rx=fmt(rx))
    return "<rect {attrs}/>".format(attrs=attrs)


def quarter(corner, r, fill, op):
    """Return a <path> element for one rounded corner of radius r."""
    r = fmt(r)
    op = fmt(op)
    paths = {
        "topleft": "M {r},{r} H 0 A {r},{r} 0 0 1 {r},0 Z",
        "topright": "M 0,{r} V 0 A {r},{r} 0 0 1 {r},{r} Z",
        "bottomleft": "M {r},0 V {r} A {r},{r} 0 0 1 0,0 Z",
        "bottomright": "M 0,0 H {r} A {r},{r} 0 0 1 0,{r} Z",
    }
    d = paths[corner].format(r=r)
    return '<path d="{d}" fill="{fill}" fill-opacity="{op}"/>'.format(d=d, fill=fill, op=op)


def underline(op, colour):
    """Return two <rect> elements forming a glowing underline."""
    o25 = fmt(op * 0.25)
    o1 = fmt(op)
    c7 = fmt(C - 7)
    c4 = fmt(C - 4)
    return (
        '<rect x="0" y="{c7}" width="{m}" height="6" fill="{colour}" fill-opacity="{o25}" rx="3"/>'
        '<rect x="0" y="{c4}" width="{m}" height="2" fill="{colour}" fill-opacity="{o1}" rx="1"/>'
    ).format(c7=c7, c4=c4, m=fmt(M), colour=colour, o25=o25, o1=o1)


def state(name, ox, oy, fill, fill_op, line_op, line_colour):
    """Return all nine 9-slice <g> elements for one button state."""
    parts = []
    positions = [
        ("topleft", ox, oy, C, C),
        ("top", ox + C, oy, M, C),
        ("topright", ox + C + M, oy, C, C),
        ("left", ox, oy + C, C, M),
        ("center", ox + C, oy + C, M, M),
        ("right", ox + C + M, oy + C, C, M),
        ("bottomleft", ox, oy + C + M, C, C),
        ("bottom", ox + C, oy + C + M, M, C),
        ("bottomright", ox + C + M, oy + C + M, C, C),
    ]
    corners = {"topleft", "topright", "bottomleft", "bottomright"}
    for pname, px, py, pw, ph in positions:
        body = ""
        if fill is not None:
            if pname in corners:
                body = quarter(pname, C, fill, fill_op)
            else:
                body = rect(0, 0, pw, ph, fill, fill_op)
        if pname == "bottom" and line_op > 0:
            body += underline(line_op, line_colour)
        parts.append(part(name + "-" + pname, px, py, pw, ph, body))
    return "".join(parts)


STATES = [
    ("normal", None, 0, 0.95, FLARE),
    ("focus", CURRENT, 0.20, 1.0, FLARE),
    ("hover", CURRENT, 0.10, 0, FLARE),
    ("attention", WARNING, 0.22, 0.95, WARNING),
    ("minimized", None, 0, 0.45, FLARE),
    ("progress", PULSE, 0.25, 0, FLARE),
]


def hint_margins(x, y):
    """Return four magenta <rect> elements defining icon padding margins."""
    return (
        '<rect id="normal-hint-top-margin" x="{x}" y="{y}" width="4" height="4" fill="#ff00ff"/>'
        '<rect id="normal-hint-bottom-margin" x="{x12}" y="{y}" width="4" height="6" fill="#ff00ff"/>'
        '<rect id="normal-hint-left-margin" x="{x24}" y="{y}" width="4" height="4" fill="#ff00ff"/>'
        '<rect id="normal-hint-right-margin" x="{x36}" y="{y}" width="4" height="4" fill="#ff00ff"/>'
    ).format(x=fmt(x), y=fmt(y), x12=fmt(x + 12), x24=fmt(x + 24), x36=fmt(x + 36))


def tasks_svg():
    """Return the complete SVG string for all button states."""
    states = ""
    for i, (name, fill, fill_op, line_op, line_colour) in enumerate(STATES):
        ox = 0
        oy = i * (2 * C + M + GAP)
        states += state(name, ox, oy, fill, fill_op, line_op, line_colour)
    return '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="400" viewBox="0 0 300 400">{stretch}{states}{hints}</svg>'.format(
        stretch='<rect id="hint-stretch-borders" x="200" y="0" width="4" height="4" fill="#ff00ff"/>',
        states=states, hints=hint_margins(120, 0)
    )


if __name__ == "__main__":
    print(len(tasks_svg()))
