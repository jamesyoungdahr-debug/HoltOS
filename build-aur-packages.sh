#!/usr/bin/env bash
# Run as root inside a container from containers/aur-builder.Containerfile
# (see BUILD.md). Builds every AUR package our archiso profile needs, plus
# HoltOS' own packages (packaging/*/PKGBUILD), as the 'builder' user,
# leaving the resulting .pkg.tar.zst files in /tmp/pkgout for extraction
# into local-repo/.
#
# Environment (all optional, passed through by build-local-repo.sh):
#   AUR_PKGS     space-separated subset of the AUR packages to (re)build;
#                "none" skips the AUR phase entirely.
#   HOLTOS_PKGS  space-separated subset of packaging/* to (re)build;
#                "none" skips them. Default: every directory in /pkgbuilds.
#   HOLTOS_REV   version suffix for the HoltOS packages (commit count).
set -euo pipefail

# The image's package database is as old as the image; makepkg -s installs
# dependencies with plain pacman -S, which 404s once the mirrors have moved
# on. Refresh (and upgrade, so headers match the libraries) first.
pacman -Syu --noconfirm

mkdir -p /tmp/pkgout
chown builder:builder /tmp/pkgout

AUR_DEFAULT="calamares zfs-dkms zfs-utils limine-mkinitcpio-hook limine-entry-tool"
AUR_PKGS="${AUR_PKGS:-$AUR_DEFAULT}"

if [ "$AUR_PKGS" != "none" ]; then
    # zfs-dkms's tarball is signed by the OpenZFS release key, which isn't in
    # the default keyring — import it before makepkg tries to verify sources.
    su - builder -c "gpg --keyserver keyserver.ubuntu.com --recv-keys 6AD860EED4598027" || \
    su - builder -c "gpg --keyserver hkps://keys.openpgp.org --recv-keys 6AD860EED4598027"

    for pkg in $AUR_PKGS; do
        echo "=== Building ${pkg} (AUR) ==="
        rm -rf "/tmp/build-${pkg}"
        su - builder -c "git clone https://aur.archlinux.org/${pkg}.git /tmp/build-${pkg}"
        su - builder -c "cd /tmp/build-${pkg} && makepkg -s --noconfirm --needed"
        cp /tmp/build-"${pkg}"/*.pkg.tar.zst /tmp/pkgout/
    done
fi

# HoltOS' own packages: PKGBUILDs from the HoltOS repo's packaging/
# directory (mounted at /pkgbuilds), sources from the repo's forks/
# directory (mounted at /forks): each is tarred into the build dir as
# <name>.tar, which the PKGBUILD lists as its only source. HOLTOS_REV
# (the HoltOS commit count, from build-local-repo.sh) versions them.
if [ -d /pkgbuilds ]; then
    HOLTOS_PKGS="${HOLTOS_PKGS:-$(ls /pkgbuilds)}"
    if [ "$HOLTOS_PKGS" != "none" ]; then
        for pkg in $HOLTOS_PKGS; do
            echo "=== Building ${pkg} (HoltOS) ==="
            [ -f "/pkgbuilds/${pkg}/PKGBUILD" ] || { echo "no /pkgbuilds/${pkg}/PKGBUILD" >&2; exit 1; }
            rm -rf "/tmp/build-${pkg}"
            mkdir -p "/tmp/build-${pkg}"
            cp "/pkgbuilds/${pkg}/"* "/tmp/build-${pkg}/"
            if [ -d "/forks/${pkg}" ]; then
                # Some HoltOS packages (like holtos-kwin, holtos-plasma-workspace) are too large to vendor into forks/ and instead have a git source directly in their PKGBUILD, so there's no /forks tree to tar for them.
                tar -cf "/tmp/build-${pkg}/${pkg}.tar" -C /forks "${pkg}"
            fi
            chown -R builder:builder "/tmp/build-${pkg}"
            su - builder -c "cd /tmp/build-${pkg} && HOLTOS_REV='${HOLTOS_REV:-0}' makepkg -s --noconfirm --needed"
            # An older build of the same package would otherwise sit next to
            # the new one and repo-add would keep whichever sorts last.
            rm -f /tmp/pkgout/"${pkg}"-*.pkg.tar.zst
            cp /tmp/build-"${pkg}"/*.pkg.tar.zst /tmp/pkgout/
        done
    fi
fi

# pacman.conf's [homelab] repo needs an actual repo database, not just a
# directory of loose packages — repo-add builds/updates homelab.db(.tar.gz)
# and homelab.files(.tar.gz) (+ the .db/.files symlinks pacman expects) from
# whatever .pkg.tar.zst files are already sitting in /tmp/pkgout. Safe to
# rerun: adding a package that's already in the database just updates it.
chown builder:builder /tmp/pkgout/*.pkg.tar.zst
su - builder -c "cd /tmp/pkgout && repo-add -R homelab.db.tar.gz *.pkg.tar.zst"

echo "=== Done, packages in /tmp/pkgout ==="
ls -la /tmp/pkgout/
