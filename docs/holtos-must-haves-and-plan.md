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

### 1.1 Steam preinstalled with Proton and Proton GE — planned

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

### 1.3 Controllers and the living room — planned

`steam-devices` udev rules, Bluetooth (done: bluedevil/bluez), HDMI CEC via
`libcec` for TV remotes, `xpadneo`/`xone` DKMS for Xbox pads, and audio
passthrough defaults for an AVR. Add a "Living room" preset in Game Mode:
TV resolution, HDR on, 4K@120 where possible.

### 1.4 Performance defaults — planned

`gamemoded` enabled; `amd-pstate` EPP "performance" while a game runs
(gamemode hook); zram (`zram-generator`, half of RAM); CachyOS-style
udev/sysctl tweaks (I/O schedulers per disk type, `vm.max_map_count` for
games). Optional CachyOS kernel later if measurements justify it.

## 2. Apps

### 2.1 A HoltOS app store — planned

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

SMB/NFS with systemd automount, GUI, tray entry. Next: browse the LAN
(Avahi/WS-Discovery) so servers and shares can be picked instead of
typed, and a "share this folder" (Samba server) page for the box itself.

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
  repo). Add: update window (e.g. 04:00) and auto-rollback if the desktop
  fails to come up twice.
- Disk health — done (plasma-disks). Add: desktop notification on SMART
  failure and a monthly scrub timer for Btrfs/ZFS.
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
