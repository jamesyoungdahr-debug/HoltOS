#!/usr/bin/env bash
# Run by mkarchiso, chrooted into the live airootfs, during image build.
# (This hook is marked deprecated upstream but still functions as of the
# archiso version this profile was built against — see mkarchiso's own
# source, _make_customize_airootfs.)
#
# Whatever this script does to the live rootfs also ends up on the
# INSTALLED target too, since Calamares' unpackfs module just copies this
# same squashfs onto the target disk (see unpackfs.conf) — so enabling
# NetworkManager/sddm here covers both the live session and the final
# installed system in one step.
set -euo pipefail

# /etc/locale.conf is already set (LANG=C.UTF-8, from releng-reference) but
# /etc/localtime is not — systemd-firstboot blocks live boot on an
# interactive console prompt for whichever of {timezone, locale, hostname,
# root password} isn't already configured. A live/install medium must never
# require interactive input just to reach a login screen, so pre-seed the
# timezone and mask the service as a defense-in-depth backstop.
ln -sf /usr/share/zoneinfo/UTC /etc/localtime
systemctl mask systemd-firstboot.service

systemctl enable NetworkManager.service
systemctl enable sddm.service
# Power profiles (performance / balanced / power saver) for the Power KCM
# and the battery widget.
systemctl enable power-profiles-daemon.service
# bluez daemon for bluedevil (Bluetooth remotes/headphones); added with the
# System Settings pages that were missing from build 9 (2026-09-12).
systemctl enable bluetooth.service

# systemd only honors real symlinks in *.wants/ directories, and git on
# Windows can't store symlinks (the releng wants/ entries flattened into
# plain files that systemd silently ignored — confirmed live 2026-09-11).
# Enabling here creates proper symlinks at image-build time instead.
systemctl enable choose-mirror.service livecd-alsa-unmuter.service
systemctl enable holtos-pacman-keyring-init.service
# Finishes a snapshot restore on the next boot (deletes the replaced root
# subvolume, which cannot be removed while it is the running root).
systemctl enable holtos-btrfs-restore-cleanup.service
# Disk health: smartd polls SMART and records failures for the per-login
# notice (etc/smartd.conf -> holtos-disk-alert); the timer scrubs every
# Btrfs filesystem and ZFS pool monthly (holtos-scrub).
systemctl enable smartd.service holtos-scrub.timer
# Update checks on a schedule (holtos-update-status; HoltOS Updates > Settings).
systemctl enable holtos-update-check.timer
# Undo an update that stops the desktop from starting (holtos-boot-guard).
systemctl enable holtos-boot-guard.service holtos-boot-guard-check.timer
# Network Shares browses the LAN: avahi finds servers, and .local names
# resolve through nss-mdns (before resolve, as the Arch wiki sets it up).
systemctl enable avahi-daemon.service
sed -i '/^hosts:/{/mdns_minimal/!s/resolve/mdns_minimal [NOTFOUND=return] resolve/}' /etc/nsswitch.conf
# Create Flatpak's system repository now, which also adds Flathub from
# /etc/flatpak/remotes.d. Flatpak only does that on first use by root, so
# without this Stash's search finds nothing until something runs as
# root. Needs no network (verified with networking cut off).
flatpak remotes --system >/dev/null 2>&1 || true

# [multilib] for the live AND installed system (Steam + lib32 drivers are
# in the image; without this the installed system could not update them).
sed -i '/^#\[multilib\]/,/^#Include = \/etc\/pacman.d\/mirrorlist/ s/^#//' /etc/pacman.conf

# The HoltOS package repository for the live AND installed system: the
# profile's pacman.conf (with its build-time file:// server) is only used
# by mkarchiso itself; the rootfs carries the pacman package's stock
# /etc/pacman.conf, so the installed system never had the repository until
# now (found 2026-09-12 when pointing an install at the published repo).
# Called [homelab] until the rename to HoltOS (2026-09-14).
if ! grep -q '^\[holtos\]' /etc/pacman.conf; then
    cat /usr/share/holtos/pacman-holtos.conf >> /etc/pacman.conf
