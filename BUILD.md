# Building the HoltOS ISO

This is the real, complete build pipeline — written after finding that
the previous version of this document (a few lines in `README.md`)
assumed two container images that already existed on one specific
machine, built by hand, never captured anywhere reproducible. If a build
is failing on a machine that isn't the one this was first developed on,
that's very likely why. Everything below has been reconstructed from what
those images actually contained and turned into real, checked-in
`Containerfile`s and scripts, so the whole pipeline now runs the same way
on any machine that meets the prerequisites.

## What you need

- **A Linux environment with `podman`** (or Docker, with `podman` swapped
  for `docker` in the commands below). The scripts here assume **WSL2
  Ubuntu on Windows**, since that's how this project is actually
  developed — see [Running on Linux directly](#running-on-linux-directly)
  if you're not on Windows.
- **`git`**, to fetch the AUR PKGBUILDs.
- Enough disk space for the containers plus the built ISO — budget
  **~15GB** free (container images, `mkarchiso`'s working directory, the
  final ~2.2GB ISO).
- No Arch Linux host needed anywhere — `mkarchiso` only needs to run
  *inside* a container built from an Arch base image, which works from
  any host OS podman/Docker can run on.

Nothing here needs network access to anything but `pacman`'s mirrors and
the AUR — no accounts, no API keys.

## The three things that have to happen, in order

(Plus a fourth `build.sh` does for you every run: `build-vendor-apps.sh`
fetches the latest tagged release of The Den and The Den Client into
`archiso/airootfs/opt/holtos-vendor/`, and `customize_airootfs.sh` installs
them inside the mkarchiso chroot — so a build needs network access to
GitHub and PyPI as well as the pacman mirrors.)

1. **Build `local-repo/`** — five AUR packages this profile needs that
   aren't in the official Arch repos, plus HoltOS' own two packages
   (`packaging/*`, built from the forks in `forks/`), built once (and
   rebuilt only when you want to update them).
2. **Build the `archiso-image` container** — the environment `mkarchiso`
   actually runs inside.
3. **Run `build.sh`** — mounts the profile, `local-repo/`, and an output
   directory into a container from that image and runs `mkarchiso`.

### 1. Build the AUR packages

```bash
./build-local-repo.sh
```

This builds a small `aur-builder` container (see
`containers/aur-builder.Containerfile`) and runs
`build-aur-packages.sh` inside it, which:

- clones and `makepkg -s`'s **calamares**, **zfs-dkms**, **zfs-utils**,
  **limine-mkinitcpio-hook**, and **limine-entry-tool** straight from the
  AUR,
- imports the OpenZFS release GPG key first (zfs-dkms's source tarball is
  signed with it, and it isn't in the default keyring),
- builds HoltOS' own packages from `packaging/*/PKGBUILD`:
  **holtos-glass-effect** (the KWin blur fork) and
  **holtos-window-decoration** (the Klassy fork, which replaces the AUR
  `klassy` package this used to build), each from a tarball of the
  matching `forks/<name>` tree, versioned by the HoltOS commit count.
  Subset rebuilds: `AUR_PKGS=none HOLTOS_PKGS=holtos-glass-effect
  ./build-local-repo.sh`,
- runs `repo-add` over the results to produce `local-repo/holtos.db*`
  and `holtos.files*` — **this step existed nowhere before**; without a
  real repo database, `archiso/pacman.conf`'s `[holtos]` repo is just a
  directory of files pacman won't recognize as a repo at all.

Expect this to take a while — calamares alone pulls in a real Qt6/KF6
build. `local-repo/` is gitignored; you only need to rerun this when you
want newer versions of these packages (or changed the forks), not on
every ISO build.

### 2. Build the `archiso-image` container

```bash
MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- sudo podman build -t archiso-image \
  -f "/mnt$(pwd)/containers/archiso-image.Containerfile" "/mnt$(pwd)"
```

(Run from Git Bash at the repo root, same path-derivation trick
`build.sh` uses — see that script's own comment for why it's derived
rather than hardcoded. The `MSYS_NO_PATHCONV=1` prefix is not optional:
Git Bash otherwise rewrites the `/mnt/c/...` arguments into Windows
paths before `wsl.exe` ever sees them, and `podman build` inside WSL
then can't find the Containerfile or the build context.) This is just Arch's own base image plus the
`archiso` package — nothing else. Only needs rebuilding if you want to
pick up newer Arch/archiso releases.

### 3. Build the ISO

```bash
./build.sh
```

Backs up any ISO already in `out/`, seeds the updater's own
`deployed-commit` state file from the current git commit, then runs
`mkarchiso -v -w /tmp/work -o /tmp/out archiso/` inside a privileged
container from `archiso-image`, with `archiso/` (the profile),
`local-repo/` (from step 1), and `out/` bind-mounted in. Finishes by
fixing the built ISO's Windows ACLs so Hyper-V can actually attach it as
a virtual DVD without an "Access is denied" error.

The finished ISO lands in `out/holtos-<version>-x86_64.iso`.

## Why three separate container images used to exist (and now don't)

The pipeline used to depend on two more images —
`calamares-build-base` and `calamares-installed` — that were built once,
by hand, and never turned into a `Containerfile`. `calamares-installed`
existed only so `calamares` itself (an AUR package like the other four)
could be built and pre-installed into an image *before*
`build-aur-packages.sh`'s own comment called it out as building "the
**remaining** AUR packages" — implying calamares was already handled by
something else, with no record of what.

`archiso/pacman.conf`'s own comment already described `[holtos]` as
carrying calamares alongside the other four — the uniform, one-script,
one-image treatment below is what that comment always implied; the extra
images were never actually necessary, just how it happened to get built
the first time. `build-aur-packages.sh` now builds all the AUR packages
(and the HoltOS ones) the same way, in the one `aur-builder` container.

## Common failure: "it built something, but the ISO won't boot / won't install"

- **`local-repo/holtos.db` missing or stale.** If you copied
  `.pkg.tar.zst` files into `local-repo/` some other way (or ran an older
  version of `build-aur-packages.sh` from before `repo-add` was added),
  pacman won't see them as a repo at all — `mkarchiso` will just silently
  not install `calamares`/`zfs-dkms`/etc., and the profile's `packages.x86_64`
  entries for them will fail to resolve. Rerun `./build-local-repo.sh`.
- **Wrong WSL path.** If `build.sh` or `build-local-repo.sh` were edited
  to hardcode a path again (or copied from an older version that still
  does), the container mounts point at nothing or the wrong directory,
  and `mkarchiso` either fails immediately or silently builds from stale
  files. Both scripts now derive the WSL-side path from `pwd` — don't
  hardcode it back.
- **ISO built, but Hyper-V won't attach it.** That's the ACL issue
  `build.sh`'s last step already handles automatically
  (`icacls ... //grant "Authenticated Users:(R)"` — the doubled slash is
  required from Git Bash, which otherwise rewrites `/grant` into a path)
  — if you're inspecting a `.iso` that `build.sh` didn't finish writing (e.g. the process was
  killed mid-build), that step never ran; re-run the build rather than
  trying to fix permissions on a partial file.
- **`podman build`/`podman run` needs `sudo` inside WSL2** in every
  command above — that matches how `build.sh` already invokes it; if a
  step is failing with a permissions error rather than a build error,
  confirm the WSL2 user actually has passwordless (or interactive) sudo.

## Running on Linux directly

Everything above is really just "run these commands inside `podman`" —
the WSL2 wrapping (`wsl -d Ubuntu -- sudo podman ...` and the
`/mnt$(pwd)` path derivation) exists only because this is developed on
Windows. On a real Linux host, drop the `wsl -d Ubuntu --` prefix and
mount the repo's actual absolute path directly instead of `/mnt$(pwd)` —
the `podman build`/`podman run` commands themselves, and every
`Containerfile`, are unchanged.
