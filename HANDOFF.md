# HoltOS Session Handoff — 2026-09-09

What shipped, what broke, what got fixed, and what's still open — for
whoever picks this branch up next (including future you).

Commit: `d8b20b1` on `master`. Test VM: `homelab-os-test` (Hyper-V).
ISO: `holtos-0.0.1-alpha-x86_64.iso`.

## At a glance

- **4** real bugs found and fixed this session
- **3×** fresh installs run to confirm each fix
- **3** items still genuinely unverified

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

## Still open

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

1. **Watch the Limine menu render, start to finish.** Fresh install, and
   this time actually sit through the boot menu before logging in — the
   one visual check every round so far skipped.
2. **Trigger a snapshot and boot into it.** From the tray: *Create
   Snapshot Now*, then confirm the Limine menu grows a matching entry
   and it actually boots. Verify with `btrfs subvolume list /`.
3. **Run six update cycles to test retention.** Confirm the oldest
   snapshot — subvolume, ESP kernel copy, and Limine entry — is evicted
   cleanly on the sixth.
4. **Give the test VM a clean disk.** Clears the accumulated NVRAM
   boot-entry cruft so future fallback-path tests aren't racing against
   stale entries again.

## Where things live

| | Path |
|---|---|
| new | `archiso/airootfs/etc/calamares/modules/partition.conf` |
| new | `archiso/airootfs/etc/calamares/modules/mount.conf` |
| new | `archiso/airootfs/usr/local/bin/holtos-btrfs-snapshot` |
| new | `archiso/airootfs/usr/local/bin/holtos-snapshot-now` |
| fix | `archiso/airootfs/usr/local/bin/homelab-limine-install.sh` |
| fix | `archiso/airootfs/usr/local/bin/homelab-cleanup-live.sh` |
| fix | `archiso/airootfs/usr/local/bin/holtos-update-apply` |
| fix | `archiso/airootfs/usr/local/bin/holtos-update-check` |
| fix | `archiso/airootfs/usr/local/bin/holtos-tray` |
| log | `BRANDING-STATUS.md`, `CHANGELOG.md` |

---
Full styled version: https://claude.ai/code/artifact/224f740f-629d-43fc-a927-c155a6ce1c4c
