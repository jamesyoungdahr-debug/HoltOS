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

# systemd only honors real symlinks in *.wants/ directories, and git on
# Windows can't store symlinks (the releng wants/ entries flattened into
# plain files that systemd silently ignored — confirmed live 2026-09-11).
# Enabling here creates proper symlinks at image-build time instead.
systemctl enable choose-mirror.service livecd-alsa-unmuter.service
systemctl enable holtos-pacman-keyring-init.service

# Stage the NVIDIA driver packages on the ISO WITHOUT installing them:
# homelab-detect-hardware.sh installs them into the target at install
# time only if an NVIDIA GPU is present (no network needed then). The
# dependency set is resolved against THIS image, so nothing already in
# packages.x86_64 is duplicated. The [homelab] local repo is only
# reachable at build time from the host, so the download uses a
# pacman.conf without it — and with signature checking off: the chroot
# has no pacman keyring (creating one here proved unreliable — see
# homelab-cleanup-live.sh), the files come straight from the HTTPS
# mirrors, and they are only STAGED here, not installed. CheckSpace is
# dropped too: inside the mkarchiso chroot pacman cannot map the cache
# dir to a mount point and aborts with a bogus "not enough free disk
# space" (this exact failure killed a build on 2026-09-11), and
# DownloadUser goes with it so the download runs as root and can write
# to the root-owned staging dir.
echo "==> Staging NVIDIA driver packages for install-time detection..."
sed -e '/^\[homelab\]/,$d' \
    -e 's/^SigLevel .*/SigLevel = Never/' \
    -e 's/^LocalFileSigLevel .*/LocalFileSigLevel = Never/' \
    -e '/^CheckSpace/d' \
    -e '/^DownloadUser/d' \
    /etc/pacman.conf > /tmp/pacman-stage.conf
mkdir -p /usr/share/holtos/drivers/nvidia
pacman -Syw --noconfirm --config /tmp/pacman-stage.conf \
    --cachedir /usr/share/holtos/drivers/nvidia nvidia-open-dkms nvidia-utils
rm -f /usr/share/holtos/drivers/nvidia/*.sig /tmp/pacman-stage.conf
echo "    staged: $(ls /usr/share/holtos/drivers/nvidia | tr '\n' ' ')"

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
cp /usr/share/applications/homelab-install.desktop /home/liveuser/Desktop/homelab-install.desktop
chmod +x /home/liveuser/Desktop/homelab-install.desktop
chown -R liveuser:liveuser /home/liveuser
