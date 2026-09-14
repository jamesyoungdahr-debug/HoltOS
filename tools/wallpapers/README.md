# HoltOS wallpaper pipeline

Renders, checks and packages the HoltOS neon wallpapers on LiamPC's RTX 4090.
Every prompt, seed and denoise strength lives in `wallpapers.json`, so any
wallpaper can be re-made exactly.

| Step | Command | What it does |
|---|---|---|
| Render | `python render.py --ids rain forest` | Claims the GPU through the local LLM scheduler (`comfy_hook.py`), queues every missing seed on ComfyUI (Z-Image-Turbo bf16, 1920x1088) and saves `renders/<id>-<w>x<h>-s<seed>.png`. `--seeds` tries extra seeds, `--size 2560x1440` another size, `--chosen` re-renders each approved choice. |
| Check | `python qa.py` | Flags blank renders, quadrants too dark to show colour through the glass, and near-duplicate seeds; writes `qa/report.json` and `qa/sheet-<id>.png` contact sheets. |
| Pick | edit `wallpapers.json` | Set `status` to `approved`, `chosen` to the seed and size, and `denoise` (about 0.3 photo-like, 0.6-0.7 flat graphics). |
| Package | `python package.py` | Claims the GPU, denoises and upscales with Real-ESRGAN general-x4v3 (blended with the wdn weights by `denoise`), resizes 1080p/1440p/4K from the float result with dithering, sharpens 1080p lightly, and writes JPEG quality 95 (4:4:4) plus `metadata.json` into `archiso/airootfs/usr/share/wallpapers/HoltOS-Neon-<Name>/`. |
| Preview | `python preview.py` | Mocks translucent blurred windows and the panel over each packaged wallpaper: `qa/preview-<Name>.png` and `qa/preview-sheet.png`. |

`qa.py` and `package.py` need numpy, Pillow (and for packaging torch + spandrel):
run them with ComfyUI's bundled Python,
`C:\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe`.
`render.py` and `preview.py` also run on the system Python.

Not in git (see `.gitignore`): `renders/`, `qa/` and `models/` (the Real-ESRGAN
`realesr-general-x4v3.pth` and `realesr-general-wdn-x4v3.pth` weights, from the
Real-ESRGAN v0.2.5.0 release).

Rules that apply (global image workflow standard in Liam's CLAUDE.md): free
models only; write positive scene prompts (Z-Image ignores negative wording);
three seeds per concept and let Liam pick; review at full size.
