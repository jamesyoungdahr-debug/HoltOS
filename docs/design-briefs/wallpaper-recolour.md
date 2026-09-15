# Neon wallpaper recolour (2026-09-15)

Liam: "keep them the same but incorporate the new colours." The ten
`HoltOS-Neon-*` wallpapers keep their composition and get the neon rebrand's
colours. This is a reprocessing pass over the chosen art, not a new render.

## Method

Z-Image-Turbo img2img, built from the saved txt2img graph
(`holtos/z-image-turbo.json` in ComfyUI's library):

- `LoadImage` (the packaged `1920x1080.jpg` of the wallpaper) > `VAEEncode`
  into the `KSampler`'s latent, instead of an empty latent.
- `ModelSamplingAuraFlow` shift 3, cfg 1, `res_multistep` / `simple`,
  8 steps, Z-Image-Turbo bf16 + `qwen_3_4b` + `ae.safetensors`.
- Seed = the wallpaper's own seed in `wallpapers.json`, so a wallpaper is
  reproducible.
- Denoise is the only retouch control: 0.6 / 0.7 / 0.8 were rendered per
  wallpaper. 0.35-0.5 is too weak to matter - at cfg 1 the base image beats
  the colour words in the prompt, so a low-denoise recolour barely moves.

## Palette

The art colours from `docs/holtos-brand.md`: purple `#B14DFF`, magenta
`#FF4FD8`, electric blue `#4F7BFF`, teal `#28E0C8`, lime `#C6FF3D`, over the
near-black ground `#0D0B12`. Lime is a rare spark, never a background.

## Findings

- 27 of 30 candidates were good from one batch with a single shared
  colour-forward prompt.
- `otter-night` failed all three at 0.7 and above: with no "otter" in the
  prompt the subject was replaced by a human figure. Both mascot wallpapers
  (`otter`, `otter-night`) were re-rendered with prompts that name the otter.
- **Rule: above about 0.6 the prompt must name the subject, or the subject
  drifts.** Keep the per-wallpaper prompt from `wallpapers.json` in play and
  add the colour wording to it.

## Candidates

In ComfyUI's `output/holtos/` on LiamPC:

- `recol-<id>-d{6,7,8}_00001_.png` for the eight without a mascot.
- `recol2-<id>-d{6,7,8}_00001_.png` for `otter` and `otter-night`.

Not committed to the repo. Awaiting Liam's pick of one denoise per wallpaper;
`tools/wallpapers/package.py` then regenerates the packaged sizes from the
chosen files.