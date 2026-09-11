#!/usr/bin/env bash
# Installs and configures Limine as the bootloader for the just-installed
# system. Run by Calamares' shellprocess@limine-bootloader job, chrooted
# into the target — so every path/command here operates on the target
# system, not the live session.
#
# Written as a real script rather than a static limine.conf baked into the
# image, specifically to avoid depending on Calamares' own GlobalStorage
# placeholder-substitution syntax for the root partition UUID — this script
# determines it itself, live, from the actual target it's running in
# (findmnt on "/" inside a chroot reflects the chroot's own root, i.e. the
# target system Calamares just built).

set -euo pipefail

# The ESP is the partition Calamares mounted at /boot/efi (or /efi,
# depending on partition layout) — check both, matching limine-entry-tool's
# own documented auto-detection order.
for candidate in /boot/efi /efi /boot; do
    if mountpoint -q "$candidate" 2>/dev/null && [ -d "$candidate/EFI" -o -w "$candidate" ]; then
        ESP="$candidate"
        break
    fi
done
: "${ESP:?Could not find a mounted EFI System Partition under /boot/efi, /efi, or /boot}"

mkdir -p "${ESP}/EFI/limine"
cp /usr/share/limine/BOOTX64.EFI "${ESP}/EFI/limine/BOOTX64.EFI"
# Also drop a copy at the removable-media fallback path — boots correctly
# even on firmware that ignores/loses the NVRAM entry below, which matters
# for a homelab server whose exact firmware behavior isn't fully known yet.
mkdir -p "${ESP}/EFI/BOOT"
cp /usr/share/limine/BOOTX64.EFI "${ESP}/EFI/BOOT/BOOTX64.EFI"

ROOT_UUID="$(findmnt -no UUID /)"
ROOT_DEVICE="$(findmnt -no SOURCE /)"
ESP_DISK="$(lsblk -no PKNAME "$(findmnt -no SOURCE "${ESP}")")"
ESP_PARTNUM="$(findmnt -no SOURCE "${ESP}" | grep -oE '[0-9]+$')"

# Kernel/initramfs are loaded from the ESP via `boot():` (resolves to "the
# partition Limine itself was loaded from") instead of straight from root,
# root filesystem be damned what it is. Originally forced by a real ext4
# bug: mkfs.ext4 on a current e2fsprogs enables the `orphan_file` and
# `metadata_csum_seed` features by default, which Limine's ext4 driver
# doesn't understand, so it failed to open ANY path on that partition
# (confirmed live: PANIC "Failed to open kernel with path" even with a
# correct uuid()-referenced path and a verified-matching UUID). Root is
# Btrfs now (see etc/calamares/modules/partition.conf), and Limine does
# have a Btrfs driver — but keeping this same ESP-copy pattern anyway
# rather than trusting an unverified claim that it reads OUR specific
# subvolume layout cleanly, and it needs to exist regardless for the
# per-snapshot kernel/initramfs copies holtos-btrfs-snapshot adds later
# (see the HOLTOS SNAPSHOTS block below) — those load the exact same way.
# Kept in sync on kernel upgrades by the homelab-limine-sync pacman hook
# (see /etc/pacman.d/hooks/95-homelab-limine-sync.hook).
mkdir -p "${ESP}/boot"
cp /boot/vmlinuz-linux "${ESP}/boot/vmlinuz-linux"
cp /boot/initramfs-linux.img "${ESP}/boot/initramfs-linux.img"

# Root is Btrfs (see etc/calamares/modules/partition.conf) with a @
# subvolume, not the top-level (subvolid=5) — rootflags=subvol=@ is what
# tells the kernel/initramfs which subvolume to actually mount as / on
# first boot, same as the subvol= mount option Calamares' own mount.conf
# (btrfsSubvolumes) already puts in the target's /etc/fstab for every
# later remount. Without it the kernel mounts the raw top-level subvolume
# instead of @, which is essentially empty — none of the installed
# system's actual files live there.
ROOTFLAGS="subvol=@"

# HoltOS-branded wallpaper for the Limine menu itself — reuses the same
# raster image already used as the installed system's KDE desktop
# wallpaper (see usr/share/plasma/look-and-feel/org.holtos.desktop), so
# boot menu and desktop match. Limine can only read its own ESP
# (boot():), same reason the kernel/initramfs live there instead of on
# root — see the comment above this block for the full story; copying a
# 30KB PNG here costs nothing.
cp /usr/share/wallpapers/HoltOS/contents/images/1920x1080.png "${ESP}/wallpaper.png"

# Real bug found live-testing this exact fallback path (not a Btrfs-
# specific issue — pre-existed, just never actually exercised until a test
# forced the VM to boot via the generic HDD/removable-media path instead
# of the NVRAM entry below): Limine's own config search checks the
# directory of the EFI binary THAT WAS ACTUALLY LOADED first (confirmed
# against Limine's real init_efi_app_path()/init_config_disk() source) —
# it does not automatically also check the OTHER copy's directory. Loaded
# via /EFI/limine/BOOTX64.EFI (the NVRAM entry below), it looks for
# /EFI/limine/limine.conf and finds it fine. Loaded via the
# /EFI/BOOT/BOOTX64.EFI fallback copy above (what actually happens on
# firmware that ignores/loses NVRAM — the whole reason that copy exists),
# it looked for /EFI/BOOT/limine.conf, found nothing, and refused to boot
# at all ("[config file not found]", confirmed live). Writing the exact
# same config to both paths makes it boot correctly regardless of which
# copy the firmware actually runs.
LIMINE_CONF_CONTENT="$(cat <<EOF
timeout: 3

wallpaper: boot():/wallpaper.png
wallpaper_style: stretched
backdrop: 0D0B12
term_palette: 0D0B12;B14DFF;28E0C8;F4EBFF;171423;B14DFF;28E0C8;F4EBFF

/HoltOS
    protocol: linux
    path: boot():/boot/vmlinuz-linux
    cmdline: root=UUID=${ROOT_UUID} rootflags=${ROOTFLAGS} rw quiet splash
    module_path: boot():/boot/initramfs-linux.img

#### HOLTOS SNAPSHOTS START ####
#### HOLTOS SNAPSHOTS END ####
EOF
)"
printf '%s\n' "$LIMINE_CONF_CONTENT" > "${ESP}/EFI/limine/limine.conf"
printf '%s\n' "$LIMINE_CONF_CONTENT" > "${ESP}/EFI/BOOT/limine.conf"

# NVRAM entry — best-effort; the fallback path copy above is what actually
# guarantees boot if this doesn't take (e.g. firmware without NVRAM
# support, or running inside a VM that doesn't persist it).
efibootmgr --create \
    --disk "/dev/${ESP_DISK}" \
    --part "${ESP_PARTNUM}" \
    --label "HoltOS" \
    --loader '\EFI\limine\BOOTX64.EFI' \
    --unicode || true

echo "Limine installed: root=${ROOT_DEVICE} (UUID=${ROOT_UUID}), ESP=${ESP}"
