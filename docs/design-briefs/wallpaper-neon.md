# Brief: HoltOS neon wallpapers (for ComfyUI)

Status: waiting on the ComfyUI machine (unreachable twice, 2026-09-13).

## Why
The shipped pool-rings and corner-otter wallpapers are almost solid black, so
KWin's blur has no colour to reveal and HoltOS Glass looks flat. Liam wants a
neon-light style: bright glowing colour that turns into a soft wash behind
frosted windows and panels.

## Brand
- Base: deep ink `#0D0B12` to `#171423`.
- Neon colours: accent purple `#B14DFF`, deep purple `#8F2FE0`, teal
  `#28E0C8`, amber `#FFB84D` used sparingly, lilac `#F4EBFF` for hot cores.
- Marks: purple ring mark; friendly rounded otter (optional, subtle).
- Style: minimal and clean, not busy. Glow must stay recognisable once
  blurred (large soft shapes, no fine detail doing the work).

## Concepts (make 3)
1. Neon rings: the HoltOS ring mark as glowing neon tubes, off-centre, with
   purple and teal bloom spilling across the frame.
2. Neon otter sign: a simple otter outline as a neon sign in the lower right,
   purple tube with teal accents, soft haze on a dark wall.
3. Abstract neon flow: sweeping purple-to-teal light ribbons with a faint
   amber highlight, glow reaching every quadrant.

## Rules
- Colour in all four quadrants so any window position shows it through blur.
- Keep the upper-left and centre calm enough for desktop icons and text.
- No text, no logos other than the marks above, no photo-real clutter.
- 16:9, render 1920x1080 then upscale 2x to 3840x2160; also export
  2560x1440. Ships as `usr/share/wallpapers/HoltOS-Neon*/contents/images/`.
- Review: set each on the VM and screenshot Dolphin and the panel over it to
  confirm the colour reads through the glass.
