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

## Concepts: a suite of 10 (Liam, 2026-09-13)
One family: same palette, glow softness and calm upper-left, so any of them
can be the default. Each ships as its own wallpaper package.
1. Neon Rings: the HoltOS ring mark as glowing neon tubes, off-centre, with
   purple and teal bloom spilling across the frame.
2. Neon Otter: a simple otter outline as a neon sign in the lower right,
   purple tube with teal accents, soft haze on a dark wall.
3. Neon Flow: sweeping purple-to-teal light ribbons with a faint amber
   highlight, glow reaching every quadrant.
4. Neon Pool: concentric ripple rings on dark water, purple and teal
   reflections (the old pool-rings idea, now bright).
5. Neon Horizon: a low synthwave-style horizon line and grid in purple with a
   teal-to-amber glow above it, no sun disc or text.
6. Neon Aurora: soft vertical curtains of teal and purple light across a dark
   sky.
7. Neon Den: a cosy dark room corner lit by a small purple neon ring and a
   teal strip light, glow washing the walls (media and gaming mood).
8. Neon Bokeh: large out-of-focus purple, teal and amber light circles.
9. Neon Circuit: sparse rounded light traces in purple and teal meeting at a
   glowing ring node, bottom-right weighted.
10. Neon Otter Night: the otter mark small and low-right, floating on a dark
    river that reflects purple and teal neon.

## Rules
- Colour in all four quadrants so any window position shows it through blur.
- Keep the upper-left and centre calm enough for desktop icons and text.
- No text, no logos other than the marks above, no photo-real clutter.
- 16:9, render 1920x1080 then upscale 2x to 3840x2160; also export
  2560x1440. Ships as `usr/share/wallpapers/HoltOS-Neon*/contents/images/`.
- Review: set each on the VM and screenshot Dolphin and the panel over it to
  confirm the colour reads through the glass.
