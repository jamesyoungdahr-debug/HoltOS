# HoltOS Glass v2 — forking KWin + plasma-workspace

Written 2026-09-13. Liam's call: the existing lightweight plugin forks
(`holtos-glass-effect`, a KWin blur *plugin*; `holtos-window-decoration`, a
Klassy-based *window decoration* plugin) have hit a real ceiling — KWin's
dual-Kawase blur can't be pushed to the soft "milk glass" look in Liam's
reference photo, and System Settings' Kirigami sidebar isn't reachable by a
KWin plugin or Kvantum at all. Decision: fork the actual engines, not just
their plugin surfaces, for full design control. This is a large, ongoing
commitment — both are big KDE C++ codebases HoltOS would now maintain
against upstream indefinitely — so it's tracked here as its own project
with milestones, not folded into a quick pass.

## What's already done (2026-09-13)

- Forked on GitHub: `jamesyoungdahr-debug/holtos-kwin` (from `KDE/kwin`),
  `jamesyoungdahr-debug/holtos-plasma-workspace` (from `KDE/plasma-workspace`).
- Both cloned to `C:\projects\holtos-kwin` and `C:\projects\holtos-plasma-workspace`
  (shallow clones — depth 1 on the default branch).
- Both pinned to tag `v6.7.5` — matches the Plasma version HoltOS actually
  ships (`kwin`/`plasma-workspace` in `extra`), so we're not building
  against a mismatched pre-release ABI. A `holtos` branch was created off
  that tag in each repo as the base for HoltOS's own commits.
- Arch's real PKGBUILDs for `kwin`/`plasma-workspace` were unreachable
  (gitlab.archlinux.org serves an Anubis bot-check page from this network;
  a stale GitHub svntogit mirror only has the old Plasma 5 version). Wrote
  PKGBUILDs from scratch instead, using the actual `find_package()`/
  `pkg_check_modules()` calls in each repo's own current `CMakeLists.txt`
  as the ground-truth dependency list (arguably better than a possibly-
  stale reference PKGBUILD, since it's the literal build requirement of
  the exact commit being built).
- `packaging/holtos-kwin/PKGBUILD` and `packaging/holtos-plasma-workspace/PKGBUILD`
  drafted (both `git+https://github.com/jamesyoungdahr-debug/<name>.git#branch=holtos`
  sources — standard Arch `-git` package convention, no vendoring, no
  submodule; `makepkg` clones them itself at build time).
- `build-aur-packages.sh`'s `HOLTOS_PKGS` loop only required a `/forks/<pkg>`
  source tree unconditionally — fixed to only tar/require it when that
  directory actually exists, since these two new packages fetch their own
  git source and were never meant to be vendored into `forks/` (600MB+ and
  460MB — vendoring either into the main repo's git history the way the
  tiny existing forks are would be a serious, permanent bloat mistake).
- **First real build attempt** (scoped to just these two packages via
  `AUR_PKGS=none HOLTOS_PKGS="holtos-kwin holtos-plasma-workspace"`) got
  past the container build and into actual dependency resolution — hit two
  bad package names in the hand-derived list (`kinit`, not a real
  dependency; `eis` should be `libei`, the real Arch package for libeis).
  Both fixed, a duplicate `kxmlgui` entry also cleaned up. **Retry in
  progress** as of this write.

## Milestone 0 — Scaffolding

- [x] Fork both repos, pin to `v6.7.5`, create `holtos` branches
- [x] PKGBUILDs drafted for both (see above — written from CMakeLists.txt
      ground truth rather than a fetched reference PKGBUILD)
- [x] `build-aur-packages.sh` extended to support git-sourced HoltOS
      packages alongside the existing vendored-tarball ones
- [x] Full dependency list build-verified end to end — both packages now
      compile completely and produce real .pkg.tar.zst artifacts (see
      Milestone 1)

## Milestone 1 — Vanilla build proof (no design changes yet)

