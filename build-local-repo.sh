#!/usr/bin/env bash
# Builds local-repo/ — the AUR packages (calamares, zfs-dkms, zfs-utils,
# limine-mkinitcpio-hook, limine-entry-tool) and HoltOS' own packages
# (packaging/*, sources in forks/) that archiso/pacman.conf's [homelab]
# repo serves during the actual ISO build (build.sh). Run this once before
# the first build.sh, and again any time those packages need updating —
# it's safe to rerun, repo-add just refreshes the database.
#
# Rebuilding everything takes a long time (calamares, zfs). To rebuild a
# subset:
#   AUR_PKGS=none HOLTOS_PKGS=holtos-glass-effect ./build-local-repo.sh
#
# HoltOS' own packages are built from the source trees in forks/ (this
# repo), versioned with the current commit count so a rebuild always
# sorts newer than the previous package.
#
# Run from Git Bash on Windows, same as build.sh — see that script's own
# comment for why the WSL-side path is derived rather than hardcoded.
set -euo pipefail
cd "$(dirname "$0")"

WSL_ROOT="/mnt$(pwd)"
HOLTOS_REV="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
mkdir -p local-repo
mkdir -p .pacman-cache

# Must be set BEFORE the first wsl call, not just before `podman run`: Git
# Bash rewrites any argument that looks like a POSIX path (/mnt/c/...)
# into a Windows path before handing it to a native exe like wsl.exe, so
# without this the Containerfile and build-context paths below arrive
# inside WSL mangled and `podman build` fails to find either.
export MSYS_NO_PATHCONV=1

wsl -d Ubuntu -- sudo podman build -t aur-builder \
    -f "${WSL_ROOT}/containers/aur-builder.Containerfile" "${WSL_ROOT}"

# persists pacman's downloaded packages across container runs (which are --rm and otherwise start from an empty cache each time), since rebuilding holtos-kwin/holtos-plasma-workspace during iteration re-downloads the same ~266MB of shared dependencies every single retry otherwise
wsl -d Ubuntu -- sudo podman run --rm \
    -e "AUR_PKGS=${AUR_PKGS:-}" \
    -e "HOLTOS_PKGS=${HOLTOS_PKGS:-}" \
    -e "HOLTOS_REV=${HOLTOS_REV}" \
    -v "${WSL_ROOT}/build-aur-packages.sh:/build-aur-packages.sh:Z" \
    -v "${WSL_ROOT}/packaging:/pkgbuilds:Z" \
    -v "${WSL_ROOT}/forks:/forks:Z" \
    -v "${WSL_ROOT}/local-repo:/tmp/pkgout:Z" \
    -v "${WSL_ROOT}/.pacman-cache:/var/cache/pacman/pkg:Z" \
    aur-builder \
    bash /build-aur-packages.sh

echo "local-repo/ ready:"
ls -la local-repo/
