# HoltOS bare-metal test list (neon rebrand, 0.1.0)

For Liam. Derived from `LIVETEST.md`'s "Neon rebrand" section plus the items
only hardware can prove. Order: **Z13 first, then the 4090.**

Anything marked **NEW** is a fix from 2026-09-15 that has never run on real
hardware. Everything else has never been tested on hardware at all.

---

## Z13 first

### 0. The stuck updater — do this before anything else

It blocks the rest, and it is a *different* fault from the downgrade bug that
was fixed and shipped tonight (`v0.0.7l-alpha` on stable, and the dev branch).

    cat /var/lib/holtos/update-status.json; df -h / | tail -1; journalctl -u holtos-update-install -n 25 --no-pager | tail -25

Leading suspects, in order:

1. **Disk space.** A system update refuses to start without room for twice the
   download plus 1 GB, and that refusal is easy to miss.
2. **A long system update.** The dev channel can pull a large package set; the
   window can sit there looking frozen while it downloads.
3. **A stale pacman lock** left by the earlier downgrade mess.

If it is genuinely wedged, reinstall from the new Ventoy ISO — that build has
tonight's fix baked in, so a fresh install is clean from the first boot.

### 1. Tonight's fixes (worth a reboot)

- [ ] **Boot splash — NEW:** the neon glow should be visible in the top-right.
      Before tonight only ~29% of it was on screen, so the splash read as flat
      black. Also check the glow shows no hard rectangular edge.
- [ ] **Login screen (SDDM) — NEW:** the card should be translucent glass, not
      a solid dark slab. This is the one Liam reported: it fell back to opaque
      wherever Qt used software rendering, which the Z13 does.
- [ ] **System Settings glass:** see the warning at the bottom — the lighter
      values are not published yet, so judge only whether it is translucent at
      all.

### 2. The rebrand checklist (hardware-only items)

- [ ] **Dock seams:** look closely at the dock's rounded ends where they meet
      the straight edges — any faint lines? (Only ever seen in the VM.)
- [ ] **Menu bar:** floats with a small gap from the screen edges; otter
      launcher, app menus, tray and clock all present.
- [ ] **Glass popups and tooltips over a bright wallpaper:** readable? Calendar,
      tray popups, tooltips. The most likely to disappoint, since adaptive
      contrast is not shipped.
- [ ] **Text shadow:** buttons, tabs and menu text over a bright wallpaper stay
      readable; nothing looks blurry or doubled.
- [ ] **GTK glass:** open a GTK app (a Flatpak GNOME app, or `zenity`) — it
      should be translucent with blur behind it, and readable.
- [ ] **CJK text** shows in the menu bar's app menus and the tray, not only in
      Steam.
- [ ] **Title bar buttons** are small plain circles; dock icons are not crowded.
- [ ] **Running apps** have a magenta underline; the active app a soft purple
      glow.
- [ ] **Global Theme:** lists only HoltOS and HoltOS Classic. Pick Classic —
      one bottom panel on plain glass. Switch back — menu bar and dock return.
      Log out and in — the choice sticks.
- [ ] **Colours** lists only HoltOS. **Plasma Style** lists HoltOS Glass,
      HoltOS Glass Classic and the default fallback.
- [ ] **The otter appears** in HoltOS Updates, Stash, Gaming and Network Shares
      — never the old flat logo.
- [ ] `ls /usr/share/icons/hicolor/scalable/apps/holtos-logo.svg` reports
      **no such file**.
- [ ] **Network Shares > Add > Browse:** lists the NAS or other SMB/NFS
      servers; picking one lists its shares. A server needing a login: enter
      user and password first, then browse.
- [ ] **Network Shares > Share from this computer:** set a network password,
      share a folder, open it from a Windows PC at `\\<name>\<share>`. The
      machine also appears in Windows' Network view. "Anyone on the network can
      open it" = a guest can read but not change files.
- [ ] **HoltOS Updates > Hardware:** Check again — the button greys out, then
      reports when the check finished and how many drivers are installed. Sound
      devices lists your speakers and mics; the "built-in microphone: not
      supported on Linux yet" row is present, and a USB mic adds itself.
- [ ] **Stash:** install an app (progress, no password prompt), queue two and
      cancel one, remove an app with "delete its settings and data", and check
      "Update all".
- [ ] **Automatic rollback:** only if an update ever stops the desktop starting
      — after two failed boots HoltOS should restore the pre-update snapshot and
      say "HoltOS undid the last update" at login.

---

## 4090 next (fresh install, NVIDIA)

- [ ] **Install from the new Ventoy ISO:** the installer run itself, then first
      boot. Check `/var/lib/holtos/hardware.log` from the driver step.
- [ ] **The NVIDIA driver path** — the one thing the VM can never prove.
- [ ] **Dual boot next to Windows:** the boot menu offers both; the small-ESP
      kernel logic behaves.
- [ ] **Glass installer** (`pkexec calamares -style kvantum`): the blank white
      top bar was reproduced on the new ISO on 2026-09-15. Most promising lead
      is the **root installer on Wayland**.
- [ ] **Boot splash and login glass** again — the NVIDIA/GL path rather than
      the Z13's software path, so SDDM's live blur may work here where it
      cannot on the Z13.

---

## Not yet testable

**The lighter System Settings glass is committed but not built or published.**
`forks/holtos-qqc2-desktop-style` moved Page and Pane to 40% and Drawer to 60%
(was 60%/60%/80%), but the package needs `./build-local-repo.sh` then
`tools/publish-packages.sh` before any machine sees it. Opening System Settings
on the Z13 shows the **current 60%** version: translucent, but darker than what
is coming. Do not judge the final look from it.
