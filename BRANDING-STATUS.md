# HoltOS Branding — Status

Working log for the "brand Arch into HoltOS" effort. Updated as each step
lands. See `CHANGELOG.md` for the user-facing version of this same work.

## HoltOS Glass (from HoltOS-Glass-Design-Handoff.md) — built 2026-09-11, NOT yet seen on screen

Everything in this section is implemented and committed but has not been
looked at on a real boot yet. Update each line to "confirmed on screen"
or a bug as it is checked, in boot order:

- Limine: pool-rings wallpaper — **confirmed on screen** (first Glass install's reboot).
- Plymouth: ring draws + glow **confirmed on screen** (live boot). The wordmark
  rendered as boxes — the lockup PNG had been rasterised without Nunito
  in the container; re-rendered (commit 138f2d4), not yet seen in a build.
- SDDM: custom `holtos` theme. First build FAILED to load (`font.pixelSize:
  10.5` — Qt wants an int; SDDM fell back to its built-in theme, so the
  machine stayed usable). Fixed; **confirmed on screen** via
  `sddm-greeter-qt6 --test-mode` on the installed VM: glass card with the
  blurred pool rings + otter behind it, gradient avatar, purple Log in,
  quiet Restart / Shut down. **Confirmed as the real greeter** after a reboot
  of the installed VM (lockup, `HOLTOS-VM` eyebrow, otter at 7% in the corner).
- KSplash `org.holtos.desktop`: naming the package in kdeglobals does NOT
  select the splash; added `etc/xdg/ksplashrc`. Still NOT confirmed: a
  real login on the VM went to the desktop between two 2-second captures,
  and `ksplashqml --test` only showed a dimmed desktop. Needs a slower
  machine or a video capture to see.
- Plasma: **confirmed on screen** — HoltOS palette applied (kdeglobals
  carries the full HoltOS `[Colors:*]` groups), Nunito on panel/clock/
  labels, pool-rings wallpaper, translucent+blurred panel, lock screen
  branded. KWin Blur/Background Contrast are Plasma 6 defaults (no keys
  needed). The layout script's `panel.opacity` did not produce a
  `panelOpacity` key — likely not an API; adaptive default looks right.
- Installer: **confirmed on screen** — mono step bar with purple marker,
  Nunito nav, raised inputs, hairline buttons, deep slideshow with drawn
  dots (white frame gone). Partition-bar first-line labels are STILL dark:
  Calamares paints them with a hardcoded `Qt::black`
  (PartitionLabelsView.cpp), unfixable from QSS — needs a Calamares patch.
- Updater copy ("Everything's fine.") — not yet seen.
- **Glass application windows** (added on request, beyond the brief):
  Kvantum theme `HoltOSGlass` (KvSimplicityDark's SVG with window/dialog
  backgrounds at holt-surface 70% / 84%, blur on, palette mapped to the
  tokens), selected via skel `Kvantum/kvantum.kvconfig` and
  `widgetStyle=kvantum`. **Confirmed on screen** on the installed VM:
  Dolphin and Konsole translucent with the blurred pool rings behind.
  **Title bars are glass too**: Klassy (AUR, in local-repo/) with
  etc/skel/.config/klassy/klassyrc — 70%/60% opacity, blur behind, bold
  centred title, poor-contrast guard on; **confirmed on screen** on the
  VM (Konsole's title visible through Dolphin's). KWin blur strength
  raised to 11 via etc/xdg/kwinrc. The "dim Dolphin labels" seen earlier
  were an artifact of launching apps over SSH without the KDE platform
  theme; launched from the session they are white Nunito — readable.

Contrast to check per §7 of the brief: ink-55 (#8C8C8C) step names on
`#171423`; ink at 85% on deep; error amber on the glass card.

## 2026-09-11 — first full clean-machine build + two fresh installs

Everything below this heading that was marked "not yet tested" has now
been seen live unless listed here. Confirmed on screen: Limine menu
(wallpaper, palette, snapshot entries — screenshots in the session
handoff), Plymouth otter + ring, SDDM background, Plasma dark + accent +
wallpaper, Konsole scheme, installer top/bottom bars, content-area
stylesheet, tray icon under Wayland, branded syslinux splash added (was
still stock Arch). Two installer items remain cosmetic-only: partition-bar
labels render dark-on-dark, and the slideshow page has a white frame. See
`HANDOFF.md` for the full bug list and `PLAN.md` for what's next.

## Limine branding + boot-environment snapshots — implemented, NOT yet tested

Requested after (and deferred until) the full code review below. Two
asks: theme the Limine menu, and set up snapshot support "out of the box."
Root was actually ext4 (verified, not assumed — see the review's own bug
below for why that verification habit matters), so real snapshots needed
a real filesystem change: switched the installed system's root to Btrfs.
Full design/rationale in the plan file this was built from (Limine: brand
it + give it out-of-the-box boot-environment snapshots).

**What changed:**
- New `etc/calamares/modules/partition.conf` / `mount.conf` — Btrfs root
  (`@`/`@home`/`@cache`/`@log`/`@snapshots` subvolumes), ESP bumped to
  1024MiB/512MiB to fit multiple retained kernel+initramfs copies.
- `homelab-limine-install.sh` — `rootflags=subvol=@`, HoltOS wallpaper +
  color theme in `limine.conf`, empty snapshot-block markers for the new
  script to fill in.
- New `holtos-btrfs-snapshot` — read-only root snapshot + ESP kernel copy
  + regenerated Limine menu entry, 5-snapshot retention. Wired into
  `holtos-update-apply`'s `update_system()`/`update_config()` (best-
  effort, non-fatal on failure) and a new tray entry "Create Snapshot
  Now" (`holtos-snapshot-now`).
- Both new scripts added to `profiledef.sh`'s `file_permissions` — this
  project has hit the "script silently loses its executable bit through
  the Windows/WSL2/archiso build round-trip" bug for real, twice, before
  (see the updater tray icon entry below), so this was checked
  deliberately rather than assumed fine this time.

**Verified by research, not by a live boot** (this is a root-filesystem
change — needs an actual fresh VM install, not an in-place test):
- Calamares' real `btrfsSubvolumes` config key/schema (fetched the actual
  stock `mount.conf`/`partition.conf` from calamares/calamares upstream —
  same technique already proven for `bootstrap-override.yaml`).
