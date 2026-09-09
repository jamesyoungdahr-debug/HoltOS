# HoltOS Session Handoff — updated 2026-09-09

What shipped, what broke, what got fixed, and what's still open — for
whoever picks this branch up next. **This handoff is going to a
different model (Gemma) taking over the work**, so treat nothing here as
already-shared context — the ground rules below are things the prior
session learned the hard way and are worth following rather than
rediscovering.

Commit: `234412f` on `master`. Test VM: `homelab-os-test` (Hyper-V).
ISO: `holtos-0.0.1-alpha-x86_64.iso`.

## Ground rules for whoever/whatever picks this up

- **Never guess at a root cause — verify it.** Every bug below got found
  by pulling real diagnostic output (`coredumpctl`, `journalctl`,
  `git ls-remote` against the actual repo, a live VM's own log files) and
  reasoning from that, after earlier blind guesses in this same project
  turned out wrong more than once. Read `BUILD.md` before touching the
  build pipeline and `README.md` before touching install/boot behavior —
  both explain *why* things are built the way they are, not just what to
  run.
- **Only build/push when explicitly told to.** Standing rule from the
  human running this project — don't rebuild the ISO or push commits on
  your own initiative mid-task.
- **Test in the VM, not by inspection alone.** `homelab-os-test`
  (Hyper-V) is the existing test VM — a fresh install (Erase Disk) is
  required to pick up any partition/bootloader change; an in-place boot
  of an already-installed disk won't. See `BUILD.md` for how the ISO
  itself gets built before it can be tested.
- **This is being handed to a different, more limited local model.** Keep
  changes small and verifiable one at a time rather than large
  speculative batches — easier to confirm each step actually worked
  before building on it.

## At a glance

- **5** real bugs found and fixed last session (4 runtime bugs + 1 build-
  pipeline bug, see below)
- **3×** fresh installs run to confirm the runtime fixes
- **3** runtime items still genuinely unverified, **1** build-pipeline
  item worth a real test run (see "Picking this back up")

## What shipped

**Root filesystem is now Btrfs**, not ext4 — subvolumes `@` `@home`
`@cache` `@log` `@snapshots`, EFI system partition raised from
Calamares' stock 300MiB to **1024MiB** to hold multiple retained kernel
copies. This only takes effect on a fresh install.

**Limine is themed** — HoltOS wallpaper, brand colors, `backdrop`/
`term_palette` — and now writes its config to both the primary
`/EFI/limine/` path and the removable-media `/EFI/BOOT/` fallback
(see Bug 2).

**Boot-environment snapshots** ship out of the box: `holtos-btrfs-snapshot`
takes a read-only snapshot + a matching Limine boot entry before every
`config`/`system` update, 5-snapshot retention, plus a "Create Snapshot
Now" tray entry for on-demand use.

## Bugs found & fixed

### 01 — Updater reports "update available" forever — VERIFIED

**Files:** `holtos-update-apply`, `holtos-update-check`

**Root cause:** `git ls-remote --refs` against an *annotated* tag returns
the tag object's own SHA, not the commit it points to. HoltOS's own
`v0.0.1-alpha` tag is annotated — confirmed live against the real repo.

```
$ git ls-remote --tags https://github.com/jamesyoungdahr-debug/HoltOS.git
5664b1c4...  refs/tags/v0.0.1-alpha
0ba1ac12...  refs/tags/v0.0.1-alpha^{}   # ← the real commit sha
```

**Fix:** Query without `--refs`, prefer the peeled `^{}` line. Falls back
cleanly to lightweight tags, which have no peeled line at all.

### 02 — Limine refuses to boot: `[config file not found]` — VERIFIED

**Files:** `homelab-limine-install.sh`, `holtos-btrfs-snapshot`

**Root cause:** Limine checks the directory of the EFI binary it was
*actually* loaded from, first. `limine.conf` only ever lived next to the
primary `/EFI/limine/BOOTX64.EFI` copy — never next to the
`/EFI/BOOT/BOOTX64.EFI` fallback, which is the entire reason that
fallback copy exists.

```
Limine 12.8.0 (x86_64, UEFI)
[config file not found]
```

Reproduced by forcing the VM's boot device straight to the disk, which
resolves through the generic fallback path instead of the NVRAM entry.

**Fix:** Write the identical config to both `/EFI/limine/limine.conf` and
`/EFI/BOOT/limine.conf`; the snapshot regen logic keeps both copies in
sync on every run.

### 03 — Real account has no working `sudo` — VERIFIED

**Files:** `homelab-cleanup-live.sh`

**Root cause:** Cleanup correctly deletes the live medium's passwordless
wheel-sudo rule (leaving it in place would hand the real account
unrestricted no-password root) — but never replaced it with anything.
Account was correctly in `wheel`; no sudoers rule for that group existed
at all.

```
[holtos@holtos-virtualmachine ~]$ sudo whoami
holtos is not in the sudoers file. This incident will be reported.

# pkexec still worked — separate, polkit-based mechanism, unaffected:
[holtos@holtos-virtualmachine ~]$ pkexec whoami
root
```

**Fix:** `/etc/sudoers.d/10-wheel`, `%wheel ALL=(ALL:ALL) ALL`, mode
`0440` — sudo silently refuses a looser-permissioned file.

### 04 — Tray icon segfaults, every single launch — VERIFIED

**Files:** `holtos-tray`

**Root cause:** `QSystemTrayIcon.isSystemTrayAvailable()` was called
before `QApplication(sys.argv)` existed — touching QtWidgets before
platform integration is initialized is a classic segfault, confirmed via
`coredumpctl`.

```
$ coredumpctl info
Signal: 11 (SEGV)  si_code: SEGV_MAPERR
Stack trace of thread 4500:
#0 _ZN15QSystemTrayIcon21isSystemTrayAvailableEv (libQt6Widgets.so.6)
```

**Fix:** Construct `QApplication` first, then check tray availability.
Also added `qt6-wayland` to `packages.x86_64` — independently correct
for native Wayland platform integration, though it wasn't the segfault's
actual cause on its own.

### 05 — Pacman keyring never initialized on install — VERIFIED

**Files:** `homelab-cleanup-live.sh`

**Root cause:** The live medium's own `/etc/pacman.d/gnupg` state doesn't
survive an unpackfs copy into something the installed target can use
directly — silent until the first real package operation, which is
exactly what the updater's `system` item runs.

```
$ sudo pacman -S qt6-wayland
warning: Public keyring not found; have you run 'pacman-key --init'?
error: failed to commit transaction (could not find or read file)
```

**Fix:** `pacman-key --init && pacman-key --populate archlinux`, once, on
the real target during cleanup.

### 06 — Build pipeline unreproducible on any machine but this one — FIXED, NOT YET RE-VERIFIED

**Files:** `build.sh`, `build-aur-packages.sh`, `containers/*.Containerfile`
(new), `build-local-repo.sh` (new), `BUILD.md` (new)

**Root cause:** Two of the three container images the build needs
(`archiso-image`, plus a since-removed `calamares-installed`) were only
ever built by hand on this machine — `podman commit`, never a
`Containerfile` — so there was no way to reproduce them anywhere else.
`build.sh` also hardcoded the WSL-side mount path with the Windows
username `Liam` baked in (`/mnt/c/Users/Liam/...`), which silently points
at nothing on any other username or clone location. And nothing anywhere
called `repo-add`, so `local-repo/` was never actually a valid pacman
repo by itself — it happened to work here only because a real repo
database was left over from however it was first set up.

**Fix:** Reconstructed both images as real `containers/*.Containerfile`s
(folding the redundant `calamares-installed` image away — `calamares`
now builds through the same AUR-build script as the other four
packages), added the missing `repo-add` step to
`build-aur-packages.sh`, and made both `build.sh` and the new
`build-local-repo.sh` derive the WSL path from the actual checkout
location instead of a hardcoded one. Full pipeline documented in
`BUILD.md`.

**Not yet verified:** this was fixed by inspecting the existing working
images and reconstructing what must have produced them — logically
sound, but nobody has actually run `build-local-repo.sh` +
`build.sh` from a totally clean state (no pre-existing `local-repo/`,
no pre-existing container images) to confirm the reconstruction is
complete. This is the single highest-value thing to verify next if the
build is still failing on the machine it's being handed off to.

## Still open

- **Build pipeline reconstruction (bug 06), never run from a clean
  state.** See above — this blocks everything else if it doesn't
  actually work, so verify it first.
- **Limine wallpaper/theme, visual confirmation.** The config keys are
  written and Limine boots correctly, but nobody has actually watched the
  branded boot menu render — every round this session got sidetracked
  chasing a bug before reaching that screen.
- **Full snapshot lifecycle.** Create → Limine entry appears → boot into
  it → retention evicts the oldest — logic reviewed carefully, awk
  block-replacement hand-traced, but never run start to finish on real
  hardware or VM.
- **Stale NVRAM boot entries** accumulated on `homelab-os-test` across
  repeated reinstalls (10+ `File` boot entries) — a real install only
  ever runs `efibootmgr --create` once per disk wipe, so this is a
  test-VM artifact, not a code fix, but worth a clean VM at some point.

## Picking this back up

Roughly in priority order — each step assumes the one before it actually
worked, so confirm before moving on rather than batching them:

1. **Verify the build pipeline actually works from clean.** Delete (or
   rename aside) `local-repo/` and the `archiso-image`/`aur-builder`
   podman images if they already exist locally, then follow `BUILD.md`
   exactly: `./build-local-repo.sh` then `./build.sh`. If it fails, the
   error will point at which reconstructed piece (a `Containerfile`, the
   `repo-add` step, the path derivation) is still wrong — fix that one
   piece and rerun, don't restart the whole reconstruction from scratch.
2. **Watch the Limine menu render, start to finish.** Fresh install
   (Erase Disk, in the `homelab-os-test` VM), and this time actually sit
   through the boot menu before logging in — the one visual check every
   round so far skipped.
3. **Trigger a snapshot and boot into it.** From the tray: *Create
   Snapshot Now*, then confirm the Limine menu grows a matching entry
   and it actually boots. Verify with `btrfs subvolume list /`.
4. **Run six update cycles to test retention.** Confirm the oldest
   snapshot — subvolume, ESP kernel copy, and Limine entry — is evicted
   cleanly on the sixth.
5. **Give the test VM a clean disk.** Clears the accumulated NVRAM
   boot-entry cruft so future fallback-path tests aren't racing against
   stale entries again.

## Where things live

| | Path |
|---|---|
| **start here** | `BUILD.md` — full build pipeline, read before touching `build.sh` |
| **start here** | `README.md` — architecture, install flow, repo layout |
| new | `archiso/airootfs/etc/calamares/modules/partition.conf` |
| new | `archiso/airootfs/etc/calamares/modules/mount.conf` |
| new | `archiso/airootfs/usr/local/bin/holtos-btrfs-snapshot` |
| new | `archiso/airootfs/usr/local/bin/holtos-snapshot-now` |
| new | `containers/archiso-image.Containerfile` |
| new | `containers/aur-builder.Containerfile` |
| new | `build-local-repo.sh` |
| fix | `archiso/airootfs/usr/local/bin/homelab-limine-install.sh` |
| fix | `archiso/airootfs/usr/local/bin/homelab-cleanup-live.sh` |
| fix | `archiso/airootfs/usr/local/bin/holtos-update-apply` |
| fix | `archiso/airootfs/usr/local/bin/holtos-update-check` |
| fix | `archiso/airootfs/usr/local/bin/holtos-tray` |
| fix | `build.sh` (WSL path derivation) |
| fix | `build-aur-packages.sh` (added calamares + repo-add) |
| log | `BRANDING-STATUS.md`, `CHANGELOG.md` |

---
Full styled version (may be stale after this update — this file is the
source of truth going forward): https://claude.ai/code/artifact/224f740f-629d-43fc-a927-c155a6ce1c4c
