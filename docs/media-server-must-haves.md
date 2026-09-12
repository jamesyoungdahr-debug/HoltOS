# HoltOS as a media server — must-have feature list

Written 2026-09-12 for Liam. Scope: a home media server that a
non-technical household uses daily, built on HoltOS (Arch, Btrfs, Plasma,
The Den). Ordered by what breaks the experience if it is missing.

## Tier 1 — without these it is not a media server

1. **Hardware video transcoding, verified at install.** VA-API for
   AMD/Intel (already in the image) and NVENC/NVDEC when an NVIDIA card is
   detected (needs `nvidia-utils`, already on the NVIDIA path). Ship a
   one-shot check that logs which codecs the GPU can decode/encode
   (`vainfo` / `nvidia-smi -q | grep Encoder`) into `hardware.log`, and
   surface it in About this System. Without this, 4K HEVC/AV1 remux to a
   phone or TV app is CPU-bound and stutters.
2. **A media player/server with client apps** (Jellyfin is the open
   choice; Plex is the closed one). The Den is the library/acquisition
   layer, but playback on TVs, phones and browsers needs a server with
   real client apps, subtitle handling, watch state, and transcoding
   ladders. Decide which one ships; make The Den hand finished files to
   it and trigger a library scan.
3. **Storage that survives a disk dying.** Btrfs RAID1 or ZFS mirror /
   RAIDZ for the media pool (ZFS is already in the image), created by a
   guided "Storage" step or a first-run wizard: pick disks, pick
   redundancy, done. Monthly scrub timer, SMART monitoring
   (`smartd`), and a desktop notification when a disk degrades.
4. **Snapshots that can actually be restored.** The Btrfs `@` root is
   snapshotted before every update already; the open item is a
   "Restore this snapshot" action so a bad update is a 30-second
   rollback, not a rescue boot. The media pool needs its own scheduled
   snapshots (deleted-file insurance) with retention.
5. **Network shares out of the box.** Samba (SMB3) share of the media
   pool, discoverable on Windows/macOS/iOS via WS-Discovery + Avahi;
   NFS optional. Read-only guest for players, read-write for the owner.
6. **Remote access that is safe by default.** Tailscale (or WireGuard)
   pre-installed with a one-click "Enable remote access" that gives
   phones and laptops the server on the tailnet. No open ports, no
   dynamic DNS, no reverse-proxy setup for the household.
7. **Unattended, reversible updates.** Already the design (updater +
   snapshot). Add: update window (e.g. 04:00), auto-rollback if the
   system fails to reach the desktop twice, and a health page.

## Tier 2 — expected by anyone who has run a media box before

8. **Wake-on-LAN + scheduled sleep/wake** with `power-profiles-daemon`
   and a "media box" profile: idle to low power, wake on request.
9. **Automatic subtitle fetching** (Bazarr-equivalent) wired into The
   Den, with language preference set at install.
10. **Metadata and artwork agents** with local caching so the library
    renders offline.
11. **Per-user profiles and parental controls** in the player (kids
    profile, PIN), and a guest/kiosk desktop session for the TV.
12. **HTPC mode**: a 10-foot UI launcher on the local display (the
    player's TV client in fullscreen at login), remote-control input
    (CEC over HDMI via `libcec`, Bluetooth remotes), and audio passthrough
    (HDMI bitstream) configured for the living-room TV/AVR.
13. **HDR and refresh-rate matching on the local display.** Plasma 6
    Wayland exposes HDR/VRR/refresh only when the DRM driver supports it
    — NVIDIA needs `nvidia_drm.modeset=1` (done) and, for the HDR toggle
    on Plasma 6.2+, `KWIN_DRM_ALLOW_NVIDIA_COLORSPACE=1`. The player
    should switch refresh rate to match content (23.976/24/50/60).
14. **Download/acquisition hygiene**: VPN-bound torrent client (kill
    switch), bandwidth schedule, seeding limits, and a clear "what is
    downloading" view in The Den.
15. **Backups of the important small stuff**: the Den database,
    player database, and config, to a second disk or cloud, nightly.
16. **Monitoring and alerts**: disk space, disk health, temperatures,
    failed services; a status page and desktop/phone notification.

## Tier 3 — polish that makes it feel like a product

17. **First-run wizard** covering: storage layout, media folders,
    remote access, player choice, subtitle languages, update window.
18. **One place for logs and support bundle** (`holtos-support-bundle`
    that tars journal, hardware.log, history.log, disk health).
19. **Mobile companion**: The Den Client on Android/iOS or a PWA for
    requests and status.
20. **Energy/thermal tuning**: zram, `bfq`/`mq-deadline` schedulers per
    disk type, HDD spindown, fan curves where supported. CachyOS's
    settings package is a good reference for the udev/sysctl bits.
21. **Hardware compatibility page**: known-good GPUs for transcoding,
    HBA cards (the R720's PERC in HBA mode), NICs.
22. **Transcode cache on fast storage** with size limit, and a
    pre-transcode option for low-power clients.

## Explicitly out of scope for now

- A full arr-suite reimplementation (The Den is the replacement).
- Multi-tenant/enterprise features (LDAP, SSO): Authentik was removed
  for a reason.
- DVR/live TV — only if a tuner shows up as a real need.
