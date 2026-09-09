#!/usr/bin/env bash
# Builds local-repo/ — the AUR packages (calamares, zfs-dkms, zfs-utils,
# limine-mkinitcpio-hook, limine-entry-tool) archiso/pacman.conf's
# [homelab] repo serves during the actual ISO build (build.sh). Run this
# once before the first build.sh, and again any time those packages need
# updating — it's safe to rerun, repo-add just refreshes the database.
#
# Run from Git Bash on Windows, same as build.sh — see that script's own
# comment for why the WSL-side path is derived rather than hardcoded.
set -euo pipefail
cd "$(dirname "$0")"

WSL_ROOT="/mnt$(pwd)"
mkdir -p local-repo

wsl -d Ubuntu -- sudo podman build -t aur-builder \
    -f "${WSL_ROOT}/containers/aur-builder.Containerfile" "${WSL_ROOT}"

export MSYS_NO_PATHCONV=1
wsl -d Ubuntu -- sudo podman run --rm \
    -v "${WSL_ROOT}/build-aur-packages.sh:/build-aur-packages.sh:Z" \
    -v "${WSL_ROOT}/local-repo:/tmp/pkgout:Z" \
    aur-builder \
    bash /build-aur-packages.sh

echo "local-repo/ ready:"
ls -la local-repo/
