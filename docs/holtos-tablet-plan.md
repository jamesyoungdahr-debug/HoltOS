# HoltOS on tablets: research and plan

Research 2026-09-15 (Liam: "research ways to make HoltOS more tablet
friendly"), with the ASUS ROG Flow Z13 (GZ302) as the reference device. Not
built yet: each item below needs a unit, a test on the Z13 and Liam's go.

## What HoltOS already has

- The on-screen keyboard: `plasma-keyboard` is in the image and
  `/etc/xdg/kwinrc` sets `[Wayland] InputMethod` to it, so KWin can show it
  for touch input. Reviewers prefer it to Maliit.
- Auto-rotation hardware support: the hardware rules install
  `iio-sensor-proxy` on machines with IIO sensors.
- Plasma's own touch support: on Wayland, Plasma switches to touch mode
  when the system reports tablet mode (keyboard detached or folded back):
  larger controls in Kirigami apps, auto-rotate, touch-friendly behaviour.
- KWin touchscreen edge swipes (one finger from a screen edge, at least 20 %
  in) can open Overview, Desktop Grid, Show Windows or Show Desktop.
- Kernel support for the Z13's touchscreen multi-touch and fan key.

## Gaps found

1. **The Z13 never tells Plasma it is a tablet.** `asus-nb-wmi` advertises a
   `SW_TABLET_MODE` switch but sends no event when the keyboard cover comes
   off, so Plasma never enters touch mode. Bazzite users also report the
   touchscreen stopping after the cover is detached (kernel 6.17). The known
   workaround, `z13-tablet-switch` (Rust, "vibecoded for this machine", no
   licence stated), watches for the cover's USB device (0b05:1a30,
   "GZ302EA-Keyboard Touchpad") and emits `SW_TABLET_MODE` through a
   virtual uinput device. `tablet-mode-vswitch` (GPL-3.0) does the same for
   a list of HID devices.
2. **No way to type the password at login without a keyboard.** HoltOS's
   SDDM theme has no on-screen keyboard: no `InputMethod` in sddm.conf and
   no keyboard button in the `holtos` theme. The lock screen needs the same
   check.
3. **HoltOS's own layout is sized for a mouse.** The menu bar is 1.8 grid
   units high, the dock 2.6, and the title bar buttons were made smaller on
   purpose (Liam, 2026-09-14). None of it grows in touch mode.
4. **No tablet defaults.** No touchscreen edge swipes, no touch mode or
   rotation settings in /etc/xdg; everything is Plasma's default.
5. **HoltOS's own apps are QtWidgets** (HoltOS Updates, Stash, Network
   Shares, Gaming, Welcome): no kinetic touch scrolling, small buttons.

## Plan, in order

1. **HoltOS tablet-mode switch** (`holtos-tablet-switch`): a small root
   service that watches udev for a machine's keyboard cover and exposes a
   virtual `SW_TABLET_MODE` switch through uinput. Written by HoltOS (Python
   with python-evdev, or a few hundred lines of C), not the unlicensed Rust
   daemon. Cover IDs per model in a rules file, first entry the Z13
   (0b05:1a30), installed through the hardware rules
   (`dmi board_name=GZ302EA*`). Check at the same time whether the
   touchscreen still responds after a detach on HoltOS's kernel; if not,
   find the HID fix before shipping.
2. **Keyboard at login and lock screen:** add `qt6-virtualkeyboard`, set
   `InputMethod=qtvirtualkeyboard` for SDDM, and give the `holtos` SDDM
   theme a keyboard button (shown automatically when no physical keyboard
   is attached). Check that the lock screen shows plasma-keyboard on touch.
3. **Touch mode sizing:** when Plasma is in touch mode, a larger menu bar
   and dock (for example 2.4 and 3.4 grid units) and larger title bar
   buttons, switched back in laptop mode. The panels can follow
   `Kirigami.Settings.tabletMode` from a small Plasma script or KWin script;
   the decoration fork can read the same state.
4. **Tablet defaults in /etc/xdg:** touchscreen edge swipes (for example the
   top edge for Overview, left edge for Show Windows), auto-rotate only in
   tablet mode, and plasma-keyboard shown only for touch input.
5. **Touch in HoltOS apps:** `QScroller` kinetic scrolling on every scroll
   area and list, and a touch-friendly minimum button height when touch mode
   is on. One shared helper module for all HoltOS PySide6 apps.
6. **Stylus:** check the Z13's pen (hid-multitouch) follows rotation and
   maps to the built-in screen; Plasma 6.2+ has a tablet calibration tool.
7. **Later, only if 1-5 are not enough:** a tablet session such as Plasma
   Bigscreen was tested by reviewers on a 13-inch tablet and worked, but it
   still needs scaling and touch work and would be a second desktop to
   maintain. Not recommended now.

## Tests on the Z13 (for LIVETEST.md when built)

- Detach the keyboard: Plasma switches to touch mode within a second;
  reattach: back to laptop mode. The touchscreen keeps working both ways.
- Log out, detach the keyboard, log in with the on-screen keyboard.
- Lock the screen with the keyboard detached and unlock by touch.
- In touch mode: the menu bar, dock and title bar buttons are easy to hit;
  edge swipes open Overview; the screen rotates; the on-screen keyboard
  appears when a text field is tapped and not when typing on the cover.
- HoltOS Updates and Stash lists scroll with a finger flick.

## Sources

- Plasma tablet use: https://www.makeuseof.com/i-put-linux-on-a-tablet-and-kde-plasma-handled-everything-i-threw-at-it/
- Touchscreen edge swipes and touch mode: https://en.windowsnoticias.com/KDE-Plasma-optimizes-for-touch-and-natural-gestures/
- Plasma 6.2 tablet features: https://kde.org/announcements/plasma/6/6.2.0/
- Z13 touchscreen after detach, tablet switch workaround: https://github.com/ublue-os/bazzite/issues/4386
- z13-tablet-switch: https://github.com/m4rw3r/z13-tablet-switch
- tablet-mode-vswitch: https://github.com/skgsergio/tablet-mode-vswitch
- KWin touchscreen edge swipe commit: https://github.com/KDE/kwin/commit/aa6c8f81168e4f89c67b9e88065aee675e306d1a
