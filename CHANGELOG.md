# Changelog

All notable changes to HoltOS are logged here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

- Set the installer's account password requirement to a plain 4-character
  minimum, nothing else — no complexity/class requirements. Added
  `etc/calamares/modules/users.conf` (didn't exist before; Calamares was
  running on its own built-in defaults, which enforce no minimum length
  at all). Deliberately minimal — only touches `passwordRequirements`,
  every other users-module setting stays on Calamares' defaults.
- Authentik's admin login username now matches the OS account's username
  instead of staying the hardcoded `akadmin` (which is all
  `AUTHENTIK_BOOTSTRAP_*` env vars can ever produce — no username
  variable exists there). Added a blueprint
  (`etc/authentik/blueprints/admin-username.yaml`) that renames the
  bootstrap-created account after the fact, using the same OS-account
  username `homelab-generate-secrets.sh` already captures. Falls back to
  a no-op rename (stays `akadmin`) if capture failed. Untested against a
  live instance — flagged in BRANDING-STATUS.
- Fixed Authentik's bootstrap admin password never actually matching the
  OS account's password (real bug hit live: install completes fine,
  Authentik comes up fine, but the credentials just don't work — no
  error anywhere, because there wasn't one to see). Root cause: Calamares'
  GlobalStorage `password` key isn't the plaintext password — the `users`
  module runs it through `Calamares::String::obscure()` first (a
  self-inverse substitution cipher, confirmed against that function's
  actual C++ source: characters <= `0x21` pass through, everything else
  maps to `0x1001F - codepoint`), so `capture-user-creds` was faithfully
  capturing a garbled, unusable string the whole time and
  `homelab-generate-secrets.sh`'s "no captured password → fall back to a
  random one" path was silently kicking in on every single install. Fixed
  by reversing the transform (via `python3`, for correct Unicode
  handling) before using the value. **Reminder, unrelated to this bug:**
  the Authentik login *username* is always `akadmin` — never the OS
  account's own username — Authentik has no setting to change that.
- Fixed the HoltOS updater tray icon never appearing on the installed
  system. `holtos-tray.desktop`'s `X-KDE-autostart-phase=2` key — a
  leftover concept from KSMServer's old phased autostart — makes Plasma
  6's `systemd-xdg-autostart-generator` (which converts autostart
  `.desktop` files into systemd user services) silently skip the file
  entirely, so no service, no tray icon, ever. Removed the key; it
  wasn't serving any purpose here anyway.
- Fixed the Calamares "Next" button doing nothing on the Finished page
  (real bug hit live, after a full successful install). Root cause: the
  custom `calamares-navigation.qml` set `enabled: ViewManager.nextEnabled`
  directly on each button's Rectangle — in QML, `enabled: false` on an
  Item cascades to disable every descendant, including the nested
  `MouseArea`, even though that MouseArea's own color binding (driven by
  hover state, not `enabled`) still rendered the button looking perfectly
  normal and clickable. Every button now stays interactive; each
  `onClicked` guards on the ViewManager flag itself instead.
- Fixed the desktop wallpaper not carrying through to the installed
  system. The `/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc`
  approach was the wrong mechanism entirely — hand-writing Plasma's
  containment file is fragile and Plasma just falls back to its own
  defaults when the file doesn't look like what it expects. The actual,
  correct mechanism (confirmed against a real KDE source file) is a
  Plasma Look-and-Feel package's `contents/defaults`, using
  `[Wallpaper] Image=<wallpaper-package-id>` — same mechanism that
  already made dark mode work correctly via `LookAndFeelPackage=` in
  kdeglobals. Added `org.holtos.desktop` (a new look-and-feel package,
  not overriding any package-owned path this time) cascading dark mode +
  brand accent + the HoltOS wallpaper together, and pointed kdeglobals at
  it instead of `org.kde.breezedark.desktop`.
- Fixed the ISO build failing entirely ("checking for file conflicts...
  Errors occurred, no packages were upgraded", every package download
  wasted): the `/usr/lib/os-release` override landed on a path the
  `filesystem` package actually owns, and mkarchiso copies `airootfs/`
  onto the pacstrap target *before* installing packages — so pacman saw
  our file already sitting there, unowned, and refused to let
  `filesystem` install over it. `/etc/os-release` (a symlink to
  `usr/lib/os-release`, *not* itself shipped by any package — confirmed
  via `pacman -Fl`) is the actual convention every other Arch-based
  distro's archiso profile uses for exactly this reason. Moved the
  override there instead.
- Config updates now log to `/var/lib/holtos/history.log` (every applied
  service/config/system update, world-readable, viewable via the tray's
  new "Update History" item), which also backs a new "Rollback Config"
  tray action (`holtos-rollback-config`) that re-applies the tagged
  release before the currently-deployed one.
