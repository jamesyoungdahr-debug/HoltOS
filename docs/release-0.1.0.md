# Releasing 0.1.0 (the neon rebrand)

`neon-rebrand` is feature-complete and `archiso/profiledef.sh` already says
`iso_version="0.1.0"`. This is the runbook for turning it into a release.
**The order below matters** — see the warning in step 2.

## Before you start

- A Hyper-V VM holding an ISO locks the file: turn off any VM before `build.sh`.
- Build from Git Bash: `./build.sh` in `C:\projects\holtos-neon-rebrand`.
- Do not run any of this while a machine is mid-update.

## 1. Version strings

`profiledef.sh` is already `0.1.0`. Also check:

| File | What |
|---|---|
| `archiso/airootfs/etc/os-release` | `VERSION_ID`, `PRETTY_NAME` |
| `archiso/airootfs/etc/calamares/branding/holtos/branding.desc` | version |
| `CHANGELOG.md` | promote the `[Unreleased]` section to 0.1.0 |

## 2. Publish the packages first — BEFORE flipping the URL

Refresh `local-repo/` from the current branch (`./build-local-repo.sh`), then
publish with the override:

```bash
PACKAGES_RELEASE=packages tools/publish-packages.sh
```

**The override is required from this branch.** `publish-packages.sh` picks the
target release from the branch name — `master` goes to `packages`, any other
branch goes to `packages-dev` — so without it, a run on `neon-rebrand` lands in
the dev repo only.

> **Why this order.** `master` points its pacman config at `packages`;
> `neon-rebrand` points at `packages-dev` and its config carries the note "back
> to `packages` at release". If the URL is flipped before the 0.1.0 packages
> exist in `packages`, every dev-channel machine (the Z13) takes the update,
> rewrites its pacman config to `packages`, and then pulls **0.0.7k stable**
> packages — it downgrades itself.

## 3. Flip the repo URL

These places on `neon-rebrand` name `packages-dev` and must become `packages`:

- `archiso/pacman.conf` (the Server line, and drop the dev comment above it)
- `archiso/airootfs/usr/share/holtos/pacman-holtos.conf` (the Server line and
  its comment)
- `tools/publish-packages.sh`
- `CONTEXT.txt` and `docs/holtos-arch-snapshot.md` mention it in prose

This is the recorded decision from the dev-repo experiment ("switch URLs back
to `packages` at 0.1.0"). A future dev cycle would stand up a fresh dev repo.

## 4. Merge to master and tag

```bash
git checkout master
git merge --no-ff neon-rebrand
git tag v0.1.0
git push origin master --tags
```

## 5. Build and test the ISO from the tag

`./build.sh`, then boot it in a VM: the installer pages, then an install and
first boot. **The install needs a user account, which Claude may not create** —
that step is Liam's.

## 6. After the release

- Confirm an installed machine runs `pacman -Sy` against `[holtos]` cleanly.
- The dev branch keeps `packages-dev`; only the release points at `packages`.
- Drop the `homelab.db` copies a few releases later.

## Open at release time (not blockers)

- The glass installer is parked: under `pkexec` the QML top bar draws blank.
- Glass for System Settings and other Kirigami apps (glass plan G7) — research
  started 2026-09-15, fork build to follow.
- Bare-metal tests, `LIVETEST.md` "Neon rebrand" section.
