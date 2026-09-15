# HoltOS qqc2-desktop-style

HoltOS' fork of [qqc2-desktop-style](https://invent.kde.org/frameworks/qqc2-desktop-style)
(KDE's Qt Quick Controls style), taken at tag v6.30.0 and kept in the HoltOS
repo under `forks/holtos-qqc2-desktop-style` (the `.git` directory dropped,
nothing else). The upstream README.md is kept as is; this file describes what
HoltOS changes.

Why a fork: HoltOS glass (glass plan G7). The style paints the backgrounds of
pages, panes and drawers in Kirigami apps with the solid theme colour.

## Changes from upstream (keep this list current)

Every change is marked with a `HoltOS glass (G7)` comment.

- `org.kde.desktop/Page.qml`: background at 40 % of the theme background.
- `org.kde.desktop/Pane.qml`: background at 40 % of the theme background.
- `org.kde.desktop/Drawer.qml`: background at 60 % (drawers slide over
  content, so they keep a denser tint).

Buttons, text fields, list delegates and text keep their solid colours, so
only one translucent layer sits over KWin's blur. The glass needs
`holtos-plasma-integration` (alpha buffer and blur) and `holtos-kirigami`
(transparent window).

## Updating

Unpack the new tag next to this tree, apply the changes above on top, replace
the tree, bump `pkgver` in `packaging/holtos-qqc2-desktop-style/PKGBUILD` and
copy the dependency list from Arch's `qqc2-desktop-style` PKGBUILD. It must
match the Kirigami version (both are KDE Frameworks releases).

## Building

```
AUR_PKGS=none HOLTOS_PKGS=holtos-qqc2-desktop-style ./build-local-repo.sh
```