fi

# Only HoltOS wallpapers: pacman never unpacks another package's wallpapers
# (KDE's extra wallpapers, Breeze's "Next"), and the copies already
# installed into the image are removed. pacman reads NoExtract patterns
# last to first, so the HoltOS exception wins.
if ! grep -q '^NoExtract = usr/share/wallpapers/' /etc/pacman.conf; then
    sed -i '/^\[options\]/a NoExtract = usr/share/wallpapers/* !usr/share/wallpapers/HoltOS*' /etc/pacman.conf
fi
find /usr/share/wallpapers -mindepth 1 -maxdepth 1 ! -name 'HoltOS*' -exec rm -rf {} +

# Only HoltOS themes (neon rebrand, Liam 2026-09-14): the same NoExtract rule
# and removal as holtos-system-extras' trim_themes (keep the lists in sync).
# Plasma's "default" style, SDDM's breeze and Plymouth's text and details stay
# as fallbacks.
if ! grep -q '^NoExtract = usr/share/Kvantum/Kv' /etc/pacman.conf; then
    sed -i '/^\[options\]/a NoExtract = usr/share/Kvantum/Kv* usr/share/color-schemes/Kv* usr/share/color-schemes/Breeze* usr/share/plasma/desktoptheme/breeze-dark/* usr/share/plasma/desktoptheme/breeze-light/* usr/share/sddm/themes/elarun/* usr/share/sddm/themes/maldives/* usr/share/sddm/themes/maya/* usr/share/plymouth/themes/bgrt/* usr/share/plymouth/themes/fade-in/* usr/share/plymouth/themes/glow/* usr/share/plymouth/themes/script/* usr/share/plymouth/themes/solar/* usr/share/plymouth/themes/spinfinity/* usr/share/plymouth/themes/spinner/* usr/share/plymouth/themes/tribar/*' /etc/pacman.conf
fi
rm -rf /usr/share/Kvantum/Kv* /usr/share/color-schemes/Kv*.colors /usr/share/color-schemes/Breeze*.colors \
       /usr/share/plasma/desktoptheme/breeze-dark /usr/share/plasma/desktoptheme/breeze-light \
       /usr/share/sddm/themes/elarun /usr/share/sddm/themes/maldives /usr/share/sddm/themes/maya \
       /usr/share/plymouth/themes/bgrt /usr/share/plymouth/themes/fade-in /usr/share/plymouth/themes/glow \
       /usr/share/plymouth/themes/script /usr/share/plymouth/themes/solar /usr/share/plymouth/themes/spinfinity \
       /usr/share/plymouth/themes/spinner /usr/share/plymouth/themes/tribar

# The OS is called HoltOS everywhere: Arch's filesystem package ships
# /usr/lib/os-release naming Arch Linux (Steam's system info showed it). Use
# ours and keep pacman from unpacking Arch's again (same as
# holtos-system-extras' fix_os_identity). /etc/lsb-release is written from
# os-release too, so the version lives in one file.
if ! grep -q '^NoExtract = usr/lib/os-release' /etc/pacman.conf; then
    sed -i '/^\[options\]/a NoExtract = usr/lib/os-release' /etc/pacman.conf
fi
install -m 644 /etc/os-release /usr/lib/os-release
(
    . /etc/os-release
    printf 'DISTRIB_ID="%s"\nDISTRIB_RELEASE="%s"\nDISTRIB_DESCRIPTION="%s"\n' \
        "$NAME" "$VERSION_ID" "$PRETTY_NAME" > /etc/lsb-release
)

