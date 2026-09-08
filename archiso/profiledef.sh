#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="holtos"
iso_label="HOLTOS_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="HoltOS <https://github.com/jamesyoungdahr-debug/HoltOS>"
iso_application="HoltOS Live/Install Medium"
iso_version="0.0.1-alpha"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux'
           'uefi.systemd-boot')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86,arm64' '-b' '1M' '-Xdict-size' '1M')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/usr/local/bin/homelab-limine-install.sh"]="0:0:755"
  ["/usr/local/bin/homelab-fix-mkinitcpio.sh"]="0:0:755"
  ["/usr/local/bin/homelab-limine-sync.sh"]="0:0:755"
  ["/usr/local/bin/homelab-cleanup-live.sh"]="0:0:755"
  ["/usr/local/bin/homelab-generate-secrets.sh"]="0:0:755"
  ["/usr/local/bin/homelab-sync-arr-keys.sh"]="0:0:755"
)