- `gawk` (used by both this and the earlier resolve_release fix) is a
  real `base` package dependency, confirmed via search, not assumed.
- Deliberately did NOT switch root to ZFS despite the data pool already
  being ZFS — ZFS-root-on-Arch is a much bigger lift (dracut/zfsbootmenu
  territory, not a small addition to what's already built), and did NOT
  use the one existing third-party Limine+Btrfs snapshot tool
  (`limine-btrfs`) — checked its actual GitHub repo: 1 star, zero tagged
  releases, single small distro's own project. Both were real trade-offs
  weighed against a hand-rolled bash approach, not skipped without
  looking.

**LIVE-TESTED (2026-09-09), first real Btrfs install + boot attempt:**
- Fresh install via Calamares completed with no errors. Directly confirmed
  in both the live partition-preview UI and the install job log: ESP
  created at exactly 1024MiB (up from stock 300MiB), root created as
  Btrfs at the remaining ~39GiB. `partition.conf`'s two real changes both
  verified working as intended.
- 4-character password (`allowWeakPasswords`/`minLength: 4`) also
  reconfirmed working during this same install — showed a "shorter than
  6 characters" warning (libpwquality's own floor) but did NOT block
  proceeding, matching the intended design from earlier this session.
- **Real bug found and fixed**: booting the fresh install first tried the
  VM's stale NVRAM boot entries from a PREVIOUS test's install (now
  pointing at a destroyed partition layout after Erase Disk) and hung on
  a black screen. Forcing the VM's first boot device straight to the hard
  disk — which resolves through the generic `/EFI/BOOT/BOOTX64.EFI`
  fallback path, not the `/EFI/limine/` NVRAM one — surfaced a SEPARATE,
  real, pre-existing bug: Limine printed `[config file not found]` and
  refused to boot at all. Root-caused against Limine's actual source
  (confirmed via search: it checks the directory of the EFI binary it was
  loaded from, first): `homelab-limine-install.sh` only ever wrote
  `limine.conf` next to the primary copy, never next to the fallback
  copy — so any firmware that actually falls back to that path (the
  entire reason the fallback copy exists) would always have hit this,
  Btrfs or not. Never caught before because every earlier test this
  session happened to boot via the NVRAM entry, not the fallback. Fixed:
  write the identical config to both `/EFI/limine/limine.conf` and
  `/EFI/BOOT/limine.conf`; `holtos-btrfs-snapshot` updated to keep both
  copies in sync on every snapshot too. Rebuilding and re-testing now.

**CONFIRMED WORKING (2026-09-09), second fresh install + forced-fallback-
path boot:**
- The Limine `[config file not found]` fix — confirmed. Rebuilt, fresh
  install, DVD ejected, VM forced to boot via the generic
  `/EFI/BOOT/BOOTX64.EFI` fallback path (the exact same forced-HDD-first
  test that hit the bug originally) — booted straight through to the
  installed system's own SDDM login screen this time, no error.
- Logged in as the real account, opened Konsole, and directly confirmed
  the whole Btrfs chain end to end: `findmnt /` shows
  `/dev/sda2[/@] btrfs rw,relatime,compress=zstd:1,...,subvol=/@` — root
  is really mounted as the `@` subvolume (not the top-level), with the
  `compress=zstd:1` option from `mount.conf`'s `mountOptions` applied.
- **Second real bug found in the same session**, this one NOT about
  Btrfs: `sudo` was completely broken for the real account (see
  CHANGELOG.md `[Unreleased]` for the full root-cause). Confirmed via
  `groups` that the account IS in `wheel`; confirmed via `pkexec whoami`
  → `root` that the updater's own privilege-escalation path (polkit, not
  sudo) was NOT affected. Fixed in `homelab-cleanup-live.sh`. **Not yet
  re-verified with a rebuild** — logically sound (matches the documented
  sudoers.d mechanism exactly, 0440 permission requirement respected) but
  flagging per this session's own standard until an actual `sudo`
  invocation is re-tested post-fix.

