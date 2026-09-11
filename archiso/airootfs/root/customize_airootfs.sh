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

# systemd only honors real symlinks in *.wants/ directories. This profile
# used to ship plain FILES there (copies of the units — git on Windows
# can't store symlinks, so releng-reference's symlinks flattened into
# copies on the way in), and systemd silently ignored every one of them:
# confirmed live 2026-09-11, holtos-first-boot-apps and
# homelab-sync-arr-keys had never run on the installed system and
# `systemctl list-dependencies multi-user.target` didn't list them.
# Enabling here creates proper symlinks at image-build time instead.
systemctl enable choose-mirror.service livecd-alsa-unmuter.service
systemctl enable holtos-first-boot-apps.service
systemctl enable holtos-pacman-keyring-init.service

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
cp /usr/share/applications/homelab-install.desktop /home/liveuser/Desktop/homelab-install.desktop
chmod +x /home/liveuser/Desktop/homelab-install.desktop
chown -R liveuser:liveuser /home/liveuser
