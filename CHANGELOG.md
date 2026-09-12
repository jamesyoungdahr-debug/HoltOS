# Changelog

All notable changes to HoltOS are logged here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

- **HoltOS Glass is now HoltOS-owned code, built by our pipeline.** Two
  forks live in this repo under `forks/` and are packaged by
  `packaging/*/PKGBUILD` into the `[homelab]` local repo alongside the
  AUR packages: `holtos-glass-effect` (KWin effect `holtosglass`, forked
  from KWin 6.7's blur: blurs behind every window including decorations
  and menus, tints the blur towards the ink colour so text stays
  readable on any wallpaper, adjustable contrast/brightness/saturation,
  rounded corners for undecorated windows) and `holtos-window-decoration`
  (plugin `org.holtos.glass`, forked from Klassy 6.7.2 with the glass
  title-bar opacity and 10 px corners compiled in as defaults; replaces
  the AUR `klassy` package). `/etc/xdg/kwinrc` enables the effect and
  decoration system-wide and disables stock blur. Verified in the build 9
  live session (2026-09-12): `holtosglass` is the only blur effect
  loaded, the decoration library is `org.holtos.glass`, Konsole and
  Dolphin render translucent with blurred content behind them.
- **System Settings > About this System and power profiles**:
  `kinfocenter` with `kcm-about-distrorc` pointing at the HoltOS logo and
  repo, `power-profiles-daemon` enabled, `plasma-systemmonitor` added.
  `python-gobject` added too: `powerprofilesctl` is a Python script that
  tracebacked without it (seen in the build 9 live session).
- **Image needs `qt6-declarative` for The Den Client >= v0.4.3**: its
  PKGBUILD lists it, and `build-vendor-apps.sh` correctly refused to build
  the image until `packages.x86_64` carried it.
- **Installer partition legend readable.** Calamares paints the
  "Current:"/"After:" legend with hardcoded `Qt::black`/`Qt::gray` pens
  (`PartitionLabelsView::drawLabel`), so the colour rule added on
  2026-09-11 could never work — it was still dark-on-dark in build 9. The
  legend now sits on a light chip via the one property a stylesheet can
  set on that view, its background.
- **Live-ISO guards verified** (PLAN.md step 3, build 9): no
  `holtos-tray` process and no first-boot unit in the live session.
- **Dev machine rebuilt from nothing (2026-09-12)**: Git, GitHub CLI,
  WSL2 Ubuntu 26.04 + podman 5.7, Hyper-V and a new `holtos-test` VM; the
  whole pipeline (AUR + HoltOS packages, `archiso-image`, `build.sh`) ran
  clean on it — build 9.
