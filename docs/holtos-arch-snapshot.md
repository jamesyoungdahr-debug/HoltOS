# Arch packages from a tested snapshot date

Liam, 2026-09-15: "can we change -Syu so it only pulls HoltOS". A plain
system update used to install whatever Arch's live mirrors had that morning;
kernel 7.2.6 reached the ROG Flow Z13 that way untested, and together with the
Limine sync hook bug (fixed in 0.0.7h-alpha) it stopped the machine booting.

## How it works

- Arch's `core`, `extra` and `multilib` repositories read
  `/etc/pacman.d/holtos-mirrorlist` instead of `/etc/pacman.d/mirrorlist`.
  That file has a single server: one day of the Arch Linux Archive,
  `https://archive.archlinux.org/repos/YYYY/MM/DD/$repo/os/$arch`.
- HoltOS's own packages still come from the `[holtos]` repository
  (`packages` for stable, `packages-dev` for the dev channel).
- Each branch carries its own date in
  `archiso/airootfs/etc/pacman.d/holtos-mirrorlist`: `neon-rebrand` (dev)
  moves first, `master` (stable) follows once the date has been tested.
- The config update copies the file to installed systems and switches the
  three `Include` lines in `/etc/pacman.conf` (only inside `[core]`,
  `[extra]` and `[multilib]`; other sections and commented testing repos are
  left alone). New installs get the same change at image build
  (customize_airootfs.sh).
- The system update step runs `pacman -Suu`, so a package installed from a
  live mirror before the pin, newer than the snapshot, goes back to the tested
  version.
- Live mirrors are never mixed with the snapshot: the Arch Wiki warns that a
  download failure would otherwise fall back to an up-to-date mirror and mix
  package sets from different days.

## Moving the date

1. `tools/set-arch-snapshot.sh YYYY/MM/DD` on `neon-rebrand` (it refuses a
   date the Archive does not have for all three repositories; a day usually
   appears the next day). `tools/set-arch-snapshot.sh` alone prints the
   current date.
2. Commit and push; the dev channel (the Z13) takes it with its next HoltOS
   update, then the system update.
3. Check the machine boots and the desktop, Game Mode and sound work.
4. Set the same date on `master` and tag a stable release.

Kernel jumps need extra care: DKMS packages built only for one kernel series
(holtos-acp-mic-dkms is 7.2-only) must be updated before a date with a new
series is released.

## Limits

- The Archive is a single server, not a mirror network: downloads can be
  slower than a nearby mirror.
- Security fixes from Arch reach HoltOS only when the date moves.
- `checkupdates` (the update check) does not list downgrades, so a machine
  that is only ahead of the snapshot is not offered a system update until
  something in the snapshot is newer than what it has.

Source: https://wiki.archlinux.org/title/Arch_Linux_Archive
