# HoltOS brand guide

The one reference for how HoltOS looks and sounds. Every value here comes from
the file that implements it; when this guide and a file disagree, fix one of
them (see section 9). Checked against v0.0.7-alpha, 2026-09-14.

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

### Marks

- **OtterMark**, the primary mark: the otter's head, used at 38 px and up. Its
  expression lives in the eyes only: *happy* (all good), *idle* (asleep, flat
  eye bars) and *alert* (needs you: an amber ring around the eye). It is built
  only from circles, one squashed ellipse and rounded rectangles.
- **RingMark**, below 38 px: the pool the otter curls around, which also reads
  as an eye, a lens or a platter. Stroke `max(2, round(size × 0.25))`. An
  optional filled centre dot is the first frame of the boot animation. Any
  brand colour; purple by default.
- **OtterFull**, the full-body otter for illustration (wallpapers, splash):
  flat and rounded, using only current, current-deep, lilac and deep.

Logo colours: head `#B14DFF`; ears and brow band `#8F2FE0`; cheek pads and
whiskers `#F4EBFF`; eyes and nose `#0D0B12`; eye highlight `#FFFFFF`; blush
`#FF7ABE` at 50 % (the one colour outside the tokens).

Files:
- `usr/share/icons/hicolor/scalable/apps/holtos-logo.svg`: the installed icon,
  used by os-release, the About page and every HoltOS app launcher.
- `etc/calamares/branding/holtos/logo-icon.svg` (square) and `logo-wide.svg`
  (horizontal lockup on a baked deep background).
- Rasterised lockups in the Plymouth, SDDM and KSplash themes.

### Lockup

- Otter above 38 px, ring below.
- Wordmark: Nunito 900 at `size × 0.55`, tracking `size × −0.027` px, line
  height 1. The wordmark token is 20 px, weight 900, tracking −0.6.
- Tagline: JetBrains Mono 9 px, tracking 1.6, healthy teal, uppercase.
- Gap between mark and wordmark: 13 horizontal, 10 stacked.
- Reverse version: ring and wordmark in deep on a purple card.

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

Rules:
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

### Desktop (0.0.7-alpha)

| Layer | Value | File |
|---|---|---|
| Blur | KWin's blur forced on every window, title bar and menu: BlurStrength 15, NoiseStrength 1, no tint, corner radius 10 | `etc/xdg/kwinrc` |
| Window fill | surface `#171423` at 30 % | Kvantum `HoltOSGlass.svg`, `window-normal` |
| Dialog fill | surface at 45 % | `dialog-normal` |
| Title bar | surface at 30 %, active and inactive; no separator line | `etc/skel/.config/klassy/klassyrc` |
| Sidebar, toolbar, tabs, status bar | nothing added | Kvantum SVG |
| Selection / pressed / hover | current at 22 / 30 / 10 % | Kvantum SVG (`itemview-*`, `tab-*`, `tbutton-*`) |
| Window outline | 1 px contrast outline at 12 % (inactive 8 %) | klassyrc |
| Shadow | large; strength 255 active, 128 inactive | klassyrc |
| Konsole | 75 % opacity with blur | `usr/share/konsole/HoltOS.colorscheme` |

- Retune the Kvantum alphas with `tools/glass/kvantum_glass.py`, and keep the
  title bar opacity equal to the window fill.
- Video and creative apps stay opaque (Kvantum's `opaque=` list: VLC, Kdenlive,
  digiKam and others), and so do Chromium and Electron apps.
- **Title bar buttons:** small circles on the right, visible at rest, coloured
  from the scheme's warning, neutral and healthy colours. Hovering one spreads
  a radial glow in its colour onto the glass, clipped to the title bar
  (`ButtonHoverGlowRadius=250`).

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
| Boot menu (Limine) | Otter Night wallpaper, deep backdrop, translucent surface panel, lilac text, purple highlight, HoltOS name in purple | `usr/local/bin/homelab-limine-theme.sh` |
| Boot splash (Plymouth) | deep ground, purple glow, otter watermark, dot ring drawing over 1.6 s, lockup | `usr/share/plymouth/themes/holtos/` |
| Login (SDDM) | glass card, avatar, one purple Log in button, quiet Restart and Shut down, mono hostname | `usr/share/sddm/themes/holtos/` |
| Plasma splash | deep ground, glow, purple ring | look-and-feel `org.holtos.desktop` |
| Desktop | look-and-feel `org.holtos.desktop`, colour scheme `HoltOS`, Kvantum `HoltOSGlass`, decoration `org.holtos.glass`, Konsole `HoltOS`; Breeze Dark icons and Breeze cursor | `usr/share/`, `etc/xdg/`, `etc/skel/` |
| GTK apps | opaque twin of the colours (GTK cannot blur yet) | `etc/skel/.config/gtk-3.0/gtk.css` |
| Installer (Calamares) | deep ground, surface sidebar with the current step in purple, raised inputs | `etc/calamares/branding/holtos/` |
| HoltOS apps | HoltOS Updates, HoltOS Apps, Gaming, Network Shares and the tray, all with `holtos-logo` | `usr/share/applications/` |
| The Den | web UI, KDE client and Android app from the shared tokens | the-den repos |

## 9. Known gaps

- **Plasma theme:** `etc/xdg/plasmarc` names `klassy-dark` while the
  look-and-feel uses `default`; the panel and popups are still Breeze. Waiting
  on Liam's pick (G5).
- **Views outside Dolphin still add a layer:** Kvantum's Base and AltBase carry
  40 % on top of the 30 % window fill, so file dialogs, Kate and other list
  views look darker than Dolphin.
- **Stale numbers in comments:** the HoltOSGlass.kvconfig header,
  `kvantum_glass.py`'s defaults and `tools/wallpapers/preview.py` still say
  40 / 55 %; `BRANDING-STATUS.md` says 70 / 84 % and blur 11; the glass plan's
  early tables say 70 / 60 % for the title bar.
- **Title bar button colours:** the plan asked for red, yellow and green; the
  scheme gives amber, amber and teal, so close and minimise may look alike on
  real hardware (checked in LIVETEST.md).
- **Glass depth differs by product:** desktop 30 / 45 %, The Den web and client
  70 / 84 %, SDDM 84 %, Konsole 75 %.
- **Colours outside the tokens:** logo blush `#FF7ABE`, disabled grey
  `#6B6B6B`, Kvantum `#2A2438`, `#262033` and `#221D2F`, Limine bright teal
  `#5FF0DC`, Calamares sidebar text `#8C8C8C`, SDDM hover `#C46EFF` (the token
  is `#C77DFF`), inactive header text `180,180,180`.
- **Eyebrow weight:** the tokens say 400; the typography page shows 600.
- **Missing logo files:** no RingMark SVG, no transparent-background or stacked
  lockup, no monochrome, light-background or symbolic tray icon; the otter's
  expressions exist only as React components; the wide lockup's wordmark is
  live text that needs Nunito installed.
- **Stale positioning:** `README.md` still describes a homelab server for a Dell
  R720, and Kvantum's comment and the look-and-feel defaults still name the old
  pool-rings wallpaper.
- **Not built yet:** GTK glass (G6), Kirigami and Qt Quick glass (G7), adaptive
  contrast (G8 and G9), installer glass (G11), The Den client's live blur, a
  HoltOS Plasma theme. Icons and cursor are stock Breeze.
