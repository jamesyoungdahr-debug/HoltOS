# HoltOS Glass (KWin effect)

The background-blur effect behind every HoltOS window. This is HoltOS-owned
code: a fork of KWin 6.7's built-in blur effect (`src/plugins/blur`), built
out of tree against the installed KWin, with features ported from
[Better Blur](https://github.com/taj-ny/kwin-effects-forceblur).

Why a fork instead of configuration: the stock effect only blurs behind
windows that ask for it and offers strength, noise and saturation. HoltOS
Glass is meant to blur behind *every* window, round the blurred corners to
match the window decoration, and control brightness/contrast so text on a
translucent window stays readable on any wallpaper. That needs code.

Plugin id: `holtosglass`. It replaces the stock blur — in `kwinrc`:

```
[Plugins]
blurEnabled=false
holtosglassEnabled=true

[Effect-holtosglass]
BlurStrength=15
NoiseStrength=0
Saturation=150
```

## Building

Needs the KWin development headers of the exact minor release the sources
were ported to (see the version check in `CMakeLists.txt`).

```
cmake -B build -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build
sudo cmake --install build
```

This tree lives in the HoltOS repo under `forks/holtos-glass-effect` and is
packaged by `packaging/holtos-glass-effect/PKGBUILD`, built into the
image's local package repo by `build-local-repo.sh`.

## Tracking KWin

KWin's effect API is private and changes between minor releases. When
HoltOS moves to a new Plasma minor, re-diff `src/` against that release's
`src/plugins/blur`, reapply the HoltOS changes (see the HoltOS repo's git log for this directory), and bump the
version range in `CMakeLists.txt`.

## License

GPL-3.0-or-later. Derived from KWin's blur effect (GPL-2.0-or-later,
copyright the KWin development team) and Better Blur (GPL-3.0-or-later).
