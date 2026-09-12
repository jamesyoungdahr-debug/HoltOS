# HoltOS Glass window decoration

This is HoltOS' fork of [Klassy](https://github.com/paulmcauley/klassy)
(Paul A McAuley), taken at tag v6.7.2 (commit c144ad45) for Plasma 6.7
and kept in the HoltOS repo under `forks/holtos-window-decoration`
(Klassy's `screenshots/` directory dropped, nothing else). Klassy's own
README.md is kept as is; this file describes what HoltOS changes.

Why a fork: HoltOS wants full control of its window chrome — translucent,
blurred title bars whose defaults are compiled in rather than shipped as
a config file, its own plugin identity, and the freedom to change the
drawing later without waiting on upstream.

## Changes from upstream (keep this list current)

- Decoration plugin id `org.holtos.glass`, shown as "HoltOS Glass"
  (`kdecoration/CMakeLists.txt` OUTPUT_NAME, `kdecoration/breeze.json`).
- Defaults in `libbreezecommon/breezesettingsdata.kcfg`: title bar
  opacity 70 % active / 60 % inactive with the override switched on,
  window corner radius 10, glass kept on maximized windows.
- LF line endings enforced (`.gitattributes`).

Everything else — the KCM, the application style, presets, colour
schemes, the Plasma theme — is untouched so a newer upstream release can
be brought in by diffing: unpack the new tag next to this tree, apply the
changes listed above on top, replace the tree.

The decoration still reads `klassy/klassyrc`; HoltOS ships the
remaining styling (buttons, shadows, alignment) in
`etc/skel/.config/klassy/klassyrc` in the HoltOS repo.

## Building

Packaged by `packaging/holtos-window-decoration/PKGBUILD` in the HoltOS
repo (Qt 6 only, conflicts with the AUR `klassy` package). By hand:

```
cmake -B build -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_TESTING=OFF -DBUILD_QT5=OFF
cmake --build build && sudo cmake --install build
```

Licences are Klassy's (see `LICENSES/`).
