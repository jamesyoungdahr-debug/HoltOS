#!/usr/bin/env bash
# Publishes local-repo/ (the output of build-local-repo.sh) as the HoltOS
# pacman repository: the GitHub release tagged "packages" on this repo.
# archiso/pacman.conf's [homelab] section lists its download URL as the
# second server, so installed systems get HoltOS-built packages (the glass
# forks, Calamares, Limine tools, ZFS, model extras such as z13ctl) through
# `pacman -Syu` from HoltOS' own release instead of only at image-build time.
#
# Some local-repo packages must not reach installed systems yet: everything
# named in EXCLUDE (by default HoltOS' KWin and plasma-workspace forks,
# which replace the stock packages and have only run in the VM). They stay
# in ISO builds; the published database is rebuilt without them, so an
# installed system's `pacman -Syu` never swaps its compositor.
#
#   tools/publish-packages.sh
#   EXCLUDE="pkg other-pkg" tools/publish-packages.sh
#
# Rerun after every build-local-repo.sh whose packages should reach
# installed systems. Assets are replaced (--clobber); pacman needs the
# database under its plain name (homelab.db), so real copies are uploaded.
# Excluded packages that an earlier run published are deleted from the
# release. The "packages" tag is never picked up by the updater (it only
# looks at v* tags).
set -euo pipefail
cd "$(dirname "$0")/.."
repo="jamesyoungdahr-debug/holtos"
EXCLUDE="${EXCLUDE-holtos-kwin holtos-plasma-workspace}"
[ -f local-repo/homelab.db.tar.gz ] || { echo "local-repo/ is empty — run ./build-local-repo.sh first" >&2; exit 1; }

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
    bash -c "cd /stage && repo-add -q homelab.db.tar.gz *.pkg.tar.zst"
unset MSYS_NO_PATHCONV
# repo-add leaves homelab.db and homelab.files as symlinks; replace them with
# real copies (cp onto the symlink would write into its own target).
rm -f "$stage/homelab.db" "$stage/homelab.files" "$stage"/*.old
cp "$stage/homelab.db.tar.gz" "$stage/homelab.db"
cp "$stage/homelab.files.tar.gz" "$stage/homelab.files"

if ! gh release view packages --repo "$repo" >/dev/null 2>&1; then
    gh release create packages --repo "$repo" --target master --prerelease \
        --title "HoltOS package repository" \
        --notes "pacman repository for HoltOS-built packages. Not a release: this tag is what archiso/pacman.conf's [homelab] section points at. Assets are replaced by tools/publish-packages.sh after each build-local-repo.sh."
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