- **Installer works from a USB stick on machines with enough RAM.** The
  first real-hardware install (2026-09-11, Ventoy stick, then GRUB2
  mode — both the same) failed in unpackfs with "airootfs.sfs missing".
  Root cause is not Ventoy: current mkinitcpio-archiso defaults to
  `copytoram=auto`, which on a non-optical medium with MemAvailable >
  image + 2 GiB copies the squashfs into RAM and then unmounts *and
  removes* `/run/archiso/bootmnt` — the fixed path `unpackfs.conf`
  reads from. The Hyper-V VM never hit it because it boots from a
  virtual DVD, which auto excludes. New `shellprocess@locate-airootfs`
  (`homelab-locate-airootfs.sh`, live session, right before unpackfs)
  links the RAM copy plus the kernel from `/usr/lib/modules/` (mkarchiso
  empties the airootfs' `/boot`), or else mounts `/dev/mapper/ventoy`,
  loop devices, a `HOLTOS_*` labelled medium, or bind-mounts an
  already-mounted copy; if nothing is found it fails with `lsblk` output
  and a hint. The automatic RAM check is kept: it is exactly the "load
  into RAM when there is enough memory, else run from the stick"
  behaviour wanted. Verified on real hardware: pending.
- **Live medium compressed with zstd instead of xz** (squashfs level 19,
  initramfs too): the live session decompresses every file it reads, and
  zstd decompresses several times faster than xz, so the live desktop
  and the installer are noticeably snappier from USB; the image grows
  by roughly 10-15 %.
- **Build fix: NVIDIA staging no longer kills the image build.** Inside
  the mkarchiso chroot pacman cannot map the staging cache dir to a
  mount point, so `CheckSpace` aborted the download with a bogus "not
  enough free disk space" and the whole build failed. The temporary
  staging `pacman.conf` now drops `CheckSpace` and `DownloadUser`.
- **Hardware detection at install** (PLAN.md step 7): a new Calamares
  `detect-hardware` step (`homelab-detect-hardware.sh`, after
  cleanup-live) logs CPU/PCI to `/var/lib/holtos/hardware.log`; if an
  NVIDIA GPU is present it installs `nvidia-open-dkms` + `nvidia-utils`
  from packages staged on the ISO at build time
  (`/usr/share/holtos/drivers/nvidia/`, no network needed) and appends
  `nvidia_drm.modeset=1` to the Limine command line (main entry and
  snapshot entries). Vulkan (AMD/Intel) and VA-API drivers are always in
  the image. Only the "no NVIDIA" path is verifiable in the Hyper-V VM.
- **Updater: The Den is restarted and health-checked after every
  update.** `install_the_den` now waits up to 30 s for the service to be
  active and answering on port 8686; if it does not come back the update
  is logged as failed and the last journal lines are shown, instead of
  silently reporting success.
- **HoltOS Glass, all the way down.** Desktop: Kvantum widget style with
  a `HoltOSGlass` theme (70% window / 84% dialog opacity over the ink
  base), Klassy window decorations with 70%/60% translucent, blurred
  title bars, KWin blur strength 11 + background contrast, Nunito UI
  font and JetBrains Mono for mono. Greeter: self-contained SDDM theme
  with a blurred glass card over the pool-rings ground (opaque twin when
  the renderer is software). Installer: Glass stylesheet, sidebar,
  navigation and slideshow. Plymouth: drawn ring + lockup. Confirmed on
  screen in the VM; real-GPU blur quality still to be seen.
- **Updater: apps' OS dependencies are installed with the update.**
  Real outage 2026-09-11: the tray moved a v0.1.0 install of The Den to
  v0.2.0, whose built-in torrent client needs `libtorrent-rasterbar`'s
  Python bindings, and the service died with "No module named
  libtorrent". `holtos-update-apply` now reads `depends=(...)` from the
  release's own PKGBUILD and `pacman -S --needed`s what's missing before
  touching any files (a failed install aborts the update); the venv is
  created with `--system-site-packages` (older venvs are opened in
  place); deploy files (unit, sysusers, tmpfiles) are re-installed on
  every update; settings a new release introduces are appended to
  `/etc/the-den/the-den.env` with the release defaults (v0.2.0's
  `STATE_DIR` — without it the app fell back to a relative path and hit
  PermissionError). `build-vendor-apps.sh` fails the build if a vendored
  app's depends aren't in `packages.x86_64`; `libtorrent-rasterbar` added.
  Still broken upstream: The Den v0.2.0 reads `libtorrent.version`, which
  Arch's 2.1 bindings don't have — fixed in the-den's repo, needs a tag.
- **The container stack is gone** (PLAN.md step 1): the twelve Podman
  Quadlets, their launchers/icons, the Authentik blueprints, the
  `/var/mnt/tank` tmpfiles tree, secrets generation + the Calamares
  credential capture, the arr-keys sync, `podman` on the installed
  system, and the per-service/Authentik updater items. HoltOS is now the
  base OS plus The Den.
- **The Den and The Den Client ship inside the image** (PLAN.md step 2):
  `build-vendor-apps.sh` (run by `build.sh`) fetches their latest tagged
  release; `customize_airootfs.sh` installs both in the build chroot via
  `holtos-update-apply vendor`, the same code the tray updater uses (now
  split into `install_the_den`/`install_the_den_client` taking a local
  tree, with `systemctl --now`/`daemon-reload` skipped when not booted).
  `the-den.service` gets a `!/run/archiso` drop-in so it stays off the
  live medium. `holtos-first-boot-apps` is retired.
- Keyring backstop now gates on "no master secret key" via an
  `ExecCondition` instead of the pubring file (which `pacman-key --init`
  writes before generating the key).
- **Second fresh install from a rebuilt ISO confirmed every fix from the
  first VM run**: pacman keyring present and `pacman -S` works (backstop
  unit's condition unmet — the chroot init succeeded once the tmpfs unit
  was gone); `holtos-first-boot-apps` and `homelab-sync-arr-keys` ran on
  first boot, and first-boot-apps installed The Den v0.1.0-alpha (sysusers,
  venv, pip, alembic, service active) and The Den Client end to end;
  Finished page's "Restart now" visible, ticked, and Done rebooted the
  machine; Limine entry and EFI label read `HoltOS`.
- Limine boot entry and `efibootmgr` label renamed from the pre-rename
  `homelab-os` to `HoltOS`.
- The updater tray, `holtos-first-boot-apps`, and `homelab-sync-arr-keys`
  are now gated on `/run/archiso` not existing, so none of them start on
  the live ISO (the tray was appearing in the live session). Committed
  after the last ISO build — not yet verified in a built image.
- Direction change: the container stack is being removed and The Den
  vendored into the image at build time — see `PLAN.md`.
- **First full VM test of the clean-machine build (2026-09-11)** — the
  handoff's steps 1-4 all done for real: pipeline from clean, fresh
  Erase-Disk install, Limine menu watched rendering (wallpaper, palette,
  snapshot entries), a snapshot created from the tray script, booted into
  it (read-only root, SDDM comes up, container stack correctly can't
  start — a rescue environment, not a rollback), and six snapshot cycles
  confirming 5-snapshot retention evicts subvolume + ESP copy + Limine
  entry together. Confirmed working: tray icon (Wayland/PySide6), sudo,
  Btrfs `@` root with zstd, both limine.conf copies, all 13 stack
  services, generated secrets, installer content-area stylesheet.
  **Four real bugs found**, three fixed here:
  - Installed system had **no usable pacman keyring** ("keyring is not
    writable") despite the earlier `pacman-key --init` fix. archiso's
    `etc-pacman.d-gnupg.mount` (tmpfs for the live medium) rides into the
    install, and gnupg's socket units pull it in by name on every boot,
    hiding the on-disk keyring — which was itself incomplete because the
    chroot-time init failed silently. `homelab-cleanup-live.sh` now removes
    both archiso units from the target and logs init failures; new
    `holtos-pacman-keyring-init.service` re-runs init/populate on first
    boot if no pubring exists.
  - `holtos-first-boot-apps` and `homelab-sync-arr-keys` **never ran**:
    their `*.wants/` entries were plain files (Windows git can't store the
    releng symlinks), which systemd ignores. Same for archiso's
    `choose-mirror`/`livecd-alsa-unmuter`. All four now `systemctl enable`d
    in `customize_airootfs.sh`; the fake wants files are gone.
  - Finished page's Done did not restart: Calamares' stock
    `restartNowMode` is `user-unchecked`, and the dark stylesheet made the
    checkbox invisible. Added `finished.conf` (`user-checked`) and explicit
    `QCheckBox`/`QRadioButton` indicator styling.
  - **Not fixed (needs a decision): the updater cannot reach the HoltOS
    repo** — it is private, so anonymous `git ls-remote`/release-tarball
    download fail (`holtos-update-check` exits 128), exactly the failure
    the-den hit before it was made public.
  - Cosmetic, not fixed: Calamares' partition-bar labels render dark on
    dark (painted via palette, not stylesheet); the slideshow page has a
    white frame around the slide.
- **First genuinely clean-state run of the build pipeline** (fresh Windows
  machine, fresh clone, no pre-existing container images or `local-repo/`)
  found two real bugs, both fixed:
  - Git for Windows defaults `core.autocrlf=true`, so every text file
    checked out with CRLF; `build-aur-packages.sh` died inside the
    container on `set -euo pipefail` (`pipefail: invalid option name`),
    and every script/unit file under `airootfs/` would have shipped
    broken into the ISO the same way. Added `.gitattributes`
    (`* text=auto eol=lf`) so checkouts are LF regardless of local git
    settings.
  - The `archlinux` base image has a populated keyring but no local
    master key, so `archlinux-keyring`'s upgrade hook failed during
    `podman build` ("There is no secret key available to sign with"),
    leaving newer packager keys untrusted. Both Containerfiles now run
    `pacman-key --init && pacman-key --populate archlinux` first.
- Branding audit (every asset referenced by branding.desc, the
  look-and-feel package, SDDM, Plymouth, Konsole, os-release, the
  `.desktop` launchers, the updater scripts, and both boot menus was
  checked to exist and be a valid image/config): one gap found.
  `archiso/syslinux/splash.png` — the BIOS boot menu background — was
  still upstream releng's stock Arch Linux artwork under the HoltOS
  `MENU TITLE`. Replaced with a HoltOS splash built from the desktop
  wallpaper, letterboxed onto the brand background to fit syslinux's
  640x480 frame. The UEFI menu (systemd-boot) is text-only and was
  already branded.
- `build-local-repo.sh` exported `MSYS_NO_PATHCONV=1` only *after* its
  `podman build` call, so Git Bash rewrote the `/mnt/c/...` Containerfile
  and context paths into Windows paths before `wsl.exe` saw them. Moved
  the export ahead of the first `wsl` call; BUILD.md's manual
  `archiso-image` build command gained the same prefix.
- **Two more real bugs found in the same live-testing round**, both
  confirmed and fixed:
  - `holtos-tray` segfaulted every time — on autostart AND on a manual
    foreground run, 100% reproducible. Root-caused via `coredumpctl info`:
    `QSystemTrayIcon.isSystemTrayAvailable()` was called before
    `QApplication(sys.argv)` was constructed. Touching almost any
    QtWidgets API before a QApplication instance exists is a well-known
    way to crash into uninitialized platform state — confirmed directly
    by deleting the offending pre-QApplication call on a live VM: the
    segfault disappeared immediately, replaced by an ordinary Python
    error from the (intentionally rough) test edit. Fixed properly by
    reordering `main()` so `QApplication` is constructed first. Also
    added `qt6-wayland` to `packages.x86_64` — a real, independently
    correct dependency for proper Qt6 native Wayland platform
    integration (this session runs `XDG_SESSION_TYPE=wayland`), even
    though it turned out not to be the actual segfault cause on its own.
  - Pacman's keyring was never initialized on the installed system at
    all — `sudo pacman -S <anything>` failed with "Public keyring not
    found; have you run 'pacman-key --init'?" on a completely fresh
    install. Silent until the first real package operation, which is
    exactly what `holtos-update-apply`'s `system` item runs
    (`pacman -Syu`) — this would have quietly broken the whole "System
    Packages" updater path for every real install. Fixed in
    `homelab-cleanup-live.sh`: `pacman-key --init` +
    `pacman-key --populate archlinux`, once, on the real target.
- **Real bug found live-testing the fresh Btrfs install**: the installed
  system's real user account had NO working `sudo` at all — not even
  password-prompted. Root-caused in `homelab-cleanup-live.sh`: it
  correctly removes the live medium's own wheel-group *passwordless*-sudo
  rule (a deliberate security choice — leaving that in place on the real
  install would hand any wheel-group account, including the one just
  created, unrestricted no-password root), but never replaced it with a
  normal rule, leaving wheel with no sudo access whatsoever. Confirmed
  live: `sudo` failed with "holtos is not in the sudoers file" even though
  `groups` showed the account correctly in `wheel`. Also confirmed this
  did NOT silently break the updater too — it's pkexec-based, and
  polkit's own default rule grants admin actions to wheel-group members
  independently of `/etc/sudoers`, confirmed still working
  (`pkexec whoami` → `root`) even with `sudo` itself broken. Fixed by
  replacing the passwordless rule with a normal password-required one
  (`/etc/sudoers.d/10-wheel`, `%wheel ALL=(ALL:ALL) ALL`, mode 0440 —
  sudo refuses to read a sudoers.d file at any looser permission).
- **Root filesystem switched from ext4 to Btrfs**, and Limine now themed +
  set up for automatic boot-environment snapshots, both requested after
  the code review below. This is a root-fs change: only takes effect on a
  **fresh install**, not an in-place upgrade.
  - `etc/calamares/modules/partition.conf` (new): `defaultFileSystemType`
    is now `btrfs`; EFI system partition size raised from Calamares'
    stock 300MiB/32MiB default to 1024MiB/512MiB (headroom for the
    per-snapshot kernel+initramfs copies below).
  - `etc/calamares/modules/mount.conf` (new): Btrfs subvolume layout —
    `@`, `@home`, `@cache`, `@log`, plus a new `@snapshots` subvolume for
    the snapshots themselves.
  - `homelab-limine-install.sh`: `rootflags=subvol=@` added to the
    cmdline (Btrfs's top-level subvolume isn't `@` by default — has to be
    told explicitly). Also now installs a HoltOS wallpaper/color theme
    into `limine.conf` (`wallpaper:`, `backdrop:`, `term_palette:`,
    reusing the same PNG already used as the KDE desktop wallpaper), and
    leaves an empty `#### HOLTOS SNAPSHOTS START/END ####`
    comment-delimited block for the new snapshot script to regenerate.
  - New `holtos-btrfs-snapshot <label>`: read-only `btrfs subvolume
    snapshot` of root + a matching kernel/initramfs copy on the ESP +
    a regenerated Limine "boot into this snapshot" menu entry, with a
    5-snapshot retention limit (oldest evicted first, subvolume and ESP
    copy both). Deliberately hand-rolled rather than using the one
    existing third-party tool for this (`limine-btrfs`) — checked its
    repo, it's a 1-star, zero-release Rust project, too unproven to
    depend on for an unattended homelab server. Wired into
    `holtos-update-apply`: `update_system()` (before `pacman -Syu` — the
    update most likely to break boot) and `update_config()` both take a
    snapshot first, best-effort (a failed snapshot doesn't block the
    actual update). Also reachable on-demand via a new "Create Snapshot
    Now" tray menu entry (`holtos-snapshot-now`).
  - **Live-tested in the Hyper-V VM.** Fresh install completed cleanly —
    confirmed the 1024MiB ESP and Btrfs root actually get created (both
    visible live in Calamares' own partition preview and install log).
    Found and fixed one real bug in the process, unrelated to Btrfs
    itself: Limine's config search only checks the directory of the
    EFI binary it was ACTUALLY loaded from (confirmed against Limine's
    real source) — `homelab-limine-install.sh` wrote `limine.conf` only
    next to the primary `/EFI/limine/BOOTX64.EFI` copy, not next to the
    `/EFI/BOOT/BOOTX64.EFI` fallback copy (installed for firmware that
    ignores/loses the NVRAM boot entry). Booting via that fallback path
    — confirmed live, this is a pre-existing bug, not new from the Btrfs
    switch, it had just never actually been exercised in a test before —
    hit `[config file not found]` and refused to boot. Fixed by writing
    the identical `limine.conf` to both paths, and updated
    `holtos-btrfs-snapshot`'s own regeneration logic to keep both copies
    in sync going forward. Rebuilt and re-verifying now — see
    BRANDING-STATUS.md for the live blow-by-blow.
- Full step-by-step code review of everything built this session
  (Calamares installer files, boot chain, KDE desktop defaults, updater
  scripts, Authentik integration, The Den/Client install logic,
  packages.x86_64/profiledef.sh, and cross-cutting path/ID references).
  Found and fixed one real bug: `resolve_release()` (in
  `holtos-update-apply`) and `holtos-update-check`'s own copy of the same
  query both used `git ls-remote --tags --refs`, which — confirmed live
  against this repo's own `v0.0.1-alpha` tag — returns an ANNOTATED tag's
  own object sha, not the commit it points to (verified via the
  `refs/tags/v0.0.1-alpha^{}` peeled line, which has a different sha).
  Since `deployed-commit` is seeded from a real commit sha
  (`git rev-parse HEAD` in build.sh), the two would never match even when
  already up to date — the tray's background check would have reported
  "update available" forever, starting from first boot. Fixed by querying
  without `--refs` and preferring the peeled (`^{}`) commit sha, falling
  back to the plain ref sha for lightweight tags (which have no peeled
  line and are already the commit sha). All other areas checked out
  clean — see BRANDING-STATUS.md for the full pass.
- Both The Den and The Den Client have real tagged releases now
  (`v0.1.0-alpha`) — verified the actual release tarball contents
  against what `update_the_den`/`update_the_den_client` expect.
  `update_the_den` already matched exactly. `update_the_den_client`
  didn't: the repo has grown its own `deploy/` (an official launcher,
  `.desktop` file, and proper icon-theme install path) since that
  function was first written against an earlier version of the repo
  that didn't have one yet. Switched to installing those real files
  (`/usr/bin/the-den-client`, matching icon-theme name, etc.) instead of
  the hand-written launcher/.desktop this function used to generate
  itself.
- `holtos-first-boot-apps.service` (added earlier, previously always a
  no-op since neither repo had a tagged release to install) will now
  actually install both automatically on a fresh install's first boot,
  now that real tags exist — no code changes needed, this was the whole
  point of building it ahead of time.
- Found the actual, definitive reason `holtos-tray` never autostarted,
  after two earlier real-but-insufficient fixes: pulled
  `/tmp/holtos-tray.log` off a live installed system and found `yad
  --notification` failing with "WARNING: This mode not supported outside
  X11" — this session runs Wayland, and yad's tray-icon mode is built on
  GTK3's deprecated, X11-only `GtkStatusIcon`, never ported to the
  StatusNotifierItem protocol Wayland compositors actually use. Neither
  the autostart-phase key nor the missing executable bit (both real bugs,
  both already fixed) could ever have mattered — the log confirms the
  script was launching and reaching yad fine both times. Rewrote
  `holtos-tray` in Python using PySide6's `QSystemTrayIcon` instead,
  which properly implements SNI and works under both X11 and Wayland
  (PySide6 was already a dependency, for The Den Client — no new
  packages needed).
- `update_the_den`'s first install now runs `systemctl enable --now
  the-den` instead of just `enable` — it starts immediately (with
  placeholder settings from `the-den.env.example` until the user edits
  in real TMDB/qBittorrent credentials) rather than waiting for a manual
  `systemctl start`, matching how the rest of the stack comes up
  automatically. `enable` alone already covered "launches on every
  future boot" — this is specifically about *this* first boot too.
- Made `the-den`/`the-den-client` public on GitHub — they were private,
  so the updater's anonymous git/curl (same mechanism it uses for HoltOS
  itself) could never reach them; hit live as a `git ls-remote`
  credential-prompt crash. No code was broken — the updater's improved
  error dialog (below) surfaced the real reason in one shot.
- Fixed the updater's error dialogs showing a generic, useless message
  on failure ("Update failed (exit 1). Check your network connection
  and try again." regardless of the real reason). The actual output was
  only ever streamed through the progress dialog, which `--auto-close`
  closes the instant the process exits — no time to read the last line.
  `holtos-update-picker` and `holtos-rollback-config` now `tee` the
  output to a temp file and show its last few lines in the failure
  dialog instead.
- Added logging and a startup delay to `holtos-tray`, still investigating
  why it doesn't autostart (fixed twice already for two different
  reasons — an autostart-phase key the systemd generator chokes on, then
  a missing executable bit — and it *still* doesn't launch on login even
  with both of those genuinely fixed). Logs to `/tmp/holtos-tray.log` so
  the next failure has real data instead of a third guess; the delay
  defends against a plausible remaining cause (racing Plasma's own
  tray-icon host on startup, a known category of bug for autostart
  tray apps generally).
- Rebranded the installer's main content area (the actual page
  background behind Welcome/Location/Users/etc., which was still plain
  white — everything customized so far was the top/bottom QML bars
  around it) to the HoltOS dark/purple palette. Added
  `stylesheet.qss` (auto-loaded by Calamares since it sits next to
  `branding.desc`, no config entry needed) styling the generic `QWidget`
  selector rather than `#mainApp` alone — confirmed against a real
  shipped example (SalientOS's Calamares branding) that individual page
  widgets don't have their own dedicated ids, `#mainApp` alone doesn't
  reach them. Also styles inputs, buttons, progress bar, scrollbar, and
  list/tree views to match. Doesn't touch the top/bottom bars themselves
  (QML, styled separately via `branding.desc`'s `style:` keys).
- Fixed the "Homepage Dashboard" app tile in Authentik failing to load
  after login (real bug hit live, right after confirming Authentik login
  itself finally works). `homepage-oidc.yaml`'s `meta_launch_url` was
  hardcoded to `http://homepage-dashboard:3000` — the *internal Podman
  network* hostname, which only resolves between containers, never from
  a browser. This exact class of mistake was already called out in a
  comment on the neighboring `redirect_uris` field in the same file, just
  missed for this one. Added `AUTHENTIK_DASHBOARD_URL` (same
  hostname-based address the dashboard's own `NEXTAUTH_URL` already
  uses) in `homelab-generate-secrets.sh` and reference it via `!Env`
  instead of the hardcoded internal name.
- Fixed the account password still requiring 6 characters after the
  previous `minlen=0` attempt (tested live, unchanged). libpwquality's
  own docs are explicit that "disable libpwquality at build-time" is the
  only listed way to fully remove its influence — no config value
  actually clears its ~6-character floor, `minlen=0` included. Bypassed
  it via `allowWeakPasswords`/`allowWeakPasswordsDefault: true` instead
  (pre-checked, so nothing changes from a user's perspective beyond one
  extra checkbox), relying purely on Calamares' own separate `minLength`
  — which has no such floor — for the actual 4-character enforcement.
- Fixed the updater failing to launch at all ("The program
  '/usr/local/bin/holtos-update-picker' is missing executable
  permissions" — real error hit live, from the new System-menu entry).
  Root cause almost certainly also explains the still-unresolved tray
  icon issue: every `holtos-*` script's executable bit was set via
  `chmod +x` in the working copy, but this repo is edited on
  Windows/Git Bash while the archiso build reads it back through WSL2's
  drvfs mount — that bit doesn't reliably survive the round trip.
  `homelab-*.sh` already worked around this via `profiledef.sh`'s
  `file_permissions` override (which forces permissions independent of
  whatever the source filesystem reports); the `holtos-*` scripts were
  simply never added to that same list. Added all eight.
- Replaced the Authentik admin-username approach entirely — Authentik
  login still didn't work with the OS account's username after the
  previous fix, tested live. Root cause: that fix (`admin-username.yaml`,
  a *separate* blueprint renaming the bootstrap-created "akadmin" user
  after the fact) raced against Authentik's own built-in bootstrap
  blueprint. Fetched that built-in blueprint's actual source
  (`goauthentik/authentik`'s `blueprints/system/bootstrap.yaml`) to
  confirm: if the rename blueprint's `identifiers: {username: akadmin}`
  runs *before* the built-in one has created that account yet, `state:
  present` semantics mean it creates a new, mostly-empty user (no
  password, no superuser group) under the desired username instead of
  finding anything to rename — while the built-in blueprint then
  separately creates the *real* akadmin once it runs. Two accounts,
  neither one usable as "OS username + OS password". Fixed by mounting a
  full replacement for Authentik's own `/blueprints/system/bootstrap.yaml`
  (`etc/authentik/blueprints/bootstrap-override.yaml`, adapted from that
  same fetched source with the username parameterized) directly over
  that path, so the account is created correctly — right username,
  password, and superuser group — in one step, no race possible.
- Hardened the password-capture pipeline against locale-dependent text
  corruption: the obscured password (see the earlier `String::obscure()`
  fix) round-trips through several codepoints in Unicode's "Specials"
  block, including ones that coincide with the UTF-8 replacement
  character — a real risk if any tool in the pipeline (printf, bash,
  python) isn't interpreting it as UTF-8. Both `capture-user-creds.conf`
  and `homelab-generate-secrets.sh`'s deobscure step now force
  `LC_ALL=C.UTF-8` explicitly rather than relying on the chroot's ambient
  locale.
- Added a proper "HoltOS Updater" entry to the System category of the
  app menu (`holtos-updater.desktop`, launches the same update picker
  the tray icon opens) — a reliable way to reach the updater regardless
  of the tray icon's autostart status, and useful on its own regardless.
- Fixed the installer's Finished-page "Next" button not restarting the
  system (real bug hit live, after the earlier click-does-nothing fix
  for the same button — this was a second, separate bug on the same
  control). Calamares only runs the configured restart command when it
  *exits* from the Finished page, and exiting is `ViewManager.quit()`,
  not `next()` — on the last page there's nowhere for `next()` to
  advance to, so it was just silently doing nothing. The button now
  calls `quit()` specifically when already on the last page (and shows
  "Done" instead of "Next" there).
- Set the installer's account password requirement to a plain 4-character
  minimum, nothing else — no complexity/class requirements. Added
  `etc/calamares/modules/users.conf` (didn't exist before; Calamares was
  running on its own built-in defaults, which enforce no minimum length
  at all) — deliberately minimal, only touches `passwordRequirements`,
  every other users-module setting stays on Calamares' defaults. Took
  two passes to actually land on 4: the first attempt set
  libpwquality's own `minlen=4`, but libpwquality silently clamps any
  `minlen` below 6 back up to 6 (confirmed against its own docs — hit
  live, `minlen=4` still produced "The password is shorter than 6
  characters", libpwquality's own message, not Calamares'). Fixed by
  setting `minlen=0` (libpwquality's actual "disabled" value) instead,
  leaving Calamares' own separate `minLength: 4` — no such floor — as
  the real enforcement.
- Authentik's admin login username now matches the OS account's username
  instead of staying the hardcoded `akadmin` (which is all
  `AUTHENTIK_BOOTSTRAP_*` env vars can ever produce — no username
  variable exists there). Added a blueprint
  (`etc/authentik/blueprints/admin-username.yaml`) that renames the
  bootstrap-created account after the fact, using the same OS-account
  username `homelab-generate-secrets.sh` already captures. Falls back to
  a no-op rename (stays `akadmin`) if capture failed. Untested against a
  live instance — flagged in BRANDING-STATUS.
- Fixed Authentik's bootstrap admin password never actually matching the
  OS account's password (real bug hit live: install completes fine,
  Authentik comes up fine, but the credentials just don't work — no
  error anywhere, because there wasn't one to see). Root cause: Calamares'
  GlobalStorage `password` key isn't the plaintext password — the `users`
  module runs it through `Calamares::String::obscure()` first (a
  self-inverse substitution cipher, confirmed against that function's
  actual C++ source: characters <= `0x21` pass through, everything else
  maps to `0x1001F - codepoint`), so `capture-user-creds` was faithfully
  capturing a garbled, unusable string the whole time and
  `homelab-generate-secrets.sh`'s "no captured password → fall back to a
  random one" path was silently kicking in on every single install. Fixed
  by reversing the transform (via `python3`, for correct Unicode
  handling) before using the value. **Reminder, unrelated to this bug:**
  the Authentik login *username* is always `akadmin` — never the OS
  account's own username — Authentik has no setting to change that.
- Fixed the HoltOS updater tray icon never appearing on the installed
  system. `holtos-tray.desktop`'s `X-KDE-autostart-phase=2` key — a
  leftover concept from KSMServer's old phased autostart — makes Plasma
  6's `systemd-xdg-autostart-generator` (which converts autostart
  `.desktop` files into systemd user services) silently skip the file
  entirely, so no service, no tray icon, ever. Removed the key; it
  wasn't serving any purpose here anyway.
- Fixed the Calamares "Next" button doing nothing on the Finished page
  (real bug hit live, after a full successful install). Root cause: the
  custom `calamares-navigation.qml` set `enabled: ViewManager.nextEnabled`
  directly on each button's Rectangle — in QML, `enabled: false` on an
  Item cascades to disable every descendant, including the nested
  `MouseArea`, even though that MouseArea's own color binding (driven by
  hover state, not `enabled`) still rendered the button looking perfectly
  normal and clickable. Every button now stays interactive; each
  `onClicked` guards on the ViewManager flag itself instead.
- Fixed the desktop wallpaper not carrying through to the installed
  system. The `/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc`
  approach was the wrong mechanism entirely — hand-writing Plasma's
  containment file is fragile and Plasma just falls back to its own
  defaults when the file doesn't look like what it expects. The actual,
  correct mechanism (confirmed against a real KDE source file) is a
  Plasma Look-and-Feel package's `contents/defaults`, using
  `[Wallpaper] Image=<wallpaper-package-id>` — same mechanism that
  already made dark mode work correctly via `LookAndFeelPackage=` in
  kdeglobals. Added `org.holtos.desktop` (a new look-and-feel package,
  not overriding any package-owned path this time) cascading dark mode +
  brand accent + the HoltOS wallpaper together, and pointed kdeglobals at
  it instead of `org.kde.breezedark.desktop`.
- Fixed the ISO build failing entirely ("checking for file conflicts...
  Errors occurred, no packages were upgraded", every package download
  wasted): the `/usr/lib/os-release` override landed on a path the
  `filesystem` package actually owns, and mkarchiso copies `airootfs/`
  onto the pacstrap target *before* installing packages — so pacman saw
  our file already sitting there, unowned, and refused to let
  `filesystem` install over it. `/etc/os-release` (a symlink to
  `usr/lib/os-release`, *not* itself shipped by any package — confirmed
  via `pacman -Fl`) is the actual convention every other Arch-based
  distro's archiso profile uses for exactly this reason. Moved the
  override there instead.
- Config updates now log to `/var/lib/holtos/history.log` (every applied
  service/config/system update, world-readable, viewable via the tray's
  new "Update History" item), which also backs a new "Rollback Config"
  tray action (`holtos-rollback-config`) that re-applies the tagged
  release before the currently-deployed one.
- Update-available notifications now include the release's notes (pulled
  from the GitHub Release body for that tag, via the GitHub API — falls
  back to the generic message if the tag has no Release object). Added
  `jq` to parse it.
- Integrated two separately-maintained companion repos, updatable through
  the same picker as everything else: **The Den**
  (`jamesyoungdahr-debug/the-den`, a native systemd service — movie/TV
  library manager) and **The Den Client**
  (`jamesyoungdahr-debug/the-den-client`, its PySide6/Kirigami desktop
  app). Both are gated on tagged releases only, same as `config` — never
  raw commits. Neither is baked into the ISO image (neither has a tagged
  release yet, so there's nothing to vendor at build time); picking
  either in the updater installs it fresh if it's not present, or updates
  it in place if it is, using the same `holtos-update-apply` mechanism.
  `update_the_den` mirrors that repo's own PKGBUILD/`the-den.install`
  step for step (sysusers, tmpfiles, systemd service, venv, alembic
  migrations) but runs it directly instead of through a rebuilt pacman
  package, so the installed system doesn't need a build toolchain for
  what's really just "copy files + venv + pip install." Added `python`,
  `pyside6`, `kirigami`, `qqc2-desktop-style` to the package list.
- Added `holtos-first-boot-apps.service`: on the installed system's first
  boot, automatically installs The Den / The Den Client if either repo
  has a tagged release yet (does nothing, quietly, for whichever doesn't
  — same as picking it manually in the tray before a release exists). A
  marker file makes this run exactly once; the tray's picker still works
  normally afterward for real updates.
- Fixed a real bug in `holtos-update-apply`: picking multiple items in
  the tray where one had no release yet (e.g. Sonarr + The Den, before
  The Den had a tag) silently skipped every item *after* the failing one
  — `set -e` was aborting the whole batch on the first failure. Each
  item is now attempted independently; failures are collected and
  reported at the end instead of stopping the batch.

## [0.0.1-alpha] - 2026-09-08

- Added a HoltOS updater: a system tray icon (`holtos-tray`, autostarted)
  with a per-item picker (`holtos-update-picker`) rather than one
  all-or-nothing update — check boxes for the dashboard, each individual
  podman service (Sonarr, Radarr, Plex, etc.), the shared config
  (Podman Quadlet units + `homelab-*.sh` scripts), and system packages,
  in any combination, applied through a single `pkexec` prompt
  (`holtos-update-apply`) with progress in a yad dialog. Per-service
  updates are a plain `podman pull` + `systemctl restart`, so they're
  always as current as that service's own upstream image — no git
  involved. The config item is the one exception: it's gated on the
  latest *tagged* HoltOS release (e.g. `v0.0.1-alpha`), downloaded as a
  GitHub release tarball (no `git clone`, no repo history) rather than
  raw commits, so in-progress work on the repo never lands on a running
  system. System packages just runs `pacman -Syu` — kernel/OS updates
  are pacman's job, not something the git repo drives.
  The tray's background loop (every 6h, or on demand via "Check for
  Updates") only watches for new tagged releases and notifies when one's
  out; `build.sh` stamps the ISO with its build commit so a fresh
  install's first check is accurate.
- Branded the updater's GTK dialogs: added `breeze-gtk` plus dark-mode and
  brand-purple-accent defaults under `/etc/skel/.config/gtk-{3,4}.0/`
  (yad is a GTK3 app — without a theme it was rendering as plain light
  Adwaita against the rest of the dark/purple system). Also added
  `--window-icon`, a success dialog, and brand-voice copy to
  `holtos-update-picker`'s dialogs.
- Reworked the Calamares installer layout: the step list moved from a
  vertical left sidebar to a horizontal bar along the bottom
  (`calamares-sidebar.qml`), and Back/Cancel/Next moved into a new top
  bar with the HoltOS logo centered between them
  (`calamares-navigation.qml`), replacing Calamares' default widgets.
  Both are custom QML (Calamares ships no built-in fallback for the
  `sidebar: qml` / `navigation: qml` branding.desc options in this
  build), adapted from a real shipped reference (KaOS's branding
  component) rather than written from scratch. Also fixed the
  `style:` section in `branding.desc`: `SidebarTextSelect` /
  `SidebarTextHighlight` were never real Calamares style keys — the
  actual ones are `SidebarBackgroundCurrent` / `SidebarTextCurrent`,
  which now actually drive the current-step/current-button highlight
  color instead of being silently ignored.
- Calamares Welcome page: removed the opaque background rect from
  `logo-icon.svg` that showed as a black box on the white welcome content
  area; converted `rgba()` fills to hex + `fill-opacity` (Qt's SVG renderer
  doesn't reliably support `rgba()`).
- KDE Plasma now defaults to dark mode (Breeze Dark) for both the live
  session and the installed system, via `/etc/skel/.config/kdeglobals`.
- Authentik's bootstrap admin password now matches the OS account's
  password, captured via a custom Calamares job
  (`capture-user-creds`) before Calamares hashes it. The bootstrap admin
  *username* stays `akadmin` — Authentik has no
  `AUTHENTIK_BOOTSTRAP_USERNAME` variable to change that.
- Brand color pass: MOTD and the BIOS (syslinux) boot menu title now use
  `#B14DFF` instead of an arbitrary blue.
- Added a HoltOS-branded Plymouth boot animation (dark background +
  otter watermark) for both the live medium and the installed system.
- Added a HoltOS background color to the installed system's SDDM login
  screen (Breeze theme, `theme.conf.user` override).
- Added branded per-service app-menu icons (Sonarr, Radarr, Prowlarr,
  Jellyseerr, Plex, qBittorrent, Authentik, Dashboard) replacing the
  generic `applications-internet` icon.
- Added a dashboard app favicon (`app/icon.svg`) using the otter mark.
- Renamed ISO metadata from leftover `homelab-os` naming to `holtos`/HoltOS
  throughout `profiledef.sh`.
- Set the HoltOS product version to `0.0.1-alpha` (`branding.desc`,
  `profiledef.sh`).
- Added `build.sh`: wraps the mkarchiso build and backs up any existing
  ISO in `out/` to `out/backups/<timestamp>/` before building, so a build
  never silently overwrites a previous one. Also grants Hyper-V read access
  on the built ISO automatically (the WSL2/podman build writes it with ACLs
  that block the Hyper-V VMMS service otherwise).
- Fixed `capture-user-creds`: the original `interface: python` Calamares
  job module never loaded (this Calamares build has no pythonjob plugin
  compiled in), which broke the installer entirely. Rewritten as a
  `shellprocess` job using Calamares' `${gs[...]}` GlobalStorage
  substitution instead.
- Fixed the Calamares sidebar logo rendering squished — the sidebar's logo
  slot is a fixed 80×80 square; `logo-wide.svg` (a wide icon+wordmark
  lockup) was being force-stretched into it. `productLogo` now points at
  the square-padded `logo-icon.svg`.
- Fixed the welcome page showing "Welcome to the Calamares installer for
  HoltOS" — `welcomeStyleCalamares` was set backwards; `false` (the
  Calamares default) is what gives the clean, de-branded text.
- Replaced the Plymouth `spinner` theme with a `script`-based one — this
  Plymouth build doesn't ship a `spinner` renderer plugin at all, so the
  original theme silently failed to build. The script theme draws the
  otter watermark plus a Windows-11-style rotating ring spinner in brand
  colors.
- Overrode `/usr/lib/os-release` (the real target of the `/etc/os-release`
  symlink) with HoltOS identity — fixes KDE's "About This System" dialog,
  `hostnamectl`, and any `neofetch`-style tool still reporting plain Arch
  Linux. Added a `holtos-logo` icon so the `LOGO=` field resolves.
- Renamed the live-medium hostname from `archiso` to `holtos` (was showing
  in every live-session terminal prompt).
- Set the Plasma accent color to brand purple (`AccentColor=177,77,255` in
  kdeglobals) so buttons/toggles/selection match the brand, not default
  blue.
- Added a HoltOS Konsole color scheme + profile, set as the default for
  new terminals.
- Rebranded `/etc/issue` (console pre-login banner) from "Arch Linux" to
  "HoltOS".
- Explicitly pointed the lock screen (`kscreenlockerrc`) at the desktop
  wallpaper image, rather than relying on Plasma's default inheritance
  behavior.
- Added real desktop wallpaper and SDDM login background art (otter
  bleeding off the bottom-right corner at low opacity, brand lockup +
  teal hairline), designed by the HoltOS Design System project and wired
  in via a Plasma wallpaper package + SDDM `theme.conf.user`.

### Earlier work in this release (initial validated build)

- archiso + Calamares + Limine profile with a validated real
  install → reboot cycle in a Hyper-V VM.
- Podman Quadlets for Authentik (SSO), Sonarr, Radarr, Prowlarr,
  Jellyseerr, qBittorrent, Plex, and the custom dashboard app; stack runs
  off local disk with ZFS mounted separately.
- Auto-generated secrets (`authentik.env`, `dashboard.env`) with no manual
  setup; *arr API keys auto-synced into `dashboard.env` after first boot.
- App-menu launchers for every service's web UI.
- Custom HoltOS Calamares branding (logo, sidebar colors, install
  slideshow) replacing Calamares' stock Arch Linux branding.
