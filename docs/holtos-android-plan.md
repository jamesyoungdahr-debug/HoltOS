# Android on HoltOS: research and plan

Liam, 2026-09-15: "see if it's possible to have Android run on the system
natively; if we can't do native, research compatibility layers like gamescope
and Steam do and present a plan", then "I want a tabley mode like we have a
game mode - it should be on the newest version of Android". Research only;
nothing is built. Reference machine: ASUS ROG Flow Z13 (Strix Halo, Radeon
8060S), HoltOS on Arch kernel 7.2.4.

## Options found

| Option | How it runs | Newest Android available | Fit for an "Android Mode" |
|---|---|---|---|
| Native Android (Bliss OS, Android-x86) | its own OS, dual boot from the Limine menu | Bliss OS 16.9 = Android 13; public PC images are paused; Bliss 18 (Android 15) source only | Not the newest Android, no shared files or quick switch, a second OS to update. Not recommended. |
| Waydroid | a real Android system in an LXC container on the HoltOS kernel, drawing to Wayland, host GPU through Mesa | official images Android 13 (LineageOS 20); community WayDroid-ATV builds of LineageOS 23.2 = Android 16 QPR2 (July 2026); Waydroid 1.6.3 (May 2026) added initial Android 16 support | Best performance and battery, shares the kernel, fullscreen UI like Game Mode. Risks below. |
| Android emulator (Google's emulator with KVM, or nux-emulator on crosvm) | a small VM with gfxstream GPU acceleration | Google publishes current Android system images, including Google Play images, for its emulator; nux-emulator ships Android 16 (AOSP), GPLv3, but is very early (no releases) | Newest Android and most compatible, but heavier, a VM per session, and Google's SDK licence terms mean images are downloaded by the user, not shipped in HoltOS. Fallback. |
| Android Translation Layer (ATL) | Wine-like: runs APKs as GTK4 apps, no Android OS | not an Android version; old or simple apps work best | Not a tablet mode. Not recommended. |

## Risks checked

- **Binder on Arch's kernel.** HoltOS's kernel (Arch linux 7.2.4) has
  `CONFIG_ANDROID_BINDER_IPC_RUST=y` and the C binder unset. Since Arch
  switched to the Rust binder in 6.18, Waydroid users reported partial
  breakage ("Transaction failed" for audio through the system stack, e.g. the
  built-in music app; VLC still played). No documented fix was found. Must be
  tested on 7.2.4; options if it fails: the AUR binder_linux-dkms module or a
  kernel with the C binder.
- **Android 16 on AMD integrated graphics.** The WayDroid-ATV LineageOS 23.2
  build has a bootloop report on an AMD Z1 Extreme (Phoenix) iGPU, closed
  without a fix. The Radeon 8060S is a different GPU but the same driver
  family: must be tested.
- **ARM-only apps.** Most Play Store games are ARM-only. On x86 they need
  libndk_translation (better on AMD) or libhoudini, both proprietary; HoltOS
  cannot ship them in the image. A user-installed, opt-in step at most.
- **Google Play.** GApps can be added to Waydroid images, but such installs
  are uncertified and apps that check Play Integrity (banking, some games)
  may refuse to run. MicroG, F-Droid and Aurora Store avoid Google services.
- **Wayland only.** Waydroid needs Wayland; HoltOS sessions already are.

## Recommended design: "Android Mode", like Game Mode

HoltOS Game Mode is a separate login session (`holtos-gamemode.desktop` in
wayland-sessions, `holtos-gamemode-session` running gamescope with Steam)
with Switch to Desktop through `steamos-session-select` and
`holtos-session-apply`. Android Mode copies that pattern:

1. **Session:** `holtos-android.desktop` in wayland-sessions and
   `holtos-android-session`, which starts the Waydroid container and runs
   `waydroid show-full-ui` fullscreen in a kiosk compositor (cage, as in
   Waydroid's own "Waydroid-only sessions" guide; gamescope as an
   alternative for games). Touch, rotation and the on-screen keyboard come
   from Android itself.
2. **Switching:** "Switch to Android Mode" in the tray, dock and Game Mode,
   and a "Return to Desktop" tile inside Android (a small HoltOS app or a
   quick-settings tile calling the same session switch), plus a keyboard
   shortcut. The HoltOS desktop keeps running services (The Den stays up) as
   it does for Game Mode.
3. **Android version:** the newest image that passes the Z13 tests, i.e.
   Android 16 (LineageOS 23.2) if it boots and is stable on the Radeon 8060S;
   otherwise the official Android 13 image until a fixed Android 16 build
   exists. HoltOS Updates offers image updates like other components.
4. **Apps:** F-Droid and Aurora Store preinstalled in the image option;
   GApps and ARM translation as clearly labelled, opt-in extras the user
   installs (licences), with a note that Play Integrity apps may not work.
5. **Files and devices:** a shared folder between HoltOS and Android
   (Downloads, Pictures), network through Waydroid's bridge, audio through
   PipeWire, controllers passed through.
6. **Tablet link:** when the Z13's keyboard is detached (see
   docs/holtos-tablet-plan.md, tablet-mode switch), offer Android Mode.

Fallback backend: if Waydroid's Android 16 does not run well on Strix Halo,
the same session can run Google's Android emulator fullscreen with the
current Android image the user downloads (newest Android, Play images, VM
overhead), keeping the same switching and tray entries.

## Phases (each needs Liam's go and a Z13 test)

0. **Feasibility on the Z13** (commands from Claude, nothing installed
   permanently where possible): binder under the Rust driver on 7.2.4;
   Waydroid with the official Android 13 image; then the Android 16 image;
   GPU acceleration, audio, touch, rotation, suspend. Decide Waydroid vs
   emulator.
1. **Packaging:** build waydroid (AUR) into the HoltOS package repository
   with its dependencies (lxc, python-gbinder, etc.), and an image download
   step, not images in the ISO.
2. **Session and switching:** holtos-android-session, the session entry,
   tray/dock/Game Mode entries, Return to Desktop.
3. **Apps and extras:** F-Droid/Aurora, opt-in GApps and ARM translation
   with licence notes, shared folders.
4. **Tablet integration** with the tablet plan.
5. **Updates and docs:** image updates in HoltOS Updates, LIVETEST items.

## Sources

- Waydroid: https://waydro.id/
- Waydroid-only sessions: https://docs.waydro.id/faq/setting-up-waydroid-only-sessions
- Arch Wiki, Waydroid: https://wiki.archlinux.org/title/Waydroid
- Rust binder breakage on Arch 6.18: https://github.com/waydroid/waydroid/issues/2157
- Android 16 images request: https://github.com/waydroid/waydroid/issues/2229
- WayDroid-ATV builds (LineageOS 23.2): https://github.com/WayDroid-ATV/waydroid-builds/releases
- AMD iGPU bootloop report: https://github.com/WayDroid-ATV/waydroid-builds/issues/35
- ARM translation and GApps (waydroid_script): https://deepwiki.com/casualsnek/waydroid_script/5.4-arm-translation-(libndk-and-libhoudini)
- Android Translation Layer: https://nlnet.nl/project/ATL/
- Bliss OS status: https://tech-insider.org/how-to-install-bliss-os-pc-2026/
- nux-emulator: https://github.com/nux-emulator/nux-emulator
- Android emulator release notes: https://developer.android.com/studio/releases/emulator
