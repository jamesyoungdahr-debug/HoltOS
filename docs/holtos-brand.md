# HoltOS brand guide

The one reference for how HoltOS looks and sounds. Every value here comes from
the file that implements it; when this guide and a file disagree, fix one of
them (see section 9). Checked against the neon rebrand (branch `neon-rebrand`,
after v0.0.7c-alpha), 2026-09-14.

Sources of truth: the design tokens in the-den repo (`design/tokens.json`,
shared by HoltOS's web, Qt and Android surfaces) and the desktop theme files
under `archiso/airootfs/` in this repo.

## 1. Identity

- **Name:** HoltOS, one word.
- **What it is:** an Arch-based distro for media and gaming at home. Steam with
  Proton and Proton GE, a gamescope Game Mode, HoltOS Apps from Flathub, The Den
  for movies and TV, and KDE Plasma dressed as glass.
- **Tagline:** "Media-first Arch", set in mono, uppercase and teal under the
  wordmark.
- **Personality:** cute, but level. The otter earns a sticker; the interface
  still runs the machine.

### Marks (neon rebrand, next major release)

Every mark comes from a ComfyUI render (Liam, 2026-09-14). Nothing is drawn
by hand in SVG or CSS: a hand-drawn otter drifted into a teddy bear twice.
Smaller, one-colour and cut-out versions are derived from the chosen render
by scripts, and shown next to it for review.

- **Otter mark**, the primary mark: a flat purple otter head with a wide
  flattened skull, tiny low ears, lilac whisker pads, long white whiskers and
  a neon rim running magenta on the left to electric blue on the right, with
  two small lime sparks. Render: concept C, seed 4202; app icon seed 4301.
- **Symbolic mark:** the same head as a white one-colour glyph for the tray
  and small sizes (seed 4401).
- **HoltOS Apps icon** (2026-09-15, Liam's pick): a rounded glass tile with
  the magenta-to-blue neon rim, a grid of glowing app squares in purple,
  teal, electric blue and lilac, and a long purple otter curving through the
  grid (flat head, low ears, long body and tail), with lime sparks. Render:
  concept B, seed 5201, image 1
  (`docs/design-references/holtos-apps-icon-B1-seed5201.png`); icon files
  `holtos-apps.png` from `tools/brand/derive_app_icon.py`. The store had used
  the head mark, which reads as a teddy bear at dock size.
- **Otter expressions** (2026-09-15, Liam's picks): the mark's head with the
  feeling in its eyes and mouth, same flat purple, low ears, lilac whisker pad
  and neon rim. **Happy** (closed smiling eyes, smile, lime sparks; seed 6101,
  image 2) for success and "all done"; **Idle** (sleepy closed eyes and a lime
  "z"; seed 6201, image 1) for waiting, empty and nothing-to-do states;
  **Alert** (big round eyes, open mouth, amber sparks, since amber means "needs
  you"; seed 6301, image 2) for warnings. Renders in
  `docs/design-references/holtos-otter-*-seed*.png`; transparent files
  `usr/share/holtos/brand/holtos-otter-{happy,idle,alert}-{1024,512}.png` from
  `tools/brand/derive_expressions.py`. They replace The Den's hand-drawn React
  expressions, which still show the old otter.
- **Full-body otter**, for the login screen and illustration: standing, long
  slender body, webbed feet, long tapered tail, the same neon rim. Render:
  seed 7301 #2. Otters have wide flat heads, ears low on the sides and long
  bodies; round heads with ears on top read as bears.

Files (all derived, never edited by hand):
- `usr/share/icons/hicolor/<size>/apps/holtos-logo.png` (16–512 px) and
  `holtos-logo-symbolic.png` (16–64 px), and
  `usr/share/holtos/brand/holtos-mark-512.png` / `-1024.png`, from
  `tools/brand/derive_logo.py`.
- Login otter and glow, boot watermark and glow, the lockups, the Plasma
  splash mark and the installer's `logo-icon.png`, from
  `tools/brand/derive_splash_art.py`.
- `usr/share/holtos/brand/holtos-lockup-horizontal.png` and
  `-horizontal-light.png` (1080 × 312), `holtos-lockup-stacked.png` and
  `-stacked-light.png` (640 × 760), from `tools/brand/derive_lockups.py`.

### Lockup

- The otter mark on the left, "HoltOS" on the right in Nunito ExtraBold,
  white, on a transparent background; 360 × 104 px in the boot splash, login
  card and Plasma splash.
- The mark fills 80 % of the height; the gap is 16 % of the height.
- **Stacked:** the mark centred above the name, the mark 62 % of the height,
  the name 4 % of the height below it.
- **Light backgrounds:** the same layouts with the name in holt-night
  `#0D0B12`; the mark is unchanged.
- The name is set in the font, not rendered by an image model, so it is
  always spelled right.

## 2. Voice

1. **Plain language over jargon.** "Where should your movies live?", not
   "Select target vdev". Mono type carries the paths and numbers.
2. **State is never decorative.** Teal claims healthy; amber asks for a human.
   "Everything's fine."
3. **Primitives, not illustration**, inside the interface.
4. **Drawn, never spun.** Progress draws (the boot ring draws over 1.6 s);
   nothing spins.
5. **One shout per screen.** A single purple primary action.
6. **Cute, but level.**

Copy examples: "Nothing waiting on you" (empty state), "Everything's fine."
(updater). Icons are stroke icons on a 24 px grid, 1.8 stroke, round caps,
`currentColor`. Never emoji.

## 3. Colour

HoltOS is dark first; there is no light theme.

| Token | Value | Use |
|---|---|---|
| deep | `#0D0B12` | page and window ground |
| surface | `#171423` | panels, views, title bar; the glass tint |
| raised | `#1D1927` | buttons, tooltips, surfaces inside panels |
| hairline | `rgba(255,255,255,.09)` | borders |
| hairline-strong | `rgba(255,255,255,.15)` | stronger borders |
| ink | `#FFFFFF` | text and system icons |
| ink-70 / 55 / 42 / 28 | white at 70 / 55 / 42 / 28 % | secondary text; ink-42 for inactive |
| current | `#B14DFF` | identity and the one primary action; selection, focus, links |
| current-hover | `#C77DFF` | hover on purple actions and links |
| current-deep | `#8F2FE0` | shading only (ears, brow band); visited links |
| current-tint | `rgba(177,77,255,.10)` | active navigation background |
| lilac | `#F4EBFF` | cheek pads, whiskers, focus text, light accents |
| healthy | `#28E0C8` | online, healthy, available, and nothing else |
| warning | `#FFB84D` | needs a human: both neutral and negative states |
| pulse | `#4F7BFF` | electric blue: information and work in progress; cool neon light in art |
| flare | `#FF4FD8` | magenta glow: the logo glow, highlights, gradients with purple; never a state or an action |
| volt | `#C6FF3D` | lime spark: rare "new" markers and sparks in art; never success (teal owns healthy) |

Rules:
- **Five neon colours, five jobs** (Liam, 2026-09-14): purple acts, teal
  means healthy, blue informs, magenta glows, lime sparks. Blue, magenta and
  lime never replace purple for the primary action or teal and amber for a
  state. In illustration and wallpapers all five can mix freely.
- **Purple shouts once per screen.**
- **Teal is a promise about the machine**, never decoration.
- **Amber means "needs you".** There is no red: errors and warnings are both
  amber, and amber is never a second accent.
- Text on solid purple is deep `#0D0B12`, not white.

Ambient layer: glow-current `rgba(177,77,255,.18)`, glow-healthy
`rgba(40,224,200,.07)`, ring `rgba(244,235,255,.05)`, stripe
`rgba(177,77,255,.24)`. Scrims: deep at 92 / 62 / 12 %.

Status badges: available `#28E0C8`; pending and processing `#B14DFF`; partial
and error `#FFB84D`; missing white at 42 % (dot at 28 %).

Contrast: white text must reach 4.5:1 over glass. Use ink, not ink-55, for
primary labels on glass. Inactive windows never dim their text.

## 4. Typography

- **Nunito** (400, 600, 700, 800, 900): display, titles, body, buttons. The
  warmth.
- **JetBrains Mono** (400, 500, 600): paths, labels, numbers, eyebrows. The
  technical truth.

| Role | Size | Weight | Tracking | Line height |
|---|---|---|---|---|
| Display hero | 64 | 900 | −2.6 | 0.95 |
| Display | 42 | 900 | −1.8 | 0.98 |
| Page title | 26 | 800 | −1.2 | 1.05 |
| Section title | 16 | 800 | −0.4 | 1.2 |
| Wordmark | 20 | 900 | −0.6 | 1 |
| Body | 15 | 400 | 0 | 1.6 |
| Body small | 13 | 400 | 0 | 1.55 |
| Label | 13.5 | 700 | 0 | 1.2 |
| Button | 12.5 | 800 | −0.2 | 1 |
| Eyebrow (mono, uppercase) | 10.5 | 400 | 2.2 | 1.2 |
| Meta (mono) | 10.5 | 400 | 0 | 1.7 |
| Field label (mono, uppercase) | 10.5 | 400 | 1.2 | 1.2 |

On the desktop:
- Interface, menus and toolbars: Nunito 10, weight 400; smallest readable
  Nunito 8.
- Window titles: Nunito 10, weight 400 (not bold).
- Fixed width and Konsole: JetBrains Mono 10.
- Login screen: user name Nunito ExtraBold 18, fields Nunito 14, hostname
  eyebrow JetBrains Mono 11 uppercase.
- Installer: Nunito, buttons weight 700.
- Boot menu: Terminus Bold 12×24 (Limine cannot load Nunito).

## 5. Glass

Every window is one continuous pane of frosted glass over the wallpaper.
Reference: `docs/design-references/glass-dolphin-reference.jpg`. Glass only
goes over something worth blurring.

### Desktop (0.0.7a-alpha and the neon rebrand)

| Layer | Value | File |
|---|---|---|
| Blur | KWin's blur forced on every window, title bar and menu: BlurStrength 8, NoiseStrength 1, no tint, corner radius 10 | `etc/xdg/kwinrc` |
| Window fill | surface `#171423` at 15 % | Kvantum `HoltOSGlass.svg`, `window-normal` |
| Dialog fill | surface at 30 % | `dialog-normal` |
| Title bar | opacity 12 (matches the 15 % window fill on screen), active and inactive; no separator line | `etc/skel/.config/klassy/klassyrc` |
| Sidebar, toolbar, tabs, status bar | nothing added | Kvantum SVG |
| Selection / pressed / hover | current at 22 / 30 / 10 % | Kvantum SVG (`itemview-*`, `tab-*`, `tbutton-*`) |
| Window outline | 1 px contrast outline at 12 % (inactive 8 %) | klassyrc |
| Shadow | large; strength 255 active, 128 inactive | klassyrc |
| Konsole | 75 % opacity with blur | `usr/share/konsole/HoltOS.colorscheme` |

- Retune the Kvantum alphas with `tools/glass/kvantum_glass.py`, and keep the
  title bar opacity equal to the window fill.
- Video and creative apps stay opaque (Kvantum's `opaque=` list: VLC, Kdenlive,
  digiKam and others), and so do Chromium and Electron apps.
- **Title bar buttons:** small plain circles on the right (`IconSize=IconSmall`,
  a less cluttered title bar; Liam, 2026-09-14), visible at rest, with no
  close, minimise or maximise glyphs at rest, on hover or on press. They are
  coloured from the scheme's warning, neutral and healthy colours. Hovering
  one spreads a radial glow in its colour onto the glass, clipped to the title
  bar (`ButtonHoverGlowRadius=250`).

### Web, Qt and Android (The Den)

- **Ground:** deep, a purple radial glow top right, a faint teal glow bottom
  left, and one or two ring hairlines.
- **Glass panel:** surface at 70 %, 18 px blur, saturate 140 %, hairline
  border, a 1 px inset highlight (white at 6 %), shadow 1.
- **Floating glass:** surface at 84 %, 28 px blur, shadow 3, large radius.
- **Badges** on deep at 72 % with 8 px blur; **inputs** on deep at 50 %.
- **Reduced transparency** swaps every glass surface for its opaque twin.
- The Den's KDE client moves to the desktop values (handoff: the-den
  `docs/holtos-glass-desktop-handoff.md`).

Readability plan: adaptive contrast in KWin's blur, a per-pixel brightness
clamp so white text keeps 4.5:1 (milestones G8 and G9 in
`docs/holtos-glass-design-plan.md`).

## 6. Shape, space and motion

- **Radius:** sm 8, md 10 (windows, fields, buttons), lg 14 (cards, the login
  card, service icons), pill 999.
- **Space:** 6, 10, 16, 22, 32, 48.
- **Sizes:** sidebar 240 (rail 72), top bar 60, content max 1400, hit target 44,
  posters 112 / 132 / 148 / 220, avatar 28, mobile breakpoint 900.
- **Shadows:** 1 `0 2px 14px rgba(0,0,0,.28)`; 2 `0 8px 24px rgba(0,0,0,.35)`;
  3 `0 24px 60px rgba(0,0,0,.50)`.
- **Motion:** fast 160 ms (hover, focus), base 220 ms (enter, exit, progress),
  draw 1600 ms (boot and loading ring), all on `cubic-bezier(.2,.8,.2,1)`.
  Nothing spins; progress is never indeterminate (show a skeleton instead);
  dialogs scale in from 96 %; reduced motion sets every duration to zero.

## 7. Imagery

- **Wallpapers are atmospheric neon scenes, not abstract shapes** (Liam,
  2026-09-13): a near-black deep ground, glowing purple and teal light, amber
  sparingly, lilac for the hottest cores. Colour in all four quadrants so the
  glass has something to show, a calm upper left and centre for windows, no
  text, no logos except the ring and the otter, 16:9.
- **Shipped:** ten neon sets (Aurora, Bokeh, Cabin, Den, Forest, Nebula, Otter,
  Otter Night, Rain, Rings) at 1920×1080, 2560×1440 and 3840×2160.
  **Default: Neon Otter Night** on the desktop, lock screen, login screen and
  boot menu.
- **Pipeline** (`tools/wallpapers/`): local, free models only (Z-Image-Turbo),
  three seeds per concept for Liam to pick, QA for blank renders, dark
  quadrants and near-duplicates, Real-ESRGAN general-x4v3 denoise and upscale,
  resize with dither to each size, JPEG quality 95 with 4:4:4 chroma.
- Every design brief includes these tokens and the reference screenshot.

## 8. Where the brand is applied

| Surface | What it shows | Files |
|---|---|---|
| Boot menu (Limine) | Otter Night wallpaper, deep backdrop, translucent surface panel, lilac text, purple highlight, HoltOS name in purple | `usr/local/bin/holtos-limine-theme.sh` |
| Boot splash (Plymouth) | deep ground, magenta-purple-blue neon glow, otter mark, dot ring drawing over 1.6 s, lockup | `usr/share/plymouth/themes/holtos/` |
| Login (SDDM) | neon glow, the full-body otter, glass card with the lockup, avatar, one purple Log in button, quiet Restart and Shut down, mono hostname | `usr/share/sddm/themes/holtos/` |
| Plasma splash | deep ground, glow, otter mark, lockup | look-and-feel `org.holtos.desktop` |
| Desktop | glass menu bar on top (launcher, app menus, tray, clock) and a floating dock with a neon rim; Plasma style `holtos-glass`; look-and-feel `org.holtos.desktop`, colour scheme `HoltOS`, Kvantum `HoltOSGlass`, decoration `org.holtos.glass`, Konsole `HoltOS`; Breeze Dark icons and Breeze cursor | `usr/share/`, `etc/xdg/`, `etc/skel/` |
| Desktop, HoltOS Classic | the old single bottom panel on plain glass; Plasma style `holtos-glass-classic` | look-and-feel `org.holtos.classic.desktop` |
| GTK apps | opaque twin of the colours (GTK cannot blur yet) | `etc/skel/.config/gtk-3.0/gtk.css` |
| Installer (Calamares) | deep ground, surface sidebar with the current step in purple, raised inputs | `etc/calamares/branding/holtos/` |
| HoltOS apps | HoltOS Updates, HoltOS Apps, Gaming, Network Shares and the tray, all with `holtos-logo` | `usr/share/applications/` |
| The Den | web UI, KDE client and Android app from the shared tokens | the-den repos |

## 9. Known gaps

- **Plasma style covers panels, popups and tooltips:** `holtos-glass` (and
  Classic) draw the menu bar, the dock, task buttons, popups (45 % glass,
  10 px corners) and tooltips (8 px corners); other widgets (buttons,
  sliders, switches inside popups) still fall back to Plasma's default style.
  The frame generator used to fill only part of each stretched centre tile,
  which left popups half untinted; fixed 2026-09-15, and the same fix may
  remove the faint seams seen where the dock's rounded ends meet its straight
  edges. To be judged on real hardware.
- **List views are as clear as their window (by choice):** since 0.0.7a
  Kvantum's Base and AltBase are fully transparent, so file dialogs, Kate and
  other list views show the same single window tint as Dolphin (Liam: clearer
  glass). Darker list backgrounds would undo that decision; revisit only if
  text over a bright wallpaper proves hard to read on real hardware, and then
  with adaptive contrast (G8, G9) rather than a darker Base.
- **Old numbers in history:** the glass plan's early tables (70 / 60 % for the
  title bar) are kept as history; everything that ships and every tool
  default use the current values.
- **Title bar button colours (settled 2026-09-15, Liam):** the traffic-light
  balance in HoltOS colours, since the palette has no red: magenta flare
  `#FF4FD8` close, amber `#FFB84D` minimise, teal `#28E0C8` maximise, as
  per-button override colours in `klassyrc` (dimmed to 45 % in inactive
  windows). The colour scheme's warning colours are unchanged.
- **Glass depth differs by product:** desktop 30 / 45 %, The Den web and client
  70 / 84 %, SDDM 84 %, Konsole 75 %.
- **Colours outside the tokens:** logo blush `#FF7ABE`, disabled grey
  `#6B6B6B`, Kvantum `#2A2438`, `#262033` and `#221D2F`, Limine bright teal
  `#5FF0DC`, inactive header text `180,180,180`. (The Calamares sidebar text
  and the SDDM and installer hover colours now use the tokens.)
- **Eyebrow weight:** the tokens say 400; the typography page shows 600.
- **Missing logo files:** no vector version of the mark (the icons and the
  lockups are PNGs derived from the render, 16–1024 px). The stacked and
  light-background lockups exist since 2026-09-15. The otter's expressions (happy, idle, alert) are
  rendered for the new mark (2026-09-15); The Den still uses its old React
  versions until its client is rebranded. The old hand-drawn SVG logos are deleted from the image and removed
  from installed systems by `holtos-system-extras`.
- **Not built yet:** GTK glass (G6), Kirigami and Qt Quick glass (G7), adaptive
  contrast (G8 and G9), installer glass (G11), The Den client's live blur, a
  HoltOS Plasma theme. Icons and cursor are stock Breeze.
