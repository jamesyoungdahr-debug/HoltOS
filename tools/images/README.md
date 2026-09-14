# HoltOS image renders

`zimage.py` renders logos, icons, mockups and concept art with Z-Image-Turbo on
LiamPC's ComfyUI (RTX 4090). Wallpapers keep their own pipeline in
`tools/wallpapers/`.

    python tools/images/zimage.py --prompt "..." --out renders/logo --name logo --size 1024x1024
    python tools/images/zimage.py --prompt-file brief.txt --out renders/mockup --seeds 4101 4102 4103

- Images render only on the 4090. The script claims ComfyUI's lease from the
  LLM scheduler first (`comfy_hook.py`); `--no-claim` skips that, for re-runs
  that only need already-saved files.
- Output: `<out>/<name>-<w>x<h>-s<seed>.png`. Files that already exist are
  skipped, so a run can be repeated safely.
- Sizes must be multiples of 16; the default is 1920x1088. Three seeds per
  concept by default.
- Write positive, descriptive prompts: at cfg 1 Z-Image ignores negative
  wording.
- The same graph is saved in ComfyUI's workflow library as
  `holtos/z-image-turbo.json`, for the web UI and the comfyui MCP
  (`enqueue_workflow`). ComfyUI MCP's `generate_image` cannot run Z-Image: it
  only builds checkpoint graphs.
- Finished deliverables go through the wallpaper pipeline's denoise, upscale
  and JPEG steps (`tools/wallpapers/package.py`).
