"""Generate the HoltOS Plasma styles from the brand colours.

holtos-glass is the default: a glass menu bar on top and a smoked-glass dock
with a neon rim at the bottom. holtos-glass-classic is plain glass for the
HoltOS Classic global theme (single bottom panel). Both styles also draw Plasma's popups and tooltips as glass. Run from the repo root:
    python tools/glass/plasma_theme.py --root archiso/airootfs
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plasma_panel_svg import panel_background_svg
from plasma_tasks_svg import tasks_svg
from plasma_dialog_svg import dialog_background_svg, tooltip_svg

OPAQUE_ALPHA = 0.85
GLASS_ALPHA = 0.30
# Popups and tooltips sit over busy windows as well as the wallpaper, so their
# glass is one step deeper: the glass plan's dialog depth.
POPUP_GLASS_ALPHA = 0.45
THEMES = [
    ("holtos-glass", "HoltOS Glass", "Glass menu bar and neon-rim dock for HoltOS", "dock"),
    ("holtos-glass-classic", "HoltOS Glass Classic", "Plain glass panel for HoltOS Classic", "classic")
]

def metadata(theme_id: str, name: str, description: str) -> str:
    return json.dumps({
        "KPlugin": {
            "Authors": [{"Name": "HoltOS"}],
            "Category": "",
            "Description": description,
            "EnabledByDefault": True,
            "Id": theme_id,
            "License": "GPL-3.0-or-later",
            "Name": name,
            "Version": "1.0",
            "Website": "https://github.com/jamesyoungdahr-debug/holtos"
        },
        "X-Plasma-API": "5.0"
    }, indent=4) + "\n"

def plasmarc() -> str:
    return "[AdaptiveTransparency]\nenabled=false\n\n[ContrastEffect]\nenabled=true\ncontrast=0.9\nintensity=1.0\nsaturation=1.4\n\n[BlurBehindEffect]\nenabled=true\n"

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(path)

def build(root: Path) -> None:
    for theme_id, name, description, variant in THEMES:
        base = root / "usr/share/plasma/desktoptheme" / theme_id
        write(base / "metadata.json", metadata(theme_id, name, description))
        write(base / "plasmarc", plasmarc())
        write(base / "widgets/panel-background.svg", panel_background_svg(variant, OPAQUE_ALPHA))
        write(base / "translucent/widgets/panel-background.svg", panel_background_svg(variant, GLASS_ALPHA))
        # Plasma uses solid/ for opaque panels; without it the default theme's panel is drawn.
        write(base / "solid/widgets/panel-background.svg", panel_background_svg(variant, OPAQUE_ALPHA))
        write(base / "widgets/tasks.svg", tasks_svg())
        # Popups and tooltips: translucent/ with blur, solid/ and the base file when compositing is off.
        for folder, alpha in (("", OPAQUE_ALPHA), ("translucent/", POPUP_GLASS_ALPHA), ("solid/", OPAQUE_ALPHA)):
            write(base / f"{folder}dialogs/background.svg", dialog_background_svg(alpha))
            write(base / f"{folder}widgets/tooltip.svg", tooltip_svg(alpha))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    build(Path(args.root))

if __name__ == "__main__":
    main()