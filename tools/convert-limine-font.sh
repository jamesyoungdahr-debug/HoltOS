#!/usr/bin/env bash
# Regenerates archiso/airootfs/usr/share/holtos/limine/ter-124b.bin — the
# Limine menu font — from the Terminus PSF2 font. Limine's term_font wants
# raw glyph rows (256 glyphs x 24 rows x 2 bytes = 12288 bytes), not a PSF
# file, so this strips the PSF2 header. The result is committed so neither
# the image build nor the updater needs the terminus-font package: HoltOS
# components come from the HoltOS repo, not fetched ad hoc from Arch.
#
# Usage (any Linux with python3 and a Terminus PSF, e.g. Arch's
# terminus-font package or Ubuntu's fonts-terminus... the Arch file is
# /usr/share/kbd/consolefonts/ter-124b.psf.gz):
#   tools/convert-limine-font.sh /usr/share/kbd/consolefonts/ter-124b.psf.gz
set -euo pipefail
src="${1:?usage: $0 <ter-124b.psf.gz>}"
out="$(dirname "$0")/../archiso/airootfs/usr/share/holtos/limine/ter-124b.bin"
mkdir -p "$(dirname "$out")"
tmp="$(mktemp)"
case "$src" in *.gz) gunzip -c "$src" > "$tmp" ;; *) cp "$src" "$tmp" ;; esac
python3 - "$tmp" "$out" <<'EOF'
import struct, sys
d = open(sys.argv[1], "rb").read()
assert d[:4] == b"\x72\xb5\x4a\x86", "not a PSF2 font"
_ver, hs, _flags, cnt, cs, h, w = struct.unpack("<IIIIIII", d[4:32])
assert (w, h) == (12, 24), f"unexpected glyph size {w}x{h}"
open(sys.argv[2], "wb").write(d[hs:hs + 256 * cs])
print(f"wrote {sys.argv[2]}: 256 glyphs of {w}x{h}, {256 * cs} bytes")
EOF
rm -f "$tmp"
