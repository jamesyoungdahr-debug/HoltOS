#!/usr/bin/env bash
# Run by the holtos-limine-sync pacman hook after every kernel/initramfs
# update. Limine loads the kernel via `boot():` (see holtos-limine-install.sh
# for why: its ext4 driver can't read a filesystem with the orphan_file /
# metadata_csum_seed features current mkfs.ext4 enables by default) — that
# means the copies living on the ESP are what actually boots, not
# /boot/vmlinuz-linux itself. Without this, a routine kernel upgrade would
# regenerate /boot/initramfs-linux.img but leave the ESP's copy stale, and
# the next boot would run the OLD kernel with a mismatched initramfs.
set -euo pipefail

for candidate in /boot/efi /efi /boot; do
    if mountpoint -q "$candidate" 2>/dev/null && [ -d "$candidate/EFI" -o -w "$candidate" ]; then
        ESP="$candidate"
        break
    fi
done
: "${ESP:?Could not find a mounted EFI System Partition under /boot/efi, /efi, or /boot}"

mkdir -p "${ESP}/boot"

# Small ESPs (HoltOS installed alongside Windows on its 100MiB EFI
# partition): a bigger new kernel or initramfs might not fit, and a
# half-copied kernel would not boot. Count the space the old copy frees,
# and remove the oldest snapshot kernel copies until the new one fits
# (Liam, 2026-09-14: dual boot).
need_kb=$(( ( $(stat -c %s /boot/vmlinuz-linux) + $(stat -c %s /boot/initramfs-linux.img) ) / 1024 + 4096 ))
room_kb() {
    echo $(( $(df -Pk "$ESP" | awk 'NR == 2 { print $4 }') + $(du -sk "${ESP}/boot" 2>/dev/null | cut -f1) ))
}
pruned=0
while [ "$(room_kb)" -lt "$need_kb" ]; do
    oldest="$(ls -1d "${ESP}"/holtos-snapshots/*/ 2>/dev/null | sort | head -n 1)"
    [ -n "$oldest" ] || break
    echo "==> Not enough room on the EFI partition; removing the kernel copy of snapshot $(basename "$oldest")"
    rm -rf "$oldest"
    pruned=1
done
[ "$(room_kb)" -ge "$need_kb" ] || echo "==> WARNING: the EFI partition may be too small for this kernel" >&2

cp /boot/vmlinuz-linux "${ESP}/boot/vmlinuz-linux"
cp /boot/initramfs-linux.img "${ESP}/boot/initramfs-linux.img"
# Snapshots whose kernel copy was removed lose their boot entries.
if [ "$pruned" -eq 1 ]; then
    /usr/local/bin/holtos-btrfs-snapshot --regen || true
fi

# Same moment is a good one to re-detect other operating systems (a
# Windows install added after HoltOS, a removed disk): see
# holtos-limine-other-os. Best-effort.
/usr/local/bin/holtos-limine-other-os || true
