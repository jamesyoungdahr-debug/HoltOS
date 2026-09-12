#!/usr/bin/env bash
# Applies the HoltOS look to Limine's menu: rewrites the GLOBAL section of
# both limine.conf copies (everything above the first "/" entry) with the
# theme keys, and puts the menu font on the ESP. Entries and the HOLTOS
# SNAPSHOTS / OTHER OS blocks are left exactly as they are, so this is
# safe to run on an installed system — holtos-update-apply's config
# update does, which is how a theme change reaches existing installs.
# Called at install time by homelab-limine-install.sh.
#
# Limine 12 theming keys (see its CONFIG.md): branded header instead of
# "Limine x.y.z", the HoltOS palette for help/countdown/selection, a
# real 12x24 bitmap font (Terminus Bold, shipped pre-converted as
# /usr/share/holtos/limine/ter-124b.bin — see tools/convert-limine-font.sh
# — because Limine wants raw glyph rows, not a PSF file), and the menu in
# a translucent ink panel (term_background TTRRGGBB) with a soft gradient
# margin over the wallpaper. Prototyped on screen in the VM 2026-09-12.
set -euo pipefail

for candidate in /boot/efi /efi /boot; do
    if mountpoint -q "$candidate" 2>/dev/null && [ -d "$candidate/EFI" -o -w "$candidate" ]; then
        ESP="$candidate"
        break
    fi
done
: "${ESP:?Could not find a mounted EFI System Partition under /boot/efi, /efi, or /boot}"

mkdir -p "${ESP}/holtos"
cp /usr/share/holtos/limine/ter-124b.bin "${ESP}/holtos/ter-124b.bin"
[ -f "${ESP}/wallpaper.png" ] || cp /usr/share/wallpapers/HoltOS/contents/images/1920x1080.png "${ESP}/wallpaper.png"

. /etc/os-release

updated=0
for LIMINE_CONF in "${ESP}/EFI/limine/limine.conf" "${ESP}/EFI/BOOT/limine.conf"; do
    [ -f "$LIMINE_CONF" ] || continue
    # Keep whatever timeout the file has (holtos-limine-other-os raises it
    # to 5 when there is a choice); default 3.
    timeout="$(grep -m1 -oE '^timeout: [0-9]+' "$LIMINE_CONF" | grep -oE '[0-9]+$' || true)"
    : "${timeout:=3}"
    header="$(cat <<EOF
timeout: ${timeout}

interface_branding: ${PRETTY_NAME:-HoltOS}
interface_branding_colour: B14DFF
interface_help_colour: 6B6B6B
interface_help_colour_bright: 28E0C8

wallpaper: boot():/wallpaper.png
wallpaper_style: stretched
backdrop: 0D0B12

term_font: boot():/holtos/ter-124b.bin
term_font_size: 12x24
term_font_spacing: 1
term_margin: 120
term_margin_gradient: 40
term_background: 90171423
term_foreground: F4EBFF
term_background_bright: B14DFF
term_foreground_bright: 0D0B12
term_palette: 0D0B12;B14DFF;28E0C8;F4EBFF;171423;B14DFF;28E0C8;F4EBFF
term_palette_bright: 171423;C77DFF;5FF0DC;FFFFFF;2A2438;C77DFF;5FF0DC;FFFFFF
EOF
)"
    # Everything from the first entry ("/...") onward is kept verbatim.
    entries="$(awk 'found { print; next } /^\// { found = 1; print }' "$LIMINE_CONF")"
    printf '%s\n\n%s\n' "$header" "$entries" > "${LIMINE_CONF}.tmp"
    mv "${LIMINE_CONF}.tmp" "$LIMINE_CONF"
    updated=1
done

if [ "$updated" -eq 1 ]; then
    echo "==> Limine menu themed (${PRETTY_NAME:-HoltOS})"
else
    echo "==> WARNING: no limine.conf found under ${ESP}" >&2
    exit 1
fi
