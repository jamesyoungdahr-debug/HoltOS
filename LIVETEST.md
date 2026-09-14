# HoltOS live test checklist

What still needs checking on real hardware after v0.0.7-alpha (2026-09-14).
Everything here was either only tested in the Hyper-V test VM or never tested.
Tick items off, and send Claude the output for anything that fails.

Machines: **Z13** = Liamtab (ROG Flow Z13, Radeon 8060S). **4090** = LiamPC's
HoltOS install (RTX 4090). Checks that need a reboot or a boot-menu choice on
LiamPC are for Liam to do in person.

Do section 1 first; most of the rest depends on it.

## 0.0.7c-alpha: Switch to Desktop and update notices (Z13 first, then 4090)

- [ ] Update to `v0.0.7c-alpha` (it may install on its own), then restart.
  Expect: `grep VERSION_ID /etc/os-release` shows `0.0.7c-alpha`, and after
  logging in to the desktop the tray shows **HoltOS updated** naming
  HoltOS v0.0.7c-alpha.
- [ ] `ls -l /usr/bin/steamos-session-select` exists and is executable.
- [ ] Game Mode > Power > **Switch to Desktop** returns to Plasma, still
  logged in. If it does not, send Claude the output of
  `journalctl -b -t holtos-session-select -t holtos-gamemode --no-pager`
  and `cat /etc/holtos/session.conf; ls /etc/sddm.conf.d/`.

## 0.0.7b-alpha: Game Mode fixes (Z13 first, then 4090)

- [ ] HoltOS Updates > Check for updates, install `v0.0.7b-alpha`. Expect:
  `grep VERSION_ID /etc/os-release` shows `0.0.7b-alpha`.
- [ ] Game Mode > Steam's power menu > **Switch to Desktop** returns to
  Plasma, still logged in. Try it once with Tray > Start in Game Mode on as
  well: it still returns to Plasma, and the next restart boots into Game
  Mode.
- [ ] Game Mode > Settings > System: the OS name is **HoltOS**, not Arch
  Linux. On the desktop, `lsb_release -d` and `head -n 1 /usr/lib/os-release`
  both say HoltOS.
- [ ] Game Mode > Settings > System > Language: Chinese, Japanese and Korean
  show their names, not empty boxes. `pacman -Q noto-fonts-cjk` prints a
  version.

## 1. Update to 0.0.7-alpha (Z13, 4090)

- [ ] HoltOS Updates > Check for updates, install `v0.0.7-alpha`, then also
  install **System packages**. Save your work first, then restart.
  Expect: `grep VERSION_ID /etc/os-release` shows `0.0.7-alpha`, and
  `pacman -Q holtos-kwin holtos-window-decoration holtos-plasma-workspace`
  shows `6.7.5.r134-1`, `6.7.2.r130-1` and `6.7.5.r89-1`. Stock `kwin` and
  `plasma-workspace` are replaced.
- [ ] **4090 only:** the desktop starts on NVIDIA with holtos-kwin. This is
  the first time it reaches that install through an update. If it does not
  start, pick the pre-update snapshot in the Limine menu and tell Claude.
- [ ] The system update shows Downloading % > Installing > Installed, and a
  restart banner appears because KWin was updated. After the restart the
  banner is gone (`ls /run/holtos-reboot-required` reports no such file).
- [ ] Log out and back in once. Expect: `cat ~/.local/state/holtos/glass-user-update-2`
  shows a date, `~/.config/klassy/klassyrc.before-glass-look` exists on
  older accounts, and
  `journalctl --user -b | grep -i 'Could not locate decoration plugin'`
  prints nothing.

## 2. Glass look (Z13, 4090)

- [ ] Dolphin over a bright wallpaper, next to
  `docs/design-references/glass-dolphin-reference.jpg`: one even glass tint
  over the title bar, toolbar, Places sidebar, tabs, files and status bar; no
  line under the title; regular-weight title; a faint light outline.
- [ ] Selection, hover and tabs are translucent purple; toolbar buttons are
  flat.
