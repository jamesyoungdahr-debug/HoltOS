#!/usr/bin/env bash
# Sets the Arch Linux snapshot date this branch's HoltOS installs update from.
#
# HoltOS pins Arch's core, extra and multilib repositories to one day of the
# Arch Linux Archive (https://archive.archlinux.org/repos/YYYY/MM/DD/), so a
# system update installs only the package set HoltOS tested, never whatever
# Arch published that morning (Liam, 2026-09-15, after kernel 7.2.6 reached
# the ROG Flow Z13 untested). Each branch carries its own date: neon-rebrand
# (the dev channel) moves first, master (stable) follows once a date has been
# tested. The date lives in archiso/airootfs/etc/pacman.d/holtos-mirrorlist,
# which the config update copies to installed systems.
#
#   tools/set-arch-snapshot.sh 2026/09/14     set that date (checked first)
#   tools/set-arch-snapshot.sh                print the current date
#
# The date must exist on the Archive for core, extra and multilib; today's
# date usually appears only the next day.
set -euo pipefail
cd "$(dirname "$0")/.."

FILE=archiso/airootfs/etc/pacman.d/holtos-mirrorlist
ARCHIVE=https://archive.archlinux.org/repos

if [ $# -eq 0 ]; then
    if [ -f "$FILE" ]; then
        grep -oE 'repos/[0-9]{4}/[0-9]{2}/[0-9]{2}' "$FILE" | head -n 1 | sed 's|^repos/||'
    else
        echo "no $FILE yet" >&2
        exit 1
    fi
    exit 0
fi

date="$1"
if ! [[ "$date" =~ ^[0-9]{4}/[0-9]{2}/[0-9]{2}$ ]]; then
    echo "usage: tools/set-arch-snapshot.sh YYYY/MM/DD" >&2
    exit 2
fi

for repo in core extra multilib; do
    url="$ARCHIVE/$date/$repo/os/x86_64/$repo.db"
    code="$(curl -sIL -m 30 -o /dev/null -w '%{http_code}' "$url" || true)"
    if [ "$code" != 200 ]; then
        echo "The Arch Linux Archive has no $repo database for $date (HTTP $code): $url" >&2
        exit 1
    fi
done

mkdir -p "$(dirname "$FILE")"
cat > "$FILE" <<EOF
# HoltOS: the Arch Linux packages this HoltOS release updates from.
#
# core, extra and multilib in /etc/pacman.conf read this file instead of
# /etc/pacman.d/mirrorlist, so a system update installs exactly the Arch
# package set of one day in the Arch Linux Archive, the day HoltOS tested.
# HoltOS releases move the date forward; the config update replaces this
# file. Do not add live mirrors here: mixing a dated snapshot with an
# up-to-date mirror installs packages from different days.
#
# Set with tools/set-arch-snapshot.sh in the HoltOS repository.
Server = $ARCHIVE/$date/\$repo/os/\$arch
EOF
echo "Arch snapshot date set to $date in $FILE"
