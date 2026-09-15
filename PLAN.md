# HoltOS — Plan (written 2026-09-11)

Direction decided at the end of the 2026-09-11 session: **the current
container stack is being removed** (Authentik, Postgres, Redis, Sonarr,
Radarr, Prowlarr, Jellyseerr, qBittorrent, the dashboard — Plex is the
one open question). HoltOS becomes the base OS plus **The Den** and
**The Den Client**, preinstalled at build time instead of fetched by the
updater on first boot. A proper arr-style suite comes later as its own
project.

Work one step at a time. Each step ends with a fresh Erase-Disk install
in `holtos-test` and the listed check — don't batch steps.

## Step 0 — Decisions (before any code)

- [x] **Repo visibility: public** (Liam, 2026-09-12). Verified the same
      hour on the build 10 install: `holtos-update-check` went from exit
      128 to reporting v0.0.2-alpha; `holtos-update-apply config`
      snapshotted, downloaded the release tarball, applied it, and
      `holtos-update-check` then exits 1 (up to date).
- [x] **Plex: goes** — removed with the rest of the stack on 2026-09-11.
      Trivial to re-add as a single unit later if playback needs it.
- [x] **Snapshot semantics: real rollback** (Liam, 2026-09-12). Built as
      `holtos-btrfs-restore` + tray "Restore Snapshot..." + snapshot-boot
      notice; see CHANGELOG [Unreleased]. Booting a snapshot entry stays a
      read-only rescue root, with the restore one click away.

## Step 1 — Strip the container stack — DONE 2026-09-11 (commit 8de9375)

Remove, in one commit, everything that only existed for the stack:

- `archiso/airootfs/usr/share/containers/systemd/*.container` and
  `homelab.network` (keep `podman` itself only if Plex stays as a
  Quadlet).
- `usr/share/applications/{authentik,sonarr,radarr,prowlarr,jellyseerr,qbittorrent-web,homepage-dashboard,plex}.desktop`
  and the matching `usr/share/icons/.../holtos-*.svg` (keep
  `holtos-logo.svg`).
- `etc/authentik/` (blueprints), `etc/tmpfiles.d/homelab-data-dirs.conf`
  (or trim it to what The Den needs), `homelab-generate-secrets.sh` +
  `generate-secrets.conf` + `capture-user-creds.conf` (only existed to
  feed Authentik), `homelab-sync-arr-keys.sh` + its `.service`.
- In `holtos-update-apply` / `holtos-update-picker`: the `service`,
  `authentik`, and dashboard items; keep `config`, `system`,
  `the-den`, `the-den-client`, `rollback`.
- `customize_airootfs.sh`: drop `systemctl enable` of removed units.
- `profiledef.sh` `file_permissions`: drop removed scripts.
- `packages.x86_64`: drop `podman` if nothing uses it; drop `falkon` if
  no web UI is left to open.
- `README.md`, `CHANGELOG.md`: describe the new shape.

**Check:** fresh install boots to SDDM, `systemctl --failed` is empty,
no leftover `.container` units, `journalctl -p err -b` is quiet.

## Step 2 — Vendor The Den into the image at build time — DONE 2026-09-11 (verification: see HANDOFF.md)

Goal: a fresh install has The Den and The Den Client present and running
from first boot with no network dependency, and the updater still
updates them.

- Add a `build-vendor-apps.sh` (run from `build.sh`) that downloads the
  latest tagged release tarballs of `jamesyoungdahr-debug/the-den` and
  `the-den-client` into `archiso/airootfs/opt/` (gitignored, like
  `local-repo/`) — the same layout `update_the_den` /
  `update_the_den_client` produce today, so the updater's in-place update
  path keeps working.
- Move the venv + `pip install` + `sysusers`/`tmpfiles` + launcher/icon
  steps into `customize_airootfs.sh` (network is available in the
  mkarchiso chroot). Keep the alembic migration + `systemctl enable --now`
  as a first-boot oneshot (it needs the real `/var/lib/the-den`), reusing
  `holtos-first-boot-apps` but without the download.
- Stamp the vendored versions into `/var/lib/holtos/history.log` at build
  so "Rollback" has a baseline.

**Check:** fresh install with the VM's network disconnected → `the-den`
active, `the-den-client` in the app menu and launches, migration ran.

## Step 3 — Verify the live-ISO guards — DONE 2026-09-12 (build 9)

Live session: no `holtos-tray` process, no first-boot unit at all (the
vendoring in Step 2 removed it; The Den's migration runs from
`holtos-update-apply vendor` at build time and `the-den.service` on the
installed system, which was active with HTTP 200 on first boot). The
installed system has the tray running. Also found and fixed in the same
round: the live session auto-locked after 5 minutes (installer finished
behind the lock screen) — `Autolock=false` for liveuser only.

## Step 4 — Finish the cosmetic installer items — DONE 2026-09-12 (verified in build 10: legend readable on the chip, Current and After rows)

- Partition-bar legend: NOT fixable with a colour rule — Calamares'
  `PartitionLabelsView::drawLabel` uses hardcoded `Qt::black` /
  `Qt::gray` pens. The stylesheet now gives the view a light
  (rgba 255,255,255,0.88) rounded background instead, so black text reads.
- Slideshow white frame: already fixed (root Rectangle in `show.qml`),
  confirmed on screen in build 9.

