#!/usr/bin/env bash
# Run by Calamares (chrooted into the target), after users/displaymanager.
# unpackfs copies the ENTIRE live squashfs onto the target verbatim,
# including live-session-only accounts and config that customize_airootfs.sh
# set up purely for the live ISO's own convenience (see
# airootfs/root/customize_airootfs.sh): the liveuser account, a
# wheel-GROUP-wide passwordless-sudo rule (not just for liveuser — it would
# grant unrestricted passwordless root to the real account just created,
# since Calamares' users module puts that account in wheel too), SDDM
# autologin pointed at liveuser, and the "Install homelab-os" desktop
# launcher. None of that belongs on the installed system — left in place,
# the install boots straight into a stale liveuser desktop instead of
# prompting for the real account.
#
# Real bug found live-testing the Btrfs install (session that added
# etc/calamares/modules/partition.conf): removing liveuser-wheel here with
# nothing to replace it left the real account with NO sudo at all — not
# even password-prompted. `sudo` itself failed outright ("holtos is not in
# the sudoers file"), even though the account IS correctly in the wheel
# group (Calamares' users module put it there) — because *no* sudoers rule
# for wheel existed anymore, passwordless or otherwise. Confirmed this
# didn't silently break the updater too: it's pkexec-based, and polkit's
# own default rule grants admin actions to wheel-group members
# independently of /etc/sudoers — a separate mechanism, confirmed still
# working (`pkexec whoami` → root) even with sudo broken. Fixed by
# replacing the passwordless rule with a normal, password-required one
# instead of just deleting it — sudoers.d files MUST be mode 0440 or sudo
# refuses to read them at all (a stricter check than most config files).
userdel -r liveuser 2>/dev/null || true
rm -f /etc/sudoers.d/liveuser-wheel
install -m 440 /dev/null /etc/sudoers.d/10-wheel
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel
rm -f /etc/sddm.conf.d/autologin.conf
rm -f /usr/share/applications/homelab-install.desktop
pacman -Rns --noconfirm calamares

# Real bug found in the same live-testing round as the sudoers one above:
# the installed target's pacman keyring was never initialized at all —
# confirmed live, `pacman -S` on the freshly booted install failed with
# "Public keyring not found; have you run 'pacman-key --init'?" even
# though the live medium itself installs packages fine during the build.
# unpackfs copies /etc/pacman.d/gnupg from the live squashfs verbatim, but
# archiso's own live-build keyring setup evidently doesn't carry over into
# something the installed system can use directly (GnuPG's random/session
# state doesn't survive a live→install copy the way plain config files
# do). Silent until the first `pacman -S`/`-Syu` — which is exactly what
# holtos-update-apply's `system` item runs, so this would have quietly
# broken the whole "System Packages" updater path for every real install.
# Fixed by just initializing it for real here, once, on the actual target.
# Live-tested 2026-09-11 on the first install from a clean-machine build:
# the init below was NOT enough on its own — the installed system STILL had
# no usable keyring ("keyring is not writable"). Two separate causes, both
# confirmed on the booted target:
#   1. archiso's own etc-pacman.d-gnupg.mount (a tmpfs over
#      /etc/pacman.d/gnupg, meant for the live medium only) rides along
#      into the install verbatim, and gnupg's socket units for that
#      directory (gpg-agent-pacman.d-gnupg.socket etc., via
#      RequiresMountsFor=) pull that mount unit in by name on every boot —
#      so whatever the chroot wrote to disk sits hidden under an empty
#      tmpfs. pacman-init.service is the matching archiso-only unit.
#   2. Even underneath that tmpfs the on-disk directory only had
#      gpg.conf/gpg-agent.conf: the master-key generation half of
#      `pacman-key --init` did not complete inside Calamares' chroot (this
#      script has no set -e, so it failed silently). The exact same two
#      commands run on the booted system worked first time.
# So: drop both archiso units from the target, still attempt the init here
# (harmless, and loud on failure now), and let
# holtos-pacman-keyring-init.service (etc/systemd/system/) finish the job on
# first boot if the chroot attempt left no pubring behind.
rm -f /etc/systemd/system/etc-pacman.d-gnupg.mount \
      /etc/systemd/system/pacman-init.service \
      /etc/systemd/system/multi-user.target.wants/pacman-init.service
{ pacman-key --init && pacman-key --populate archlinux; } \
    || echo "WARNING: pacman-key init/populate failed in chroot; holtos-pacman-keyring-init.service will retry on first boot" >&2

# unpackfs copies the live ISO's /etc/motd onto the target verbatim, and it
# ends with 'Double-click "Install HoltOS" on the desktop to launch the
# installer' -- wrong on an installed system (seen live 2026-09-12 at the
# Konsole/SSH login). Replace it with a one-liner. /etc/issue is fine as
# is ("HoltOS \r (\l)").
printf 'Welcome to \033[38;2;177;77;255mHoltOS\033[0m -- your media and gaming box. The Den runs as a service; open "The Den" from the app menu.\n\n' > /etc/motd

# The live-medium udev rule that hides the boot ISO/EFI partition from
# udisks must not ship on installs (real sticks with that label would vanish).
rm -f /etc/udev/rules.d/90-holtos-live-media.rules

# SDDM remembers the last session in /var/lib/sddm/state.conf and, with no
# state, preselects the first session file alphabetically -- that is
# holtos-gamemode.desktop, so a fresh install's login screen defaulted to
# Game Mode (seen live 2026-09-12, build 18). Seed it with Plasma;
# holtos-session-apply keeps it in sync afterwards.
if getent passwd sddm >/dev/null; then
    install -d -m 750 -o sddm -g sddm /var/lib/sddm
    printf '[Last]\nSession=/usr/share/wayland-sessions/plasma.desktop\n' > /var/lib/sddm/state.conf
    chown sddm:sddm /var/lib/sddm/state.conf
    chmod 600 /var/lib/sddm/state.conf
fi
