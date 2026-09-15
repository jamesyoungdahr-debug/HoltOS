# HoltOS plasma-integration

HoltOS' fork of [plasma-integration](https://invent.kde.org/plasma/plasma-integration)
(the Qt platform theme every KDE app loads), taken at tag v6.7.5 and kept in the
HoltOS repo under `forks/holtos-plasma-integration` (the `.git` directory
dropped, nothing else). The upstream README.md is kept as is; this file
describes what HoltOS changes. Only the Qt 6 plugin is built.

Why a fork: HoltOS glass (glass plan G7). A Qt Quick window has no alpha
buffer by default, so Kirigami apps stayed opaque whatever their QML painted,
and nothing asked KWin to blur behind them. The platform theme is loaded inside
every Qt app's QGuiApplication constructor, before any window exists, which
makes it the one place that reaches every Kirigami app without patching the
apps.

## Changes from upstream (keep this list current)

Every change is marked with a `HoltOS glass (G7)` comment.

- `qt6/src/platformtheme/kdeplatformtheme.cpp`: `holtosGlassWanted()` and, at
  the start of the constructor, `QQuickWindow::setDefaultAlphaBuffer(true)` plus
  the application property `holtos.glass`. Skipped when `HOLTOS_GLASS=0`, when
  not on Wayland, and for plasmashell, kwin_wayland, krunner, ksplashqml,
  kscreenlocker_greet, ksmserver-logout-greeter, sddm-greeter(-qt6),
  plasmawindowed, xdg-desktop-portal-kde, polkit-kde-authentication-agent-1
  and kded6 (matched on the executable name from /proc/self/exe).
- `qt6/src/platformtheme/kwaylandintegration.cpp`, `shellSurfaceCreated`: for
  normal and dialog QQuickWindows in a glass app (and only when the window did
  not set its own blur hint), `KWindowEffects::enableBlurBehind` and
  `enableBackgroundContrast(0.9, 1.0, 1.4)`, the holtos-glass Plasma style's
  contrast. Fullscreen windows get neither, and a state change switches it.
  Popups and tooltips are left out, as upstream already does for its hints.
- `qt6/CMakeLists.txt` and `qt6/src/platformtheme/CMakeLists.txt`: Qt6::Quick
  is found and linked (for QQuickWindow).

QtWidgets apps are unaffected (they already get glass from Kvantum).

## Things to watch on real hardware

Text contrast over bright wallpapers, GPU cost of blur on the Strix Halo iGPU,
apps that paint their own solid backgrounds (they stay partly opaque), and
fullscreen video.

## Updating

Unpack the new tag next to this tree, apply the changes above on top, replace
the tree, bump `pkgver` in `packaging/holtos-plasma-integration/PKGBUILD` and
copy the dependency list from Arch's `plasma-integration` PKGBUILD (Qt 6 part).

## Building

```
AUR_PKGS=none HOLTOS_PKGS=holtos-plasma-integration ./build-local-repo.sh
```
