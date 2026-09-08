# Changelog

All notable changes to HoltOS are logged here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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

## [0.0.1-alpha] - initial validated build

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
