# HoltOS — must-have features and how to build them

Written 2026-09-12 for Liam. HoltOS is a **media and gaming/entertainment
focused** distro: a living-room box that plays your library, runs your
games, and stays out of the way. This list is what such a box must do,
each item with the plan to implement it on top of what HoltOS already has
(Arch + KDE Plasma 6 with HoltOS Glass, Btrfs snapshots with one-click
restore, The Den, themed Limine with other-OS detection, the HoltOS
updater and package repo, Network Shares).

Status key: **done** · **planned** (designed here, not built) · **later**.

## 1. Gaming

### 1.1 Steam preinstalled with Proton and Proton GE — mostly done, doc was stale

- Packages: `steam` (multilib), `gamemode`, `mangohud`, `lib32-*` Vulkan
  drivers (`lib32-vulkan-radeon`, `lib32-vulkan-intel`, NVIDIA's lib32 on
  the NVIDIA path), `xdg-desktop-portal-kde` (there), `gamescope`.
  `[multilib]` must be enabled in `pacman.conf` (build and installed).
- Proton comes with Steam; **Proton GE** does not. Ship a HoltOS tool
  `holtos-proton-ge` (root-less, runs as the user): fetches the latest
  GloriousEggroll release tarball from GitHub, verifies the sha512 it
  publishes, unpacks into `~/.steam/root/compatibilitytools.d/`, keeps the
  last two versions, and is offered from the tray ("Update Proton GE") and
  by the updater's check ("Proton GE x available"). First-boot: install
  it once Steam has created its directories (a per-user oneshot in the
  autostart, like the snapshot notice).
- Steam itself is installed in the image; first launch does its own
  update. A "Gaming" page in the tray/updater picker shows Steam, Proton
  GE, and gamescope versions.
- Verification: VM can prove packaging and Proton GE fetch/unpack; the
  Strix Halo box proves a game launches under Proton GE with MangoHud.