**Complete (2026-09-13 11:06 UTC).** Both packages now build successfully from source and produce real installable artifacts in `local-repo/`:
- `holtos-kwin-6.7.5.r86-1-x86_64.pkg.tar.zst` (13.3MB)
- `holtos-plasma-workspace-6.7.5.r86-1-x86_64.pkg.tar.zst` (25.8MB)

Got there through 17 rounds of real dependency-name fixes across both PKGBUILDs (wrong names, missing packages, one packaging gap worked around with a disabled CMake option) plus one earlier git-branch-not-pushed mistake -- all logged above. Neither package has been installed anywhere yet, and neither has any HoltOS customization -- this milestone only proves the toolchain can compile KDE's own unmodified compositor and shell from our forks, which it now does. Not yet done: installing these built packages anywhere or verifying the resulting desktop still works (that's Milestone 2).

## Milestone 2 — Replace the stock packages in the ISO

- Point `packages.x86_64` / the local package repo at our built
  `kwin`/`plasma-workspace` instead of `extra`'s, via the same
  `[homelab]` local-repo mechanism already used for other HoltOS-built
  packages
- **Mechanism (2026-09-13): `provides=()`/`conflicts=()`/`replaces=()` on both PKGBUILDs, plus explicit `packages.x86_64` entries.** Both PKGBUILDs now carry all three: `provides=(kwin=6.7.5) conflicts=(kwin) replaces=(kwin)` and the plasma-workspace equivalent. `holtos-kwin`/`holtos-plasma-workspace` were added as their own lines in `packages.x86_64` (same pattern as `holtos-glass-effect`/`holtos-window-decoration`), so pacman satisfies `plasma-desktop`'s (and `powerdevil`/`plasma-nm`/`plasma-pa`/`holtos-glass-effect`'s) dependency on the real package name via our `provides=` instead of pulling in the stock `extra/` one.

  A first attempt added `IgnorePkg = kwin plasma-workspace` to `archiso/pacman.conf`'s `[options]` to stop pacman selecting both packages at once. That was wrong and made it worse: pacman's `IgnorePkg` blocks the named package outright rather than deferring to a `provides=`-based substitute, so the real build log showed `warning: ignoring package plasma-workspace-6.7.5-1` followed by `error: failed to prepare transaction (could not satisfy dependencies)` -- pacman never even considered `holtos-plasma-workspace`'s `provides=` as a candidate once the literal name was ignored. Fix: removed `IgnorePkg` from `pacman.conf` entirely and added `replaces=()` to both PKGBUILDs alongside the existing `provides=()`/`conflicts=()`, which is the complete, correct pacman signal for "this package supersedes that one" without blocking dependency resolution. Rebuilding `local-repo/` and retrying the full ISO build to confirm.
