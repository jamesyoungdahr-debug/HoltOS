# HoltOS Branding — Status

Working log for the "brand Arch into HoltOS" effort. Updated as each step
lands. See `CHANGELOG.md` for the user-facing version of this same work.

## ⚠️ Highest-risk untested change: custom navigation QML

`calamares-navigation.qml` rebuilds Back/Cancel/Next from scratch (a real
Calamares distro's shipped reference was used, not guessed syntax — see
CHANGELOG — but it has never actually been loaded by Calamares). If
something's wrong with it, the installer could load but leave Next/Back
non-functional, which would block every install. **Test this before
anything else** next time the ISO is rebuilt: click through every page,
confirm Back/Next/Cancel all work, confirm Cancel hides correctly on the
last step, confirm the step bar at the bottom highlights the current step.

## Tested & confirmed (booted in Hyper-V VM)

- Calamares Welcome page logo — no black box (fixed `logo-icon.svg` rgba/bg)
- Calamares sidebar logo — fixed vertical squish (80x80 slot needs a square
  source image; was using the wide icon+wordmark lockup)
- Calamares welcome text — de-branded ("Welcome to the HoltOS installer",
  not "...the Calamares installer for HoltOS" — `welcomeStyleCalamares` was
  backwards)
- Version `0.0.1-alpha` displays correctly throughout the installer
- Plymouth boot animation — otter watermark + Windows-11-style ring spinner
  render correctly (had to switch from the `spinner` plugin, which this
  Plymouth build doesn't ship, to the `script` plugin)
- KDE Plasma dark mode default — confirmed via Quick Settings (Breeze Dark
  selected)
- Branded per-service app-menu icons — render distinctly, not broken
- `capture-user-creds` — confirmed the installer no longer fails to launch
  after switching it from a (nonfunctional) Python job module to a
  `shellprocess` job using `${gs[...]}` GlobalStorage substitution

## Done, not yet tested (pending rebuild + VM boot)

- Desktop wallpaper — real "corner otter" design from Design (otter at 8%
  opacity, bottom-right, lockup + teal hairline), wired via
  `/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc`
- SDDM login background — same design at 14% opacity (no desktop icons to
  protect), wired via `theme.conf.user`

## Known issues / accepted limitations

- Calamares' built-in "About" dialog still says "Calamares" — standard
  upstream disclosure on every Calamares-based distro, not something
  `branding.desc` can suppress. Leaving as-is.
- `capture-user-creds.conf`: a password containing a literal single-quote
  breaks the install step (Calamares' `${gs[...]}` substitution has no
  escaping). Documented in the file itself. Low real-world risk (single-user
  homelab install).
- Background-task build status can report a false "failed" while the actual
  `wsl`/podman build keeps running and succeeds — always confirm via
  `out/build-*.log` (look for "Creating ISO image... Done!") and the ISO's
  mtime, not the task notification alone.

## Environment notes

- The WSL2 Ubuntu instance used for builds also runs a separate, persistent
  podman stack (Plex/Postgres/Authentik/etc.) from another dev session —
  can cause resource contention/slow builds. Don't stop those containers.
- `build.sh` now grants `Authenticated Users:(R)` on the built ISO
  automatically after mkarchiso finishes — without it, Hyper-V's VMMS
  service can't attach the ISO ("Access is denied").

## Done, not yet tested (step 2)

- `/usr/lib/os-release` → HoltOS (`/etc/os-release` symlinks to it already,
  no need to touch `/etc`). Drives KDE "About This System", `hostnamectl`,
  `neofetch`-likes. Added a `holtos-logo` icon so the `LOGO=` field
  resolves to real art instead of a broken/generic icon.

## Done, not yet tested (step 3)

- `/etc/hostname`: `archiso` → `holtos` (live-session terminal prompt is now
  `liveuser@holtos` instead of `liveuser@archiso`). No `/etc/hosts`
  override exists in this profile to also update — stock archiso relies on
  `nss-myhostname`, not a static hosts entry.

## Done, not yet tested (step 4 — final sweep, no ISO built yet)

- `kdeglobals`: `AccentColor=177,77,255` (Plasma accent color format is
  comma-separated RGB, not hex) — buttons/toggles/selection now brand
  purple.
- Konsole: new `HoltOS.colorscheme` (holt-deep bg, holt-lilac fg, brand
  purple standing in for blue/magenta, holt-healthy teal standing in for
  green/cyan) + `HoltOS.profile` + `konsolerc` `DefaultProfile=` so new
  terminals use it by default.
- `/etc/issue`: `Arch Linux \r (\l)` → `HoltOS \r (\l)`.
- Lock screen: `kscreenlockerrc` now explicitly points at the same
  desktop wallpaper image, rather than relying on Plasma's
  version-dependent "inherit desktop wallpaper" default.

## Skipped (not worth the effort for this project)

- Cursor theme, window decoration accent, Dolphin theming — low visual
  impact relative to the work involved. Revisit only if requested.

## Not yet built/tested

None of step 4's changes have been through a rebuild + VM boot yet — next
ISO build should verify all of: os-release, hostname, AccentColor, Konsole
scheme, issue banner, lock screen, plus the still-unverified wallpaper/SDDM
background from step 2.