- **Status correction (2026-09-13):** `holtos-proton-ge`, `holtos-update-proton-ge`, and the first-run autostart entry already exist in `archiso/airootfs/usr/local/bin/` and `archiso/airootfs/etc/xdg/autostart/` — this item was marked "planned" but the tool itself is built. `xdg-desktop-portal-kde` has now also been added to `packages.x86_64` (was referenced in this doc's own text above but was missing from the actual package list until now). Not yet build-verified in the VM. **Gaming page written (2026-09-13):** `archiso/airootfs/usr/local/bin/holtos-gaming` (PySide6 dialog, same pattern as holtos-shares) shows the Steam/gamescope/gamemode/MangoHud package versions, the Proton GE builds installed for the user, checks GitHub for a newer Proton GE in a background thread, and exposes the "Start in Game Mode" default plus "Switch to Game Mode now" -- all buttons hand off to the existing tools (`holtos-update-proton-ge`, `steamos-session-select`, `holtos-session-apply --default`) rather than duplicating them. Wired in as a "Gaming..." tray entry, a `holtos-gaming.desktop` launcher, and a `profiledef.sh` permission entry; the updater already ships it via its `usr/local/bin/holtos-*` and `holtos-*.desktop` globs. Syntax-checked, not yet run live -- the tray (and so this page) deliberately doesn't start on the live ISO, so it needs an installed system to test.

### 1.2 Game Mode: gamescope session, switch both ways — built (builds 18–20), real-hardware check pending

What SteamOS/Bazzite do, done HoltOS' way:

- A second session for SDDM, **"HoltOS Game Mode"**: `gamescope-session`
  running Steam in Big Picture on gamescope's own Wayland compositor
  (`gamescope -e --steam -- steam -gamepadui`), with `--hdr-enabled` and
  VRR flags when the display supports them, and `mangoapp` overlay.
- **Switching**: Plasma → Game Mode is a launcher "Game Mode" that tells
  SDDM to end the Plasma session and start the gamescope one (session
  handoff through `loginctl` + SDDM's autologin override for one boot,
  the same trick Bazzite's `steamos-session-select` uses). Game Mode →
  Plasma is Steam's own "Switch to Desktop" button, which calls the same
  script the other way. Both keep the user logged in through the switch.
- **Boot straight into Game Mode**: a setting in the tray ("Start in Game
  Mode") that writes SDDM's autologin session; the Limine entry stays one
  ("HoltOS"), the session decides.
- **The Den keeps running**: it is `the-den.service`, a system service
  independent of any graphical session, so it is unaffected by the switch;
  the client app is a desktop app and is simply not shown in Game Mode.
  The Den's web UI stays reachable from Big Picture's browser.
- Verification: VM can prove the session exists, switches both ways and
  The Den stays up (gamescope runs on llvmpipe); real GPU for HDR/VRR.
- **NVIDIA fixes (2026-09-13):** `homelab-detect-hardware.sh`'s NVIDIA install path now also writes `/etc/modprobe.d/nvidia-drm.conf` (`modeset=1`, `fbdev=1`) alongside the existing kernel cmdline `nvidia_drm.modeset=1` -- required for gamescope/Wayland to behave well on NVIDIA (CachyOS ships the same file). `gamescope-wsi` was investigated as a possible second fix but turned out not to be a real separate package -- the WSI layer is already bundled in the `gamescope` package HoltOS already ships. HDR/VRR under gamescope specifically (not just Plasma) remains genuinely less mature on NVIDIA than AMD as of current upstream state -- not something this fix resolves, flagged here so it isn't mistaken for done.
- **Considering (not started), contract now confirmed (2026-09-13):** `gamescope-session-git`/`gamescope-session-steam-git` (AUR, both already added to `build-aur-packages.sh`'s AUR_DEFAULT list, not yet wired into `packages.x86_64`) are trivial to build (`depends=(gamescope)` / `depends=(gamescope gamescope-session-git)`, no unusual build steps) -- but build order matters, `gamescope-session-git` must build/publish to the local repo before `gamescope-session-steam-git`'s `makepkg -s` runs. **Real bug found and fixed (2026-09-13):** `build-aur-packages.sh` only ran `repo-add` once at the very end of its whole AUR loop, so a same-run dependency like this would have failed -- pacman would have had no repo yet to resolve `gamescope-session-git` from when building `gamescope-session-steam-git`. Fixed by having the loop `pacman -U` each package immediately after building it, so it's already present on the system for any later package's `makepkg -s` dependency check, not reliant on a repo database at all. Their `/usr/bin/steamos-session-select` (source verified at github.com/ChimeraOS/gamescope-session-steam) execs exactly one hook path, `/usr/lib/os-session-select`, forwarding all arguments unchanged, falling back to `steam -shutdown` if the hook is absent -- the earlier claim of a second `/usr/libexec/` fallback path was wrong, corrected here. HoltOS's own `steamos-session-select` already lives at `/usr/local/bin/` and is never on the path Steam's client or this AUR package's hook actually calls -- today's Game Mode -> Plasma switch already works without that hook, because `holtos-gamemode-session` returns to Plasma on any clean gamescope exit regardless of how the exit happened. **The real Phase A integration, when started, is narrow**: add a 3-line `/usr/lib/os-session-select` shim that execs HoltOS's existing `/usr/local/bin/steamos-session-select "$@"`, so if/when `gamescope-session-steam-git` is later added to `packages.x86_64`, its hook delegates to HoltOS's already-working switch logic instead of silently falling back to `steam -shutdown`. **Written (2026-09-13):** `archiso/airootfs/usr/lib/os-session-select` (3 lines, execs the existing script with all args), permission entry added to `profiledef.sh`, shellcheck clean. Still not referenced by anything until `gamescope-session-git`/`gamescope-session-steam-git` are actually added to `packages.x86_64` -- harmless to ship in the meantime.
- **Decky Loader risk flagged (2026-09-13):** the AUR `decky-loader` PKGBUILD (added to AUR_DEFAULT alongside the above two) is meaningfully more fragile than a normal AUR package -- it fetches a GitHub release tarball, runs a `pnpm i --frozen-lockfile` JS build and a `python-poetry` wheel build with version-pin `sed` hacks to `pyproject.toml`, needing both a Node/pnpm toolchain and network access mid-build inside the aur-builder container. `makepkg -s` should auto-install its makedepends (`pnpm`, `python-poetry`) same as any other package, so it isn't necessarily broken, but it's the single most likely of the three new AUR packages to fail on first real build attempt. Its systemd unit is `decky-loader@<username>.service` (system-level, root, NOT auto-enabled by the package -- needs an explicit `systemctl enable --now` step), which also diverges from upstream's own installer (a differently-named `plugin_loader.service`) -- don't conflate the two when writing the session-hook that starts/stops it. **Wiring not done (2026-09-13), on purpose:** starting/stopping `decky-loader@<username>.service` from `holtos-gamemode-session` needs a `pkexec`-or-equivalent call, since it's a root-owned system unit and the session runs as the logged-in user with no keyboard available in Big Picture to answer a password prompt (same constraint `50-holtos-session.rules` already solves for the Plasma<->Game Mode switch itself). That existing rule only grants `org.freedesktop.policykit.exec` for one exact program path; a systemd unit start/stop needs a different polkit action (`org.freedesktop.systemd1.manage-units`, scoped to the specific unit) written correctly by hand, not guessed -- this is security-relevant logic and deliberately not rushed in alongside the rest of this session's Phase A/B/C work. Do this only after `decky-loader` itself is confirmed to actually build (still unverified, see the risk above) and only as its own deliberate, reviewed change.

**Polkit rule researched and ready (2026-09-13), not yet written:** confirmed via systemd's own upstream commit (88ced61bf9673407f4b15bf51b1b408fd78c149d, "core: pass details to polkit for some unit actions") that systemd's native start/stop authorization uses action id `org.freedesktop.systemd1.manage-units` with two lookup keys polkit rules can read: `action.lookup("unit")` (the resolved unit name, e.g. `decky-loader@liam.service`, not the bare template) and `action.lookup("verb")` (`start`/`stop`/etc). The commit's own verbatim example hardcodes one user and one unit name; the HoltOS-specific version (scoping to the invoking user's own instance of the template, matching `50-holtos-session.rules`'s existing `subject.local && subject.active` posture) is drafted but NOT independently verified upstream -- it's a straightforward adaptation of the confirmed API, not copied working code:

```javascript
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.systemd1.manage-units" &&
        action.lookup("unit") == "decky-loader@" + subject.user + ".service" &&
        (action.lookup("verb") == "start" || action.lookup("verb") == "stop") &&
        subject.local && subject.active) {
        return polkit.Result.YES;
    }
});
```

Not written to disk yet -- waiting on decky-loader's own build verification first, per the paragraph above.

### 1.3 Controllers and the living room — in progress (2026-09-13, branch `defaults`)

- **Done**: `steam-devices` udev rules (comes with Steam), Bluetooth
  (bluedevil/bluez), `libcec` for TV remotes over HDMI-CEC.
- **Building**: `xpadneo-dkms` (Xbox pads over Bluetooth) and
  `game-devices-udev` (non-Steam controllers without root) are in the AUR
  build list. They join `packages.x86_64` once `build-local-repo.sh` has
  actually built them, so an ISO build never asks for a package the local
  repo does not have.
- **Left out on purpose**: `xone` (the Xbox wireless dongle). Its
  `xone-dongle-firmware` package downloads Microsoft's driver, which the
  image cannot redistribute; if wanted, it has to be an opt-in download on
  the user's own machine.
- **Still planned**: audio passthrough defaults for an AVR, and a "Living
  room" preset in Game Mode (TV resolution, HDR on, 4K@120 where possible).

### 1.4 Performance defaults — done (2026-09-13, branch `defaults`)

- **zram**: `zram-generator`, half of RAM, zstd (already shipped; verified
  on the build 24 live VM: 3.9G of 8G).
- **I/O schedulers per disk type**:
  `etc/udev/rules.d/60-holtos-ioschedulers.rules`, from CachyOS-Settings
  (BFQ for HDDs, mq-deadline for SATA SSDs and SD cards, kyber for NVMe).
  Verified live: rotational disks switch from `none` to `bfq`.
- **`vm.max_map_count`**: nothing to do. Arch already sets 1048576 in
  `/usr/lib/sysctl.d/10-arch.conf` (verified on the VM).
- **CPU performance while a game runs**: nothing to add. `gamemode`
  (shipped) switches the CPU governor and platform profile to "performance"
  and restores them afterwards by default; on `amd-pstate` the performance
  governor also forces the performance energy preference.
- Optional CachyOS kernel later if measurements justify it.

## 2. Apps

### 2.1 A HoltOS app store — built (2026-09-13, branch `apps`)

- **Status**: HoltOS Apps (`holtos-apps`): 27 curated Flathub apps in five
  categories (`usr/share/holtos/apps.json`), search, and an Installed tab,
  each with Install / Open / Remove; system-wide installs with no password
  through Flatpak's own polkit rule; Flathub from `etc/flatpak/remotes.d`.
  Verified on the build 24 live VM (installing and removing Flatseal from
  the desktop). Updates go through HoltOS Updates. The name stays "HoltOS
  Apps" until Liam picks one.
- **Source**: Flathub. It is what every other distro uses and where the
  media/gaming apps live (Jellyfin, Plex, Kodi, Heroic, Lutris, OBS,
  Discord, VLC, Firefox). Own repo only for HoltOS-built apps later.
- **Shape**: not a fork of Discover. A HoltOS-owned PySide6 app — same
  toolkit as the tray and Network Shares — over `libflatpak` /
  `flatpak` CLI: a curated **front page** (HoltOS picks: media players,
  game launchers, streaming, browsers, chat), search across Flathub,
  install/remove/update with progress, and "Updates" wired into the
  HoltOS updater's check so Flatpak updates show in the tray count.
  Curation is a JSON list in the HoltOS repo (name, Flathub id, blurb,
  category, icon), updatable through the config update like everything
  else.
- **Name**: to decide. Candidates that fit the otter/holt branding: *The
  Holt* (an otter's den — but "Den" is taken by The Den), *Otter Shop*,
  *HoltOS Apps*. Plain **"HoltOS Apps"** is the safe default until Liam
  picks.
- Base: `flatpak` + `flatpak-kcm` + the Flathub remote added at image
  build (`flatpak remote-add --if-not-exists flathub`), portals already in.
- Verification: VM installs a Flathub app from the store and it appears
  in the app menu.

### 2.2 Network Shares — done (2026-09-12)

SMB/NFS with systemd automount, GUI, tray entry.

**LAN browsing and sharing from this computer — done (2026-09-15, neon
branch):** "Browse..." in the Add dialog runs `holtos-share browse`
(avahi `_smb._tcp`/`_nfs._tcp`, NetBIOS through nmblookup) and
`holtos-share shares` (smbclient -L / showmount -e), both as the user with no
password prompt; avahi-daemon and nss-mdns are enabled on new installs and by
`holtos-system-extras` on updated ones. The "Share from this computer" tab
drives `holtos-samba` (root, written by hand): folders only under the
owner's home (not hidden) or /mnt, /media, /run/media/<owner>, /srv; files
served as the owner (`force user`), guests read-only; LAN-only `hosts
allow`, SMB2+, no NetBIOS; the generated smb.conf passes testparm before use;
smb + wsdd run only while something is shared. VM-tested: refusals, guest
read/no write, symlink escape blocked, mDNS announce, services stop when the
last share goes. Not tested: opening a share with a network password (needs a
password set on real hardware), WS-Discovery from a Windows PC. Still open:
WS-Discovery browsing of Windows PCs that do not answer NetBIOS (wsdd 0.9's
discovery socket), and the media-pool export decision (2.3).

### 2.3 Media stack — see `docs/media-server-must-haves.md`

The Den is the library and acquisition layer. Still to decide: the
player/server (Jellyfin is the open choice) — installed from the store or
shipped; storage layout wizard (Btrfs RAID1 / ZFS for the media pool);
Samba export of the pool; Tailscale for remote access.

## 3. Display and hardware

- **HDR / VRR / refresh** — done for AMD/Intel via amdgpu/i915 KMS; NVIDIA
  needs PLAN step 7's driver install and `KWIN_DRM_ALLOW_NVIDIA_COLORSPACE=1`
  for the HDR toggle (documented, not shipped by default).
- **Refresh-rate matching** for video playback — planned with the player
  choice (Jellyfin Media Player / mpv can do it).
- **Hardware detection** — done: NVIDIA install path, AMD/Intel logging
  (vainfo/vulkaninfo) in `hardware.log`.
- **Strix Halo** — nothing special needed; verify on Liam's machine.

## 4. System

- Snapshots with one-click restore — done. Add: scheduled snapshots of
  the media pool (deleted-file insurance), retention setting in the tray.
- Updates from HoltOS' own sources — done (component whitelist + package
  repo). **Windows-style updater (2026-09-13, branch `updater`):** automatic
  checks on a timer and after Game Mode, version-aware installs, the HoltOS
  Updates window with live progress and settings (interval, auto-download,
  auto-install, install window), system packages including the kernel,
  Flatpak, fwupd firmware, and Steam's own Software Updates page in Game
  Mode. Still to add: auto-rollback if the desktop fails to come up twice.
- Disk health — done (plasma-disks). **SMART notification + monthly scrub
  added (2026-09-13):** `etc/smartd.conf` (DEVICESCAN, no spin-up of
  sleeping disks, `-M exec`) has smartd call `holtos-disk-alert`, which
  records the failure in `/var/lib/holtos/disk-alert`; `holtos-scrub.timer`
  (monthly, Persistent, idle I/O priority) runs `holtos-scrub` over every
  mounted Btrfs filesystem and imported ZFS pool, logging to
  `/var/lib/holtos/scrub.log` and recording any errors in the same alert
  file. Root services can't reach the desktop, so a per-login autostart
  (`holtos-disk-alert-notice`, same pattern as the snapshot boot notice)
  shows the alert with an "Open Disk Health" button; dismissal is per user
  via the file's mtime, no root needed. `smartmontools` listed explicitly
  in `packages.x86_64`; `smartd.service` + the timer enabled in
  `customize_airootfs.sh`; the updater's enable loop now covers
  `holtos-*.timer` too. Syntax/shellcheck clean, not yet run on a live
  install.
- Support bundle — planned: `holtos-support-bundle` tars journal,
  hardware.log, history.log, disk health, for pasting into an issue.
- First-run wizard — planned: storage, media folders, shares, remote
  access, Game Mode on/off, store picks.

## Order of work (proposal)

1. **Gaming base** (1.1): multilib, Steam, gamemode, mangohud, gamescope,
   Proton GE tool. One build, VM-verified packaging, Strix Halo-verified
   play.
2. **Game Mode session** (1.2) with the switch both ways and "start in
   Game Mode".
3. **HoltOS Apps** (2.1) over Flathub with the curated front page.
4. Controllers/CEC (1.3) and performance defaults (1.4).
5. Media player decision + storage wizard + Samba export (2.3).
6. Update window / auto-rollback / scheduled snapshots (4).
7. First-run wizard tying it together.

Each step: one commit series, a VM install, an entry here and in
CHANGELOG, and a release tag when Liam has seen it on real hardware.
