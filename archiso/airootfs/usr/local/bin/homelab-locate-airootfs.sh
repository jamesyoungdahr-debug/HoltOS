#!/usr/bin/env bash
# Calamares shellprocess (dontChroot: true — runs in the LIVE session),
# right before unpackfs. unpackfs.conf hard-codes the live medium's
# squashfs at /run/archiso/bootmnt/arch/x86_64/airootfs.sfs — the path
# the archiso initramfs hook mounts it at when booted from a plainly
# written (dd / Rufus DD mode / Etcher) USB stick or a DVD. Booted other
# ways the file ends up somewhere else and Calamares failed with
# "airootfs.sfs missing" on the very first real-hardware attempt
# (2026-09-11, Ventoy). Cases handled here:
#   - copytoram: the hook copies the sfs to /run/archiso/copytoram/ and
#     unmounts bootmnt;
#   - Ventoy and other loop-style boots: the ISO is exposed as a block
#     device (/dev/mapper/ventoy, /dev/loop*) that is not, or no longer,
#     mounted at bootmnt;
#   - a labelled HOLTOS_* medium that is simply not mounted.
# Whatever is found is mounted or symlinked so unpackfs.conf's fixed
# paths resolve. Fails loudly, listing what it looked at, so the
# Calamares log (and the error dialog) shows the real reason.
set -uo pipefail

BOOTMNT=/run/archiso/bootmnt
SFS_REL=arch/x86_64/airootfs.sfs
KERNEL_REL=arch/boot/x86_64/vmlinuz-linux

have_medium() { [ -f "$BOOTMNT/$SFS_REL" ] && [ -f "$BOOTMNT/$KERNEL_REL" ]; }

if have_medium; then
    echo "live medium present at $BOOTMNT ($(findmnt -no SOURCE "$BOOTMNT" 2>/dev/null || echo 'not a mountpoint'))"
    exit 0
fi

echo "==> $BOOTMNT/$SFS_REL not found — locating the live medium..."
echo "    cmdline: $(cat /proc/cmdline)"
findmnt "$BOOTMNT" 2>/dev/null || echo "    $BOOTMNT is not a mountpoint"
ls -la /run/archiso 2>/dev/null | sed 's/^/    /'

# Case 1: copytoram — the sfs is already in RAM; the kernel is still in
# the live root's /boot (mkarchiso copies it out of airootfs/boot, it
# does not remove it).
if [ -f /run/archiso/copytoram/airootfs.sfs ]; then
    echo "==> copytoram boot: linking /run/archiso/copytoram/airootfs.sfs into $BOOTMNT"
    mkdir -p "$BOOTMNT/arch/x86_64" "$BOOTMNT/arch/boot/x86_64"
    ln -sf /run/archiso/copytoram/airootfs.sfs "$BOOTMNT/$SFS_REL"
    [ -f "$BOOTMNT/$KERNEL_REL" ] || ln -sf /boot/vmlinuz-linux "$BOOTMNT/$KERNEL_REL"
    have_medium && { echo "    ok"; exit 0; }
fi

# Case 2: a block device carrying the ISO (Ventoy's dm-mapped ISO first,
# then any loop device, then a labelled stick/DVD). Mounted read-only on
# top of whatever is or isn't at bootmnt; unmounted again if it is not
# ours.
mkdir -p "$BOOTMNT"
for dev in /dev/mapper/ventoy /dev/loop[0-9]* /dev/disk/by-label/HOLTOS_* /dev/sr[0-9]*; do
    [ -b "$dev" ] || continue
    if mount -o ro "$dev" "$BOOTMNT" 2>/dev/null; then
        if have_medium; then
            echo "==> live medium found on $dev, mounted at $BOOTMNT"
            exit 0
        fi
        echo "    $dev: mounts but has no $SFS_REL"
        umount "$BOOTMNT" 2>/dev/null || true
    else
        echo "    $dev: not mountable"
    fi
done

# Case 3: already mounted somewhere else (e.g. a file manager mounted
# the stick). Bind-mount the directory that holds arch/.
found="$(find /run/media /media /mnt -maxdepth 5 -path "*/$SFS_REL" -print -quit 2>/dev/null || true)"
if [ -n "$found" ]; then
    root="${found%/$SFS_REL}"
    echo "==> live medium found at $root, bind-mounting to $BOOTMNT"
    mount --bind "$root" "$BOOTMNT" && have_medium && exit 0
fi

echo "ERROR: cannot find the HoltOS live medium (airootfs.sfs) anywhere." >&2
echo "       Block devices:" >&2
lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINTS 2>/dev/null | sed 's/^/       /' >&2
echo "       If this stick was made with Ventoy, try Ventoy's 'Boot in normal mode';" >&2
echo "       otherwise write the ISO with dd / Rufus (DD image mode) / balenaEtcher." >&2
exit 1
