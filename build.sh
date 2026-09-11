#!/usr/bin/env bash
# Builds the HoltOS ISO via mkarchiso inside a privileged podman container in
# WSL2 Ubuntu. Run from Git Bash on Windows (uses /mnt/c/... paths for the
# WSL side, /c/... for the host side).
#
# Any ISO(s) already in out/ get moved to out/backups/<timestamp>/ first —
# a build never silently overwrites a previous one worth keeping.
set -euo pipefail
cd "$(dirname "$0")"

if compgen -G "out/*.iso" > /dev/null; then
    ts="$(date +%Y%m%d-%H%M%S)"
    mkdir -p "out/backups/$ts"
    mv out/*.iso "out/backups/$ts/"
    echo "Backed up previous ISO(s) to out/backups/$ts/"
fi

# Seed the state file holtos-update-check compares against, so a fresh
# install doesn't immediately think it's out of date against the very
# commit it was built from.
mkdir -p archiso/airootfs/var/lib/holtos
git rev-parse HEAD > archiso/airootfs/var/lib/holtos/deployed-commit

# Git Bash's own /c/... paths and WSL2's /mnt/c/... paths use the same
# layout under the drive letter, just a different mount prefix — real bug
# hit trying to run this on a machine other than the one it was first
# written on: this used to hardcode /mnt/c/Users/Liam/..., which silently
# pointed at nothing (or someone else's files) for any other Windows
# username or clone location. Derive it from wherever this checkout
# actually is instead.
WSL_ROOT="/mnt$(pwd)"

LOG="out/build-$(date +%Y%m%d-%H%M%S).log"
export MSYS_NO_PATHCONV=1
wsl -d Ubuntu -- sudo podman run --privileged --rm \
    -v "${WSL_ROOT}/archiso:/profile:Z" \
    -v "${WSL_ROOT}/local-repo:/homelab-local-repo:Z" \
    -v "${WSL_ROOT}/out:/tmp/out:Z" \
    archiso-image \
    bash -c "mkarchiso -v -w /tmp/work -o /tmp/out /profile" | tee "$LOG"

echo "Build finished. Log: $LOG"
ls -la out/*.iso

# The container writes the ISO as root via a WSL2 drvfs mount, which drops
# the ACL entries a normally-created Windows file would have — Hyper-V's
# VMMS service then can't open it as a VM DVD attachment ("Access is
# denied"). Grant read to Authenticated Users so Start-VM works without a
# manual icacls fix after every rebuild. (unset so icacls, a native Windows
# exe, gets a real Windows path instead of the literal POSIX one — but that
# same conversion then also rewrites the /grant switch itself into
# "C:/Program Files/Git/grant" (real failure, exit 87 "Invalid parameter",
# hit on the first clean-machine build); the doubled slash is Git Bash's
# documented escape for a literal leading-slash argument.)
unset MSYS_NO_PATHCONV
for iso in out/*.iso; do
    icacls "$iso" //grant "Authenticated Users:(R)" > /dev/null
done
