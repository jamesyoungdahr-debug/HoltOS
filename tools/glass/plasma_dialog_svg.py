"""Builds dialogs/background.svg and widgets/tooltip.svg for the HoltOS Plasma
styles: the same holt-surface glass as the panels, rounded, with a faint white
outline and a blur mask, so Plasma popups (calendar, tray, launcher) and
tooltips match the menu bar instead of falling back to Plasma's default style."""

from plasma_panel_svg import defs, hints, plain_frame

def _svg(body):
    body += '<rect id="hint-stretch-borders" x="300" y="0" width="4" height="4" fill="#ff00ff"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">{defs()}{body}</svg>'

def dialog_background_svg(alpha):
    # Popups: 10 px corners, 8 px content margins.
    body = plain_frame("", 0, 0, alpha, 10, "all")
    body += hints("", 0, 60, 8, 8, 8, 8)
    return _svg(body)

def tooltip_svg(alpha):
    # Tooltips: 8 px corners, 6 px margins.
    body = plain_frame("", 0, 0, alpha, 8, "all")
    body += hints("", 0, 60, 6, 6, 6, 6)
    return _svg(body)

if __name__ == "__main__":
    print(len(dialog_background_svg(0.45)), len(tooltip_svg(0.45)))
