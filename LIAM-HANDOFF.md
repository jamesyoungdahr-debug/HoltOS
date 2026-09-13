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

## 3. The Den server

The Den runs as a system service (`the-den.service`) that starts at boot and
does not depend on Plasma or Game Mode, so it should answer in both. The
update history on Liamtab shows `the-den v0.8.0a (FAILED to start)` at 21:15,
which may have been a false failure.

In Game Mode or on the desktop, check:

    systemctl is-active the-den; systemctl is-enabled the-den
    grep -E "^WEB_(HOST|PORT)=" /etc/the-den/the-den.env
    journalctl -u the-den -n 20 --no-pager

Expect `active` and `enabled`. If it is not active, send the journal lines.

## 4. Network Shares still will not mount (open)

Reported after 0.0.6d: the `plex` share will not connect or mount. The image
already ships `cifs-utils` and `nfs-utils`, so the next step is the test
output. Replace `YOUR-SERVER` with the server's IP address or name.

Check the mount tools are installed:

    pacman -Q cifs-utils nfs-utils smbclient; ls /usr/bin/mount.cifs

Share with no login:

    sudo /usr/local/bin/holtos-share test smb YOUR-SERVER plex 2>&1 | tail -15

Share with a username and password (the test reads the password from input):

    sudo -v
    read -rsp 'Share password: ' P; echo
    printf '%s' "$P" | sudo /usr/local/bin/holtos-share test smb YOUR-SERVER plex YOUR-USERNAME 2>&1 | tail -15; unset P

The test tries SMB 3.1.1, 3.0, 2.1, 2.0 and 1.0 in turn and prints
`==> OK over SMB ...` or the error for each. Send the whole output.

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

## 6. Already verified on Liamtab

- 0.0.6c-alpha: the updater copies files that are new in a release
  (holtos-system-extras and holtos-apps arrived).
- z13ctl-bin 1.3.2, z13gui-bin 1.4.1, plasma-keyboard and fuse2 installed;
  z13ctl and z13gui run in Plasma.
