# HoltOS Glass design plan: every window is glass

Liam's end goal (2026-09-14): every window and every user-facing surface is
one continuous pane of frosted glass. Title bar, toolbar, sidebar, tabs,
content and status bar all show the blurred wallpaper, like his reference
screenshot of Dolphin over a pink wallpaper, and text stays readable. This
plan comes after the fork milestones in `holtos-plasma-fork-plan.md`
(Milestones 1-3 are done and Milestone 4 is scaffolded).

Liam's requests, in his words:
- "the whole window needs to be glass"
- "if a window is moved too close to one side of the screen the glass blur
  effect breaks"
- "every window or user facing UI needs to follow the design concept"
- a font contrast adjuster that depends on what is below the glass
- macOS-style close, maximise and minimise buttons, kept on the right side,
  with a glow that spreads onto the glass around the hovered button

## Where it stands

- **Blur is already behind every window.** holtos-kwin's in-tree blur has
  `ForceBlur`, `ForceBlurDecorations` and `ForceBlurMenus` on
  (`etc/xdg/kwinrc`), and `updateBlurRegion` (`src/plugins/blur/blur.cpp`
  370-384) gives every normal window a whole-window blur region.
- **What stops the glass is opaque painting inside the apps.** Anything an
  app fills opaquely hides the blur behind it.
- **Liamtab (the Strix Halo) runs this stack now**: holtos-kwin 6.7.5.r89,
  Kvantum HoltOSGlass and the org.holtos.glass decoration. Most milestones
  can be checked there, not only in the VM.

## 1. Edge bug: glass breaks near the screen edge

**Root cause (from reading the code, not yet seen on screen).** The bug is in
upstream KWin 6.7.5. HoltOS force-blurs every window, which makes it far more
visible.
- In `BlurEffect::blur()` the offscreen textures are sized from the whole
  window (`backgroundRect`, blur.cpp:670).
- Only the part inside the output is ever copied into them: `deviceRegion` is
  clipped to the output in `workspacescene.cpp`, and the copy is at
  blur.cpp:732-735.
- The texels past the screen edge therefore stay transparent, or keep
  whatever an earlier frame left there.
- At BlurStrength 15 the four dual-Kawase passes spread those texels more
  than 100 px into the visible glass.
- The rounded-corner pass blends with `GL_ONE, GL_ONE_MINUS_SRC_ALPHA`, so
  near the edge the glass looks see-through or smeared.
- Windows that span two monitors get the same artifact at the seam.
- Upstream has no fix up to 2026-09-13.

**Fix (holtos-kwin branch `edge-blur-fix`, not compiled yet).**
- Size the textures from the window's rect clipped to the output
  (`blurShape.boundingRect().intersected(viewport.renderRect())`), and return
  early when that is empty.
- In the unclipped-region case, clip each shape rect the same way.
- The texture coordinates, projection and corner mask are all relative to
  `backgroundRect`, and the mask uses `frameGeometry()`, so nothing else
  changes.
- Cost: the textures are reallocated while a window crosses an edge.

**Verify on Liamtab.**
1. Before the fix, drag a Dolphin window half off the left edge over a bright
   wallpaper. Expect a see-through or smeared band along the edge.
   `BlurStrength=4` should shrink the band.
2. Build the branch, install it, log out and back in.
3. Repeat the drag: no band at the edge or at a monitor seam.

## 2. Make every surface glass

| Surface | Today | Change | Where it can be checked |
|---|---|---|---|
| Title bar (org.holtos.glass) | glass, 70/60 % | done | – |
| Window/dialog fill (Kvantum) | glass, 40/55 % | done | – |
| Dolphin content view | opaque | Kvantum `[Hacks] transparent_dolphin_view=true` | Liamtab |
| Other scroll-area views (Kate, Okular, QtWidgets KCMs) | opaque | alpha in Kvantum `base.color` / `alt.base.color` (check in kvantumpreview) | Liamtab |
| Toolbar / menubar | opaque gradient | alpha on the `menubar-*` SVG elements, or `interior=false` | Liamtab |
| Places sidebar (QDockWidget) | opaque `#3d3d3e` | `dock-*` SVG elements at about 0-15 % | Liamtab |
| Tabs | opaque button gradient | a separate translucent tab element | Liamtab |
| Konsole | glass (0.75 + blur) | done | – |
| Kirigami / QtQuick apps (System Settings, Discover) | opaque | fork qqc2-desktop-style: alpha backgrounds in `PlasmaDesktopTheme`; alpha buffer for Qt Quick windows; finishes fork plan Milestone 4 | build, then Liamtab |
| GTK3 | opaque "twin" | rgba `gtk.css` (best effort; libadwaita only partly follows) | Liamtab |
| Plasma panel and popups | Breeze theme | fix the `etc/xdg/plasmarc` mismatch (klassy-dark there, default in look-and-feel), then a HoltOS desktoptheme | Liamtab |
| Calamares | opaque `#0D0B12` QSS | rgba QSS plus translucent top-level windows | VM only (live ISO) |
| Chromium / Electron | opaque | left opaque (window opacity would fade text too) | – |

