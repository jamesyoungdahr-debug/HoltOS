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
CMDLINE_EXTRA=/var/lib/holtos/kernel-cmdline-extra   # read by holtos-limine-install.sh

mkdir -p /var/lib/holtos
{
    echo "# HoltOS hardware detection, $(date -u +%FT%TZ)"
    echo "## CPU"; grep -m1 'model name' /proc/cpuinfo || true
    # 0380 ("Display controller", other): AMD APUs such as Strix Halo's
    # Radeon 8060S report this class instead of 0300 VGA.
    echo "## Display controllers (PCI class 0300/0302/0380)"
    lspci -nn -d ::0300 || true
    lspci -nn -d ::0302 || true
    lspci -nn -d ::0380 || true
    echo "## Network controllers"
    lspci -nn -d ::0200 || true
    lspci -nn -d ::0280 || true
} > "$LOG"

: > "$CMDLINE_EXTRA"

# --- Drivers this machine's hardware needs ------------------------------
# The rules in /usr/share/holtos/hardware-drivers.conf decide (holtos-hardware,
# the same check every update runs); the packages come from the local repo
# staged on the ISO by customize_airootfs.sh, so no network is needed.
# Liam, 2026-09-14: check the install target's hardware and provide working
# drivers, not just NVIDIA.
needed=""
if [ -x /usr/local/bin/holtos-hardware ] && [ -f "$DRIVERS/holtos-drivers.db.tar.gz" ]; then
    needed="$(/usr/local/bin/holtos-hardware missing | cut -f1 | tr '\n' ' ')"
    echo "## Drivers this hardware needs: ${needed:-none}" >> "$LOG"
    if [ -n "${needed// /}" ]; then
        echo "==> Installing drivers for this machine: $needed"
        cat > /tmp/pacman-drivers.conf <<EOF
[options]
Architecture = auto
SigLevel = Never
LocalFileSigLevel = Never

[holtos-drivers]
Server = file://$DRIVERS
EOF
        # shellcheck disable=SC2086
        pacman -Sy --noconfirm --needed --config /tmp/pacman-drivers.conf $needed 2>&1 | tail -20 || \
            echo "WARNING: installing drivers failed: $needed" | tee -a "$LOG" >&2
        rm -f /tmp/pacman-drivers.conf /var/lib/pacman/sync/holtos-drivers.db /var/lib/pacman/sync/holtos-drivers.files
        echo "installed: $(pacman -Q $needed 2>&1 | tr '\n' ' ')" >> "$LOG"
    fi
    case " $needed " in
        *" thermald "*) systemctl enable thermald.service >/dev/null 2>&1 || true ;;
    esac
else
    echo "WARNING: no holtos-hardware or no staged driver repo under $DRIVERS — image built without them?" | tee -a "$LOG" >&2
fi

# --- NVIDIA boot settings ------------------------------------------------
if pacman -Q nvidia-utils >/dev/null 2>&1; then
    echo "## NVIDIA driver installed" >> "$LOG"
    # KMS is what Wayland/Plasma need from the nvidia driver; the
    # bootloader script appends this to the kernel command line.
    echo "nvidia_drm.modeset=1" >> "$CMDLINE_EXTRA"
    echo "cmdline: nvidia_drm.modeset=1" >> "$LOG"
    # modeset=1 alone leaves simpledrm contending for the console
    # framebuffer on NVIDIA; fbdev=1 hands it over cleanly. Needed for
    # gamescope/Game Mode to behave well on NVIDIA (CachyOS ships the
    # same file for the same reason).
    cat > /etc/modprobe.d/nvidia-drm.conf <<'EOF'
options nvidia_drm modeset=1
options nvidia_drm fbdev=1
EOF
    echo "wrote: /etc/modprobe.d/nvidia-drm.conf (modeset=1 fbdev=1)" >> "$LOG"
fi

# --- AMD / Intel (Mesa is in the image; nothing to install) --------------
# Log what the in-image stack actually reports for this GPU so a real
# machine's hardware.log answers "is hardware decode/Vulkan there?" without
# anyone having to run the tools by hand. Strix Halo (Ryzen AI Max, RDNA
# 3.5, gfx1151) is the first real AMD target (Liam, 2026-09-12): amdgpu +
# RADV + VA-API through Mesa cover it, and Plasma gets HDR/VRR from
# amdgpu's KMS. This runs in the chroot before first boot, so the DRM
# node may not be usable yet; every probe is best-effort.
if lspci -n -d 1002: 2>/dev/null | grep -qE ' 03(00|02|80): '; then
    {
        echo "## AMD GPU present (Mesa RADV + VA-API from the image)"
        lspci -nn -d 1002: | grep -E 'VGA|Display|3D' || true
        command -v vainfo >/dev/null && (vainfo --display drm 2>/dev/null | grep -E 'Driver version|VAProfile' | head -20 || echo "vainfo: no usable DRM node in the install chroot (check after first boot)")
        command -v vulkaninfo >/dev/null && (vulkaninfo --summary 2>/dev/null | grep -E 'deviceName|driverName|apiVersion' | head -6 || echo "vulkaninfo: not usable in the install chroot (check after first boot)")
    } >> "$LOG" 2>&1 || true
fi
if lspci -n -d 8086: 2>/dev/null | grep -qE ' 03(00|02|80): '; then
    { echo "## Intel GPU present (Mesa ANV + VA-API from the image)"; lspci -nn -d 8086: | grep -E 'VGA|Display' || true; } >> "$LOG" 2>&1 || true
fi

# The staged packages are only useful at install time; don't carry
# hundreds of MB of somebody else's driver on every installed system.
rm -rf "$DRIVERS"

chmod 644 "$LOG"
echo "==> Hardware detection done (see /var/lib/holtos/hardware.log)"
