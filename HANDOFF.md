# HoltOS Session Handoff — updated 2026-09-11

What shipped, what broke, what got fixed, and what's still open — for
whoever picks this branch up next. Treat nothing here as already-shared
context.

Commit: see `git log` (this file is committed with the work it describes).
Test VM: `holtos-test` (Hyper-V Gen 2, Secure Boot off, 60 GB VHDX under
`vm/`). ISO: `out/holtos-0.0.1-alpha-x86_64.iso`.

## Ground rules

- **Never guess at a root cause — verify it.** Every bug below was found
  by reading real output off a live VM (`findmnt`, `systemctl status`,
  `journalctl`, `btrfs subvolume list`, screenshots of the actual boot
  menu), not by inspection. Read `BUILD.md` before touching the build
  pipeline and `README.md` before touching install/boot behavior.
- **Only build/push when explicitly told to.**
- **Test in the VM, not by inspection alone.** A fresh install (Erase
  Disk) is required to pick up any partition/bootloader/cleanup change.
- **Keep changes small and verifiable one at a time.**
- **How to drive the VM without a console window:** the normal Windows
  token can't open vmconnect, and elevated windows reject injected
  input. Use Hyper-V WMI from an elevated PowerShell instead —
  `GetVirtualSystemThumbnailImage` for screenshots, `Msvm_Keyboard`
  `TypeKey` per character (`TypeText` drops keys), `Msvm_SyntheticMouse`
  for clicks — then switch to SSH as soon as the guest is up
  (`systemctl enable --now sshd` in Konsole, paste a pubkey). Limine's
  3-second menu is shorter than a screenshot round-trip: press a key
  every frame during boot to hold it (Down selects the snapshot entry).

## At a glance

- The build pipeline has now been run **from a genuinely clean machine**
  (fresh Windows, fresh clone, no images) and works, after 4 fixes.
- **Handoff steps 1–4 from the previous session are all done for real**:
  clean build → fresh install → Limine menu watched rendering → snapshot
  created → booted into it → 6-cycle retention confirmed.
- **7 new real bugs found, 6 fixed and re-verified on a second fresh
  install.** 1 needs a decision (below).
- Direction change decided 2026-09-11 (see `PLAN.md`): the whole
  container stack is being removed and The Den becomes the shipped app.
- Later on 2026-09-11: PLAN steps 1, 2 and 7 landed (stack gone, The Den
  vendored, hardware detection), plus HoltOS Glass across SDDM /
  Plasma / Kvantum windows / Klassy title bars / installer / Plymouth,
  and the updater now installs app dependencies and health-checks The
  Den. The first build with NVIDIA staging failed on pacman's
  `CheckSpace` inside the chroot (fixed, see CHANGELOG). Step 7's NVIDIA
  path still needs a real GPU machine.

## Bugs found & fixed this session

All verified on a second fresh install from a rebuilt ISO unless noted.

1. **Git Bash path conversion broke `build-local-repo.sh`** —
   `MSYS_NO_PATHCONV=1` was exported *after* the `podman build` call.
   Also BUILD.md's manual `archiso-image` command. `build.sh`'s
   `icacls /grant` had the same problem (exit 87). Fixed.
2. **CRLF checkouts** — Git for Windows' `autocrlf=true` default turned
   every script into `\r`-terminated garbage (`pipefail\r: invalid
   option name`). `.gitattributes` now forces LF. Fixed.
3. **Container keyring** — the `archlinux` base image has no local master
   key, so `archlinux-keyring`'s hook failed during `podman build`. Both
   Containerfiles now `pacman-key --init && --populate` first. Fixed.
