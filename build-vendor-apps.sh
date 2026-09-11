#!/usr/bin/env bash
# Fetches the latest tagged release of The Den and The Den Client into the
# archiso profile so both ship INSIDE the image, installed at build time by
# customize_airootfs.sh (`holtos-update-apply vendor`) — a fresh install
# has both present and running from first boot with no network dependency,
# instead of relying on the updater to fetch them on first boot (which was
# the previous design: holtos-first-boot-apps, retired 2026-09-11).
#
# Run by build.sh before mkarchiso; safe to run by hand. Output lands in
# archiso/airootfs/opt/holtos-vendor/ (gitignored, like local-repo/):
#   <name>/         the release's source tree
#   manifest        one "<name>\t<tag>\t<commit>" line per app, which the
#                   vendor step records into /var/lib/holtos/history.log so
#                   the tray's Update History / Rollback have a baseline.
#
# Tag resolution is the same as holtos-update-apply's resolve_release():
# latest v* tag, preferring the peeled (^{}) commit sha of an annotated tag.
set -euo pipefail
cd "$(dirname "$0")"

VENDOR_DIR="archiso/airootfs/opt/holtos-vendor"
APPS=(the-den the-den-client)
OWNER="jamesyoungdahr-debug"

resolve_release() {
    local url="https://github.com/$1.git" raw tag sha
    raw="$(git ls-remote --tags --sort=-v:refname "$url" 'v*')"
    [ -n "$raw" ] || return 1
    tag="$(head -1 <<< "$raw" | cut -f2)"
    tag="${tag%^\{\}}"
    tag="${tag#refs/tags/}"
    sha="$(awk -F'\t' -v want="refs/tags/${tag}^{}" '$2==want{print $1}' <<< "$raw")"
    [ -n "$sha" ] || sha="$(awk -F'\t' -v want="refs/tags/${tag}" '$2==want{print $1}' <<< "$raw")"
    [ -n "$sha" ] || return 1
    printf '%s\t%s\n' "$sha" "$tag"
}

rm -rf "$VENDOR_DIR"
mkdir -p "$VENDOR_DIR"
: > "$VENDOR_DIR/manifest"

for app in "${APPS[@]}"; do
    repo="$OWNER/$app"
    if ! IFS=$'\t' read -r commit tag < <(resolve_release "$repo"); then
        echo "build-vendor-apps: no tagged v* release found for $repo" >&2
        exit 1
    fi
    echo "==> Vendoring $app $tag ($commit)"
    mkdir -p "$VENDOR_DIR/$app"
    curl -fsSL "https://github.com/$repo/archive/refs/tags/${tag}.tar.gz" \
        | tar -xzf - -C "$VENDOR_DIR/$app" --strip-components=1
    printf '%s\t%s\t%s\n' "$app" "$tag" "$commit" >> "$VENDOR_DIR/manifest"
done

echo "Vendored into $VENDOR_DIR:"
cat "$VENDOR_DIR/manifest"
