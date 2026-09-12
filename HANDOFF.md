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