- [ ] Full-width status bar with the zoom slider; its text is not cut off.
- [ ] Title bar buttons are coloured circles on the right at rest; hovering
  one spreads a glow of its colour onto the glass. Say if the glow should be
  stronger, softer, bigger or smaller.
- [ ] The fixed klassyrc turns on settings that never applied before: centred
  title and large shadows. Check they look right.
- [ ] Inactive windows keep the same tint (click another window).
- [ ] Konsole is translucent with blur behind it.
- [ ] Readability: text over bright parts of the wallpaper stays readable.
  Note where it does not.
- [ ] **Edge blur (0.0.7a):** drag a Dolphin window slowly half off the left
  edge over a bright wallpaper. Expect no see-through or smeared band, no
  flicker while it moves, and no bright or dark line along the edge.
- [ ] **Title bar matches the window (0.0.7a):** after logging out and back
  in, the title bar has the same tint as the toolbar below it.
- [ ] **Clearer glass (0.0.7a):** shapes behind a window are recognisable but
  soft. Say whether the blur (strength 8) should be stronger or weaker.
- [ ] **4090 with two monitors:** drag a window across the seam. Expect no
  band.
- [ ] Performance: move and resize windows and open several at once. It stays
  smooth; the Z13's iGPU matters most.
- [ ] Fullscreen video and a fullscreen game show no blur artifacts or
  slowdown; the lock screen looks right.

If anything looks off, send:

    journalctl --user -b | grep -iE 'kwin|decoration' | tail -30

## 3. Wallpapers and boot menu (Z13, 4090)

- [ ] Settings > Wallpaper lists only HoltOS wallpapers, including the ten
  neon ones; `ls /usr/share/wallpapers` shows only `HoltOS*`.
- [ ] After a restart the Limine boot menu shows Neon Otter Night, its text is
  legible at native resolution, and the Snapshots submenu is collapsed.
- [ ] Wallpapers look sharp full screen (the Z13 panel, a 4K monitor on the
  4090).
- [ ] **4090:** the Windows entry in the Limine menu starts Windows (Liam in
  person).
- [ ] Only when a machine is reinstalled: Otter Night on the desktop, lock
  screen, login screen and boot menu; `/var/lib/holtos/hardware.log` lists
  the GPU (Z13: `c4:00.0 ... [1002:1586]` with vainfo and vulkaninfo
  sections); the USB install completes.

## 4. Game Mode (Z13 first, then 4090)

- [ ] App menu > Game Mode opens Steam Big Picture on gamescope; Steam's power
  menu > Switch to Desktop returns to Plasma, still logged in.
- [ ] Tray > Start in Game Mode, then restart: it boots into Game Mode. Turn
  it off again: it boots to Plasma.
- [ ] **Z13:** in Game Mode the Armoury Crate button opens the z13gui drawer
  and it responds to the D-pad. From SSH or Ctrl+Alt+F3:

      export XDG_RUNTIME_DIR=/run/user/$(id -u)
      systemctl --user status z13gui.service --no-pager | grep Active
      cat "$XDG_RUNTIME_DIR/gamescope-environment"

  Expect `active (running)`, then `DISPLAY=:...` and
  `GAMESCOPE_WAYLAND_DISPLAY=gamescope-...`.
- [ ] **Z13:** back on the desktop, Armoury Crate opens the drawer in Plasma
  again.
- [ ] **Z13:** z13ctl settings (lighting, performance profile, fans, charge
  limit) take effect and survive a restart.
- [ ] A Windows game runs under Proton GE with MangoHud showing; Proton GE is
  in `~/.steam/root/compatibilitytools.d/`; tray > Update Proton GE works.
- [ ] Tray > Gaming... shows package versions and the Proton GE builds.
- [ ] Steam > Settings > System > Software Updates lists and installs a HoltOS
  update in Game Mode with no password prompt.
- [ ] HDR and VRR: with `HOLTOS_GAMEMODE_HDR=on` and `HOLTOS_GAMEMODE_VRR=on`
  in `/etc/holtos/gamemode.conf`, gamescope reports HDR and adaptive sync on
  a capable display.
- [ ] The Den keeps running in Game Mode: `systemctl is-active the-den` shows
  `active`.

