# Liam's hand-off: testing 0.0.6d-alpha on the ROG Flow Z13

What this release changes and how to check it on Liamtab.

## 1. Update

1. Open HoltOS Updates and install `v0.0.6d-alpha` (click Check for updates
   first if it is not listed).
2. Confirm the version and the new Game Mode launcher arrived:

       grep VERSION_ID /etc/os-release
       ls -l /usr/local/bin/holtos-gamemode-client

   Expect `VERSION_ID="0.0.6d-alpha"` and an executable file.

## 2. Z13 controls in Game Mode (new in this release)

Before: z13ctl and z13gui only started in the Plasma desktop.
Now: Game Mode starts them once gamescope is up, and stops the Game Mode copy
of z13gui when you switch back to the desktop.

1. Switch to Game Mode (app menu > Game Mode, or tray > Game Mode now).
2. Press the Armoury Crate button. The z13gui drawer should slide out over
   Steam and respond to the D-pad and buttons.
3. From a terminal (SSH from another machine, or Ctrl+Alt+F3), check:

       export XDG_RUNTIME_DIR=/run/user/$(id -u)
       systemctl --user status z13gui.service --no-pager | grep Active
       cat "$XDG_RUNTIME_DIR/gamescope-environment"

   Expect `active (running)`, and two lines: `DISPLAY=:...` and
   `GAMESCOPE_WAYLAND_DISPLAY=gamescope-...`.
4. Switch to Desktop from Steam's power menu. In Plasma, press the Armoury
   Crate button again: the drawer should open on the desktop as before.

If the drawer does not open in Game Mode, send these:

    export XDG_RUNTIME_DIR=/run/user/$(id -u)
    systemctl --user status z13gui.service z13ctl.service --no-pager
    journalctl --user -b -u z13gui --no-pager | tail -30
    cat "$XDG_RUNTIME_DIR/holtos-gamemode.log"

## 3. The Den server (checked, working)

Checked on Liamtab on 2026-09-14 at about 02:50: `the-den` is active and
enabled, listens on `127.0.0.1:8686` and answers `/health` with 200. The
`the-den v0.8.0a (FAILED to start)` line in the update history at 21:15 UTC was a
false failure or cleared itself by the next boot; that boot's journal is gone,
so the cause can't be checked. The Den is a system service, so it should also
answer in Game Mode. If it ever stops answering, send:

    systemctl is-active the-den; journalctl -u the-den -n 20 --no-pager

## 4. Network Shares (fixed)

The `plex` share works now (2026-09-14). The problem was on the NAS, so
HoltOS needed no change. If a share fails again, the diagnostic still works:

    sudo /usr/local/bin/holtos-share test smb YOUR-SERVER plex 2>&1 | tail -15

## 4a. Next release (0.0.7): neon wallpapers

Built, not released yet. After it ships and you update:
- Settings > Wallpaper lists only HoltOS wallpapers, including the ten neon ones.
- A fresh install uses **Neon Otter Night** on the desktop, lock screen, login
  screen and boot menu. An existing install keeps its current desktop
  wallpaper (pick Otter Night in Settings); the boot menu switches after the
  update.

## 5. Virtual keyboard research (decision needed)

- plasma-keyboard (shipped now): KDE's own, pops up on text fields, Plasma
  6.7 adds press-and-hold for special characters. No Ctrl, Alt or Super keys.
- Vboard (AUR, GPLv3, Python and GTK): works on Plasma Wayland, has
  Ctrl/Alt/Super and arrow keys, opened from the tray (no pop-up). US QWERTY
  only (layouts are editable JSON), no F-keys or Home/End/Page keys, large at
  low resolutions. Types through /dev/uinput, so the permission must go only
  to the logged-in user.
- Maliit: AUR only, clashes with fcitx, replaced in KDE by plasma-keyboard.
- Squeekboard (Phosh only), wvkbd (Sway/Hyprland style desktops), Onboard
  (X11 only): not suitable.

Recommendation: keep plasma-keyboard for pop-up typing and add Vboard as a
tray "full keyboard", built into our package repo, in the next feature
release. Waiting on Liam's go-ahead.

## 5a. Glass design: what needs you (from the 2026-09-14 night shift)

The plan is `docs/holtos-glass-design-plan.md`. Tonight's work is committed
and pushed (HoltOS master, holtos-kwin branch `edge-blur-fix`), with no tag,
so the updater installs nothing from it.

1. **Build tools: done** (installed 2026-09-14). Both test builds compiled on
   Liamtab.
2. **Before installing, see the edge bug.** Drag a Dolphin window half off
   the left edge over a bright wallpaper: expect a see-through or smeared
   band along the edge.
3. **Install both test packages** (the edge fix and the glass buttons with
   the hover glow). Save your work first: this replaces KWin.

       sudo pacman -U ~/Projects/scratch/kwin-pkg/holtos-kwin-6.7.5.r90-1-x86_64.pkg.tar.zst ~/Projects/scratch/deco-pkg/holtos-window-decoration-6.7.2.r55-1-x86_64.pkg.tar.zst

   Your own decoration settings live in `~/.config/klassy/klassyrc`, which
   new installs copy from the image. To get the new buttons, back yours up
   and copy the new one:

       cp ~/.config/klassy/klassyrc ~/.config/klassy/klassyrc.bak
       cp /mnt/shares/projects/holtos-glass-buttons/archiso/airootfs/etc/skel/.config/klassy/klassyrc ~/.config/klassy/klassyrc

   Then log out and back in.
4. **Check.** Repeat the Dolphin drag: the band should be gone, also at a
   monitor seam. The title bar buttons are red, yellow and green circles on
   the right, and hovering one lights the glass around it in its colour. The
   fixed klassyrc also turns on settings the old file never applied (title
   centred across the bar, the poor-contrast guard, large shadows), so say
   if anything looks off.
5. **If something breaks**, go back to the current packages:

       sudo pacman -U /mnt/shares/projects/holtos/local-repo/holtos-kwin-6.7.5.r89-1-x86_64.pkg.tar.zst /mnt/shares/projects/holtos/local-repo/holtos-window-decoration-6.7.2.r54-1-x86_64.pkg.tar.zst
       cp ~/.config/klassy/klassyrc.bak ~/.config/klassy/klassyrc
4. **Plasma theme.** `etc/xdg/plasmarc` names `klassy-dark`, but your desktop
   uses `default`. Which should HoltOS ship until it has its own glass theme?

## 6. Already verified on Liamtab

- 0.0.6c-alpha: the updater copies files that are new in a release
  (holtos-system-extras and holtos-apps arrived).
- z13ctl-bin 1.3.2, z13gui-bin 1.4.1, plasma-keyboard and fuse2 installed;
  z13ctl and z13gui run in Plasma.
