#!/usr/bin/env bash
# Run by Calamares' shellprocess@detect-hardware job, chrooted into the
# freshly-installed target (after cleanup-live, before limine-bootloader).
#
# Installs drivers that must NOT be on every machine, based on what is
# actually in the box. Everything else the hardware needs is already in
# the image unconditionally: Mesa (AMD/Intel GPUs, Vulkan + VA-API),
# linux-firmware, both CPU microcodes, ZFS. The one real special case is
# NVIDIA: its driver is a separate package set that only belongs on a
# machine with the card, so build-time staging puts the packages on the
# ISO (customize_airootfs.sh → /usr/share/holtos/drivers/nvidia/) and this
# script installs them here, with no network needed — the same principle
# as vendoring The Den. DKMS builds the module against the installed
# kernel right here (linux-headers + the toolchain are in the image for
# zfs-dkms already), and later kernel updates rebuild it through the
# normal dkms pacman hook.
#
# Everything detected and decided is logged to /var/lib/holtos/hardware.log.
set -euo pipefail

LOG=/var/lib/holtos/hardware.log
DRIVERS=/usr/share/holtos/drivers
CMDLINE_EXTRA=/var/lib/holtos/kernel-cmdline-extra   # read by homelab-limine-install.sh

mkdir -p /var/lib/holtos
{
    echo "# HoltOS hardware detection, $(date -u +%FT%TZ)"
    echo "## CPU"; grep -m1 'model name' /proc/cpuinfo || true
    echo "## Display controllers (PCI class 0300/0302)"
    lspci -nn -d ::0300 || true
    lspci -nn -d ::0302 || true
    echo "## Network controllers"
    lspci -nn -d ::0200 || true
    lspci -nn -d ::0280 || true
} > "$LOG"

: > "$CMDLINE_EXTRA"

# --- NVIDIA -------------------------------------------------------------
if lspci -n -d 10de: 2>/dev/null | grep -qE ' 03(00|02): '; then
    echo "## NVIDIA GPU present" >> "$LOG"
    if compgen -G "$DRIVERS/nvidia/*.pkg.tar.zst" > /dev/null; then
        echo "==> NVIDIA GPU detected — installing the staged driver packages (DKMS build follows)..."
        # Local files: pacman.conf's LocalFileSigLevel is Optional, so no
        # keyring is needed for these (they came from the official mirrors
        # over HTTPS at image-build time).
        pacman -U --noconfirm --needed "$DRIVERS"/nvidia/*.pkg.tar.zst 2>&1 | tail -20
        echo "installed: $(pacman -Q nvidia-open-dkms nvidia-utils 2>&1 | tr '\n' ' ')" >> "$LOG"
        # KMS is what Wayland/Plasma need from the nvidia driver; the
        # bootloader script appends this to the kernel command line.
        echo "nvidia_drm.modeset=1" >> "$CMDLINE_EXTRA"
        echo "cmdline: nvidia_drm.modeset=1" >> "$LOG"
    else
        echo "WARNING: NVIDIA GPU detected but no staged packages under $DRIVERS/nvidia — image built without them?" | tee -a "$LOG" >&2
    fi
else
    echo "## No NVIDIA GPU — nothing to install" >> "$LOG"
fi

# The staged packages are only useful at install time; don't carry
# hundreds of MB of somebody else's driver on every installed system.
rm -rf "$DRIVERS"

chmod 644 "$LOG"
echo "==> Hardware detection done (see /var/lib/holtos/hardware.log)"
