"""Turn approved renders into HoltOS Plasma wallpaper packages, on the RTX 4090.

    C:\\ComfyUI\\ComfyUI_windows_portable\\python_embeded\\python.exe package.py [--ids rain den] [--format png] [--cpu]

Claims the GPU first (gpu_switch.py to-comfy, which unloads LM Studio), then
for each wallpaper: centre-crops the chosen render to 16:9, upscales 4x with
Real-ESRGAN general-x4v3 blended with the weak-denoise variant by the
wallpaper's "denoise" value (1 = strongest grain removal, 0 = keeps
texture), resizes every size from the float result, dithers so dark
gradients do not band, sharpens 1080p lightly and saves JPEG (quality 95,
full colour detail) plus metadata.json.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import numpy as np
import torch
from PIL import Image, ImageFilter
from spandrel import ModelLoader

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CONFIG = HERE / "wallpapers.json"
RENDERS = HERE / "renders"
MODELS = HERE / "models"
DEST_ROOT = REPO / "archiso" / "airootfs" / "usr" / "share" / "wallpapers"
SWITCH = Path(r"C:\projects\gpu-switch\gpu_switch.py")
SIZES = [(1920, 1080), (2560, 1440), (3840, 2160)]
PAD = 16


def claim_gpu() -> None:
    r = subprocess.run([sys.executable, str(SWITCH), "to-comfy"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("could not claim the GPU: " + (r.stderr or r.stdout).strip())
    print(r.stdout.strip())


class Upscaler:
    def __init__(self, device: str):
        for name in ("realesr-general-x4v3.pth", "realesr-general-wdn-x4v3.pth"):
            if not (MODELS / name).exists():
                sys.exit(f"missing {MODELS / name} (Real-ESRGAN v0.2.5.0 weights)")
        self.model = ModelLoader().load_from_file(str(MODELS / "realesr-general-x4v3.pth")).eval()
        self.strong = {k: v.clone() for k, v in self.model.model.state_dict().items()}
        self.weak = ModelLoader().load_from_file(str(MODELS / "realesr-general-wdn-x4v3.pth")).model.state_dict()
        self.device = device
        self.model.to(device)
        self.scale = self.model.scale
        self.tile = 1024 if device == "cuda" else 512

    def set_denoise(self, dn: float) -> None:
        blended = {k: dn * self.strong[k] + (1 - dn) * self.weak[k] for k in self.strong}
        self.model.model.load_state_dict(blended)  # tensors are on CPU; load_state_dict copies into the device weights

    @torch.inference_mode()
    def upscale(self, img: Image.Image) -> torch.Tensor:
        x = torch.from_numpy(np.asarray(img, dtype=np.float32) / 255).permute(2, 0, 1)[None]
        h, w = x.shape[2:]
        s = self.scale
        out = torch.zeros((1, 3, h * s, w * s))
        for y0 in range(0, h, self.tile):
            for x0 in range(0, w, self.tile):
                y1, x1 = min(y0 + self.tile, h), min(x0 + self.tile, w)
                py0, px0 = max(y0 - PAD, 0), max(x0 - PAD, 0)
                py1, px1 = min(y1 + PAD, h), min(x1 + PAD, w)
                t = self.model(x[:, :, py0:py1, px0:px1].to(self.device)).float().cpu()
                oy, ox = (y0 - py0) * s, (x0 - px0) * s
                out[:, :, y0*s:y1*s, x0*s:x1*s] = t[:, :, oy:oy + (y1-y0)*s, ox:ox + (x1-x0)*s]
        return out.clamp(0, 1)


def crop_16_9(img) -> Image:
    w, h = img.size
    ch = round(w * 9 / 16)
    if ch <= h:
        top = (h - ch) // 2
        return img.crop((0, top, w, top + ch))
    cw = round(h * 16 / 9)
    left = (w - cw) // 2
    return img.crop((left, 0, left + cw, h))


def render_size(big: torch.Tensor, sw: int, sh: int, seed: int) -> Image:
    y = torch.nn.functional.interpolate(big, size=(sh, sw), mode="bicubic", antialias=True, align_corners=False).clamp(0, 1)[0].permute(1, 2, 0).numpy()
    rng = np.random.default_rng(seed)
    noise = (rng.random(y.shape, dtype=np.float32) - rng.random(y.shape, dtype=np.float32)) / 255
    img = Image.fromarray(np.clip(np.round((y + noise) * 255), 0, 255).astype(np.uint8))
    if (sw, sh) == (1920, 1080):
        img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=35, threshold=2))
    return img


def package(entry: dict, up: Upscaler, fmt: str) -> None:
    name = entry["name"]
    slug = name.replace(" ", "")
    c = entry.get("chosen")
    if not c:
        print(f"skip {entry['id']}: no chosen render")
        return
    src = RENDERS / f"{entry['id']}-{c['width']}x{c['height']}-s{c['seed']}.png"
    if not src.exists():
        print(f"skip {entry['id']}: {src.name} not found")
        return
    dn = float(entry.get("denoise", 0.5))
    print(f"== {entry['id']} -> HoltOS-Neon-{slug} (denoise {dn})")
    up.set_denoise(dn)
    big = up.upscale(crop_16_9(Image.open(src).convert("RGB")))
    pkg = DEST_ROOT / f"HoltOS-Neon-{slug}"
    images = pkg / "contents" / "images"
    images.mkdir(parents=True, exist_ok=True)
    for (sw, sh) in SIZES:
        img = render_size(big, sw, sh, c["seed"])
        other = images / f"{sw}x{sh}.{'png' if fmt == 'jpg' else 'jpg'}"
        if other.exists():
            other.unlink()
        path = images / f"{sw}x{sh}.{fmt}"
        if fmt == "jpg":
            img.save(path, "JPEG", quality=95, subsampling=0, optimize=True, progressive=True)
        else:
            img.save(path, optimize=True)
        print(f"  {path.relative_to(REPO)}  {path.stat().st_size // 1024} KiB")
    (pkg / "metadata.json").write_text(json.dumps({"KPackageStructure": "Plasma/Wallpaper", "KPlugin": {"Id": f"HoltOS-Neon-{slug}", "Name": f"HoltOS Neon {name}"}}, indent=4) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="+")
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg")
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    entries = config["wallpapers"]
    if args.ids:
        known = {e["id"] for e in entries}
        unknown = [i for i in args.ids if i not in known]
        if unknown:
            sys.exit("unknown ids: " + ", ".join(unknown))
        entries = [e for e in entries if e["id"] in args.ids]
    else:
        entries = [e for e in entries if e.get("status") == "approved"]
    if not entries:
        sys.exit("nothing to package")
    device = "cpu" if args.cpu or not torch.cuda.is_available() else "cuda"
    if device == "cuda":
        claim_gpu()
    else:
        torch.set_num_threads(os.cpu_count() or 8)
    up = Upscaler(device)
    for e in entries:
        package(e, up, args.format)


if __name__ == "__main__":
    main()