- Update-available notifications now include the release's notes (pulled
  from the GitHub Release body for that tag, via the GitHub API — falls
  back to the generic message if the tag has no Release object). Added
  `jq` to parse it.
- Integrated two separately-maintained companion repos, updatable through
  the same picker as everything else: **The Den**
  (`jamesyoungdahr-debug/the-den`, a native systemd service — movie/TV
  library manager) and **The Den Client**
  (`jamesyoungdahr-debug/the-den-client`, its PySide6/Kirigami desktop
  app). Both are gated on tagged releases only, same as `config` — never
  raw commits. Neither is baked into the ISO image (neither has a tagged
  release yet, so there's nothing to vendor at build time); picking
  either in the updater installs it fresh if it's not present, or updates
  it in place if it is, using the same `holtos-update-apply` mechanism.
  `update_the_den` mirrors that repo's own PKGBUILD/`the-den.install`
  step for step (sysusers, tmpfiles, systemd service, venv, alembic
  migrations) but runs it directly instead of through a rebuilt pacman
  package, so the installed system doesn't need a build toolchain for
  what's really just "copy files + venv + pip install." Added `python`,
  `pyside6`, `kirigami`, `qqc2-desktop-style` to the package list.
- Added `holtos-first-boot-apps.service`: on the installed system's first
  boot, automatically installs The Den / The Den Client if either repo
  has a tagged release yet (does nothing, quietly, for whichever doesn't
  — same as picking it manually in the tray before a release exists). A
  marker file makes this run exactly once; the tray's picker still works
  normally afterward for real updates.
- Fixed a real bug in `holtos-update-apply`: picking multiple items in
  the tray where one had no release yet (e.g. Sonarr + The Den, before
  The Den had a tag) silently skipped every item *after* the failing one
  — `set -e` was aborting the whole batch on the first failure. Each
  item is now attempted independently; failures are collected and
  reported at the end instead of stopping the batch.

## [0.0.1-alpha] - 2026-09-08

- Added a HoltOS updater: a system tray icon (`holtos-tray`, autostarted)
  with a per-item picker (`holtos-update-picker`) rather than one
  all-or-nothing update — check boxes for the dashboard, each individual
  podman service (Sonarr, Radarr, Plex, etc.), the shared config
  (Podman Quadlet units + `homelab-*.sh` scripts), and system packages,
  in any combination, applied through a single `pkexec` prompt
  (`holtos-update-apply`) with progress in a yad dialog. Per-service
  updates are a plain `podman pull` + `systemctl restart`, so they're
  always as current as that service's own upstream image — no git
  involved. The config item is the one exception: it's gated on the
  latest *tagged* HoltOS release (e.g. `v0.0.1-alpha`), downloaded as a
  GitHub release tarball (no `git clone`, no repo history) rather than
  raw commits, so in-progress work on the repo never lands on a running
  system. System packages just runs `pacman -Syu` — kernel/OS updates
  are pacman's job, not something the git repo drives.
  The tray's background loop (every 6h, or on demand via "Check for
  Updates") only watches for new tagged releases and notifies when one's
  out; `build.sh` stamps the ISO with its build commit so a fresh
  install's first check is accurate.
- Branded the updater's GTK dialogs: added `breeze-gtk` plus dark-mode and
  brand-purple-accent defaults under `/etc/skel/.config/gtk-{3,4}.0/`
  (yad is a GTK3 app — without a theme it was rendering as plain light
  Adwaita against the rest of the dark/purple system). Also added
  `--window-icon`, a success dialog, and brand-voice copy to
  `holtos-update-picker`'s dialogs.
- Reworked the Calamares installer layout: the step list moved from a
  vertical left sidebar to a horizontal bar along the bottom
  (`calamares-sidebar.qml`), and Back/Cancel/Next moved into a new top
  bar with the HoltOS logo centered between them
  (`calamares-navigation.qml`), replacing Calamares' default widgets.
  Both are custom QML (Calamares ships no built-in fallback for the
  `sidebar: qml` / `navigation: qml` branding.desc options in this
  build), adapted from a real shipped reference (KaOS's branding
  component) rather than written from scratch. Also fixed the
  `style:` section in `branding.desc`: `SidebarTextSelect` /
  `SidebarTextHighlight` were never real Calamares style keys — the
  actual ones are `SidebarBackgroundCurrent` / `SidebarTextCurrent`,
  which now actually drive the current-step/current-button highlight
  color instead of being silently ignored.
- Calamares Welcome page: removed the opaque background rect from
  `logo-icon.svg` that showed as a black box on the white welcome content
  area; converted `rgba()` fills to hex + `fill-opacity` (Qt's SVG renderer
  doesn't reliably support `rgba()`).
- KDE Plasma now defaults to dark mode (Breeze Dark) for both the live
  session and the installed system, via `/etc/skel/.config/kdeglobals`.
- Authentik's bootstrap admin password now matches the OS account's
  password, captured via a custom Calamares job
  (`capture-user-creds`) before Calamares hashes it. The bootstrap admin
  *username* stays `akadmin` — Authentik has no
  `AUTHENTIK_BOOTSTRAP_USERNAME` variable to change that.
- Brand color pass: MOTD and the BIOS (syslinux) boot menu title now use
  `#B14DFF` instead of an arbitrary blue.
- Added a HoltOS-branded Plymouth boot animation (dark background +
  otter watermark) for both the live medium and the installed system.
- Added a HoltOS background color to the installed system's SDDM login
  screen (Breeze theme, `theme.conf.user` override).
- Added branded per-service app-menu icons (Sonarr, Radarr, Prowlarr,
  Jellyseerr, Plex, qBittorrent, Authentik, Dashboard) replacing the
  generic `applications-internet` icon.
- Added a dashboard app favicon (`app/icon.svg`) using the otter mark.
- Renamed ISO metadata from leftover `homelab-os` naming to `holtos`/HoltOS
  throughout `profiledef.sh`.
- Set the HoltOS product version to `0.0.1-alpha` (`branding.desc`,
  `profiledef.sh`).
- Added `build.sh`: wraps the mkarchiso build and backs up any existing
  ISO in `out/` to `out/backups/<timestamp>/` before building, so a build
  never silently overwrites a previous one. Also grants Hyper-V read access
  on the built ISO automatically (the WSL2/podman build writes it with ACLs
  that block the Hyper-V VMMS service otherwise).
- Fixed `capture-user-creds`: the original `interface: python` Calamares
  job module never loaded (this Calamares build has no pythonjob plugin
  compiled in), which broke the installer entirely. Rewritten as a
  `shellprocess` job using Calamares' `${gs[...]}` GlobalStorage
  substitution instead.
- Fixed the Calamares sidebar logo rendering squished — the sidebar's logo
  slot is a fixed 80×80 square; `logo-wide.svg` (a wide icon+wordmark
  lockup) was being force-stretched into it. `productLogo` now points at
  the square-padded `logo-icon.svg`.
- Fixed the welcome page showing "Welcome to the Calamares installer for
  HoltOS" — `welcomeStyleCalamares` was set backwards; `false` (the
  Calamares default) is what gives the clean, de-branded text.
- Replaced the Plymouth `spinner` theme with a `script`-based one — this
  Plymouth build doesn't ship a `spinner` renderer plugin at all, so the
  original theme silently failed to build. The script theme draws the
  otter watermark plus a Windows-11-style rotating ring spinner in brand
  colors.
- Overrode `/usr/lib/os-release` (the real target of the `/etc/os-release`
  symlink) with HoltOS identity — fixes KDE's "About This System" dialog,
  `hostnamectl`, and any `neofetch`-style tool still reporting plain Arch
  Linux. Added a `holtos-logo` icon so the `LOGO=` field resolves.
- Renamed the live-medium hostname from `archiso` to `holtos` (was showing
  in every live-session terminal prompt).
- Set the Plasma accent color to brand purple (`AccentColor=177,77,255` in
  kdeglobals) so buttons/toggles/selection match the brand, not default
  blue.
- Added a HoltOS Konsole color scheme + profile, set as the default for
  new terminals.
- Rebranded `/etc/issue` (console pre-login banner) from "Arch Linux" to
  "HoltOS".
- Explicitly pointed the lock screen (`kscreenlockerrc`) at the desktop
  wallpaper image, rather than relying on Plasma's default inheritance
  behavior.
- Added real desktop wallpaper and SDDM login background art (otter
  bleeding off the bottom-right corner at low opacity, brand lockup +
  teal hairline), designed by the HoltOS Design System project and wired
  in via a Plasma wallpaper package + SDDM `theme.conf.user`.

### Earlier work in this release (initial validated build)

- archiso + Calamares + Limine profile with a validated real
  install → reboot cycle in a Hyper-V VM.
- Podman Quadlets for Authentik (SSO), Sonarr, Radarr, Prowlarr,
  Jellyseerr, qBittorrent, Plex, and the custom dashboard app; stack runs
  off local disk with ZFS mounted separately.
- Auto-generated secrets (`authentik.env`, `dashboard.env`) with no manual
  setup; *arr API keys auto-synced into `dashboard.env` after first boot.
- App-menu launchers for every service's web UI.
- Custom HoltOS Calamares branding (logo, sidebar colors, install
  slideshow) replacing Calamares' stock Arch Linux branding.
