# HoltOS neon rebrand: plan and status

Branch `neon-rebrand`. Everything here ships together in the next major
release (Liam, 2026-09-14). Paused on 2026-09-14; this file records the plan,
what is done and what is left.

## Decisions (Liam)

- **Look:** five-colour neon palette (purple acts, teal healthy, electric blue
  informs, magenta glows, lime sparks; amber still means "needs you").
- **Logo:** otter concept C (ComfyUI seed 4202), app icon 001, symbolic 001.
  Full-body login otter: v2 seed 7301 #2.
- **Design comes only from ComfyUI renders.** Nothing is hand-drawn in SVG or
  CSS; small and one-colour versions are derived from the renders by scripts.
- **Desktop:** a glass menu bar on top and a floating dock with a neon rim
  (dock mockup #2). It is the default for everyone, existing accounts
  included, with their old panels backed up. **HoltOS Classic** keeps the old
  single bottom panel for anyone who prefers it.
- **Only HoltOS themes ship.** Stock Breeze, Klassy and Kvantum themes are
  removed; a few fallbacks stay.
- **Smaller** title bar buttons and dock icons.
- **Drivers:** the installer checks the install target's hardware and
  installs working drivers for it, not just NVIDIA; every update does the
  same and keeps them updated.
- **"homelab" becomes HoltOS everywhere.**
- **Dual boot:** HoltOS can install alongside an existing OS. On a small
  Windows EFI partition, keep fewer snapshot kernels (option a).
- **UI issues found in the VM are parked** and tested on bare metal once the
  rebrand is done.
- **Game Mode bug fixes** ship as their own bug-fix releases from master
  (0.0.7b, c, d) and are merged into this branch.

## Milestones

| # | Milestone | Status |
|---|---|---|
| 1 | Palette and colour scheme (HoltOS.colors hover tone) | Done |
| 2 | Logo and icons derived from the ComfyUI renders (`tools/brand/derive_logo.py`) | Done |
| 3 | Menu bar and dock layout, HoltOS Glass Plasma style (`tools/glass/plasma_theme.py`), HoltOS Classic, stock themes removed, account migration | Done, VM-tested |
| 4 | Boot splash, login, Plasma splash and installer art (`tools/brand/derive_splash_art.py`) | Done |
| 5 | Brand guide (`docs/holtos-brand.md`), new logo in every HoltOS tool, old logos removed on update | Done |
| 6 | Glass installer | **Parked:** under `pkexec` the QML top bar draws blank (see LIVETEST.md) |
| 7 | Hardware drivers for installer and updates (`usr/share/holtos/hardware-drivers.conf`, `holtos-hardware`, staged `holtos-drivers` repo on the ISO, `holtos-system-extras`), Hardware tab in HoltOS Updates | Done, tested with fake hardware in the VM |
| 8 | Rename "homelab" to HoltOS: scripts, hook, installer shortcut, wording, `[holtos]` package repo with a migration | Done, migration VM-tested |
| 9 | Install alongside Windows: 64 MiB EFI minimum, "Notes" installer step, snapshot kernels and kernel updates that fit a small ESP | Done, small-ESP logic VM-tested |
| 10 | Rebuild the ISO and test it in a VM | ISO built 2026-09-14 21:11 and boots: installer pages (Welcome, Notes, Partitions) checked. The install itself needs a user account, which Claude may not create, so it moves to bare metal. Tested instead through the upgrade path on `holtos-test` (see below) |
| 11 | Bare-metal tests (LIVETEST.md "Neon rebrand" section) | Open |
| 12 | Release: version number, merge to master, publish packages, tag | Open |
| 13 | Backlog run (2026-09-15, Liam: everything that is not Game Mode and does not need him): support bundle, snapshot retention setting, automatic rollback after two failed boots (`holtos-boot-guard`), Network Shares LAN browsing and "Share from this computer" (`holtos-samba`), glass popups and tooltips, stacked and light lockups | Done, VM-tested (commits 879b5f0, fc57103, 6e277ff, b7f0126, 2856ed4) |

Deliberately not done in the backlog run (need Liam): darker list views
(would undo the 0.0.7a clearer-glass decision), GTK rgba glass (GTK cannot
ask KWin for blur, so text would sit on the bare wallpaper), title bar
button colours, media player and storage decisions, first-run wizard
choices, otter expression renders, icons and cursor, adaptive contrast, The
Den client, the HoltOS Apps name, the Xbox wireless dongle, the version
number and publishing packages.

## Left to do

1. **Install from the ISO on bare metal:** the installer run itself, first boot
   (boot splash, login), and `/var/lib/holtos/hardware.log` from the
   installer's driver step. Already tested through the upgrade path on
   `holtos-test`: the account migration to the menu bar and dock, HoltOS
   Classic and back, the login theme, the Hardware tab, old files removed.
   The login screen shows no otter overlay on purpose: `theme.conf` leaves
   `otter=` empty because the Otter Night wallpaper has its own otter.
2. **Bare metal (Z13, 4090):**
   - dual boot next to Windows;
   - the installer's NVIDIA driver path on the 4090;
   - faint seams at the dock's rounded ends (seen only in the VM; the
     centre-tile fix of 2026-09-15 may have removed them);
   - Network Shares: set a network password, share a folder and open it
     from Windows (it should also appear in Windows' Network view through
     wsdd) and from another Linux or Mac machine; browse a real NAS;
   - glass popups and tooltips over bright wallpaper: readable?
   - automatic rollback: only if an update ever breaks the desktop (it was
     forced in the VM);
   - the parked glass installer (try the root installer on Wayland, or a
     non-QML top bar).
3. **Package repository:** publish packages with `tools/publish-packages.sh`
   (uploads `holtos.db` and `homelab.db`), then check that an updated install
   runs `pacman -Sy` against `[holtos]`. Drop the `homelab.db` copies a few
   releases later.
4. **Release:** Liam picks the major version number; bump `os-release`,
   `branding.desc` and `profiledef.sh`; merge `neon-rebrand` into master;
   publish packages; tag.

## Notes for whoever resumes

- A Hyper-V VM holding an ISO locks the file: turn the VM off before
  `build.sh`.
- Build the ISO from Git Bash: `./build.sh` in `C:\projects\holtos-neon-rebrand`.
- The VM cannot run gamescope (no Vulkan GPU), so Game Mode changes need real
  hardware.
- Details and history: `CONTEXT.txt`, `HANDOFF.md`, `CHANGELOG.md` `[Unreleased]`,
  `LIVETEST.md`.
