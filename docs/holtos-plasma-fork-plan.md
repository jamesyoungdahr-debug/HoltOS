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
- **Mechanism confirmed (2026-09-13), not yet acted on**: `provides=()`/`conflicts=()` were already added to both PKGBUILDs (`provides=(kwin=6.7.5) conflicts=(kwin)` and the plasma-workspace equivalent). `packages.x86_64` currently only pulls in stock `kwin`/`plasma-workspace` transitively via the `plasma-desktop` line -- explicitly adding `holtos-kwin` and `holtos-plasma-workspace` as their own lines in `packages.x86_64` (same pattern already used for `holtos-glass-effect`/`holtos-window-decoration`) is enough to make pacman satisfy `plasma-desktop`'s dependency with ours instead, no `pacman.conf` repo-priority changes needed since the package names don't collide with the stock ones. Deliberately NOT done yet -- this is a real ISO-build-affecting change and shouldn't happen until Milestone 1 is confirmed fully working (both packages actually built, not just configuring).
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