## 3. Adaptive text contrast

**Chosen design: a per-pixel brightness clamp in the blur shader, all on the
GPU.**
- After the downsample passes, the smallest blur level
  (`renderInfo.framebuffers[m_iterationCount]`) holds a tiny copy of the
  backdrop, and the upsample passes never write to it.
- The on-screen pass (blur.cpp 944 rounded, 966 plain) binds that texture on
  a second texture unit.
- `onscreen.frag` and `onscreen_rounded.frag` read the local average colour
  at the same position, compute its linear luminance L, and scale the blurred
  colour by a smoothstep-eased `min(1, AdaptiveMaxLuminance / L)`.
- Bright or busy wallpaper under a window is darkened locally, just enough
  for light text to reach at least 4.5:1.
- The target: with the 40 % `#171423` window fill on top, a backdrop
  luminance of about 0.30 keeps white text at 4.5:1.
- New kcfg keys `AdaptiveContrast` (on/off) and `AdaptiveMaxLuminance`,
  read in `reconfigure()`.
- It costs one extra texture sample per pixel, with no readback or frame lag.
  It works the same for every toolkit and for title bars.

Backstop: Kvantum text shadows on labels over glass. It is static and only
reaches QtWidgets apps.

Rejected: telling apps the brightness under them (a Wayland protocol or
D-Bus) so they switch palettes. That needs a new protocol, per-toolkit
restyling and full repaints, so it would flicker.

## 4. macOS-style buttons with a hover glow

**Layout and look (settings in `etc/skel/.config/klassy/klassyrc`).**
- The buttons stay on the right. KWin's default layout already puts minimise,
  maximise and close there, and HoltOS sets no `ButtonsOnLeft`/`ButtonsOnRight`.
- `ButtonShape=ShapeSmallCircle`.
- `ButtonBackgroundColorsActive` and `ButtonBackgroundColorsInactive` set to
  `AccentTrafficLights`: red close, yellow minimise, green maximise.
- A macOS-like icon style that shows the symbols clearly on hover. Pick it by
  eye on Liamtab.

**Glow (code in `forks/holtos-window-decoration`).**
- While a button is hovered, `Decoration::paintTitleBar` (breezedecoration.cpp
  1420) paints a soft `QRadialGradient` centred on that button, after the
  title bar fill and before the buttons.
- Colour: the button's own traffic-light colour. Radius: about 2.5 times the
  button's diameter. Alpha follows the button's existing hover animation
  (`m_opacity`, breezebutton.cpp 641-650), fading out towards the edge.
- The title bar is translucent and KWin blurs behind it, so the glow lights
  the glass around the button.
- The button's `hoveredChanged` handler (breezebutton.cpp 70-75) must repaint
  the decoration over the glow's whole rect, not only the button, while the
  animation runs.
- New klassyrc keys `ButtonHoverGlow` (on/off) and `ButtonHoverGlowRadius`.
- Built and checked on Liamtab; decoration changes apply after
  `qdbus6 org.kde.KWin /KWin reconfigure`.

## Milestones

Each one is a small unit, built and checked before the next.

| # | Unit | Verify |
|---|---|---|
| G1 | Edge-blur fix (branch `edge-blur-fix`) | compile, then Liamtab drag test |
| G2 | macOS buttons: klassyrc traffic lights and circles | Liamtab, by eye |
| G3 | Hover glow in the decoration fork | compile, then Liamtab hover test |
| G4 | Kvantum: Dolphin view, sidebar, toolbar, tabs, Base alpha | Liamtab, Dolphin next to the reference screenshot |
| G5 | plasmarc mismatch, then a HoltOS desktoptheme | Liamtab, restart plasmashell |
| G6 | GTK3 rgba css | Liamtab |
| G7 | qqc2-desktop-style fork: Kirigami alpha backgrounds, Qt Quick alpha buffer (with fork plan Milestone 4) | compile, then Liamtab with System Settings and Discover |
| G8 | Adaptive contrast, step 1: bind the smallest blur level, debug view of L | compile, then Liamtab |
| G9 | Adaptive contrast, step 2: clamp and kcfg keys, blur_config.ui | Liamtab, window over a bright wallpaper, check 4.5:1 under text |
| G10 | Text-shadow backstop for QtWidgets labels | Liamtab |
| G11 | Calamares rgba QSS | VM |
| G12 | Regression pass: fullscreen, Game Mode, excluded windows, iGPU frame time | Liamtab and VM |

## Rules for this work

- Compiled forks (holtos-kwin, the decoration, qqc2-desktop-style) change on
  branches until they compile. The ISO pipeline builds the `holtos` branch and
  master, so an untested C++ change must never land there.
- Liamtab has no cmake or KDE build tools and building needs sudo. Compiling
  happens in LiamPC's pipeline or after Liam installs them.
- Never install a new KWin or decoration into Liam's running session without
  him: a crash takes his open apps with it.
