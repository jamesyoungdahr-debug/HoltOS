#!/usr/bin/env bash
# Run as root inside a container from containers/aur-builder.Containerfile
# (see BUILD.md). Builds every AUR package our archiso profile needs as
# the 'builder' user, leaving the resulting .pkg.tar.zst files in
# /tmp/pkgout for extraction into local-repo/.
set -euo pipefail

mkdir -p /tmp/pkgout
chown builder:builder /tmp/pkgout

# zfs-dkms's tarball is signed by the OpenZFS release key, which isn't in
# the default keyring — import it before makepkg tries to verify sources.
su - builder -c "gpg --keyserver keyserver.ubuntu.com --recv-keys 6AD860EED4598027" || \
su - builder -c "gpg --keyserver hkps://keys.openpgp.org --recv-keys 6AD860EED4598027"

for pkg in calamares zfs-dkms zfs-utils limine-mkinitcpio-hook limine-entry-tool klassy; do
    echo "=== Building ${pkg} ==="
    rm -rf "/tmp/build-${pkg}"
    su - builder -c "git clone https://aur.archlinux.org/${pkg}.git /tmp/build-${pkg}"
    su - builder -c "cd /tmp/build-${pkg} && makepkg -s --noconfirm --needed"
    cp /tmp/build-"${pkg}"/*.pkg.tar.zst /tmp/pkgout/
done

# pacman.conf's [homelab] repo needs an actual repo database, not just a
# directory of loose packages — repo-add builds/updates homelab.db(.tar.gz)
# and homelab.files(.tar.gz) (+ the .db/.files symlinks pacman expects) from
# whatever .pkg.tar.zst files are already sitting in /tmp/pkgout. Safe to
# rerun: adding a package that's already in the database just updates it.
chown builder:builder /tmp/pkgout/*.pkg.tar.zst
su - builder -c "cd /tmp/pkgout && repo-add homelab.db.tar.gz *.pkg.tar.zst"

echo "=== Done, packages in /tmp/pkgout ==="
ls -la /tmp/pkgout/
