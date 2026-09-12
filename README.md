<p align="center">
  <img src="archiso/airootfs/etc/calamares/branding/holtos/logo-wide.svg" width="420" alt="HoltOS">
</p>
<p align="center"><sub>MEDIA-FIRST ARCH</sub></p>

# HoltOS

A custom Arch Linux live/install medium (archiso + Calamares + Limine) for a
self-hosted homelab server. Boots into KDE Plasma, targets a Dell PowerEdge
R720, and ships **The Den** — a movie/TV library manager
([the-den](https://github.com/jamesyoungdahr-debug/the-den)) — and its
native KDE desktop app
([the-den-client](https://github.com/jamesyoungdahr-debug/the-den-client)),
both installed into the image at build time so a fresh install runs them
from first boot with no network dependency.

Split out of the [homelab-os](https://github.com/jamesyoungdahr-debug/homelab-os)
monorepo once it had a validated end-to-end install. Until 2026-09-11 it
also carried a full Podman container stack (Authentik, Sonarr, Radarr,
Prowlarr, Jellyseerr, qBittorrent, Plex, a dashboard); that was removed —
see `CHANGELOG.md` and `PLAN.md` — and a purpose-built arr-style suite
comes later as its own project.

## Why Arch + archiso, not an atomic Fedora image

The OS was first built as a BlueBuild/Fedora-Atomic image (see
`homelab-os`'s `distro/`, now abandoned) and got fairly far — a real CI
build, a real bootable ISO. It never got a genuinely validated *live*
boot, because Anaconda's automation surface made deeper VM testing
unreliable. Arch + archiso + Calamares turned out to be a much better fit
for the actual development loop: the live session *is* the install
target, so every install/boot bug could be found and fixed through real,
repeated boot → install → reboot cycles in a VM, not just static disk
inspection.

## Repo structure

```
archiso/                      # the archiso profile passed to mkarchiso
  airootfs/                   # files copied verbatim onto the live medium —
                               # and, since Arch's install model just copies
                               # the live rootfs onto the target, onto the
                               # INSTALLED system too (see "How install
                               # works" below)
    etc/calamares/            # Calamares config: settings.conf, branding,
                               # our custom shellprocess modules
    usr/local/bin/homelab-*.sh  # the install/boot-time scripts
    usr/local/bin/holtos-*      # the updater (tray, picker, apply, ...),
                               # snapshots
    root/customize_airootfs.sh  # runs in the image-build chroot: enables
                               # units, creates liveuser, installs The Den
  packages.x86_64             # package list (base system + KDE + Calamares
                               # + ZFS + The Den's runtime)
  profiledef.sh                # ISO metadata + file permission overrides
containers/                   # Containerfiles for the two build images
  archiso-image.Containerfile  # runs mkarchiso itself (see build.sh)
  aur-builder.Containerfile    # builds the AUR packages (see build-local-repo.sh)
build-local-repo.sh           # once: builds calamares + zfs + limine AUR
                               # packages into local-repo/ — see BUILD.md
build-vendor-apps.sh          # every build (called by build.sh): fetches the
                               # latest tagged The Den / Den Client release
                               # into archiso/airootfs/opt/holtos-vendor/
build.sh                      # every build: vendors the apps, runs mkarchiso
local-repo/                   # (gitignored) built AUR packages
out/                          # (gitignored) built ISOs land here
vm/                           # (gitignored) local VM test scratch
```

## How install works (and why the custom scripts)

Arch's live-install model is fundamentally different from Anaconda/BlueBuild:
there's no package re-installation step. Calamares' `unpackfs` module just
copies the live squashfs onto the target disk — the live session *is* the
installed system, verbatim. That's simple and fast, but it means anything
that's only valid on the live medium (the `liveuser` account, its
passwordless-sudo convenience, SDDM autologin, archiso-only mkinitcpio
hooks and systemd units, the Calamares package itself) rides along onto
every install unless something explicitly strips it out afterward. The
`usr/local/bin/homelab-*.sh` scripts plus the matching
`etc/calamares/modules/*.conf` shellprocess steps exist to do exactly
that — each one chroots into the freshly-installed target and fixes up
one specific piece:

- **`homelab-fix-mkinitcpio.sh`** — strips archiso-only mkinitcpio HOOKS
  so `mkinitcpio` doesn't hard-fail building the installed initramfs.
- **`homelab-limine-install.sh`** — installs Limine, writes
  `limine.conf` to both `/EFI/limine/` and the `/EFI/BOOT/` fallback,
  copies kernel/initramfs onto the ESP (`boot():` paths), registers the
  `HoltOS` NVRAM entry. `homelab-limine-sync.sh` + its pacman hook keep
  the ESP copies in sync on kernel upgrades.
- **`homelab-cleanup-live.sh`** — removes `liveuser`, its passwordless
  sudo rule (replaced with a normal `%wheel` rule), SDDM autologin, the
  install launcher, the `calamares` package, and archiso's live-only
  keyring units (which would otherwise hide the installed keyring under
  a tmpfs); then initializes the pacman keyring.
  `holtos-pacman-keyring-init.service` re-does the keyring on first boot
  if the chroot attempt left no master key.

Anything that should only run on the installed system, never in the live
session, is gated on `/run/archiso` not existing: the updater tray,
`the-den.service`, and the keyring backstop.

The root filesystem is **Btrfs** (`@`, `@home`, `@cache`, `@log`,
`@snapshots`) with a 1024 MiB ESP. `holtos-btrfs-snapshot` takes a
read-only snapshot plus an ESP kernel copy and a Limine boot entry before
every config/system update (and on demand from the tray), keeping the
last five. Booting a snapshot entry gives a read-only rescue root — it is
not a rollback.

## The Den

`build-vendor-apps.sh` fetches the latest tagged release of both repos;
`customize_airootfs.sh` then runs `holtos-update-apply vendor` inside the
build chroot, which installs them with the same code the tray updater
uses (sysusers, tmpfiles, venv + pip, alembic migrations, service enabled
— started on first boot). Picking "The Den" in the tray later is an
in-place update of that same layout. The Den's web UI is at
`http://127.0.0.1:8686`; the client is `the-den-client` in the app menu.
Runtime settings live in `/etc/the-den/the-den.env` (installed from the
release's `.example`).

## The updater

A tray icon (`holtos-tray`) checks every 6 h for a new **tagged** HoltOS
release and offers: update The Den / The Den Client, the config scripts,
or system packages (`pacman -Syu`); roll back the config to the previous
release; view history; create a snapshot now. Config/app updates are
downloaded as GitHub release tarballs — never raw commits.

> **Note:** the updater does anonymous `git ls-remote` and tarball
> downloads. While this repo is private, the HoltOS config/rollback paths
> cannot reach it (the-den and the-den-client are public). See `PLAN.md`.

## Building the ISO

See **[BUILD.md](BUILD.md)**. Short version, from a clean checkout on
Windows with WSL2 Ubuntu + podman:

```bash
./build-local-repo.sh   # once — builds calamares + zfs + limine AUR packages
./build.sh               # every time — vendors The Den, builds the ISO into out/
```

## Writing the ISO to a USB stick

The image is a standard archiso hybrid ISO. Any raw/"DD image" write
works: `dd`, balenaEtcher, Rufus in **DD image mode** (not ISO mode).
Ventoy is supported too: the installer's `locate-airootfs` step finds
the ISO wherever Ventoy exposed it (`/dev/mapper/ventoy`) before
unpacking, so Ventoy's normal mode should work; use GRUB2 mode if the
live session fails to come up at all. If the installer still reports
that `airootfs.sfs` cannot be found, its log shows every device it tried.

## What's been validated

See `HANDOFF.md` for the current verified/unverified state. As of
2026-09-11: clean-machine build, fresh Erase-Disk install, branded Limine
menu, snapshot create/boot/retention, sudo, keyring, tray, and The Den
installing and starting on first boot — all confirmed live in a Hyper-V
VM.

## Hardware setup: Dell PowerEdge R720

This targets a 2012-era dual Xeon E5-2600 R720 with a PERC H710/H310 RAID
controller and iDRAC7. None of this is automated by the image build:

- **PERC controller → HBA/passthrough mode.** ZFS needs raw disk access.
  If the firmware doesn't support true HBA mode, one single-disk RAID-0
  virtual disk per drive works but hides SMART data.
- **iDRAC7 virtual media.** Map the ISO through Virtual Console → Virtual
  Media to install without physical USB.
- **Firmware.** Update BIOS/iDRAC first; boot mode must be **UEFI**.
- **No GPU.** Software transcoding only unless a discrete GPU is added.

Only move to the real R720 once the VM validation above is complete.
