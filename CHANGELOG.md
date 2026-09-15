# Changelog

All notable changes to HoltOS are logged here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

Neon rebrand (next major release):

- **New otter logo**, generated on ComfyUI (Liam's pick: the flat otter with a
  magenta-to-blue neon rim). App icons from 16 to 512 px, a one-colour tray
  glyph and a large mark for the About page, cut from the renders by
  `tools/brand/derive_logo.py`.
- **New desktop layout:** a thin glass menu bar across the top (app launcher,
  the active app's menus, system tray, clock) and a floating dock at the
  bottom centre that is only as wide as its apps (Dolphin, Chromium, Steam,
  HoltOS Apps, Konsole, System Settings). Existing accounts switch at their
  next login; their old panels are kept as `*.before-neon-layout`.
- GTK apps show their menus in the top bar (`appmenu-gtk-module`).
- **Smaller title bar buttons and dock icons** for a less cluttered look.
- **"homelab" is now HoltOS everywhere:** the installer and boot menu scripts,
  the kernel-update hook and the installer shortcut carry the HoltOS name.
  Updating removes the old homelab files once the renamed ones are in place,
  so the boot menu still refreshes exactly once per kernel update.
- **HoltOS Updates, more complete:**
  - Tick which updates to install; "Skip this version" leaves a HoltOS
    release out (newer ones are still offered).
  - Each update shows its download size, and system updates list every
    package with its installed and new version.
  - Before installing, HoltOS Updates warns about a low battery, a nearly
    full disk or a metered connection. Automatic updates wait in those cases
    and the window says why; a system update refuses to start without room
    to finish.
  - "Restart when finished" restarts after a 60-second countdown you can
    cancel.
  - When an update fails: the install log, Retry for just the failed
    updates, and a support bundle, one click each.
  - A Snapshots tab lists the snapshots HoltOS keeps, and creates, restores
    and deletes them.
  - Settings: hold packages at their current version, and "Fix updates"
    (clears a stuck update, repairs the package keys, picks fast mirrors,
    repairs Flatpak).
  - The tray tooltip shows an install in progress.
- **HoltOS Apps, rebuilt:**
  - Every app has its own page: screenshots, description, developer and
    verified badge, download and installed size, licence, release notes and
    links.
  - Before an app that asks for broad access installs (all your files, your
    saved passwords, programs outside its sandbox), HoltOS Apps lists what it
    wants and asks first.
  - Browse Flathub's categories and its Popular, Trending, New and Recently
    updated rows next to the HoltOS picks, which grow to 43 apps with a new
    Create group (HandBrake, Kdenlive, Audacity) and more emulators.
  - Installs, updates and removals show real progress (percent, download size
    and speed), queue up behind each other and can be cancelled.
  - The Installed page shows sizes, sorts by name or size, can delete an app's
    settings and data along with it, and cleans up runtimes no app uses.
  - The Updates page updates one app or everything.
  - "Install" links on flathub.org and downloaded .flatpakref files open the
    app's page in HoltOS Apps (Flathub only).
  - The store window is HoltOS glass (it was drawn opaque before).
- **Glass popups and tooltips:** the calendar, tray, launcher and other Plasma
  popups and all tooltips now use HoltOS glass with rounded corners instead of
  Plasma's default look, in both HoltOS and HoltOS Classic. A fix in the
  panel frames comes with it (the middle of a stretched frame was only
  partly filled).
- **Logo lockups:** horizontal and stacked HoltOS lockups for dark and light
  backgrounds in `/usr/share/holtos/brand/`, made from the rendered otter mark
  and Nunito ExtraBold (`tools/brand/derive_lockups.py`).
- **Network Shares finds servers for you:** "Browse..." in the Add dialog
  lists the SMB and NFS servers on your network (announced over mDNS, or
  Windows PCs found over NetBIOS) and the shares each one offers, so nothing
  has to be typed. Computers' `.local` names now resolve.
- **Share folders from this computer:** Network Shares > "Share from this
  computer" shares a folder with the other computers on your local network,
  optionally read-only for everyone, and sets the network password you open
  it with. Windows finds the computer in its Network view (wsdd), Macs and
  Linux over mDNS. Only folders in your home folder (not hidden ones) or on
  drives under /mnt, /media, /run/media and /srv can be shared, only local
  addresses may connect, and Samba runs only while something is shared.
- **Updates that break the desktop undo themselves:** if the desktop (or the
  login screen) does not come up on two boots in a row after an update,
  HoltOS restores the snapshot taken just before that update and restarts,
  then tells you at the next login. The system as it was is kept as a
  snapshot too, and your home folder is never touched.
- **Choose how many snapshots to keep:** HoltOS Updates > Settings > "Keep
  before updates" (2 to 10, default 5). Older snapshots, their kernel
  copies and boot entries are removed beyond that number.
- **Support bundle:** tray menu > Create Support Bundle (or
  `holtos-support-bundle`) saves the logs and system facts needed for a bug
  report into one file in your home folder, with your user and computer
  names replaced.
- **Install alongside Windows (dual boot):** the installer accepts the EFI
  partition Windows already made (usually 100 MB), a new "Notes" step before
  Partitions explains what to do first (turn off Fast Startup, have the
  BitLocker recovery key, make room, back up), and the boot menu lists
  Windows. On a small EFI partition HoltOS keeps only as many snapshot
  kernels as fit, and kernel updates make room first instead of failing;
  snapshots without a kernel copy can still be restored from the desktop.
- **The HoltOS package repository is called `[holtos]`** (was `[homelab]`).
  Updating renames the section in `pacman.conf`; the repository is published
  under both names for a while, so installs that have not updated yet keep
  getting HoltOS packages.
- **Drivers for hardware added later:** every update checks the machine's
  hardware. An NVIDIA graphics card or a Broadcom Wi-Fi chip fitted after
  installing gets its driver (NVIDIA also gets its boot settings), the
  drivers then update with the system, and HoltOS asks for a restart when a
  new driver needs one. What was found is logged in
  `/var/lib/holtos/hardware.log`, and HoltOS Updates has a **Hardware** tab
  listing the drivers this computer needs and whether each is installed.
- **Every HoltOS tool uses the new otter logo** (Updates, Apps, Gaming,
  Network Shares, the snapshot and rollback tools, notices). The old
  hand-drawn logos are removed from installed systems, so the old otter can no
  longer turn up in menus or notifications.
- **New boot, login, splash and installer art** from the new otter logo: a
  full-body otter on the login screen, a neon glow behind the login and boot
  screens, and the otter with the HoltOS name on the boot splash, login card
  and Plasma splash. Generated on ComfyUI and prepared by
  `tools/brand/derive_splash_art.py`.
- **New HoltOS Glass Plasma style (`holtos-glass`), now the default:** the menu
  bar is plain glass with a faint bottom line; the dock is a smoked-glass
  capsule with a neon rim that runs magenta to purple to electric blue. In the
  dock, running apps get a short magenta underline, the active app a soft
  purple glow, and apps asking for attention turn amber. Generated by
  `tools/glass/plasma_theme.py`.
- **HoltOS Classic global theme** for anyone who prefers the old single bottom
  panel, with its own plain glass style (`holtos-glass-classic`). Pick it in
  System Settings > Global Theme.
- **Only HoltOS themes ship now.** Removed: the Breeze, Breeze Dark and Breeze
  Twilight global themes; Klassy's global themes, Plasma styles, colour
  schemes and icons; the stock Kvantum themes; the Breeze colour schemes; the
  Breeze Dark and Breeze Light Plasma styles; and the stock SDDM and Plymouth
  themes. Plasma's default style, SDDM's Breeze, Plymouth's text themes and
  the Breeze icons and cursors stay as fallbacks.
- Existing accounts move to HoltOS Glass once at login, and anyone using a
  removed theme, colour scheme or Kvantum theme is moved to the HoltOS one.
- **Five-colour neon palette** in the brand guide and Konsole: purple, teal,
  electric blue, magenta and lime, with amber still meaning "needs you".

## [0.0.7d-alpha] - 2026-09-14

- **Fixed: "Switch to Desktop" in Game Mode stayed on "Switching to Desktop"
  (third fix, the real cause).** Steam never ran HoltOS's switch script: it
  asks SteamOS Manager, a background service on SteamOS, and HoltOS had none,
  so nothing answered. HoltOS now starts its own small stand-in
  (`holtos-steamos-manager`) with Game Mode, and it hands the request to the
  switch. Game Mode also asks Steam to quit cleanly, and closes gamescope, then
  the session, if Steam hangs. Each switch is logged in
  `~/.local/state/holtos/`.

## [0.0.7c-alpha] - 2026-09-14

- **Fixed: "Switch to Desktop" in Game Mode still stayed on "Switching to
  Desktop".** Steam runs `/usr/bin/steamos-session-select`, and HoltOS only
  had the switch in `/usr/local/bin`, so Steam found nothing to run. The
  0.0.7b fix never got a chance to work; it does now. Each switch is also
  written to the journal (`journalctl -t holtos-session-select`).
- **You are told when updates install on their own.** The tray shows
  "HoltOS updated" with what was installed (or that an update did not
  finish), including updates installed in Game Mode or while you were logged
  out, which are announced at your next login.

## [0.0.7b-alpha] - 2026-09-14

Game Mode fixes found on the Z13.

- **Fixed: "Switch to Desktop" in Game Mode did not return to the desktop.**
  Game Mode cleared the switch as it closed, so you landed on the login
  screen, or back in Game Mode with "Start in Game Mode" on.
- **Fixed: Steam's system info in Game Mode called the OS "Arch Linux".**
  Arch's `/usr/lib/os-release` and `/etc/lsb-release` now carry the HoltOS
  name and version too, on new installs and through the updater.
- **Fixed: Chinese, Japanese and Korean text showed as empty boxes**, for
  example in Steam's language list in Game Mode. HoltOS now installs the Noto
  CJK fonts, and the updater adds them to existing systems.

## [0.0.7a-alpha] - 2026-09-14

- **Fixed: the glass flickered and showed a line when a window crossed a
  screen edge** (new holtos-kwin build). The 0.0.7 edge fix resized the blur
  textures on every frame while a window moved across an edge. Their size
  now changes only in steps, and the blur mirrors at the edge instead of
  repeating the last row of pixels.
- **Clearer glass:** windows and title bars use a 15 % tint (was 30 %) with
  less blur (strength 8, was 15), so you can make out what is under a window.
  File lists no longer add a darker layer of their own.
- **Fixed: the title bar was darker than the window below it** at the same
  setting; its opacity is now tuned to match (12 %). Existing accounts get the
  new title bar at their next login.
- **Title bar buttons are plain coloured circles**, with no close, minimise or
  maximise glyphs at rest, on hover or on press. Existing accounts get the
  change from `holtos-glass-user-update` at their next login.

## [0.0.7-alpha] - 2026-09-14

- **Every window is one even pane of glass**, matched to Liam's reference
  screenshot: the title bar, toolbar, Places sidebar, tabs, file view and
  status bar share one 30 % tint over the blurred wallpaper. No line under
  the title bar, a regular-weight title, flat toolbar buttons and tabs, a
  faint light window outline, and less grain in the blur.
- **Selection, hover and tabs are translucent HoltOS purple.**
- **Title bar buttons are coloured circles** in HoltOS's warning, neutral and
  healthy colours, with a glow that spreads onto the glass around the hovered
  button.
- **Dolphin shows the full-width status bar with the zoom slider.** The small
  floating one was drawn as an opaque box with truncated text.
- **Fixed: the glass title bar never appeared on accounts made by older
  images.** Their per-account defaults named the removed Klassy decoration,
  so KWin fell back to Breeze. A one-time step at login
  (`holtos-glass-user-update`) repairs that and brings older accounts' title
  bar, blur and colour settings in line (the old `klassyrc` is kept as
  `klassyrc.before-glass-look`). Log out and back in once after updating to
  see the new title bar.
- **HoltOS's KWin and Plasma builds now update through the package
  repository.** Systems installed from images that still run stock KWin
  switch to holtos-kwin and holtos-plasma-workspace at their next system
  update.
- **Fixed: blur near screen edges (holtos-kwin 6.7.5.r134).** A window dragged
  partly off the screen or across a monitor seam could show a see-through or
  smeared band: KWin sized its blur textures from the whole window but only
  filled the part on the output. The textures now cover only the visible
  part. The test VM never showed the band, so this still needs confirming on
  real hardware (LIVETEST.md).
- HoltOS package builds use every CPU thread (holtos-kwin went from over 40
  minutes to about 4).
- **Ten neon HoltOS wallpapers** (Rings, Otter, Aurora, Den, Bokeh, Otter
  Night, Rain, Forest, Nebula, Cabin), each at 1920x1080, 2560x1440 and
  3840x2160, made to show off the Glass blur.
- **Neon Otter Night is the default wallpaper** on the desktop, lock screen,
  login screen and boot menu.
- **Only HoltOS wallpapers are installed.** pacman no longer unpacks other
  packages' wallpapers (KDE's extra set, Breeze's "Next"), existing copies are
  removed, and the updater copies every HoltOS wallpaper set.
- Wallpaper pipeline tools in `tools/wallpapers/` (render, QA, glass preview,
  packaging) for making more.
- **Fixed**: hardware detection recognises AMD APU graphics that report PCI
  class 0380 (such as the Radeon 8060S in Strix Halo machines), so
  `hardware.log` lists the GPU and its VA-API and Vulkan details. Applies to
  new installs.

## [0.0.6d-alpha] - 2026-09-13

- **ROG Flow Z13 controls work in Game Mode.** z13ctl and z13gui are started
  by the desktop's graphical-session.target, which the gamescope session
  never reaches, so they only ran in Plasma. gamescope now starts
  `holtos-gamemode-client`, which passes gamescope's `DISPLAY` and
  `GAMESCOPE_WAYLAND_DISPLAY` to z13gui (`$XDG_RUNTIME_DIR/gamescope-environment`,
  where it looks for them), starts z13ctl and z13gui, then runs Steam as
  before. Leaving Game Mode stops the Game Mode copy of z13gui, so the
  desktop starts it again in its desktop mode.

## [0.0.6c-alpha] - 2026-09-13

- **HoltOS updates deliver new files, not just changes to existing ones.**
  The config update's list of HoltOS files used unquoted patterns such as
  `usr/local/bin/holtos-*`, which bash expanded in the updater's own working
  directory instead of the downloaded release. Run as a service that is `/`,
  so the patterns matched what was already installed, and anything new in a
  release was never copied: on a ROG Flow Z13 updated to 0.0.6b-alpha,
  `holtos-system-extras` and `holtos-apps` were missing, so z13ctl and z13gui
  never installed. New units, polkit rules and udev rules were skipped the
  same way. The patterns now expand only inside the release. Installs
  get the fix on this update (the updater hands over to the new copy before
  it copies files), and the missing scripts and components install in the
  same run.

## [0.0.6b-alpha] - 2026-09-13

- **HoltOS config updates no longer end "Failed" when they succeeded.** When
  a release ships a new updater, the running one hands over with
  `holtos-update-apply config <tag>`, and the new one read the tag as a
  second, unknown item: the files installed, but the run exited 1 and the
  Updates window and tray reported a failure (seen on 0.0.6a-alpha, reported
  from The Den session). It also never used the tag it was handed and
  looked up the latest release again, which could apply the wrong one if a
  new release was tagged mid-update. A tag right after `config` is now that
  item's target; a plain `config` still installs the latest release.

## [0.0.6a-alpha] - 2026-09-13

- **Updating to a release installs what it needs straight away.** A config
  update now finishes with `holtos-system-extras apply`, so a release's
  required packages and hardware extras install in the same run. With
  0.0.6-alpha, a ROG Flow Z13 had the Z13 switch on but no z13ctl or z13gui
  until "HoltOS components" was installed separately or a system update
  ran. Installs on 0.0.6-alpha get the fix on this update: the updater hands
  over to the new copy of itself, which installs them.

## [0.0.6-alpha] - 2026-09-13

- **On-screen keyboard.** KDE's `plasma-keyboard` is in the image and KWin
  uses it as its input method, so it appears for touch input on tablets and
  2-in-1s; toggle it in System Settings > Keyboard > Virtual Keyboard.
  Installed systems get the package through HoltOS Updates ("HoltOS
  components") and the setting through the config update.
- **ASUS ROG Flow Z13 (2025) controls.** On a GZ302 machine, HoltOS Updates
  installs z13ctl and z13gui (RGB lighting, performance profiles, fan
  curves, TDP, battery limit; z13gui opens from the Armoury Crate button),
  runs `z13ctl setup`, enables their user services and adds users to the
  `users` group. Other machines never get them. Both are in the HoltOS
  package repository now.
- **AppImages start**: `fuse2` is in the image and on the required-packages
  list.
- **The HoltOS package repository never publishes the KWin and
  plasma-workspace forks** (`tools/publish-packages.sh` EXCLUDE): they
  replace the stock packages and have only run in the VM, so installed
  systems keep stock KWin; the forks stay in ISO builds.

## [0.0.5b-alpha] - 2026-09-13

- **The updater installs the packages a HoltOS release needs.** A config
  update only syncs HoltOS' own files, so installs updated to 0.0.5a-alpha
  got the new updater and HoltOS Apps without pacman-contrib, fakeroot,
  fwupd, Flatpak or libcec. The new `holtos-system-extras` installs whatever
  on the release's `required-packages` list is missing (as a full
  `pacman -Syu --needed`, never a partial upgrade). HoltOS Updates lists it
  as "HoltOS components", and every system update runs it at the end.
- **Hardware-specific extras**: the same tool installs extras only on
  matching hardware. The first, for the 2025 ASUS ROG Flow Z13 (z13ctl and
  z13gui), is switched off in this release.

## [0.0.5a-alpha] - 2026-09-13

The "a" marks a release made mainly of big fixes.

- **Network Shares no longer freezes, and connects to servers on any SMB
  version.** Saving, testing, mounting and unmounting now run in the
  background with a status line, so a slow or unreachable server cannot
  lock the window. SMB shares get a version setting (Automatic, 3.1.1, 3.0,
  2.1, 2.0, 1.0): Automatic tries each version newest first, 10 seconds
  each, and saves the one the server accepts into the share's mount
  options. Without it the kernel only offered SMB 2.1 to 3.1.1, so older
  NAS boxes failed or hung. Test connection shows which version connected
  and why the others did not.
- **Updating The Den no longer reports a false failure when its port
  changes.** The updater checked only `127.0.0.1:8686` after restarting The
  Den, so a server moved to its configured port (The Den M34 uses
  `WEB_HOST`/`WEB_PORT`, default 40204) was reported as "did not come back"
  and logged as failed. It now reads `WEB_HOST` and `WEB_PORT` from
  `/etc/the-den/the-den.env` (port 8686 when unset, as in releases up to
  v0.7.0), checks `/health` over http and then https (ready for M35's TLS),
  and rewrites The Den's menu entry with that address on every update
  instead of only on first install.
- **HoltOS Apps, an app store over Flathub** (plan 2.1). A curated front
  page of 27 apps picked for a media and gaming machine (Jellyfin, Plex,
  Kodi, Stremio, VLC, Spotify, Heroic, Lutris, ProtonUp-Qt, Moonlight,
  RetroArch, OBS, Discord, browsers and more), search across all of
  Flathub, and an Installed tab, each app with Install, Open and Remove.
  Installs are system-wide with no password for the active admin (Flatpak's
  own polkit rule), Flathub is set up out of the box, and app updates arrive
  through HoltOS Updates. Tray entry "HoltOS Apps...".
- **Performance and controller defaults** (plan 1.3/1.4): an I/O scheduler
  per disk type (BFQ for hard disks, mq-deadline for SATA SSDs, kyber for
  NVMe, from CachyOS) and `libcec` for TV remotes over HDMI-CEC. zram,
  gamemode and Arch's own `vm.max_map_count` already covered the rest.
- **Updates work like Windows Update** (Liam, 2026-09-13). HoltOS checks on
  its own (a root timer, every 6 hours by default, and each time Game Mode
  exits) and the new **HoltOS Updates** window shows what it is doing:
  "Checking for updates..." with what it looks at, "You're up to date, last
  checked today at 15:58", or each available update with its installed and
  new version, release notes, and live progress (Downloading 42% ->
  Installing -> Installed / Failed), plus a restart banner, the update
  history, and settings: how often to check, automatic download, automatic
  install (off / HoltOS and apps / everything), an install window for system
  updates, and whether to check after Game Mode. The tray only reads the
  result and notifies. Covers HoltOS itself, The Den and The Den Client,
  every Arch package (kernel, firmware, drivers; the Arch keyring is
  refreshed first), Flatpak apps and runtimes, and device firmware through
  fwupd.
- **Updates no longer reinstall what is already installed**: the updater
  compares the installed commit or release tag and skips current items
  (`--reinstall` forces it). Before, picking an item always re-downloaded
  and reinstalled the latest release.
- **Game Mode's Steam > System > Software Updates page installs HoltOS
  updates**: HoltOS ships the `steamos-update` hook Steam calls (check exits
  0/7, install reports a percentage), behind a polkit action that lets only
  the active local admin run it without a prompt.
- **Fixed**: the restart prompt could miss kernel and core upgrades on
  machines not set to UTC (it compared a UTC time with pacman.log's local
  time), and `holtos-*.timer` units never reached installed systems through
  the updater (only `.service` units were synced).

- **HoltOS's own KWin and plasma-workspace reach a working desktop**
  (fork plan Milestone 2). The first builds crashed at login: their
  `replaces=` drops the stock packages, and with them a dozen runtime
  dependencies the hand-written `depends=()` lists never named
  (`plasma-integration`, without which Qt's fallback KDE theme segfaults
  KWin, plus `kactivitymanagerd`, `kglobalacceld`, `milou`, `qt6-tools`
  and more). Both packages now carry Arch's full dependency lists; KWin
  is built with global shortcuts again.
- **Glass blur now comes from HoltOS's KWin itself** (Milestone 3): the
  image enables KWin's in-tree blur with the HoltOS additions and the
  Glass v2 tuning (strength 15, noise 4, no tint); Kvantum's window and
  dialog fills drop to 40% / 55% so the blurred wallpaper shows through.
  The separate `holtosglass` effect ships disabled until this is
  confirmed on a fresh install.
- **Title bars use the HoltOS Glass decoration again**: the look-and-feel
  still named Klassy, which the image does not ship, so KWin fell back
  to Breeze.
- **Gaming page** labels line up; the session-switch cleanup no longer
  shows as a failed unit after every normal login.

- **Restart prompt after system-package updates** (Liam, 2026-09-12).
  `holtos-update-apply system` now writes `/run/holtos-reboot-required`
  (with a reason) when the running kernel's module directory is gone or
  pacman upgraded a core package (kernel, firmware, systemd, mesa,
  microcode, NVIDIA, PipeWire, KWin, SDDM, Plasma), and prints a
  restart-required line; `holtos-update-picker` then ends with "Restart
  now / Later". "Later" leaves the marker; it clears itself on reboot.
  Picker drafted by the 4090's model; updater edit by hand after three
  handoffs timed out (the model rewrites the whole 600-line file).
  Verified on screen in the VM.

## [0.0.4-alpha] - 2026-09-12

Game Mode release. Built and verified in the Hyper-V VM (builds 18-20);
the gamescope screen itself needs a real GPU, so that check is Liam's on
the Strix Halo box.

- **Updater hands over to the release's own copy of itself** when the
  tarball ships a different `holtos-update-apply`, so whitelist additions
  reach older installs from the next release on. (An installed 0.0.3-alpha
  still needs the one-liner in the release notes first: its list lacks the
  Game Mode files.) Scripts under `usr/local/bin` are now committed with
  the executable bit so the release tarball carries it. Drafted by the
  local model.

- **Game Mode** (plan 1.2; Liam: "gamescope and an option to boot right
  into it and switch seamlessly back and forth"). A second SDDM session
  "HoltOS Game Mode" (`holtos-gamemode-session`: gamescope's own
  compositor running Steam Big Picture, HDR/VRR/resolution overridable
  in `/etc/holtos/gamemode.conf`). Switching is SteamOS-style:
  `steamos-session-select` (the name Steam's "Switch to Desktop" button
  calls) records the next session with `holtos-session-apply` and ends
  the current one; SDDM's Relogin autologin then starts the other. The
  "Game Mode" app-menu entry and tray "Game Mode now" go Plasma ->
  Game Mode; Steam's power menu goes back. Tray "Start in Game Mode"
  makes it the default at boot. A polkit rule lets the active local user
  run the apply helper without a password (a controller user has no
  keyboard); the helper refuses to act for another account and only
  writes an autologin file while a switch or the Game Mode default needs
  one. The Den is untouched by all of this — it is a system service.
  Drafted by the local model: session script, both desktop entries,
  the tray toggle; by hand (security-relevant): the apply helper and
  polkit rule, plus the selector after two failed handoffs.
- **Gaming base** (docs/holtos-must-haves-and-plan.md 1.1/1.4; Liam:
  "Steam preinstalled along with Proton + Proton GE"). `[multilib]`
  enabled for the build and the installed system (and by the config
  update on older installs); `steam`, `gamescope`, `gamemode`,
  `mangohud` (+ lib32), `vulkan-icd-loader` (+ lib32), `lib32-vulkan-radeon`,
  `lib32-vulkan-intel`, `lib32-mesa` in the image; `lib32-nvidia-utils`
  staged with the NVIDIA driver and installed on the NVIDIA path. Proton
  comes with Steam; **Proton GE** is fetched per user from GloriousEggroll's
  GitHub releases by `holtos-proton-ge` (sha512-verified, keeps the last
  two), installed once at first login by an autostart helper and updated
  from the tray ("Update Proton GE"). `zram-generator` with half of RAM as
  zstd-compressed swap.
- **Network Shares** (Liam, 2026-09-12: "make it simple to mount a share,
  NFS/Samba, and have it automount, with an easy GUI"). New
  `holtos-shares` (PySide6 window: list with mounted state, Add / Edit /
  Remove / Mount / Unmount / Open, connection test) over `holtos-share`
  (root backend via pkexec): each share is `/etc/holtos/shares/<name>.conf`
  plus a root-only credentials file for SMB, from which it writes a
  systemd `.mount` + `.automount` pair — mounts on first access under
  `/mnt/shares/<name>`, tolerates the network coming up late, never blocks
  boot; SMB files are owned by the desktop user. In the app menu
  ("Network Shares") and the tray. `cifs-utils` and `nfs-utils` added.
  Verified in the VM against local Samba and NFS servers: test, add,
  automount on access, write, unmount, remove, and the GUI on screen.
- **Updater: The Den Client launcher, .desktop and icons refresh on every
  update.** They were installed only on first install, so icon and
  desktop-file fixes in new client releases never reached an updated
  system (found 2026-09-12 checking the client's window icon on Plasma
  Wayland). The icon now lands in hicolor scalable, hicolor 64x64 and
  pixmaps like the client's PKGBUILD, from `src/assets/` or the older
  `assets/`; icon cache and desktop database are refreshed. Drafted by
  the local model. Verified in the VM: an in-place v0.4.4 update
  replaced the image-build placeholder icon and created the missing files.
- **Login screen session picker.** The HoltOS greeter now shows "Session"
  chips (Plasma / HoltOS Game Mode) whenever more than one session is
  installed, preselecting SDDM's remembered last session. Drafted by the
  local model; verified on screen in the VM.
- **Installed systems no longer show the live medium's motd** ("Double-click
  Install HoltOS..."); the Calamares cleanup step writes a one-line
  welcome instead. Written by hand after two failed handoffs (the model
  garbled the ANSI escape).
- **Live medium: no more "Disks & Devices" popup over the installer.** A
  udev rule marks the boot ISO and archiso EFI partition UDISKS_IGNORE on
  the live medium; the Calamares cleanup step drops the rule on installs.
  Drafted by the local model.
- **chromium in the image**: The Den v0.5.1 depends on it (its built-in
  Cloudflare solver for public trackers); build 18 vendors The Den v0.5.1
  and The Den Client v0.4.4.
- **Game Mode failure no longer leaves a black screen.** SDDM only
  recreates the display when the session helper exits successfully, so a
  gamescope that died at startup (no GPU in the VM) left the login screen
  black (build 18). The session script now always exits 0 and, when
  gamescope dies within 15 s of starting, asks for a one-shot relogin
  straight back into Plasma, and a Plasma autostart entry
  (`holtos-session-next-done.desktop`) clears the one-shot once the
  desktop is up so the login screen behaves normally afterwards. Verified
  in the VM: Game Mode fails, the desktop is back in seconds, no autologin
  file is left behind. Also: fresh installs seed SDDM's remembered
  session with Plasma so the login screen does not default to Game Mode
  (build 18 picked it because it sorts first). Both written by hand: the
  local model reported DONE twice without writing the file, and returned
  a bare `return 0` at script level for the seed snippet.
- **README credits** everything HoltOS forks or ships, and notes that
  HoltOS was built with help from AI (Claude Fable 5.1 via Claude Code).

## [0.0.3-alpha] - 2026-09-12

Same day as 0.0.2-alpha. Everything below was built and verified in the
Hyper-V VM during the afternoon; this is the first release the updater
can deliver whole to an existing install.

- **Every HoltOS component updates from HoltOS' own sources** (Liam,
  2026-09-12: "we shouldn't be updating from any Arch sources but our
  own"). The config update used to copy only the `homelab-*.sh` install
  scripts; it now syncs a whitelist of everything HoltOS owns on an
  installed system from the release tarball — the `holtos-*` tools,
  `holtos-*.service` units (new ones enabled), autostart entries,
  `kwinrc`/About/splash defaults, `os-release`, the pacman hook, the SDDM
  and Plymouth themes, Kvantum theme, colour scheme, icons, look-and-feel,
  wallpapers, skel — then re-themes Limine, rescans other OSes and
  regenerates the snapshot submenu. The Limine font is committed to the
  repo pre-converted (`tools/convert-limine-font.sh`) instead of being
  built from the `terminus-font` Arch package, and the theming moved to
  `homelab-limine-theme.sh` so it can be reapplied. HoltOS-built packages
  (glass forks, Calamares, Limine tools, ZFS) are published as a pacman
  repository on the GitHub release tagged `packages`
  (`tools/publish-packages.sh`); `[homelab]` in pacman.conf lists it after
  the build-time file:// server, and the config update adds it to older
  installs, so `pacman -Syu` picks up new fork builds from HoltOS.
- **Hardware log for AMD/Intel GPUs**: detection now records the GPU and
  what VA-API (`vainfo`) and Vulkan (`vulkaninfo`) report, for the Strix
  Halo test; `libva-utils` and `vulkan-tools` added.
- **The boot menu looks like HoltOS now** (Liam: "make Limine more
  modern"). Limine 12's theming keys, all set by
  `homelab-limine-install.sh`: `interface_branding` shows "HoltOS
  <version>" instead of "Limine 12.9.0", help/countdown/selection in the
  HoltOS palette, Terminus Bold 12x24 as the menu font (`terminus-font`
  added; `customize_airootfs.sh` strips the PSF2 header into the raw
  bitmap Limine wants, installed to the ESP as `/holtos/ter-124b.bin`),
  the menu drawn in a translucent ink panel with a soft gradient margin
  over the wallpaper, and a `comment` line per entry. Snapshots move into
  a collapsed "Snapshots" submenu (newest first, labelled by what they
  were taken before) so Windows and other systems sit directly under
  HoltOS. Prototyped on screen in the VM before being wired in.
- **Other operating systems appear in the Limine menu** (Liam,
  2026-09-12: "it should auto detect them, Windows etc"). Limine has no
  os-prober, but every UEFI-installed OS leaves its loader on an EFI
  System Partition, and Limine can chainload EFI applications. New
  `holtos-limine-other-os` scans every ESP on every disk (mounting
  foreign ones read-only) for `EFI/Microsoft/Boot/bootmgfw.efi`
  (Windows), `EFI/<distro>/shimx64.efi|grubx64.efi` (Ubuntu, Fedora,
  CachyOS, ...), `EFI/systemd/systemd-bootx64.efi`, and, on foreign ESPs
  only, the generic `EFI/BOOT/BOOTX64.EFI`, and writes one
  `protocol: efi` entry per find between the new HOLTOS OTHER OS markers
  in both `limine.conf` copies — `boot():` paths for loaders on our own
  ESP (a Windows sharing the disk), `guid(<partition GUID>):` for other
  disks. The menu timeout goes to 5 s when there is a choice. Runs at
  install time (from `homelab-limine-install.sh`), after every kernel
  update (`homelab-limine-sync.sh`), and from the tray's new "Rescan
  Boot Menu". Configs written before this get the markers added.
- **Snapshots can be restored — a real rollback** (PLAN.md step 0's last
  open decision, Liam 2026-09-12). New `holtos-btrfs-restore <name>`
  (root) makes a retained read-only snapshot the system: it first keeps
  the current root as a `<ts>-pre-restore` snapshot (ESP kernel copy +
  Limine entry, subject to the usual 5-snapshot retention), renames `@`
  to `@.old-<ts>`, creates a writable `@` from the snapshot, restores
  that snapshot's kernel/initramfs as the ESP's main boot files, carries
  the current `snapshots.log` / `history.log` / `kernel-cmdline-extra`
  into the new root (the snapshot's own copies are frozen at its time),
  regenerates the Limine menu, and logs a `restore` line. The replaced
  root is deleted by the new boot-time
  `holtos-btrfs-restore-cleanup.service`. Works from the live `@` or
  from a booted snapshot (`--current`) because it operates on the Btrfs
  top level (subvolid=5) it mounts itself. Only `@` is restored; `@home`,
  `@log`, `@cache` stay. UI: tray "Restore Snapshot..." (list, confirm,
  progress, reboot offer) and a login-time notice when the session is a
  booted snapshot, offering to restore it. `holtos-btrfs-snapshot` gained
  `--regen` (retention + Limine rewrite only) and `SNAP_LOG` /
  `SNAPSHOTS_DIR` overrides for that. README updated. Verified on the
  build 10 VM (restore back, restore forward, cleanup on reboot) and on a
  fresh build 14 install through the tray dialogs and the snapshot-boot
  notice (KDE polkit prompt). Two real bugs found on the way: the merge
  aborted when the very first snapshot had no `snapshots.log` inside it
  (pipefail + missing file) — now merges whatever exists, including the
  running system's own log, and reconciles the log with the subvolumes
  that actually exist; and the replaced root must never be deleted while
  it is the running root (btrfs will do it and take the session down) —
  it is renamed and removed on the next boot instead.

## [0.0.2-alpha] - 2026-09-12

First release carrying the 2026-09-11/12 work: the container stack is
gone, The Den ships in the image, HoltOS Glass is HoltOS-owned code,
hardware detection at install, and the full set of System Settings
pages. Verified on two fresh Erase-Disk installs in the Hyper-V VM
(builds 9 and 10, 2026-09-12); real-hardware NVIDIA path still pending.

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
- **System Settings > Display existed only as an error.** Real bug behind
  "the settings pane doesn't show any resolution options": the image
  installs `plasma-desktop` plus hand-picked packages, and the Display
  Configuration page lives in `kscreen`, which was never listed —
  System Settings > Display opened to "Could not find plugin
  kcm_kscreen" (build 9 install, 2026-09-12; `libkscreen` and
  `kscreen-doctor` were present, so the compositor side was fine and the
  VM's `hyperv_drm` output lists 24 modes). Added `kscreen`, and the other
  pages a Plasma desktop is expected to have that were missing for the
  same reason: `plasma-pa` (volume applet + Audio page; also
  `pipewire-pulse`/`pipewire-alsa`, without which no app had a sound
  server), `bluedevil` + `bluez`/`bluez-utils` (Bluetooth, service
  enabled), `kde-gtk-config`, `plasma-disks` (SMART health), `sddm-kcm`,
  `kwallet-pam`, `krdp` (Remote Desktop page). HDR / VRR / refresh-rate
  entries on that page appear only when the DRM driver reports them —
  `hyperv_drm` reports none, NVIDIA needs the driver from PLAN step 7
  (and `KWIN_DRM_ALLOW_NVIDIA_COLORSPACE=1` for the HDR toggle on Plasma
  6.2+), AMD/Intel get them from Mesa/amdgpu/i915 already in the image.
- **Live session no longer locks itself.** The installer finished behind
  the Plasma lock screen during the build 9 VM test; a USB install would
  hit the same after 5 idle minutes with a password (liveuser) nobody is
  told. `Autolock=false` in liveuser's `kscreenlockerrc` only — the
  installed system keeps the normal locker.
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
    container on `set -euo pipefail` (`pipefail
: invalid option name`),
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