4. **Installed system had no usable pacman keyring** (the previous
   session's `pacman-key --init` fix was not enough). archiso's
   `etc-pacman.d-gnupg.mount` (live-medium tmpfs) is copied into the
   target, and gnupg's socket units pull it in by name every boot,
   hiding the on-disk keyring — which was itself incomplete because the
   chroot-time init failed silently. `homelab-cleanup-live.sh` now
   removes both archiso units; new `holtos-pacman-keyring-init.service`
   re-runs init on first boot if no master secret key exists. **Verified:**
   `pacman -S tree` works on a fresh install; the backstop's condition
   was unmet (chroot init succeeded once the tmpfs unit was gone).
5. **`holtos-first-boot-apps` and `homelab-sync-arr-keys` had never
   run** — their `*.wants/` entries were regular files (Windows git can't
   store symlinks), which systemd ignores. Now `systemctl enable`d in
   `customize_airootfs.sh`; fake files deleted. **Verified:** both ran on
   first boot; first-boot-apps installed The Den v0.1.0-alpha (sysusers,
   venv, pip, alembic migration, service active) and The Den Client.
6. **Done on the Finished page didn't restart** — Calamares' stock
   `restartNowMode: user-unchecked`, plus the checkbox was invisible under
   the dark stylesheet. Added `finished.conf` (`user-checked`) and
   explicit checkbox/radio indicator styles. **Verified:** box visible
   and ticked, Done rebooted into the installed system.
7. **Boot entry said `homelab-os`** — Limine entry and EFI label renamed
   to `HoltOS`. **Verified** in `limine.conf` and `efibootmgr`.

Also done: branding audit (only gap was the stock Arch syslinux splash,
replaced); updater tray + first-boot services gated on `!/run/archiso`
so they never run on the live ISO (**committed after the last ISO
build — not yet verified in a built image**).

## Confirmed working (live, this session)

Live ISO boots to the branded Plasma desktop; Calamares launches with no
password prompt; dark content-area stylesheet; Btrfs `@` root with
`compress=zstd:1` and 1024 MiB ESP; both `limine.conf` copies identical;
Limine menu renders wallpaper + palette + snapshot entries; sudo; tray
icon under Wayland; all 13 stack services active; secrets generated;
`holtos-btrfs-snapshot` creates subvolume + ESP copy + Limine entry;
booting a snapshot works (see next section); retention evicts oldest
subvolume + ESP copy + Limine entry together at 5.

## Still open

- **The updater cannot reach GitHub: the HoltOS repo is private.**
  `git ls-remote` and release-tarball download are anonymous, so
  `holtos-update-check` exits 128 and the config/rollback paths can't
  work. Same failure the-den hit before it was made public. Needs a
  decision: make the repo public, or teach the updater to use a token.
- **Booting a snapshot gives a read-only root, not a rollback.** It
  boots to SDDM, but tmpfiles can't create dirs and the container stack
  fails — a rescue environment. Nothing turns a snapshot back into the
  live root. Fine for an alpha safety net; document it or build a
  restore step.
- **Cosmetic:** Calamares partition-bar labels render dark-on-dark
  (painted via palette, not stylesheet); the slideshow page has a white
  frame around the slide.
- **Test-VM artifact:** a stale `homelab-os` NVRAM entry from the
  previous install is still in the VM's firmware. Harmless.
- The Limine menu could not be caught on screen during the second
  install's reboot (too fast) — entry name verified from the config
  instead.

## Where things live

| | Path |
|---|---|
| **start here** | `PLAN.md` — next session's step-by-step plan |
| **start here** | `BUILD.md` — full build pipeline |
| **start here** | `README.md` — architecture, install flow |
| new | `.gitattributes` |
| new | `archiso/airootfs/etc/calamares/modules/finished.conf` |
| new | `archiso/airootfs/etc/systemd/system/holtos-pacman-keyring-init.service` |
| fix | `archiso/airootfs/usr/local/bin/homelab-cleanup-live.sh` |
| fix | `archiso/airootfs/usr/local/bin/homelab-limine-install.sh` |
| fix | `archiso/airootfs/usr/local/bin/holtos-tray` |
| fix | `archiso/airootfs/root/customize_airootfs.sh` |
| fix | `archiso/airootfs/etc/calamares/branding/holtos/stylesheet.qss` |
| fix | `archiso/syslinux/splash.png` |
| fix | `build.sh`, `build-local-repo.sh`, `containers/*.Containerfile` |
| log | `BRANDING-STATUS.md`, `CHANGELOG.md` |
