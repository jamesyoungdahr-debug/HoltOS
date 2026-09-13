# HoltOS Session Handoff — updated 2026-09-13

What shipped, what broke, what got fixed, and what's still open — for
whoever picks this branch up next. Treat nothing here as already-shared
context. The 2026-09-11 handoff this replaces is in git history
(`git show bc29ef6:HANDOFF.md`).

Commit: see `git log` (this file is committed with the work it describes).
Test VM: `holtos-test` (Hyper-V Gen 2, 6 vCPU, 8 GB, Secure Boot off,
60 GB VHDX under `vm/`). ISO: `out/holtos-0.0.2-alpha-x86_64.iso`
(build 11, from tag `v0.0.2-alpha`); a copy is always on `D:\` (the
Ventoy stick), old copies removed.

## Ground rules (unchanged)

- **Never guess at a root cause — verify it** on a live VM. Read
  `BUILD.md` before touching the pipeline, `README.md` before touching
  install/boot, `CONTEXT.txt` for how to drive the VM.
- **Only build/push when explicitly told to.** (This session was told:
  Liam authorised Phases 1–6 unattended.)
- **Test in the VM, not by inspection alone.** A fresh Erase-Disk install
  picks up partition/bootloader/cleanup changes.
- **Keep changes small and verifiable one at a time.**

## At a glance

- **The dev machine was a blank slate this morning** (no git, WSL,
  podman, Hyper-V, VM, ISO). It was rebuilt and the whole pipeline ran
  clean on it: build 9 (03:35), build 10 (07:27), build 11 = release.
- **Two fresh Erase-Disk installs verified** (builds 9 and 10), plus two
  live-session checks. Every item queued from the last session is now
  seen on screen: HoltOS Glass forks, About this System, power profiles,
  live-ISO guards, installer cosmetics.
- **5 new real bugs found on build 9, all fixed and re-verified on
  build 10** (below). The big one was Liam's "Display shows no
  resolution options": the Display page package was never in the image.
- **Released `v0.0.2-alpha`** (PLAN step 5): CHANGELOG, version strings,
  annotated tag, GitHub Release, ISO rebuilt from the tag so
  `deployed-commit` matches.

## Bugs found & fixed this session

All found on the build 9 install/live session, fixed, verified on build 10.

1. **System Settings > Display did not exist** — opened to "Could not
   find plugin kcm_kscreen". `kscreen` was never in `packages.x86_64`
   (only `plasma-desktop` plus hand-picked packages; `libkscreen` was
   there, which is why `kscreen-doctor` worked). Same root cause for the
   missing volume applet (`plasma-pa`, plus no PulseAudio server at all:
   `pipewire-pulse`/`pipewire-alsa`), Bluetooth (`bluedevil`, `bluez`,
   service enabled), GTK theming, SMART disk health (`plasma-disks`),
   Login Screen (`sddm-kcm`), KWallet unlock (`kwallet-pam`) and Remote
   Desktop (`krdp`). **Verified:** Display page shows 24 modes in the VM,
   volume icon in the tray, `pactl info` reports PulseAudio on PipeWire,
   all KCM plugins present.
2. **`powerprofilesctl` tracebacked** (`No module named gi.repository`) —
   `python-gobject` added. **Verified:** lists balanced/power-saver.
3. **Live session auto-locked after 5 minutes** — the build 9 install
   finished behind the Plasma lock screen (password `liveuser`, which no
   USB installer would know). `Autolock=false` appended to liveuser's
   `kscreenlockerrc` in `customize_airootfs.sh`, live only. **Verified:**
   build 10 install ran 5+ minutes unattended, no lock.
4. **Partition legend still dark-on-dark** despite the 2026-09-11 colour
   rule: Calamares' `PartitionLabelsView::drawLabel` uses hardcoded
   `Qt::black` / `Qt::gray` pens, so no colour rule can work. The
   stylesheet now gives that view a light rounded background.
   **Verified:** both legend rows readable on the Partitions and Summary
   pages.
5. **Build refused: The Den Client v0.4.3 needs `qt6-declarative`** —
   `build-vendor-apps.sh`'s dependency check did its job; package added.

Also: BUILD.md/pacman.conf still described "six AUR packages incl.
klassy" (now five AUR + two HoltOS forks) — fixed.

## After the release (same day, unreleased — builds 12–15)

Liam's afternoon requests, all built and verified in the VM:

- **Real snapshot rollback**: `holtos-btrfs-restore <name>` / `--current`,
  tray "Restore Snapshot...", and a login-time notice when booted into a
  snapshot. Verified: restore back and forward on the build 10 install,
  the tray dialogs and KDE polkit prompt on a fresh build 14 install,
  restore from a booted snapshot, and the boot-time cleanup unit removing
  the replaced roots. Two bugs found live: btrfs WILL delete the mounted
  running root if asked (session died) — the old root is now renamed and
  deleted on the next boot; and the log merge aborted when a side had no
  log file yet (pipefail) — merge now tolerates missing files, includes
  the running system's log, and reconciles the log with the subvolumes.
- **Other OSes in the boot menu**: `holtos-limine-other-os` scans every
  ESP for Windows Boot Manager / shim / GRUB / systemd-boot and writes
  `protocol: efi` entries (install time, kernel updates, tray "Rescan
  Boot Menu"). Verified with a second VHDX carrying a fake Windows and
  Ubuntu ESP: entries appear on a fresh install and the "Windows" entry
  chainloads the loader on the other disk via `guid()`.
- **Limine themed as HoltOS**: branding line, Terminus 12x24 font
  (converted at build time), translucent panel, per-entry comments,
  collapsed Snapshots submenu. Screenshots in the session scratchpad.
- **yad 15 removed `--question`/`--info`**: five dialogs (two of them in
  the release) silently failed; all switched to the plain dialog.
- The test VM now has a second disk `vm/fake-windows.vhdx` (fake ESP);
  keep it attached, it is what exercises the other-OS scan.
- **Released `v0.0.3-alpha`** (tag moved once before the GitHub release
  existed; ISO build 16 from the final tag). Liam's rule "every
  component updates from our own sources": the config update now syncs
  the whole HoltOS component whitelist from the tarball, re-themes
  Limine, rescans OSes; HoltOS-built packages are a pacman repo on the
  GitHub release tagged `packages` (`tools/publish-packages.sh` — rerun
  after every `build-local-repo.sh`), appended to installs' pacman.conf
  as `[homelab]` via `usr/share/holtos/pacman-homelab.conf`. Verified on
  the VM's build 14 install: update to v0.0.3 synced 40+ files, added the
  repo section, `pacman -Sy` fetched our database from GitHub,
  `holtos-update-check` then exits 1. **Installs of 0.0.2 cannot pull
  this by themselves** (their updater only copied install scripts) —
  the release notes carry a one-liner, or reinstall.
- **Network Shares** (after the 0.0.3 tag, unreleased): `holtos-shares`
  GUI + `holtos-share` root backend, systemd automount units under
  `/mnt/shares`, SMB creds root-only, unprivileged listing. Verified in
  the VM against local Samba/NFS servers (the VM still runs them:
  `/srv/testshare`, `/srv/testnfs`).
- **HoltOS is a media and gaming/entertainment focused distro** (Liam).
  `docs/holtos-must-haves-and-plan.md` is the feature list and build
  order; README now credits the forks (KWin/Better Blur, Klassy,
  Terminus, ...) and states the AI assistance (Claude Fable 5.1).
- Strix Halo is Liam's next real machine: nothing AMD-specific needed
  beyond what's in the image; hardware detection now logs `vainfo` /
  `vulkaninfo` for AMD/Intel so `hardware.log` shows what the stack sees.

## Confirmed working (build 10, on screen or over SSH)

Live ISO → branded Plasma desktop in ~40 s, no tray, no first-boot unit,
Calamares via `pkexec calamares` with no password. Erase-Disk install in
< 3 minutes. Installed system: SDDM glass greeter, Btrfs `@` with
`compress=zstd:1`, Limine entry `/HoltOS` with the right root UUID,
`systemctl --failed` empty, `journalctl -p err -b` only the harmless TDX
line, The Den active with HTTP 200 on :8686 and both apps stamped in
`history.log`, tray running, pacman keyring 185 keys and `pacman -Sp`
works after `-Sy`, `holtosglass` the only blur effect loaded with the
`org.holtos.glass` decoration, Konsole/Dolphin translucent with blurred
content behind them, About this System branded, hardware detection
logged "No NVIDIA GPU — nothing to install".

## Game Mode and fixes (evening, builds 16-20)

- **Game Mode** (CHANGELOG [Unreleased]): `holtos-gamemode-session`,
  `steamos-session-select`, `holtos-session-apply` (+ polkit rule), tray
  "Game Mode now" / "Start in Game Mode", greeter session picker. Fresh
  build 18 install: switch from the app menu -> SDDM autologin into the
  gamescope session -> gamescope dies (VM has no GPU) -> one-shot relogin
  back into Plasma -> autostart entry clears the one-shot. Two SDDM facts
  cost most of the evening: it only recreates the display when the session
  helper exits 0 (so the session script always exits 0), and with no
  state.conf it preselects the first session file alphabetically (so
  installs seed it with Plasma).
- **Updater**: The Den Client launcher/.desktop/icons refresh on every
  update (they were first-install only, which hid the client's icon fix).
- **Live medium**: udev rule marks the boot ISO/EFI UDISKS_IGNORE, dropped
  on install; installed motd is a one-liner instead of the live text.
- **chromium** added: The Den v0.5.1 depends on it; build-vendor-apps
  stops the build otherwise.

## HoltOS Glass v2 + KDE engine fork (2026-09-13, in progress)

- Diagnosed live in the VM why HoltOS's glass didn't match Liam's
  reference photo: not a bug in the blur effect (proved by swapping in
  stock unmodified KWin blur — same flat result), but HoltOS's own default
  wallpaper is nearly solid black outside one corner, plus Kvantum's
  window/dialog fill was too opaque (55%/72%) to show much of a background
  even when one has color. Confirmed by swapping the VM to KDE's stock
  colorful wallpaper live — Dolphin immediately showed real glass.
- Tuned and validated live: kwinrc's `[Effect-holtosglass]` (BlurStrength
  to max 15, no tint per Liam's "look exactly like the example", Saturation
  back to 100) and Konsole's colorscheme (Opacity 1->0.75 + Blur=true,
  restoring translucency BRANDING-STATUS.md already documented as intended
  but had regressed to fully opaque). Both committed as uncommitted repo
  changes (not yet pushed), reviewed, ready to fold into the next commit.
- Kvantum SVG alpha (.40/.55) and Klassy title bar opacity (45/40) were
  only tuned live in the VM's own files, not yet ported into the repo —
  the title bar change specifically is unverified (Klassy's decoration
  plugin caches opacity once per session; needs a logout/login to confirm
  it actually applies, not done yet).
- **Bigger decision**: Liam chose to fork KWin and plasma-workspace
  outright for full engine-level control, rather than keep tuning the
  existing lightweight plugin forks (`holtos-glass-effect`,
  `holtos-window-decoration`) — those have a real ceiling (dual-Kawase
  blur can't reach the reference's softness; System Settings' Kirigami
  sidebar isn't reachable by a KWin plugin or Kvantum at all). Forked to
  `jamesyoungdahr-debug/holtos-kwin` and `holtos-plasma-workspace`, pinned
  to v6.7.5, `holtos` branch created in each. Full plan with milestones:
  `docs/holtos-plasma-fork-plan.md`. This is a big, ongoing commitment
  (two large KDE C++ codebases, maintained against upstream indefinitely)
  — treat as its own project, not a quick pass. Nothing beyond forking +
  pinning the tag has happened yet.
- Tried to get the test VM real GPU-accelerated rendering (it runs on
  llvmpipe/software today) by DDA-passing the host's idle AMD integrated
  GPU to it. Failed: the host's BIOS doesn't have IOMMU (VT-d/AMD-Vi)
  enabled, which DDA requires — Windows error was "a hypervisor feature is
  not available to the user." Cleanly reverted (GPU back on the host,
  re-enabled, VM confirmed running normally). Liam is rebooting to check
  the BIOS setting; redo the same DDA steps once it's on. Deliberately did
  NOT pass through the 4090 too — that would take it away from LM Studio
  entirely while assigned, and the 4090 was still needed for coding.

## Fork Milestones 1-4, gaming/NVIDIA backlog, disk health (2026-09-13, autonomous run)

Liam authorised working through every milestone of `docs/holtos-plasma-fork-plan.md`
unattended, plus backlog items while builds ran. Everything below is committed
in this commit; nothing is pushed, tagged or released.

- **Milestone 1 done**: both from-scratch PKGBUILDs compile (17 rounds of
  real dependency-name fixes, each verified against archlinux.org rather
  than guessed). Artifacts in `local-repo/`.
- **Milestone 2 built, but boots to a crash**: `provides=/conflicts=/replaces=`
  on both PKGBUILDs + explicit `packages.x86_64` lines make pacman take our
  packages instead of `extra`'s — confirmed by the full ISO resolving 874
  packages with no stock `kwin`/`plasma-workspace` and no errors.
  (`IgnorePkg` was tried first and is the WRONG tool: it blocks the name
  outright instead of deferring to a `provides=`.) ISO
  `holtos-0.0.4-alpha-x86_64.iso` built. The first-ever live boot of this
  build: **`kwin_wayland` segfaults in `KWin::Application`'s constructor**,
  inside Qt's platform-theme init (`createPlatformIntegration` ->
  `KdeTheme::createKdeTheme` -> `QGuiApplicationPrivate::handleThemeChangedEvent`);
  every other Plasma process then crash-loops for lack of a compositor.
  Diagnosed on the VM via tty3 + `journalctl` + `coredumpctl info
  kwin_wayland`. Version skew ruled out (`.BUILDINFO` in the package matches
  the live `qt6-base-6.11.2-3`/`frameworkintegration-6.30.0-1` exactly).
  Suspect: `-DKWIN_BUILD_GLOBALSHORTCUTS=ON` (re-enabled this session with
  `kglobalacceld` only as a makedepend, not a runtime dep). Reverted to OFF
  and a rebuild was in flight when this handoff was written (see "Still
  open"). Research weakly contradicts the suspect (missing kglobalacceld is
  documented to degrade silently, not crash) — if the rebuild still crashes,
  next step is a debug-symbol build (`options=(!debug)` currently strips
  them) and checking KWin's internal QPA plugin vs the KDE theme plugin.
- **Milestone 3 applied**: the HoltOS blur additions (tint, brightness,
  force-blur, corner radius — ~149 lines, shaders byte-identical) merged
  into `holtos-kwin`'s in-tree `src/plugins/blur/` keeping stock naming;
  committed+pushed to the fork as 75d843a. Compiling in the same in-flight
  rebuild. `holtos-glass-effect` NOT removed yet — only after this is
  verified working.
- **Milestone 4 scaffolded**: `jamesyoungdahr-debug/holtos-systemsettings`
  forked, `holtos` branch off v6.7.5, `packaging/holtos-systemsettings/PKGBUILD`
  written from CMakeLists.txt ground truth (every KF6 name verified).
  Deliberately not built or wired in until Milestone 2 is stable.
- **Build pipeline fixes**: `build-local-repo.sh` persists pacman's cache
  in `.pacman-cache/` (saves ~266MB of downloads per retry);
  `build-aur-packages.sh` now `pacman -U`s each AUR package right after
  building it (repo-add only ran at the very end, so an AUR package
  depending on an earlier one in the same run — gamescope-session-steam-git
  on gamescope-session-git — would have failed); `/forks/<pkg>` is optional
  for git-sourced PKGBUILDs. Two hard-won operational rules, saved to
  memory: never edit a script while it's bind-mounted into a running
  container (bash re-reads it from disk mid-run — cost one full rebuild),
  and `TaskStop` does not stop the podman container underneath.
- **Gaming backlog (1.1/1.2)**: `holtos-gaming` (PySide6 "Gaming" page:
  versions, Proton GE check/update, Game Mode toggle) + tray entry + .desktop;
  `xdg-desktop-portal-kde` added (was referenced in the doc, missing from the
  image); `gamescope-session-git`, `gamescope-session-steam-git`,
  `decky-loader` added to the AUR build list but NOT to `packages.x86_64`;
  `/usr/lib/os-session-select` shim written (the exact hook the real
  gamescope-session-steam `steamos-session-select` execs — source-verified,
  it is the only path). Decky Loader's polkit rule is researched and drafted
  in the doc but not written: security-relevant, wait until decky-loader
  itself builds.
- **NVIDIA**: `homelab-detect-hardware.sh` also writes
  `/etc/modprobe.d/nvidia-drm.conf` (`modeset=1 fbdev=1`). `gamescope-wsi`
  is not a real package (bundled in gamescope). HDR/VRR under gamescope on
  NVIDIA is still immature upstream — documented, not "fixed".
- **Disk health (section 4)**: `etc/smartd.conf` -> `holtos-disk-alert`
  records SMART failures; `holtos-scrub.timer` (monthly) scrubs every Btrfs
  fs and ZFS pool; `holtos-disk-alert-notice` autostart shows alerts at
  login (root services can't reach the desktop). `smartmontools` explicit
  in the package list; updater's enable loop now covers `holtos-*.timer`.
  Syntax/shellcheck clean, not run on a live install yet.
- **Machines**: LiamPC dual-boots a real HoltOS install (RTX 4090) — the
  right target for the NVIDIA work once VM-verified, via the `packages`
  release + updater, never a reflash. **Never reboot LiamPC yourself**
  (Liam). Both LM Studio bridges (4090 + 4080) are co-primary workers.

## Updater redesign (2026-09-13, branch `updater`)

Liam: make the updater work like Windows Update. No clicking to check, a
real version check, visible progress, user control over automatic
installs, everything a normal update covers (kernel and the rest), and OS
and app updates inside Game Mode's own Steam update page. Every unit was
drafted by the local models except the polkit action, the polkit rule and
the settings helper (security-sensitive, written by hand).

- **Pieces**: `holtos-update-status` (root; checks HoltOS, The Den and
  Client, `checkupdates`, Flatpak and fwupd, writes
  `/var/lib/holtos/update-status.json`; `--auto` installs what
  `/etc/holtos/updates.conf` allows); `holtos-update-check.{service,timer}`;
  `holtos-update-install` and its `.service` (progress to
  `/run/holtos-update/progress.log`); `holtos-update-apply` (skips what is
  installed, `available`, `--reinstall`, `@@ item stage pct [bytes]`
  progress lines, flatpak and firmware items, pacman with the keyring first
  in a download step and an install step); `holtos-update-settings`
  (validating root writer plus the timer drop-in); `holtos-updates` (the
  PySide6 window); `holtos-tray` (reads the status, notifies);
  `/usr/bin/steamos-update`, `steamos-polkit-helpers/` and the
  `jupiter-biosupdate` stub; `org.holtos.updates.policy`;
  `51-holtos-updates.rules`. Removed: `holtos-update-check`,
  `holtos-check-notify`, `holtos-update-picker`, `holtos-update-history`.
  New packages: `pacman-contrib`, `fakeroot` (checkupdates needs it),
  `fwupd`.
- **Verified on the build 23 live VM** (files copied in; the services'
  live-medium condition lifted with a `/run` drop-in for the test): a status
  check in about 2 seconds; Steam's `check` exits 0 with an update and 7
  without, and the duplicate-detection probe exits 0; the settings helper
  rejects bad values and keys (including `04:00;rm`) and writes the timer
  drop-in; HoltOS, The Den and The Den Client skip as already installed; the
  window refreshes by itself, and "Check for updates" and "Install now"
  start the root services with no password prompt when it is opened from
  the desktop session; the install log ends `@@ all finished 0` and the
  status refreshes. Two bugs found live and fixed: an image built from an
  untagged commit offered its own release again (the same tag now counts as
  installed), and `checkupdates` failed without `fakeroot`.
- **Testing gotcha**: polkit judges the caller's login session. A window
  started from an SSH shell belongs to a remote, inactive session and is
  correctly refused; open it from the desktop (KRunner or the menu).
- **Not yet verified**: the tray (it exits on the live medium), the timer
  and automatic installs on an installed system, Steam's update page and the
  Game Mode exit check (need a real GPU), fwupd with real devices, and a real
  system or Flatpak update with its progress. Next: an ISO from this branch
  and a fresh install in the VM.

## HoltOS Apps and performance defaults (2026-09-13, branches `apps`, `defaults`)

- **HoltOS Apps** (`holtos-apps`, `usr/share/holtos/apps.json`,
  `etc/flatpak/remotes.d/flathub.flatpakrepo`, `holtos-apps.desktop`, tray
  entry; packages `flatpak`, `flatpak-kcm`). 27 curated apps, every Flathub
  ID checked against Flathub's API (Ryujinx is gone from Flathub and was
  dropped). Verified on the build 24 live VM: the Featured page with
  Flathub icons, search ("flatseal": 11 results), installing Flatseal from
  the desktop session with no password prompt (about 40 seconds), Open and
  Remove on its card, and the Installed tab before and after removal. Found
  live: Flatpak only applies `remotes.d` the first time root uses the
  system installation, so search found nothing on a fresh system. Fixed two
  ways: the image creates the system repository at build time (verified to
  work with networking cut off) and the store refreshes the Flathub
  catalogue when it opens (polkit lets the active user do that without a
  password). Not yet verified: both fixes in a built image.
- **Defaults**: `60-holtos-ioschedulers.rules` (verified live: rotational
  disks switch to `bfq`) and `libcec`. Already covered, verified on the VM:
  zram (3.9G, zstd), `vm.max_map_count` 1048576 from Arch's own
  `10-arch.conf`, and gamemode's default performance governor and profile.
- **Controller drivers, built and added to `packages.x86_64`** (not yet
  booted in an image): `xpadneo-dkms` 0.10.4 and `game-devices-udev` 1.0
  are in `local-repo/` and its database. The first build exposed two
  problems: installing each built package inside the container ran DKMS
  against a kernel the container does not have (now `pacman -U --dbonly
  --nodeps`, which also protects `zfs-dkms`), and game-devices-udev's signed
  tag needs its maintainer's key (Fabian Bornschein,
  6E58E886A8E07538A2485FAED6A4F386B4881229, imported by full fingerprint).
  Rebuild with `AUR_PKGS="xpadneo-dkms game-devices-udev" HOLTOS_PKGS=none
  ./build-local-repo.sh`, then add both to `packages.x86_64`.
- **xone left out**: its firmware package downloads Microsoft's driver,
  which the image cannot redistribute.

## Still open

- **Milestone 2 crash: root-caused, fixed and verified on a fresh ISO (build 23).**
  Not GLOBALSHORTCUTS (build 22, with it OFF, crashed identically). Cause:
  `replaces=(kwin)`/`replaces=(plasma-workspace)` means the stock
  packages never install, so their transitive runtime deps were missing:
  `plasma-integration` (no `KDEPlasmaPlatformTheme6.so`, so Qt's built-in
  fallback `QKdeTheme` segfaults), `kactivitymanagerd` (plasmashell aborts
  its shell load), `kglobalacceld`, `kde-cli-tools`, `milou`, `qt6-tools`,
  `aurorae`, `iio-sensor-proxy`, `libqaccessibilityclient-qt6`,
  `ocean-sound-theme`, `qt6-virtualkeyboard`, `xorg-xmessage`, `xorg-xrdb`.
  Installing them on the live VM brought up the full desktop on the forked
  packages. Both PKGBUILDs' `depends=()` now copy Arch's lists;
  GLOBALSHORTCUTS is back to the default (on): an OFF build ships no
  global-shortcut plugin in `/usr/lib/qt6/plugins/kwin/plugins/`, so
  `plasma-kglobalaccel.service` exits at once and every Plasma process logs
  "Couldn't start kglobalaccel" (confirmed on the VM). Detail in
  `docs/holtos-plasma-fork-plan.md`. Next: rebuild both packages + ISO,
  boot, confirm login works with no manual installs. VM driving notes:
  vmconnect needs the `key` action per character (`type` never reaches the
  guest), `shift+minus` for underscore, Ctrl+Alt+F3 for a tty; the SSH key
  and vm.ps1 live in the session scratchpad. On llvmpipe KWin can sit on
  its last frame until input arrives, so a screenshot that looks frozen
  (stale clock, a closed window still drawn) needs a mouse nudge
  (`move=x,y`) before you call it a hang.
- **Look-and-feel pointed at a decoration that isn't installed**: the
  HoltOS look-and-feel `defaults` said `org.kde.klassy` (KWin logged
  "Could not locate decoration plugin" and fell back to Breeze); now
  `org.holtos.glass`, matching `etc/xdg/kwinrc`. Verified live after
  clearing `~/.config/kdedefaults`.
- **Milestone 3 switched on**: `etc/xdg/kwinrc` enables KWin's in-tree
  blur (`[Effect-blur]`, HoltOS additions merged) and disables
  `holtosglass`; the Glass v2 values (BlurStrength 15, NoiseStrength 4,
  Kvantum window/dialog alpha .40/.55) are ported from the live VM into
  the repo. The in-tree effect loads and reads its config live;
  `holtos-glass-effect` stays in the image, disabled, until a fresh
  install confirms the look.
- **Session-cleanup autostart showed as a failed unit** on every normal
  login (its `grep` exited 1 when no switch was pending); now an `if`.
- **Dolphin's "9 folders" status label is truncated ("9 f...ers")** under
  Kvantum. Not our theme: stock KvRoughGlass does the same, Breeze is
  fine. Kvantum-wide with Dolphin 26.08's floating status bar; needs a
  Kvantum fix or patch. Cosmetic, open.
- **Gaming page (`holtos-gaming`) live-checked**: opens, reads package
  versions and the Proton GE check. Form rows were ragged (Kvantum
  right-aligns form labels); labels are now left-aligned with colons.
- **Backlog items live-checked on the ISO**: `holtos-scrub.timer` is
  enabled and skips itself on the live medium by design; `smartd` is
  enabled but its stock unit refuses to run in a VM
  (`ConditionVirtualization=no`), so `holtos-disk-alert` needs real
  hardware; the disk-alert notice autostart, `/usr/lib/os-session-select`,
  `xdg-desktop-portal-kde` and `smartmontools` are all present.
- **Design work pinned**: the ComfyUI machine is down (2026-09-13). No
  design jobs are queued; route any that come up once it is back.
- ~~Updater cannot reach GitHub~~ — **resolved 2026-09-12: Liam made the
  repo public.** Verified on the build 10 install: `holtos-update-check`
  reported v0.0.2-alpha (exit 0), `holtos-update-apply config` took a
  Btrfs snapshot + ESP kernel copy + Limine entry, downloaded and applied
  the release, and `holtos-update-check` now exits 1 (up to date). The
  tray's update flow is therefore live for every installed system.
- **Real hardware (PLAN steps 6/7)**: boot the build 11 ISO from the
  Ventoy stick on the 7950X box. Checks: `/var/lib/holtos/hardware.log`
  lists the NVIDIA GPU and "installed: nvidia-open-dkms …",
  `lsmod | grep nvidia`, Plasma Wayland starts, `cat /proc/cmdline` has
  `nvidia_drm.modeset=1`, and System Settings > Display shows real
  resolutions/refresh rates. For the HDR toggle on NVIDIA (Plasma ≥ 6.2)
  set `KWIN_DRM_ALLOW_NVIDIA_COLORSPACE=1` in `/etc/environment` — not
  shipped by default (KDE hid it behind that variable because of a
  login-blocking driver bug). Also judge the glass look/frame rate on a
  real GPU: the VM proves the pixels, not the performance.
- **v0.0.4-alpha released** (pre-release, notes on GitHub); build 21 is
  the release ISO. Liam installs it via the system updater on the Strix
  Halo box.
- **Game Mode on real hardware**: boot build 21 on the Strix Halo box,
  "Game Mode" from the app menu, Steam Big Picture on gamescope, "Switch
  to Desktop" from Steam's power menu, and "Start in Game Mode" from the
  tray. (No ISO copy to D:\ any more: Liam updates via the updater.)
- **Restart prompt after system updates** — done, verified on screen in
  the VM, pushed as 2c431c5 but not tagged (Liam: no release yet). Goes out
  with the next tagged release; installed systems only see tags.
- **the-den-client icon**: fixed 2026-09-13 in the client repo (commit
  7f601b5, logo.svg's illegal "--" inside its XML comment removed); not
  pushed/tagged yet, so it ships with the next the-den-client release.
- **Snapshot semantics** (rescue boot vs rollback) — undecided.
- ~~Two orphan public GitHub repos~~ — **deleted 2026-09-13** (Liam):
  `jamesyoungdahr-debug/holtos-glass-effect` and `/holtos-window-decoration`
  are gone from GitHub.
- **Not tested this session** (verified 2026-09-11, unchanged since):
  `holtos-btrfs-snapshot` + Limine snapshot entries, 6-cycle retention.
- **Cosmetic, new:** the Bluetooth applet shows on the VM even though
  `bluetooth.service` stays inactive there (no adapter) — harmless.

## Where things live

| | Path |
|---|---|
| **start here** | `CONTEXT.txt` — current state + how to drive the VM |
| **start here** | `PLAN.md` — steps with status |
| **start here** | `BUILD.md` — full build pipeline |
| new | `docs/media-server-must-haves.md` — feature list Liam asked for |
| fix | `archiso/packages.x86_64` (kscreen & co., qt6-declarative, python-gobject) |
| fix | `archiso/airootfs/root/customize_airootfs.sh` (bluetooth, live autolock) |
| fix | `archiso/airootfs/etc/calamares/branding/holtos/stylesheet.qss` |
| fix | `BUILD.md`, `archiso/pacman.conf` |
| release | `archiso/profiledef.sh`, `branding.desc`, `etc/os-release`, `CHANGELOG.md` |
| log | `CHANGELOG.md` |
