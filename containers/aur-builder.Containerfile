# Builds the AUR packages our archiso profile needs (calamares, zfs-dkms,
# zfs-utils, limine-mkinitcpio-hook, limine-entry-tool — none of which are
# in the official Arch repos) into local-repo/, which pacman.conf then
# treats as an extra repo during the actual ISO build. See
# build-aur-packages.sh, which runs inside a container from this image.
#
# Reconstructed the same way as archiso-image.Containerfile — this used
# to be two separate hand-built images (a "calamares-build-base" plus a
# "calamares-installed" layered on top of it, the latter apparently used
# once to build calamares itself via some manual step that was never
# scripted). Folded back into one image and one script:
# build-aur-packages.sh now builds calamares the same uniform way it
# already built the other four packages — which is what pacman.conf's own
# comment describes the local repo as containing, and what it should have
# been doing all along.
#
# `builder`: makepkg refuses to run as root, and `-s`/`--syncdeps` needs
# sudo to install each package's own build dependencies unattended —
# NOPASSWD is safe here, this container never runs anything but our own
# trusted build script. `pacman-contrib`: provides `repo-add`, which
# build-aur-packages.sh uses to generate local-repo/'s actual repo
# database (homelab.db*) — pacman won't treat a directory of loose
# .pkg.tar.zst files as a repo without one, another step that used to
# happen by hand and isn't scripted anywhere.
#
# Build once:
#   podman build -t aur-builder -f containers/aur-builder.Containerfile .
FROM docker.io/library/archlinux:latest

# The archlinux base image ships a populated keyring but no local master
# key, so the archlinux-keyring package's own upgrade hook fails with
# "There is no secret key available to sign with" (seen live, first
# clean-state build of this file) and any packager keys added since the
# base image was cut never get locally signed -- pacman then rejects
# packages signed by them. Initialize the keyring properly first.
RUN pacman-key --init && pacman-key --populate archlinux

RUN pacman -Syu --noconfirm --needed base-devel git sudo pacman-contrib && \
    useradd -m -u 1000 builder && \
    echo 'builder ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/builder && \
    chmod 440 /etc/sudoers.d/builder
