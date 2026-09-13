# HoltOS Session Handoff — updated 2026-09-12

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

## Still open

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
- **Snapshot semantics** (rescue boot vs rollback) — undecided.
- **Two orphan public GitHub repos** from before the monorepo decision
  (`jamesyoungdahr-debug/holtos-glass-effect`, `/holtos-window-decoration`)
  — `gh repo delete` needs the `delete_repo` scope, so Liam runs it.
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
