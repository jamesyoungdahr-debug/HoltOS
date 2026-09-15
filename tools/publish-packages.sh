#!/usr/bin/env bash
# Publishes local-repo/ (the output of build-local-repo.sh) as the HoltOS
# pacman repository: the GitHub release tagged "packages" on this repo.
# archiso/pacman.conf's [holtos] section lists its download URL as the
# second server, so installed systems get HoltOS-built packages (the glass
# forks, Calamares, Limine tools, ZFS, model extras such as z13ctl) through
# `pacman -Syu` from HoltOS' own release instead of only at image-build time.
#
# Every package in local-repo/ is published, including HoltOS's KWin and
# plasma-workspace forks (Liam, 2026-09-14, with 0.0.7-alpha): they replace
# the stock packages, so an installed system's `pacman -Syu` swaps in the
# HoltOS builds. EXCLUDE still keeps named packages out of the published
# database if one ever has to be held back.
#
#   tools/publish-packages.sh
#   EXCLUDE="pkg other-pkg" tools/publish-packages.sh
#
# Rerun after every build-local-repo.sh whose packages should reach
# installed systems. Assets are replaced (--clobber); pacman needs the
# database under its plain name (holtos.db, plus homelab.db for installs
# that still have the old section name), so real copies are uploaded.
# Excluded packages that an earlier run published are deleted from the
# release. The "packages" tag is never picked up by the updater (it only
# looks at v* tags).
set -euo pipefail
cd "$(dirname "$0")/.."
repo="jamesyoungdahr-debug/holtos"
EXCLUDE="${EXCLUDE-}"
[ -f local-repo/holtos.db.tar.gz ] || { echo "local-repo/ is empty — run ./build-local-repo.sh first" >&2; exit 1; }

# pkg_name FILE — the package name from name-version-release-arch.pkg.tar.zst
pkg_name() {
    local base
    base="$(basename "$1" .pkg.tar.zst)"
    printf '%s' "${base%-*-*-*}"
}

stage=".publish-stage"
rm -rf "$stage"
mkdir -p "$stage"
for f in local-repo/*.pkg.tar.zst; do
    name="$(pkg_name "$f")"
    if [[ " $EXCLUDE " == *" $name "* ]]; then
        echo "==> Not publishing $(basename "$f") (in EXCLUDE)"
        continue
    fi
    cp "$f" "$stage/"
done

# Rebuild the database for exactly the staged packages. repo-add needs
# pacman's tools, so it runs in the aur-builder container that
# build-local-repo.sh uses (Git Bash has no repo-add).
export MSYS_NO_PATHCONV=1
wsl -d Ubuntu -- sudo podman run --rm \
    -v "/mnt$(pwd)/${stage}:/stage:Z" \
    aur-builder \
    bash -c "cd /stage && repo-add -q holtos.db.tar.gz *.pkg.tar.zst"
unset MSYS_NO_PATHCONV
# repo-add leaves holtos.db and holtos.files as symlinks; replace them with
# real copies (cp onto the symlink would write into its own target).
rm -f "$stage/holtos.db" "$stage/holtos.files" "$stage"/*.old
cp "$stage/holtos.db.tar.gz" "$stage/holtos.db"
cp "$stage/holtos.files.tar.gz" "$stage/holtos.files"
# The repository was called [homelab] until the rename to HoltOS (Liam,
# 2026-09-14). Installs that have not taken the update which renames their
# pacman.conf section still ask for homelab.db, so the same database is
# published under that name too. Drop these copies a few releases later.
for ext in db files db.tar.gz files.tar.gz; do
    cp "$stage/holtos.$ext" "$stage/homelab.$ext"
done

if ! gh release view packages --repo "$repo" >/dev/null 2>&1; then
    gh release create packages --repo "$repo" --target master --prerelease \
        --title "HoltOS package repository" \
        --notes "pacman repository for HoltOS-built packages. Not a release: this tag is what archiso/pacman.conf's [holtos] section points at. Assets are replaced by tools/publish-packages.sh after each build-local-repo.sh."
fi

# Excluded packages published by an earlier run come off the release.
for name in $EXCLUDE; do
    { gh release view packages --repo "$repo" --json assets --jq '.assets[].name' \
        | grep -E "^${name}-[^-]+-[^-]+-[^-]+\.pkg\.tar\.zst$" || true; } \
        | while read -r asset; do
            echo "==> Removing ${asset} from the release (in EXCLUDE)"
            gh release delete-asset packages "$asset" --repo "$repo" --yes
        done
done

gh release upload packages --repo "$repo" --clobber "$stage"/*
count="$(ls "$stage"/*.pkg.tar.zst | wc -l)"
rm -rf "$stage"
echo "Published ${count} packages + database to https://github.com/$repo/releases/tag/packages"