- **Dependency resolution confirmed working (2026-09-13):** the full ISO build's `pacman -Sy` dependency resolution for all 874 packages completed cleanly with `holtos-kwin-6.7.5.r87-1` and `holtos-plasma-workspace-6.7.5.r87-1` in the final resolved list and **no stock `kwin` or `plasma-workspace` packages anywhere in it** -- confirms `provides=()`/`conflicts=()`/`replaces=()` correctly satisfies `plasma-desktop`/`powerdevil`/`plasma-nm`/`plasma-pa`/`holtos-glass-effect`'s dependencies via our packages instead of pulling in `extra`'s. No `unable to satisfy dependency` errors, no `IgnorePkg` needed.
- **ISO built successfully (2026-09-13):** `holtos-0.0.4-alpha-x86_64.iso`, 3.3GB. Attached to the `holtos-test` VM for a live-session boot test -- the actual first real-world runtime exercise of this from-scratch KWin/plasma-workspace build (Milestone 1 only proved it compiles; nothing had booted it before now).
- **Real crash found and root-caused (2026-09-13):** both `Plasma (Wayland)` and `Plasma (X11)` sessions fail on first boot. `journalctl -b` + `coredumpctl info kwin_wayland` show `kwin_wayland` segfaulting (SIGSEGV) inside `KWin::Application`'s own constructor, deep in Qt's platform theme init: `QApplicationPrivate::init` -> `QGuiApplicationPrivate::createPlatformIntegration` -> `KdeTheme::createKdeTheme` -> `QGuiApplicationPrivate::handleThemeChangedEvent` (the actual crash site). Every other Plasma component (confirmed: `org_kde_powerdevil`) then crash-loops separately because no Wayland compositor is running to give them a display -- a pure cascade, not a separate bug. Ruled out a Qt6/frameworkintegration version-skew theory: extracted `holtos-kwin`'s own `.BUILDINFO` and confirmed `qt6-base-6.11.2-3`/`frameworkintegration-6.30.0-1` at build time exactly match what's installed on the live system. Leading suspect: `-DKWIN_BUILD_GLOBALSHORTCUTS=ON` (re-enabled this session, see Milestone 1 log) combined with `kglobalacceld` only being a `makedepends=()` entry, not `depends=()` -- meaning the actual daemon package isn't guaranteed present at runtime, and if KWin's global-shortcuts client code runs early in the constructor and mishandles the daemon's absence, memory corruption there could plausibly surface later as an unrelated-looking crash in Qt internals. `-DKWIN_BUILD_GLOBALSHORTCUTS` reverted to `OFF` in the PKGBUILD to isolate this; rebuild and VM retest queued next. **Follow-up research (2026-09-13) weakly contradicts this hypothesis**: documented kglobalacceld-absent failure modes (Arch Forums, CachyOS issue tracker) describe silent degradation (shortcuts stop working) rather than a crash, and no report connects global-shortcut registration to Qt's theme-change event path at all -- the crash happens inside `QApplicationPrivate::init()`, before KWin's own shortcut code would typically run. A more plausible lead surfaced instead: KWin doesn't use the standard `xcb`/`wayland` Qt platform plugin for itself, it uses an internal one (`wayland-org.kde.kwin.qpa`), since kwin_wayland *is* the compositor, not a themed client app -- a KDE platform theme plugin (`createKdeTheme`, from `frameworkintegration`) firing inside that unusual context, rather than inside a normal themed application, may be the real mismatch, possibly via `QT_QPA_PLATFORMTHEME` being set when it shouldn't apply to the compositor itself. Not confirmed either -- no exact bug-report match was found for this crash signature anywhere (KDE Bugzilla, GitHub, Arch/AUR forums). The GLOBALSHORTCUTS revert is still worth testing since it's the only concrete code-level change made, but treat its result as one data point, not proof: if the crash persists with GLOBALSHORTCUTS=OFF, the QT_QPA_PLATFORMTHEME/internal-QPA-plugin theory becomes the next thing to check, not a dead end.
- **Resolved (2026-09-13, afternoon):** the GLOBALSHORTCUTS theory was wrong — the rebuild with `GLOBALSHORTCUTS=OFF` crashed identically. Actual cause, verified live on the VM: **missing runtime dependencies.** `replaces=(kwin)`/`replaces=(plasma-workspace)` mean the stock packages are never installed, so every transitive dependency they would have pulled in is simply absent unless our PKGBUILDs list it — and both `depends=()` arrays were hand-written and incomplete. `plasma-integration` was the one that crashed KWin: without `KDEPlasmaPlatformTheme6.so` in `platformthemes/`, Qt falls back to its built-in `QKdeTheme` (the `createKdeTheme` frame in the trace is Qt's own fallback, not the KDE plugin), and Qt 6.11's `QKdeTheme` segfaults in `handleThemeChanged` during `QApplication` construction. Installing it live got `kwin_wayland` running, after which `plasmashell` aborted its shell load because `kactivitymanagerd` was gone too. Full missing set, found by diffing `pacman -Si kwin` / `pacman -Si plasma-workspace` "Depends On" against `pacman -Q` on the live system: `plasma-integration kactivitymanagerd kglobalacceld kde-cli-tools milou qt6-tools aurorae iio-sensor-proxy libqaccessibilityclient-qt6 ocean-sound-theme qt6-virtualkeyboard xorg-xmessage xorg-xrdb`. Installing all of them on the live VM (after `mount -o remount,size=4G /run/archiso/cowspace`) and restarting SDDM brought up the full HoltOS desktop on the forked KWin + plasma-workspace. Fix: both `depends=()` now mirror Arch's runtime lists plus our previous extras; `kglobalacceld` moved from `makedepends` to `depends`; `-DKWIN_BUILD_GLOBALSHORTCUTS=OFF` removed again (Arch builds with it on, and OFF would have shipped a KWin with no global shortcuts). Lesson for every future `replaces=` package: copy the stock package's "Depends On" from `pacman -Si`, never write the list by hand. **Verified (2026-09-13, build 23, packages r89):** the fresh live ISO boots to the full desktop with nothing installed by hand: no coredumps, no failed user units, no "Couldn't start kglobalaccel" errors (the shortcut service answers on D-Bus, hosted inside KWin), and KWin loads the in-tree `blur` effect and the `org.holtos.glass` decoration.
- Full fresh Erase-Disk install verified in the VM: session starts, panels
  and widgets work, System Settings opens, apps launch, Game Mode still
  switches both ways, the updater still runs — a real regression-risk
  point since everything in Plasma links against these two components

## Milestone 3 — Rebuild the glass effect natively in KWin

- Port the `holtos-glass-effect` blur logic directly into KWin's own
  effect chain (not a loadable plugin against a stable-ish public API, but
  first-class code in the fork), with a properly *designed* blur — most
  likely a true multi-pass Gaussian, or a dual-Kawase iteration ceiling far
  beyond what the plugin API's `BlurStrength` slider (1–15) exposes today
  — built and tuned specifically to match Liam's reference photo's soft,
  heavy wash, not incrementally guessed via live config edits
- Verify with direct side-by-side screenshot comparisons against the
  reference, the same way this session diagnosed the wallpaper/opacity
  issue — not by eyeballing alone
- **Scoping (2026-09-13):** KWin's own tree already ships its stock blur effect as a first-party plugin at `src/plugins/blur/blur.cpp` (921 lines), built the same way every other built-in KWin effect is (`src/plugins/CMakeLists.txt`) -- not a separate out-of-tree API. Diffed it against `holtos-glass-effect`'s fork (`forks/holtos-glass-effect/src/blur.cpp`, 1032 lines): only ~149 changed lines (~15%), all HoltOS's own additions (tint blend, brightness/saturation/contrast matrix, force-blur/exclude-classes config, corner radius) layered on the same dual-Kawase base. This means the port itself is a bounded, well-understood merge -- replace `holtos-kwin`'s in-tree `src/plugins/blur/` with the HoltOS-modified version and drop the separate `holtos-glass-effect` package/PKGBUILD entirely -- not an open-ended rewrite. The separately-desired blur-quality upgrade (true multi-pass Gaussian or a higher dual-Kawase iteration ceiling than the stock 1-15 `BlurStrength` range) is additional work on top of this merge, not part of it.

**Merge applied (2026-09-13):** all six substantive hunks (colorTransformMatrix signature+body, reconfigure()'s new config reads plus the m_valid-gated re-evaluation loop, the force-blur block in updateBlurRegion, the new shouldForceBlur() method, and the corner-radius fallback logic) were applied directly to `holtos-kwin`'s in-tree `src/plugins/blur/blur.cpp`/`blur.h`/`blur.kcfg`, keeping the stock effect's own naming (`Effect-blur` kcfg group, `kwin_effect_blur` logging category, `:/effects/blur/...` shader resource paths) rather than the fork's renamed ones, since this is a true in-tree replacement of the stock effect, not a coexisting second one. All shader files (.frag/.vert) are byte-identical between stock and the fork -- zero shader changes needed, this was purely a C++-side logic port. New kcfg defaults use HoltOS's already-tuned production values (NoiseStrength 2, TintColor #171423 at 35%, etc.) rather than stock's. Every EffectWindow/Window API used (`isLockScreen`, `isDNDIcon`, `isNormalWindow`, `isDialog`, `isUtility`, `isFullScreen`, `windowClass`, `maximizeMode`, `MaximizeRestore`) was individually verified to exist in this exact KWin version before writing the code. Not yet build-verified (holtos-kwin's own container build wasn't rerun to avoid contending with the in-flight Milestone 2 verification build) -- queued as the next compile check once that finishes. The separate `holtos-glass-effect` package/PKGBUILD has NOT been removed yet -- that happens only after this in-tree version is confirmed working, so there's no gap if it needs reverting.

## Milestone 4 — plasma-workspace / Kirigami surfaces

- **Confirmed (2026-09-13): System Settings is NOT part of plasma-workspace
  or kwin at all.** It's a fully separate KDE repository,
  `invent.kde.org/plasma/systemsettings` (mirrored on GitHub as
  `KDE/systemsettings`), ~3,731 commits, its own independent project since
  May 2020. Grepped plasma-workspace's own QML for sidebar/background
  styling and found nothing relevant -- confirming the sidebar chrome
  genuinely lives elsewhere. This session already ruled out the Plasma
  desktop theme's `panel-background` asset (that's Plasma panels/taskbar
  only) and confirmed a plasmarc theme change has no visible effect on
  System Settings even after a full process restart. **This milestone now
  needs a third fork**: `systemsettings` itself, the same way KWin and
  plasma-workspace were forked -- not optional, not a maybe anymore.
- **Fork created (2026-09-13):** `github.com/jamesyoungdahr-debug/holtos-systemsettings`, `holtos` branch pinned off tag `v6.7.5` (same pattern as holtos-kwin/holtos-plasma-workspace). `packaging/holtos-systemsettings/PKGBUILD` written with a dependency list read directly from systemsettings' own CMakeLists.txt (Qt6: qt6-base, qt6-declarative; KF6: kauth, kcrash, kitemviews, kitemmodels, kcmutils, ki18n, kio, kservice, kiconthemes, kwidgetsaddons, kwindowsystem, kxmlgui, kdbusaddons, kconfig, kguiaddons, kirigami, kjobwidgets, krunner, kcolorscheme; plus plasma-activities), each verified against archlinux.org before use rather than guessed. `provides=(systemsettings=6.7.5) conflicts=(systemsettings) replaces=(systemsettings)` already included, matching the pattern that fixed Milestone 2's pacman resolution. Not yet build-verified, not yet in `build-aur-packages.sh` or `packages.x86_64` -- deliberately held back until Milestone 2 (kwin/plasma-workspace) is confirmed working end to end in a real ISO/VM install, so problems aren't debugged on two fronts at once.
- Once located, make it honor translucency/blur consistent with the rest
  of the design

## Milestone 5 — Ongoing maintenance

- Decide a cadence for rebasing both `holtos` branches onto new upstream
  KDE tags (security fixes land upstream regularly) — e.g. re-sync at every
  Plasma point release HoltOS itself upgrades to
- Write up the patch strategy (what's HoltOS-specific vs upstream, how to
  regenerate the branch) so this doesn't become tribal knowledge

## Milestone 6 — PR + merge

- Wire the finished forks into the monorepo (`packages.x86_64`,
  `profiledef.sh`, build scripts) as a PR once verified end-to-end in the
  VM and, ideally, on Liam's real hardware — **not auto-merged**, matching
  this project's standing rule that builds/pushes/releases only happen
  when Liam says so

## Working notes for whoever (agent or local model) picks up a milestone

- All actual code changes still go through the local LLM bridges first
  (`lmstudio-bridge` primary, `lmstudio-4080super` secondary/parallel for
  independent units) per this project's standing rule — this plan's job is
  to break the work into units small enough to spec and hand off that way,
  not to be done by hand.
- Route design/visual comparison work (screenshots, "does this match the
  reference") through direct VM testing, the same live-tuning technique
  used this session to diagnose the wallpaper and Kvantum-alpha issues —
  it's fast, free, and doesn't need a rebuild for KWin config-level changes
  (though it will for anything requiring a recompile once we're editing
  the forked source directly).
