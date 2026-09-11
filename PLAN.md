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

- [ ] **Repo visibility.** The updater does anonymous `git ls-remote` and
      release-tarball downloads; HoltOS is private, so every updater path
      except per-service `podman pull` is broken today. Either make the
      repo public (what was done for the-den) or add token support.
- [x] **Plex: goes** — removed with the rest of the stack on 2026-09-11.
      Trivial to re-add as a single unit later if playback needs it.
- [ ] **Snapshot semantics.** Booting a snapshot is a read-only rescue
      boot, not a rollback. Decide: document it as such, or add a
      "restore this snapshot" action (`btrfs subvolume snapshot` the
      read-only one to a new `@`, `set-default`, update Limine).

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

## Step 3 — Verify the live-ISO guards

The `!/run/archiso` gates on the tray and first-boot units were committed
after the last ISO build.

**Check:** boot the live ISO — no tray icon, `systemctl status
holtos-first-boot-apps` shows condition unmet.

## Step 4 — Finish the cosmetic installer items

- Partition-bar labels dark-on-dark: set `QWidget { color }` isn't
  reaching them (palette-painted). Try `QPalette`-driven keys via
  `branding.desc` `style:` or a `#partitionBarView` rule.
- Slideshow page white frame around the slide.

**Check:** screenshots of Partitions and Install pages.

## Step 5 — Release

- Update `CHANGELOG.md` `[Unreleased]` → `[0.0.2-alpha]`, bump
  `profiledef.sh` `iso_version` and `branding.desc` version strings.
- Tag `v0.0.2-alpha` (annotated) + GitHub Release with notes. This is
  the first release that carries any of the session's fixes — no
  installed system can receive them until it exists.
- Rebuild from that tag so `deployed-commit` matches.

**Check:** fresh install → `holtos-update-check` exits 1 (up to date).
Requires Step 0's repo-visibility decision.

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
