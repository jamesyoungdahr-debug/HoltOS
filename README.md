<p align="center">
  <img src="archiso/airootfs/etc/calamares/branding/holtos/logo-wide.svg" width="420" alt="HoltOS">
</p>
<p align="center"><sub>MEDIA-FIRST ARCH</sub></p>

# HoltOS

A custom Arch Linux live/install medium (archiso + Calamares + Limine) for a
self-hosted homelab server. Boots into KDE Plasma, targets a Dell PowerEdge
R720, and ships the whole media stack pre-wired as Podman Quadlets: Authentik
(SSO), Sonarr, Radarr, Prowlarr, Jellyseerr, qBittorrent, Plex, and a custom
dashboard app ([homepage-dashboard](https://github.com/jamesyoungdahr-debug/homelab-os/tree/master/apps/homepage-dashboard)).

Split out of the [homelab-os](https://github.com/jamesyoungdahr-debug/homelab-os)
monorepo once it had a validated end-to-end install — it has its own
build/release cadence, independent of the dashboard app.

## Why Arch + archiso, not an atomic Fedora image

The OS was first built as a BlueBuild/Fedora-Atomic image (see
`homelab-os`'s `distro/`, now abandoned) and got fairly far — a real CI
build, a real bootable ISO, disk-inspection confirming the Quadlets were
wired correctly. It never got a genuinely validated *live* boot, because
Anaconda's automation surface made deeper VM testing unreliable. Arch +
archiso + Calamares turned out to be a much better fit for the actual
development loop: the live session *is* the install target, so every
install/boot bug could be found and fixed through real, repeated boot →
install → reboot cycles in a VM, not just static disk inspection.

## Repo structure

```
archiso/                      # the archiso profile passed to mkarchiso
  airootfs/                   # files copied verbatim onto the live medium —
                               # and, since Arch's install model just copies
                               # the live rootfs onto the target, onto the
                               # INSTALLED system too (see "How install
                               # works" below)
    etc/calamares/            # Calamares config: settings.conf + our
                               # custom shellprocess modules
    usr/local/bin/homelab-*.sh  # the custom install/boot-time scripts
    usr/share/containers/systemd/  # the Podman Quadlets (*.container, *.network)
    usr/share/applications/   # app-menu launchers for the web UIs
  packages.x86_64             # package list (base system + KDE + Calamares + podman)
  profiledef.sh                # ISO metadata + file permission overrides
build-aur-packages.sh         # builds the AUR packages (zfs-dkms, limine-*)
                               # the profile needs, run once to populate local-repo/
local-repo/                   # (gitignored) built AUR packages, consumed by pacman.conf
out/                          # (gitignored) built ISOs land here
vm/                           # (gitignored) local VM test scratch (QEMU logs, disk images)
releng-reference/             # (gitignored) local copy of upstream Arch releng's
                               # archiso profile, kept only for diffing during dev
```

## How install works (and why so many custom scripts)

Arch's live-install model is fundamentally different from Anaconda/BlueBuild:
there's no package re-installation step. Calamares' `unpackfs` module just
copies the live squashfs onto the target disk — the live session *is* the
installed system, verbatim. That's simple and fast, but it means anything
that's only valid on the live medium (the `liveuser` account, its
passwordless-sudo convenience, SDDM autologin, archiso-only mkinitcpio
hooks, the Calamares package itself) rides along onto every install unless
something explicitly strips it out afterward. Everything under
`usr/local/bin/homelab-*.sh` plus the matching `etc/calamares/modules/*.conf`
shellprocess steps exists to do exactly that — each one chroots into the
freshly-installed target and fixes up one specific piece:

- **`homelab-fix-mkinitcpio.sh`** — strips archiso-only mkinitcpio HOOKS
  (and the `mkinitcpio-archiso` package's preset override that
  reintroduces them) so `mkinitcpio` doesn't hard-fail building the
  installed system's initramfs.
- **`homelab-limine-install.sh`** — installs Limine and writes
  `limine.conf`. Copies the kernel/initramfs onto the FAT32 ESP and
  references them via `boot():` rather than the ext4 root, because
  Limine's minimal ext4 driver can't read a filesystem with the
  `orphan_file`/`metadata_csum_seed` features current `mkfs.ext4` enables
  by default — confirmed by a real panic on real boot before this fix.
  `homelab-limine-sync.sh` + its pacman hook keep those ESP copies in sync
  on future kernel upgrades.
- **`homelab-cleanup-live.sh`** — removes the `liveuser` account, its
  wheel-group-wide passwordless-sudo rule (which would otherwise also
  apply to the real account just created), SDDM autologin, the install
  desktop launcher, and uninstalls the `calamares` package itself.
- **`homelab-generate-secrets.sh`** — auto-generates `authentik.env` and
  `dashboard.env` under `/var/mnt/tank/appdata/secrets/` with random
  secrets (Postgres password, Authentik secret key, OIDC client secret,
  NextAuth secret) so Authentik/Postgres/Redis/the dashboard's own SSO
  login all work with zero manual setup.
- **`homelab-sync-arr-keys.sh`** (runs at every boot, not install time) —
  Sonarr/Radarr/Prowlarr each generate their own random API key into their
  own `config.xml` on first start; this waits for that, reads the key back
  out, and writes it into `dashboard.env` so the dashboard's arr widgets
  work too — without ever touching the arr apps' own config (pre-seeding
  their `config.xml` risks a schema mismatch breaking their startup).

The Quadlets themselves reference `/var/mnt/tank/...` for all persistent
data (the real ZFS pool on the R720), but a `tmpfiles.d` config
(`etc/tmpfiles.d/homelab-data-dirs.conf`) pre-creates that whole tree as
plain directories on every boot — so the stack runs immediately off local
disk even before a ZFS pool is ever imported. Once the real pool is mounted
over that path, restart the affected services (or reboot) to pick up the
real storage; an already-running container's bind mount doesn't retroactively
follow a mount that appears later.

## Building the ISO

Requires `archiso`'s `mkarchiso` — done here via a privileged container
(built from `archiso-image`, matching upstream `archlinux/archlinux:base-devel`
plus `archiso`) so it doesn't need a native Arch host:

```bash
podman run --privileged --rm \
  -v "$(pwd)/archiso:/profile:Z" \
  -v "$(pwd)/local-repo:/homelab-local-repo:Z" \
  -v "$(pwd)/out:/tmp/out:Z" \
  archiso-image \
  bash -c "mkarchiso -v -w /tmp/work -o /tmp/out /profile"
```

The resulting ISO lands in `out/`. `local-repo/` needs the AUR packages
(`zfs-dkms`, `zfs-utils`, `limine-mkinitcpio-hook`, `limine-entry-tool`)
built once via `build-aur-packages.sh` before the first build — `pacman.conf`
points at `local-repo` as an extra repo for these.

## What's been validated

A full boot → install → reboot cycle, tested repeatedly against a real
Hyper-V VM (not just static inspection), fixing four real, previously-unknown
bugs along the way (the mkinitcpio, Limine, polkit, and liveuser-cleanup
issues described above). The confirmed-working cycle: boot the live ISO →
launch Calamares with **no password prompt** → Erase Disk → install → eject
the medium → cold reboot → Limine → a real SDDM login prompt (not stale
`liveuser` autologin) → log in → the full Quadlet stack (Postgres, Redis,
Authentik server + worker, Sonarr, Radarr, Prowlarr, Jellyseerr, qBittorrent,
Plex, the dashboard) comes up **on its own**, with `authentik.env` and
`dashboard.env` already populated with matching, correctly-generated
secrets — confirmed via `systemctl is-active` on every service and reading
the generated secrets files directly.

**Known open items:**

- The three *arr → dashboard API keys sync at boot via
  `homelab-sync-arr-keys.service`, but that path hasn't yet been verified
  against a real boot (the logic — wait for `config.xml`, extract
  `<ApiKey>`, write to `dashboard.env`, restart the dashboard — is
  straightforward but untested end-to-end).
- The app-menu web-UI launchers (`usr/share/applications/*.desktop`, using
  `falkon`) haven't been click-tested yet.
- Real R720 hardware: PERC controller reconfiguration, iDRAC virtual media
  install — see below.

## Hardware setup: Dell PowerEdge R720

This targets a 2012-era dual Xeon E5-2600 R720 with a PERC H710/H310 RAID
controller and iDRAC7. None of this is automated by the image build — it
has to happen on the physical hardware before/during install.

- **PERC controller → HBA/passthrough mode.** ZFS needs raw disk access,
  not a hardware RAID volume underneath it. Check whether your specific
  PERC H710 firmware revision supports true HBA/passthrough mode (not all
  do). If it doesn't, the fallback is one single-disk RAID-0 virtual disk
  per physical drive — it works, but still hides real SMART data behind the
  controller, so prefer true HBA mode if available.
- **iDRAC7 virtual media.** Upload the built ISO through the iDRAC web
  console (Virtual Console → Virtual Media → Map CD/DVD) to install without
  physical USB media.
- **Firmware.** Update BIOS/iDRAC firmware to the latest available for this
  generation before installing. Confirm the boot mode is set to **UEFI**,
  not legacy BIOS.
- **No GPU / no Quick Sync.** This is a rack server with no iGPU beyond a
  basic remote-KVM video chip. Plex will only be able to do software
  transcoding unless a discrete GPU is added via PCIe passthrough later.

Only move to the real R720 once the live-boot validation above is complete
and you're comfortable with the level of testing that's happened in a VM.
