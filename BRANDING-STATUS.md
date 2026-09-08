# HoltOS Branding — Status

Working log for the "brand Arch into HoltOS" effort. Updated as each step
lands. See `CHANGELOG.md` for the user-facing version of this same work.

## Authentik login — tested live twice, still not confirmed working

First pass: fixed the password never being deobscured (see CHANGELOG for
`Calamares::String::obscure()`). Tested live — login still failed with
the OS account's username + password.

Second pass, same live test: found the username side was *also* broken
— a separate rename-based blueprint racing against Authentik's own
built-in bootstrap blueprint (see CHANGELOG for the full mechanism).
Replaced with a direct override of Authentik's own
`/blueprints/system/bootstrap.yaml`
(`etc/authentik/blueprints/bootstrap-override.yaml`) — no more race,
account created correctly in one step. Also hardened the password
pipeline against a real, separate risk (locale-dependent mangling of the
obscured value's Unicode "Specials"-block characters, which weren't
being forced to any specific encoding before) with explicit
`LC_ALL=C.UTF-8`.

**Neither the bootstrap-override approach nor the LC_ALL hardening has
been tested live yet.** This is now two consecutive live tests where
Authentik login didn't work for reasons that turned out to be different
each time — treat this area as still fundamentally unverified until a
real login actually succeeds, not just until the current known bugs are
fixed. If it's *still* broken next test, worth adding a temporary debug
step that logs the captured username/deobscured-password length (not
the value) to actually see what's landing in authentik.env, rather than
reasoning about it blind again.

## Custom navigation QML — tested live twice, two real bugs found and fixed

`calamares-navigation.qml`/`calamares-sidebar.qml` have now actually been
loaded by Calamares on two real installs. Confirmed: Welcome → Users →
full install completed successfully with the custom top/bottom bars in
place, both times. Two real bugs found on the Finished page's "Next"
button specifically, one per live test so far:
1. Rendered normally, did nothing on click (QML `enabled: false`
   cascading to the nested MouseArea). Fixed.
2. After fixing #1, click registered but the system still didn't
   restart — `next()` on the last page has nowhere to advance to, it's
   a no-op; the real exit/restart trigger is `quit()` (see CHANGELOG).
   Fixed.
Both fixes are in the same file, on the same button, found on
consecutive live tests — **re-verify carefully next build**: click
Next on the Finished page and confirm the system actually restarts,
not just that the button responds. Also re-confirm Back/Cancel/step-bar
highlighting still work (the first fix touched all three buttons, not
just Next).

Also found live: the desktop wallpaper never appeared on the installed
system. Root mechanism was wrong (see CHANGELOG) — replaced with a
proper Plasma Look-and-Feel package. **Not yet tested** — this is a new
mechanism, unverified.

Also found live: the updater's tray icon never appeared at all on the
installed system. `X-KDE-autostart-phase=2` was making Plasma 6's
systemd autostart generator skip the file outright (see CHANGELOG).
Removed — tested live, **still didn't appear**. Root cause not yet
found; removing that key was a real, justified fix (confirmed via
research it's a genuine known systemd-xdg-autostart-generator gotcha)
but evidently not the whole story, or not the actual blocker here.
Added a proper "System" category app-menu entry
(`holtos-updater.desktop`) as a reliable way to reach the updater
regardless — worth checking on the next test whether autostart works
now on its own, since nothing new was changed there this round, or
whether it needs actual debugging (e.g. `systemctl --user status
app-holtos\\x2dtray@autostart.service`-style unit inspection, checking
whether `yad` itself is even installed/working, checking for a stray
process that's running but just not producing a visible icon).

## v0.0.1-alpha tagged and released

`v0.0.1-alpha` is now a real annotated git tag + GitHub Release (with
notes) at commit `0ba1ac1` — the updater's "official release" check has
something to actually find now. Also added rollback (`holtos-rollback-config`),
an update history log/viewer, and release notes in update notifications —
all untested, same caveat as everything else pending a rebuild.

## The Den / The Den Client integration

Added `update_the_den`/`update_the_den_client` to `holtos-update-apply` —
separately-maintained repos (jamesyoungdahr-debug/the-den,
the-den-client), tag-gated updates only, install-on-first-use since
neither has a release yet. This is the **least-tested code in the whole
updater**: `update_the_den` is a hand-translation of the-den's own
PKGBUILD/install script (never executed, only read), and neither repo
has a tag to actually test against yet. Once either repo cuts a `v*`
release, test the full first-install path via the tray picker before
trusting it on a real system — especially the-den's systemd-sysusers/
tmpfiles/alembic-migration sequence.

Also added `holtos-first-boot-apps.service` to auto-install both on first
boot once releases exist (untested — depends on the same untested
install path above), and fixed a real batch-abort bug in
`holtos-update-apply`'s dispatch loop while implementing this (one
failing item was silently skipping every item after it in the same
picker selection).

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
