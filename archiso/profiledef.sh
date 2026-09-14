#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="holtos"
iso_label="HOLTOS_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="HoltOS <https://github.com/jamesyoungdahr-debug/HoltOS>"
iso_application="HoltOS Live/Install Medium"
iso_version="0.0.7-alpha"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux'
           'uefi.systemd-boot')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '19' '-b' '1M')
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
  ["/usr/local/bin/homelab-limine-theme.sh"]="0:0:755"
  ["/usr/local/bin/homelab-cleanup-live.sh"]="0:0:755"
  ["/usr/local/bin/homelab-detect-hardware.sh"]="0:0:755"
  ["/usr/local/bin/homelab-locate-airootfs.sh"]="0:0:755"
  # HoltOS updater scripts. These were relying on the executable bit set
  # via `chmod +x` in the working copy surviving verbatim into the built
  # image — it doesn't reliably: this repo is edited on Windows/Git Bash,
  # and the archiso build reads it back through WSL2's drvfs mount
  # (/mnt/c/...), which doesn't always translate that bit the same way.
  # homelab-*.sh above already went through file_permissions for exactly
  # this reason; these were simply never added to the same list — real
  # bug hit live ("missing executable permissions" launching the
  # updater), not a build/packaging issue with the scripts themselves.
  ["/usr/local/bin/holtos-tray"]="0:0:755"
  ["/usr/local/bin/holtos-updates"]="0:0:755"
  ["/usr/local/bin/holtos-apps"]="0:0:755"
  ["/usr/local/bin/holtos-update-status"]="0:0:755"
  ["/usr/local/bin/holtos-update-apply"]="0:0:755"
  ["/usr/local/bin/holtos-update-install"]="0:0:755"
  ["/usr/local/bin/holtos-update-settings"]="0:0:755"
  ["/usr/local/bin/holtos-system-extras"]="0:0:755"
  ["/usr/local/bin/holtos-gamemode-client"]="0:0:755"
  ["/usr/bin/steamos-update"]="0:0:755"
  ["/usr/bin/steamos-polkit-helpers/steamos-update"]="0:0:755"
  ["/usr/bin/jupiter-biosupdate"]="0:0:755"
  ["/usr/bin/steamos-polkit-helpers/jupiter-biosupdate"]="0:0:755"
  ["/usr/local/bin/holtos-rollback-config"]="0:0:755"
  ["/usr/local/bin/holtos-btrfs-snapshot"]="0:0:755"
  ["/usr/local/bin/holtos-snapshot-now"]="0:0:755"
  ["/usr/local/bin/holtos-btrfs-restore"]="0:0:755"
  ["/usr/local/bin/holtos-restore-snapshot"]="0:0:755"
  ["/usr/local/bin/holtos-snapshot-boot-notice"]="0:0:755"
  ["/usr/local/bin/holtos-limine-other-os"]="0:0:755"
  ["/usr/local/bin/holtos-share"]="0:0:755"
  ["/usr/local/bin/holtos-proton-ge"]="0:0:755"
  ["/usr/local/bin/holtos-proton-ge-firstrun"]="0:0:755"
  ["/usr/local/bin/holtos-update-proton-ge"]="0:0:755"
  ["/usr/local/bin/holtos-gamemode-session"]="0:0:755"
  ["/usr/local/bin/holtos-session-apply"]="0:0:755"
  ["/usr/local/bin/steamos-session-select"]="0:0:755"
  ["/usr/lib/os-session-select"]="0:0:755"
  ["/usr/local/bin/holtos-shares"]="0:0:755"
  ["/usr/local/bin/holtos-gaming"]="0:0:755"
  ["/usr/local/bin/holtos-scrub"]="0:0:755"
  ["/usr/local/bin/holtos-disk-alert"]="0:0:755"
  ["/usr/local/bin/holtos-disk-alert-notice"]="0:0:755"
  ["/usr/local/bin/holtos-rescan-bootmenu"]="0:0:755"
)
