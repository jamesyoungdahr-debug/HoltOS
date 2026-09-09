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
pacman-key --init
pacman-key --populate archlinux
