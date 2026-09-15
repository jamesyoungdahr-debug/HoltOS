# HoltOS Kirigami

HoltOS' fork of [Kirigami](https://invent.kde.org/frameworks/kirigami) (KDE),
taken at tag v6.30.0 and kept in the HoltOS repo under `forks/holtos-kirigami`
(the `.git` directory dropped, nothing else). Kirigami's own README.md is kept
as is; this file describes what HoltOS changes.

Why a fork: HoltOS glass (glass plan G7). Kirigami apps such as System
Settings and Discover drew an opaque window and page background, so they were
the last desktop windows without glass.

## Changes from upstream (keep this list current)

Every change is marked with a `HoltOS glass (G7)` comment.

- `src/controls/AbstractApplicationWindow.qml`: the window `color` is
  `"transparent"` instead of the theme background.
- `src/controls/Page.qml`: the page background is the theme background colour
  at 60 % opacity.

The glass only shows together with `holtos-plasma-integration`, which gives Qt
Quick windows an alpha buffer and asks KWin for blur behind them, and
`holtos-qqc2-desktop-style`, which tints Page, Pane and Drawer backgrounds.

Kirigami's PageRow decides page transition animations by checking whether a
page background is fully opaque; with translucent pages those transitions
change. Judge that on real hardware.

## Updating to a newer Kirigami

Unpack the new tag next to this tree, apply the changes listed above on top,
replace the tree, bump `pkgver` in `packaging/holtos-kirigami/PKGBUILD` and
copy the dependency list from Arch's `kirigami` PKGBUILD.

## Building

Packaged by `packaging/holtos-kirigami/PKGBUILD` (provides, conflicts with and
replaces `kirigami`). Built with the other HoltOS packages:

```
AUR_PKGS=none HOLTOS_PKGS=holtos-kirigami ./build-local-repo.sh
```
