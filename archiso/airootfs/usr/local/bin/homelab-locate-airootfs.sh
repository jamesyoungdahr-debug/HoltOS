#!/usr/bin/env bash
# Calamares shellprocess (dontChroot: true — runs in the LIVE session),
# right before unpackfs. unpackfs.conf hard-codes the live medium's
# squashfs at /run/archiso/bootmnt/arch/x86_64/airootfs.sfs — where the
# archiso initramfs hook mounts the medium. The very first real-hardware
# install (2026-09-11, USB stick) failed with "airootfs.sfs missing"
# because of the hook's copytoram=auto DEFAULT: when the medium is not
# an optical drive and MemAvailable exceeds the image size + 2 GiB, it
# copies the sfs to /run/archiso/copytoram/, then UNMOUNTS and REMOVES
# /run/archiso/bootmnt. Every USB boot on a machine with enough RAM hits
# this; the VM never did because it boots from a virtual DVD. Also note
# mkarchiso empties the airootfs' /boot, so the kernel unpackfs.conf
# copies from the medium is otherwise only in /usr/lib/modules/.
# Cases handled here, in order:
#   - copytoram: link the RAM copy of the sfs and the kernel from
#     /usr/lib/modules (works even if the stick was pulled);
#   - the ISO exposed as a block device (Ventoy's /dev/mapper/ventoy,
#     loop devices, a HOLTOS_* labelled stick/DVD) that is not mounted;
#   - the medium already mounted elsewhere (e.g. by a file manager).
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

# Case 1: copytoram — the sfs is already in RAM. The kernel: mkarchiso
# empties /boot in the airootfs, but the linux package's own copy at
# /usr/lib/modules/<running kernel>/vmlinuz is still there (it is what
# mkinitcpio's pacman hook normally copies to /boot).
if [ -f /run/archiso/copytoram/airootfs.sfs ]; then
    echo "==> copytoram boot: linking /run/archiso/copytoram/airootfs.sfs into $BOOTMNT"
    mkdir -p "$BOOTMNT/arch/x86_64" "$BOOTMNT/arch/boot/x86_64"
    ln -sf /run/archiso/copytoram/airootfs.sfs "$BOOTMNT/$SFS_REL"
    if [ ! -f "$BOOTMNT/$KERNEL_REL" ]; then
        kernel="/usr/lib/modules/$(uname -r)/vmlinuz"
        [ -f "$kernel" ] || kernel=/boot/vmlinuz-linux
        ln -sf "$kernel" "$BOOTMNT/$KERNEL_REL"
        echo "    kernel: $kernel"
    fi
    have_medium && { echo "    ok"; exit 0; }
    echo "    RAM copy present but kernel not found — trying the medium itself"
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