**CONFIRMED WORKING (2026-09-09), third round — sudo fix verified:**
- Rebuilt with the sudoers fix, fresh install, rebooted straight into the
  installed system (no DVD trickery needed this time — ejected before
  reboot, booted the real disk directly), logged in, opened Konsole,
  `sudo whoami` → `root`. Confirmed fixed.

**Two MORE real bugs found while poking around in that same session,
both fixed, both need a rebuild+reinstall to confirm for real:**
- `holtos-tray` segfaults 100% of the time (autostart AND manual
  foreground run) — root-caused via `coredumpctl info` to
  `QSystemTrayIcon.isSystemTrayAvailable()` being called before
  `QApplication()` existed. Confirmed the fix direction empirically on
  the live VM (sed-deleted the offending lines, segfault gone, replaced
  by an unrelated ordinary Python error from the rough test edit) before
  applying the real fix to the source. Also added `qt6-wayland` to
  packages.x86_64 (independently correct, wasn't the actual cause alone).
- Pacman's keyring was never initialized on the installed system —
  `pacman -S` failed outright with "Public keyring not found." This
  would have silently broken `holtos-update-apply system`
  (`pacman -Syu`) for every real install. Fixed in
  `homelab-cleanup-live.sh` (`pacman-key --init` + `--populate
  archlinux`). Confirmed the fix works in isolation on the live VM
  (ran both commands manually, then `pacman -S qt6-wayland` succeeded
  immediately after) — but not yet confirmed as part of the actual
  install pipeline running automatically.

**Still genuinely unverified, flagged explicitly:**
- All three fixes above (tray ordering, qt6-wayland, pacman-key) baked
  into a real ISO build and exercised via a fresh install — in
  progress, this is the next rebuild.
- Whether Limine correctly renders the wallpaper/theme keys as written —
  still not visually confirmed across three rounds now; worth a
  dedicated screenshot next time the Limine menu is on screen.
- The full snapshot-create -> Limine-entry-appears -> boot-into-snapshot
  -> retention-eviction cycle — still not run for real anywhere yet.
- Stale NVRAM boot-entry accumulation across repeated test installs on
  the same VM (10+ "File" boot entries observed) is a real annoyance for
  *this specific VM's* repeated testing, not a HoltOS bug — a real
  physical/fresh VM install only ever runs `efibootmgr --create` once per
  actual disk wipe, so this doesn't need a code fix, just noting it here
  since it's what forced the fallback-path test that found the real bug
  above.

## Full code review pass — one real bug found and fixed, rest clean

Systematic step-by-step review of everything built this session, each step
verified against either the live-tested behavior already confirmed
elsewhere in this file or real upstream source/state (not just re-reading
the code and assuming it's right):

1. **Calamares installer** (branding.desc, navigation/sidebar QML,
   stylesheet.qss, users.conf, capture-user-creds.conf, settings.conf
   ordering) — clean. Cross-checked style keys, sequence order.
2. **Boot chain** (Plymouth, os-release, mkinitcpio) — clean.
3. **KDE desktop defaults** (look-and-feel package, kdeglobals, Konsole
   colorscheme) — clean. Cross-verified matching IDs across files (e.g.
   wallpaper package ID `HoltOS` == `Image=HoltOS` in look-and-feel
   defaults; Konsole `ColorScheme=HoltOS` == that colorscheme file's own
   `Description=HoltOS`).
4. **Updater scripts** (holtos-tray, holtos-check-notify,
   holtos-update-check, holtos-update-picker, holtos-rollback-config,
   holtos-update-apply, holtos-update-history, holtos-first-boot-apps) —
   **found a real, confirmed bug**, see below. Everything else clean,
   including cross-checking `update_the_den`/`update_the_den_client`
   directly against the real `v0.1.0-alpha` release tarballs on GitHub
   (port 8686 in the-den.desktop matches the real the-den.service's
   `--port 8686`; DATABASE_URL path matches; the-den-client's launcher
   path `/opt/the-den-client/src/main.py` matches what
   `update_the_den_client` actually syncs to; icon-theme name
   `the-den-client` matches the real `Icon=` key in that repo's own
   `.desktop`).
5. **Authentik integration** (bootstrap-override.yaml,
   homepage-oidc.yaml, both `.container` volume mounts,
   homelab-generate-secrets.sh, capture-user-creds.conf) — clean, full
   chain re-traced from GlobalStorage capture through deobscure through
   env-file generation through blueprint consumption.
6. **The Den / Den Client cross-check** — done as part of step 4 above.
7. **Package list & profiledef.sh** — clean. All 8 `holtos-*` scripts
   under `usr/local/bin/` have a matching `file_permissions` entry (no
   more, no fewer); the app-menu entry (`holtos-updater.desktop`,
   `Categories=System`) and autostart entry (`holtos-tray.desktop`) both
   point at real files with a real matching icon
   (`holtos-logo.svg`).
8. **Cross-cutting path/ID verification** — this is where the real bug
   surfaced (see below).

### The real bug: annotated-tag sha vs. commit sha

`resolve_release()` (holtos-update-apply) and `holtos-update-check`'s own
copy of the same query both used `git ls-remote --tags --refs`. Checked
this against the actual HoltOS repo on GitHub:

```
$ git ls-remote --tags https://github.com/jamesyoungdahr-debug/HoltOS.git
5664b1c459d4927da9208bbce34ce8a2815f4a92	refs/tags/v0.0.1-alpha
0ba1ac121993bc8c3cf34dd7e9c276354079f03e	refs/tags/v0.0.1-alpha^{}
```

The tag is annotated (confirmed by the peeled `^{}` line existing at
all — lightweight tags never produce one). `--refs` strips peeled lines,
so the old code got `5664b1c...` (the tag *object's own* sha) and treated
it as if it were the commit sha. But `deployed-commit` (what
`holtos-update-check` compares against) is seeded by `build.sh` from
`git rev-parse HEAD` — a real commit sha, e.g. `0ba1ac1...`. Those two
would never be equal, even immediately after a fresh install at the exact
tagged commit — so the tray's 6-hour background check would have shown
"HoltOS v0.0.1-alpha available" forever, starting from first boot, no
matter how current the system actually was. Same annotated-tag situation
confirmed on both companion repos' tags too (the-den, the-den-client),
though it was harmless there since neither compares shas for equality —
only cosmetic (wrong sha logged to history.log).

Fixed both call sites to query without `--refs` and explicitly prefer the
peeled (`^{}`) line — the real commit sha — falling back to the plain ref
sha for lightweight tags (no peeled line, so the ref sha already *is* the
commit sha). Verified the fix directly against the live repo (see
CHANGELOG.md `[Unreleased]` entry) — resolves to `0ba1ac1...`, matching
`git rev-parse HEAD`. **Not yet re-tested in a live VM boot** (would
require a full rebuild + fresh install + waiting to observe no spurious
notification, or manually running holtos-update-check on an already-
installed system) — logically verified against real remote state, high
confidence, but flagging per this session's own standard of being
explicit about what's live-confirmed vs. not.

## Updater error dialog — CONFIRMED WORKING; The Den repos were private

The improved failure dialog (tee output to a tempfile, show the tail on
failure) worked on the first real test — showed the actual `git
ls-remote` failure ("could not read Username for 'https://github.com'")
instead of the old generic message, which is exactly what let this get
diagnosed in one pass instead of another blind guess.

Root cause: `the-den` and `the-den-client` were **private** GitHub
repos. The updater only ever does anonymous git/curl (same as it does
for HoltOS itself) — no code bug, it correctly can't authenticate.
Made both public (user's explicit go-ahead — this is an external
account change, not something to do unprompted). Neither has a tagged
release yet, so the updater should now report "No tagged release found"
cleanly instead of the auth-prompt crash — worth a quick confirm next
test, but this isn't expected to need further code changes.

## Installer content-area theme — new, untested

Added `stylesheet.qss` to rebrand the page content background (still
plain white until now — only the QML top/bottom bars around it had been
themed). Confirmed the mechanism and the `QWidget`-not-`#mainApp`
approach against a real production example rather than guessing, but
this specific file has never been loaded by Calamares yet. **Not yet
tested** — check on the next install that every page actually picks up
the dark theme (not just the ones with simple text fields — Partitions
especially, which has several page-specific widgets like
`#partitionBarView`/`#scrollAreaWidgetContents` this stylesheet doesn't
target directly and which might not inherit the generic `QWidget` rule
cleanly), and that text stays readable everywhere (dropdowns, combo
popups, etc.).

## Authentik login — CONFIRMED WORKING (third live test)

First pass: fixed the password never being deobscured. Login still
failed. Second pass: found the username side was *also* broken (a
rename-based blueprint racing against Authentik's own bootstrap
blueprint) — replaced with a direct override of Authentik's own
`/blueprints/system/bootstrap.yaml`, and hardened the password pipeline
with `LC_ALL=C.UTF-8`. **Third live test: login succeeds** — OS
account's username + password now correctly log into Authentik. This
area can be considered done.

## Dashboard app tile — real bug found and fixed, plus one unexplained error

Follow-up detail: "Server error occurred" on Authentik's own app-picker
page, and clicking through to the dashboard "cannot find [host]:port".

The second part is a confirmed, real bug: `homepage-oidc.yaml`'s
`meta_launch_url` was hardcoded to the internal Podman network hostname
`homepage-dashboard`, which a browser can never resolve — see CHANGELOG.
Fixed via `AUTHENTIK_DASHBOARD_URL`.

The first part ("Server error occurred" on Authentik's *own* library
page) is **not yet explained** — this is Authentik's own core UI, not
anything this session customized beyond the bootstrap blueprint and this
one OIDC blueprint. Possible it's related to the same broken
`meta_launch_url` (if Authentik does strict validation when rendering
app tiles) and gets fixed as a side effect, possible it's unrelated
(e.g. something about the freshly-replaced bootstrap blueprint). **Not
yet tested** — if "Server error occurred" persists after this fix,
get the actual error detail (Authentik usually logs a real traceback
server-side even when the UI just shows a generic message) rather than
reasoning about it blind.

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
systemd autostart generator skip the file outright (see CHANGELOG) —
real, justified fix, but tested live and the tray **still didn't
appear**. Added a "System" category app-menu entry
(`holtos-updater.desktop`) as a reliable fallback — and *that* promptly
surfaced the actual root cause via a clear on-screen error: "missing
executable permissions". Every `holtos-*` script's executable bit
wasn't reliably surviving the Windows/Git Bash → WSL2 drvfs → archiso
build round trip (see CHANGELOG) — almost certainly the real reason the
tray never launched either, autostart-phase key or not. Added all eight
scripts to `profiledef.sh`'s `file_permissions` override. Tested live:
the exec-bit fix confirmed correct — the app-menu entry now launches the
updater successfully, and an actual update attempt returns a real error
(not a permissions failure) — but **autostart still doesn't fire**, so
that fix, while real and necessary, wasn't the (whole) tray-autostart
story either.

**Third pass — actual root cause, confirmed via real log data.** Pulled
`/tmp/holtos-tray.log` off the live installed system (the logging added
in the second pass) instead of guessing again: `yad --notification`
fails outright with "WARNING: This mode not supported outside X11" —
this session runs Wayland, and yad's tray mode is built on GTK3's
deprecated, X11-only `GtkStatusIcon`. Neither of the first two fixes
could ever have mattered; the log shows the script launching and
reaching yad fine both times. Rewrote `holtos-tray` in Python using
PySide6's `QSystemTrayIcon` (proper StatusNotifierItem support, works
under X11 and Wayland both) — no new dependency, PySide6 was already
installed for The Den Client. High confidence this is actually it, but
**not yet tested** — confirm the icon actually appears in the tray on
next boot, and that its menu (Check for Updates / Update... / Rollback
Config / Update History / Quit) all still work the same as before.

Separately, running an actual update surfaced a real UX bug: the
failure dialog only ever said "check your network connection" no matter
what actually went wrong, because the real output was only ever
streamed through the progress dialog before `--auto-close` closed it.
Fixed in `holtos-update-picker`/`holtos-rollback-config` — failures now
show the last few lines of real output. **Not yet tested** — next
failure (there will be one, since the live test that surfaced this
*was* itself a failed update) should show something actually
diagnostic; if it still doesn't, the tee-to-tempfile plumbing itself
needs a second look.

## v0.0.1-alpha tagged and released

`v0.0.1-alpha` is now a real annotated git tag + GitHub Release (with
notes) at commit `0ba1ac1` — the updater's "official release" check has
something to actually find now. Also added rollback (`holtos-rollback-config`),
an update history log/viewer, and release notes in update notifications —
all untested, same caveat as everything else pending a rebuild.

## The Den / The Den Client integration — real releases now exist

Added `update_the_den`/`update_the_den_client` to `holtos-update-apply` —
separately-maintained repos (jamesyoungdahr-debug/the-den,
the-den-client), tag-gated updates only. Both are now tagged
`v0.1.0-alpha` — downloaded and diffed the actual release tarballs
against what these functions expect: `update_the_den` matched exactly
(no changes). `update_the_den_client` didn't — the repo grew its own
`deploy/` (official launcher, `.desktop`, icon) since this function was
written against an earlier version without one; switched to installing
those real files instead of the hand-written launcher/.desktop this
function used to generate.

Still genuinely untested end-to-end: `update_the_den` remains a
hand-translation of the-den's own PKGBUILD/install script (verified
*there* via makepkg/pacman/systemctl per that repo's own STATUS.md, but
never executed through *this* code path). First real test should
exercise the full first-boot auto-install
(`holtos-first-boot-apps.service`, which will finally do something now
that tags exist) end to end — sysusers/tmpfiles creation, the
alembic-migration step, and confirm `the-den.service` actually comes up
and is reachable at `127.0.0.1:8686` — before trusting it on a real
system.

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