If z13gui fails in Game Mode, send:

    systemctl --user status z13gui.service z13ctl.service --no-pager
    journalctl --user -b -u z13gui --no-pager | tail -30
    cat "$XDG_RUNTIME_DIR/holtos-gamemode.log"

## 5. Updater (Z13, 4090)

- [ ] A Flatpak update installs through HoltOS Updates with progress.
- [ ] **Z13** (`AUTO_INSTALL=apps`): an app update installs by itself on the
  6-hour timer (or `sudo systemctl start holtos-update-check.service`),
  History lists it, and no system packages install outside the install
  window.
- [ ] Leaving Game Mode triggers a fresh update check (see the time in HoltOS
  Updates).
- [ ] `fwupdmgr get-devices` lists real devices, and firmware updates appear in
  HoltOS Updates when there are any.
- [ ] Tray: the status icon, the update notification, and every menu entry
  opens.
- [ ] HoltOS Apps: Featured loads, search works on first open, and Install,
  Open and Remove work without a password prompt.

## 6. Display, NVIDIA and video

- [ ] **4090:** `cat /proc/cmdline` has `nvidia_drm.modeset=1`,
  `lsmod | grep nvidia` shows the module, and System Settings > Display shows
  real resolutions and refresh rates.
- [ ] **4090, optional HDR:** add `KWIN_DRM_ALLOW_NVIDIA_COLORSPACE=1` to
  `/etc/environment` and restart (Liam in person). The HDR toggle appears and
  login still works; remove the line if login breaks.
- [ ] **Z13:** the Display page shows HDR and VRR options on a capable
  display.
- [ ] Hardware video: `vainfo` (Z13) or `nvidia-smi` (4090) lists the codecs,
  and a 4K HEVC or AV1 file plays with GPU decoding.

## 7. Disks, snapshots and restore (Z13, 4090)

- [ ] `cat /sys/block/nvme0n1/queue/scheduler` shows `[kyber]`.
- [ ] `sudo systemctl start holtos-scrub.service`: `/var/lib/holtos/scrub.log`
  shows a completed scrub, and the system stays usable while it runs.
- [ ] SMART alert: temporarily add `-M test` to the DEVICESCAN line in
  `/etc/smartd.conf` and run `sudo systemctl restart smartd`.
  `/var/lib/holtos/disk-alert` appears and the "Open Disk Health" notice shows
  at the next login. Remove `-M test` afterwards.
- [ ] Tray > Restore Snapshot..., pick a snapshot, restart: the system is back
  at that state and the old root is cleaned up on the next boot. Booting a
  snapshot from the Limine menu shows the restore notice. (Liam in person on
  LiamPC.)

## 8. Controllers, TV and touch

- [ ] `pacman -Q xpadneo-dkms game-devices-udev` lists both; an Xbox controller
  pairs over Bluetooth with rumble in Steam; `dkms status` shows xpadneo for
  the running kernel, also after a kernel update.
- [ ] Where there is an HDMI-CEC adapter, the TV remote works
  (`cec-client -l` sees the adapter).
- [ ] **Z13:** the on-screen keyboard (plasma-keyboard) pops up in text fields
  in tablet posture, including on the login and lock screens, and
  press-and-hold gives special characters.

## Already verified on real hardware

- The updater copies files that are new in a release (0.0.6c, Liamtab).
- z13ctl and z13gui run in Plasma; plasma-keyboard and fuse2 are installed
  (Liamtab).
- The Den is active and answering, and the Network Shares plex share works
  (Liamtab, 2026-09-14).
- smartd monitors the NVMe, the update timer runs, the scrub timer is
  scheduled, the tray runs, and no units have failed (Liamtab, 2026-09-14).
- Hardware detection's new PCI class 0380 match finds the Radeon 8060S
  (Liamtab).

## Not ready to test yet

Adaptive text contrast (G8/G9), glass in Kirigami apps such as System Settings
(G7), GTK apps (G6), the HoltOS Plasma theme (G5, waiting on Liam's pick of
klassy-dark or default), and the Vboard tray keyboard (waiting on Liam).
