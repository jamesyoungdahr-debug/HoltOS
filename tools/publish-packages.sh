#!/usr/bin/env bash
# Publishes local-repo/ (the output of build-local-repo.sh) as the HoltOS
# pacman repository: the GitHub release tagged "packages" on this repo.
# archiso/pacman.conf's [homelab] section lists its download URL as the
# second server, so installed systems get HoltOS-built packages (the
# glass forks, Calamares, Limine tools, ZFS) through `pacman -Syu` from
# HoltOS' own release instead of only at image-build time.
#
# Rerun after every build-local-repo.sh whose packages should reach
# installed systems. Assets are replaced (--clobber); pacman needs the
# database under its plain name (homelab.db), which local-repo/ only has
# as a symlink, so real copies are uploaded. The "packages" tag is never
# picked up by the updater (it only looks at v* tags).
set -euo pipefail
cd "$(dirname "$0")/.."
repo="jamesyoungdahr-debug/holtos"
[ -f local-repo/homelab.db.tar.gz ] || { echo "local-repo/ is empty — run ./build-local-repo.sh first" >&2; exit 1; }

stage="$(mktemp -d)"
cp local-repo/*.pkg.tar.zst "$stage/"
cp local-repo/homelab.db.tar.gz "$stage/homelab.db.tar.gz"
cp local-repo/homelab.db.tar.gz "$stage/homelab.db"
cp local-repo/homelab.files.tar.gz "$stage/homelab.files.tar.gz"
cp local-repo/homelab.files.tar.gz "$stage/homelab.files"

if ! gh release view packages --repo "$repo" >/dev/null 2>&1; then
    gh release create packages --repo "$repo" --target master --prerelease \
        --title "HoltOS package repository" \
        --notes "pacman repository for HoltOS-built packages. Not a release: this tag is what archiso/pacman.conf's [homelab] section points at. Assets are replaced by tools/publish-packages.sh after each build-local-repo.sh."
fi
gh release upload packages --repo "$repo" --clobber "$stage"/*
rm -rf "$stage"
echo "Published $(ls local-repo/*.pkg.tar.zst | wc -l) packages + database to https://github.com/$repo/releases/tag/packages"
