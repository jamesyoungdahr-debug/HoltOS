# Neon wallpapers: five-colour palette (2026-09-15)

Liam's ask began as "keep them the same but incorporate the new colours". The
recolour pass came back weak — the new colours were barely present — so Liam
ruled: "lets just generate new ones and not use the source". **Final method:
fresh txt2img renders.** The img2img notes below are kept as history.

## Method

Z-Image-Turbo txt2img through the saved graph `holtos/z-image-turbo.json`
(`UNETLoader > ModelSamplingAuraFlow shift 3 > KSampler`; cfg 1,
`res_multistep` / `simple`, 8 steps, `ConditioningZeroOut` as the negative),
rendered at 1920x1088, three seeds per wallpaper, with the palette colours
named in every prompt. Queued with the comfyui MCP (`batch` /
`enqueue_workflow`) while holding a scheduler `comfy` lease taken by hand — in
the desktop app's third-party mode the `comfy_hook` does not run, so the lease
is manual.

## Palette

The art colours from `docs/holtos-brand.md`: purple `#B14DFF`, magenta
`#FF4FD8`, electric blue `#4F7BFF`, teal `#28E0C8`, lime `#C6FF3D`, over the
near-black ground `#0D0B12`.

## Findings

- **A palette colour must be a prominent, natural element of the scene.** Lime
  rendered cleanly as an aurora curtain, forest bioluminescence, nebula wisps
  and a cabin sky-glow — and not at all when asked for as a small accent (a
  lime LED strip, "a few lime sparks"), or as a flat rectangle and garbled text
  when pushed harder. Purple, magenta, electric blue and teal land readily in
  any scene.
- **An img2img recolour cannot reliably introduce new hues.** At cfg 1 the base
  image beats the colour words: 0.35-0.5 barely moves, and 0.6-0.8 mostly
  re-asserts the original purple and teal. Above about 0.6 the prompt must name
  the subject or the subject drifts (the otter became a human figure). This is
  why the recolour was dropped.
- **A deterministic hue-remap plus spark pass was rejected.** It tints the
  brightest pixels and reads as hot-spots on the subject rather than neon —
  the script was written, rejected and deleted (`e52bce5`).

## Gotcha

The Real-ESRGAN weights are not in this worktree. They live in the master
checkout's `tools/wallpapers/models/`; copy them in before running
`package.py`, which otherwise exits with "missing ... x4v3.pth".

## Final set

Six wallpapers carry the four-colour palette (rings, otter, den, bokeh,
otter-night, rain) and four carry natural lime as well (aurora, forest, nebula,
cabin); the otter logo stays purple by design. Packaged by
`tools/wallpapers/package.py` to 1920x1080 / 2560x1440 / 3840x2160 (JPEG q95,
4:4:4). Shipped as commit `c90fafb` on `neon-rebrand`.
