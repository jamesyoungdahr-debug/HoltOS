# Runs mkarchiso to actually build the ISO — see build.sh, which mounts
# archiso/ (the profile), local-repo/ (our AUR packages), and out/ into a
# container from this image and runs mkarchiso inside it.
#
# Reconstructed from the image that was actually in use (built once,
# interactively, via `podman commit` — never captured as a Containerfile,
# which is exactly the kind of gap that breaks a build on any machine
# that isn't the one it was hand-built on). archiso itself needs nothing
# beyond the base Arch image plus the `archiso` package: `pacman -Qe`
# against the real working image showed only `base` and `archiso` as
# explicitly installed — everything else (arch-install-scripts,
# squashfs-tools, libisoburn, dosfstools, mtools, erofs-utils, ...) comes
# in as archiso's own dependency tree.
#
# Build once:
#   podman build -t archiso-image -f containers/archiso-image.Containerfile .
FROM docker.io/library/archlinux:latest

# The archlinux base image ships a populated keyring but no local master
# key, so the archlinux-keyring package's own upgrade hook fails with
# "There is no secret key available to sign with" (seen live, first
# clean-state build of this file) and any packager keys added since the
# base image was cut never get locally signed -- pacman then rejects
# packages signed by them. Initialize the keyring properly first.
RUN pacman-key --init && pacman-key --populate archlinux

RUN pacman -Syu --noconfirm --needed archiso