**Check:** screenshot of the Partitions page in the build 10 install
(legend on a light chip, both lines readable) and the Summary page.

## Step 4b — System Settings pages that were missing — DONE 2026-09-12 (verified in build 10: Display page with 24 modes, volume applet, Bluetooth/Login Screen/Remote Desktop KCMs present, PulseAudio-on-PipeWire server, powerprofilesctl works, 0 failed units)

Found while checking Liam's "Display shows no resolution options":
`kscreen` (the Display page itself) was not in the image, nor were
`plasma-pa` + `pipewire-pulse`/`-alsa`, `bluedevil` + `bluez`,
`kde-gtk-config`, `plasma-disks`, `sddm-kcm`, `kwallet-pam`, `krdp`,
`python-gobject`. All added; `bluetooth.service` enabled.

**Check:** build 10 install → System Settings > Display shows the mode
list (24 modes in the VM); volume applet in the tray; Bluetooth,
Login Screen, Remote Desktop, Disks & Devices pages present;
`powerprofilesctl list` works; `systemctl --failed` still empty.

## Step 5 — Release — DONE 2026-09-12 (v0.0.2-alpha, build 11 from the tag; update path verified after the repo went public)

- Update `CHANGELOG.md` `[Unreleased]` → `[0.0.2-alpha]`, bump
  `profiledef.sh` `iso_version` and `branding.desc` version strings.
- Tag `v0.0.2-alpha` (annotated) + GitHub Release with notes. This is
  the first release that carries any of the session's fixes — no
  installed system can receive them until it exists.
- Rebuild from that tag so `deployed-commit` matches.

**Check:** fresh install → `holtos-update-check` exits 1 (up to date).
Requires Step 0's repo-visibility decision (still private on 2026-09-12:
the build 9 install's `holtos-update-check` exits 128). Everything else
in this step can be done before that decision; only this check waits.

## Step 5b — After the release (2026-09-12, unreleased, all verified in the VM)

- Snapshot restore (`holtos-btrfs-restore`, tray "Restore Snapshot...",
  snapshot-boot notice) — verified: CLI restore back/forward, tray flow on
  a fresh build 14 install, restore from a booted snapshot, cleanup unit.
- Other operating systems in the Limine menu
  (`holtos-limine-other-os`, install time + kernel updates + tray "Rescan
  Boot Menu") — verified with a second disk carrying a fake Windows and
  Ubuntu ESP: entries appear at install time and chainloading via
  `guid()` reaches the loader on the other disk.
- Limine themed as HoltOS (branding, Terminus 12x24, glass panel,
  comments, collapsed Snapshots submenu) — verified on screen.
- yad 15 dropped `--question`/`--info`; all dialogs fixed.
- Tagged and released as `v0.0.3-alpha` the same day (Liam wanted to run
  the updater on a Strix Halo machine). Also in it: the config update
  syncs every HoltOS-owned component from the tarball (Liam: "each
  component can be updated, from our own sources"), and HoltOS-built
  packages are served from the `packages` GitHub release as a pacman
  repo. Verified on the VM's existing install.
- Next: real hardware feedback from the Strix Halo box (boot menu look,
  restore flow, Display page HDR/VRR, `hardware.log` vainfo/vulkaninfo).
- HoltOS is a **media and gaming/entertainment focused** distro (Liam,
  2026-09-12). The feature list and build order for that live in
  `docs/holtos-must-haves-and-plan.md`: Steam + Proton + Proton GE,
  a gamescope Game Mode session with a two-way switch and boot-into
  option (The Den keeps running — it is a system service), a HoltOS app
  store over Flathub with a curated front page, controllers/CEC,
  performance defaults, then the media player decision and storage
  wizard. Network Shares (SMB/NFS with automount, GUI) is done.

**Fixed (2026-09-15):** Plasma's Disks & Devices popup opened over the
installer in the live session for the live medium's own optical disc.
`etc/udev/rules.d/90-holtos-live-media.rules` sets `UDISKS_IGNORE` on the
`HOLTOS_*` and `ARCHISO_EFI` filesystems, so udisks never announces them;
`holtos-cleanup-live.sh` removes the rule from the installed system, so real
sticks carrying those labels still appear.

## Step 6 — Real hardware

Only after Step 5: R720 PERC to HBA mode, iDRAC virtual media, UEFI
boot — see `README.md`.

## Step 7 — Hardware detection at install (added 2026-09-11, built, needs real hardware)

Implemented: `homelab-detect-hardware.sh` (Calamares `detect-hardware`
step, after cleanup-live) scans PCI in the target; if an NVIDIA GPU is
present it installs `nvidia-open-dkms` + `nvidia-utils` from packages
staged on the ISO at build time (`customize_airootfs.sh` →
`/usr/share/holtos/drivers/nvidia/`), DKMS builds the module in the
chroot, and `nvidia_drm.modeset=1` is appended to the Limine command
line (main entry and snapshot entries). Vulkan (AMD/Intel) and VA-API
drivers are always in the image. Everything is logged to
`/var/lib/holtos/hardware.log`.

**Check (Liam, real NVIDIA machine):** fresh install → `hardware.log`
lists the GPU and "installed: nvidia-open-dkms ...", `lsmod | grep
nvidia`, Plasma Wayland session starts, `cat /proc/cmdline` shows
`nvidia_drm.modeset=1`. The Hyper-V VM can only prove the "no NVIDIA —
nothing to install" path.