# Stage the hardware-specific driver packages on the ISO WITHOUT installing
# them: every package named in /usr/share/holtos/hardware-drivers.conf
# (NVIDIA, Broadcom Wi-Fi, laptop audio firmware, sensors, fingerprint
# readers...), indexed as a small local repo so the installer can resolve
# their dependencies offline. holtos-detect-hardware.sh installs only the
# ones the install target's hardware needs (holtos-hardware). The
# dependency set is resolved against THIS image, so nothing already in
# packages.x86_64 is duplicated. The [holtos] local repo is only
# reachable at build time from the host, so the download uses a
# pacman.conf without it — and with signature checking off: the chroot
# has no pacman keyring (creating one here proved unreliable — see
# holtos-cleanup-live.sh), the files come straight from the HTTPS
# mirrors, and they are only STAGED here, not installed. CheckSpace is
# dropped too: inside the mkarchiso chroot pacman cannot map the cache
# dir to a mount point and aborts with a bogus "not enough free disk
# space" (this exact failure killed a build on 2026-09-11), and
# DownloadUser goes with it so the download runs as root and can write
# to the root-owned staging dir.
echo "==> Staging hardware driver packages for install-time detection..."
sed -e '/^\[holtos\]/,$d' \
    -e 's/^SigLevel .*/SigLevel = Never/' \
    -e 's/^LocalFileSigLevel .*/LocalFileSigLevel = Never/' \
    -e '/^CheckSpace/d' \
    -e '/^DownloadUser/d' \
    /etc/pacman.conf > /tmp/pacman-stage.conf
driver_packages="$(awk '!/^[[:space:]]*#/ && NF >= 3 { print $3 }' /usr/share/holtos/hardware-drivers.conf | tr ',' '\n' | sort -u | tr '\n' ' ')"
mkdir -p /usr/share/holtos/drivers
# shellcheck disable=SC2086
pacman -Syw --noconfirm --needed --config /tmp/pacman-stage.conf \
    --cachedir /usr/share/holtos/drivers $driver_packages
rm -f /usr/share/holtos/drivers/*.sig /tmp/pacman-stage.conf
repo-add -q /usr/share/holtos/drivers/holtos-drivers.db.tar.gz /usr/share/holtos/drivers/*.pkg.tar.zst
echo "    staged for: $driver_packages"
echo "    files: $(ls /usr/share/holtos/drivers | wc -l)"

# Install The Den + The Den Client from the release trees build-vendor-apps.sh
# staged under /opt/holtos-vendor (see that script). Runs the same install
# code the tray updater uses, so a later "Update The Den" is an in-place
# update of exactly this layout. Fatal if the trees are missing: a HoltOS
# image without The Den is a broken build, not a warning.
[ -f /opt/holtos-vendor/manifest ] || { echo "customize_airootfs: /opt/holtos-vendor/manifest missing — run build-vendor-apps.sh (build.sh does)" >&2; exit 1; }
bash /usr/local/bin/holtos-update-apply vendor

# A non-root live user, auto-logged into Plasma — the standard pattern for
# Calamares-based live distros (CachyOS, EndeavourOS, Manjaro all do this),
# so the live session boots straight to a usable desktop with our installer
# icon, no manual login step.
useradd -m -G wheel -s /bin/bash liveuser
echo "liveuser:liveuser" | chpasswd
echo "%wheel ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/liveuser-wheel

mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/autologin.conf <<'EOF'
[Autologin]
User=liveuser
Session=plasma
EOF

# Desktop launcher for our installer, visible on the live session's desktop.
mkdir -p /home/liveuser/Desktop
cp /usr/share/applications/holtos-install.desktop /home/liveuser/Desktop/holtos-install.desktop
chmod +x /home/liveuser/Desktop/holtos-install.desktop
# The live session must never lock itself: the installer ran to completion
# behind a lock screen during the build 9 VM test (2026-09-12) and anyone
# installing from a USB stick would hit the same thing after 5 idle
# minutes, with a password nobody told them (liveuser). Live-only — the
# installed system keeps the normal locker; this file is liveuser's, not
# skel's.
cat >> /home/liveuser/.config/kscreenlockerrc <<'EOF'

[Daemon]
Autolock=false
LockOnResume=false
EOF
chown -R liveuser:liveuser /home/liveuser
