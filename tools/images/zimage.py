"""HoltOS image renderer for LiamPC's ComfyUI (Z-Image-Turbo on RTX 4090).

Purpose: general command-line renderer for logos, icons, mockups and concept art.
Wallpapers keep their own tools/wallpapers pipeline.

Usage examples:
    python tools/images/zimage.py --prompt "..." --out renders/logo \\
        --seeds 4101 4102 4103 --size 1024x1024
    python tools/images/zimage.py --prompt-file brief.txt --out renders/mockup

Rules:
- Renders only on LiamPC's RTX 4090 through the LLM scheduler's comfy lease.
- Free local models only.
- Positive descriptive prompts (Z-Image ignores negative wording at cfg 1).
- Three seeds per concept.
- Review at full size.
- Finished deliverables go through the wallpaper package step
  (denoise, upscale, JPEG q95).
- The same graph is saved in ComfyUI's workflow library as holtos/z-image-turbo.json.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from subprocess import run

COMFY = "http://127.0.0.1:8188"
HOOK = Path(r"C:\projects\llm-scheduler\comfy_hook.py")
JOB_TIMEOUT = 600.0


def graph(prompt, width, height, seed, prefix, steps=8):
    """Return the ComfyUI API graph dict for Z-Image-Turbo."""
    return {
        "28": {
            "class_type": "UNETLoader",
            "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"},
        },
        "30": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"},
        },
        "29": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "ae.safetensors"},
        },
        "11": {
            "class_type": "ModelSamplingAuraFlow",
            "inputs": {"shift": 3, "model": ["28", 0]},
        },
        "27": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["30", 0]},
        },
        "33": {
            "class_type": "ConditioningZeroOut",
            "inputs": {"conditioning": ["27", 0]},
        },
        "13": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 1,
                "sampler_name": "res_multistep",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["11", 0],
                "positive": ["27", 0],
                "negative": ["33", 0],
                "latent_image": ["13", 0],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["29", 0]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": prefix, "images": ["8", 0]},
        },
    }


def http_json(url, body=None, timeout=30):
    """GET when body is None else POST JSON; return parsed JSON."""
    if body is None:
        req = urllib.request.Request(url)
    else:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def claim_gpu():
    """Run the comfy_hook to lease the GPU; exit on failure."""
    r = run([sys.executable, str(HOOK)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Could not claim the GPU for ComfyUI: " + (r.stderr or r.stdout).strip())


def parse_size(text):
    """Parse 'WxH' string; both must be positive multiples of 16."""
    parts = text.lower().split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"Invalid size format '{text}', expected WxH")
    try:
        w, h = int(parts[0]), int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(f"Non-integer dimensions in '{text}'")
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError(f"Dimensions must be positive in '{text}'")
    if w % 16 != 0 or h % 16 != 0:
        raise argparse.ArgumentTypeError(
            f"Both dimensions must be multiples of 16 in '{text}'"
        )
    return (w, h)


def render(prompt, out_dir, name, size, seeds, steps):
    """Submit jobs for each seed and download results; return saved paths."""
    w, h = size
    targets = []
    prompt_ids = []

    for seed in seeds:
        target = out_dir / f"{name}-{w}x{h}-s{seed}.png"
        if target.exists():
            print(f"exists {target}")
            targets.append(target)
            continue
        prefix = f"holtos-images/{name}-s{seed}"
        g = graph(prompt, w, h, seed, prefix, steps)
        resp = http_json(COMFY + "/prompt", body={"prompt": g})
        prompt_ids.append((resp["prompt_id"], target))

    if not prompt_ids:
        return targets

    finished = set()
    deadline = time.time() + JOB_TIMEOUT

    while len(finished) < len(prompt_ids) and time.time() < deadline:
        for pid, tgt in prompt_ids:
            if pid in finished:
                continue
            try:
                history = http_json(COMFY + "/history/" + pid)
            except Exception:
                time.sleep(2)
                continue
            if pid not in history:
                continue
            entry = history[pid]
            outputs = entry.get("outputs", {})
            for node_out in outputs.values():
                for img_info in node_out.get("images", []):
                    filename = img_info["filename"]
                    subfolder = img_info.get("subfolder", "")
                    img_type = img_info.get("type", "output")
                    view_url = COMFY + "/view?" + urllib.parse.urlencode(
                        {"filename": filename, "subfolder": subfolder, "type": img_type}
                    )
                    with urllib.request.urlopen(view_url, timeout=60) as resp:
                        data = resp.read()
                    tgt.write_bytes(data)
                    print(f"saved {tgt}")
                    targets.append(tgt)
            finished.add(pid)
        time.sleep(2)

    unfinished = [tgt for pid, tgt in prompt_ids if pid not in finished]
    if unfinished:
        sys.exit("Timed out waiting for:\n  " + "\n  ".join(str(p) for p in unfinished))

    return targets


def main():
    """Parse args and run the render pipeline."""
    parser = argparse.ArgumentParser(description="HoltOS Z-Image-Turbo renderer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", help="Positive descriptive prompt text")
    group.add_argument("--prompt-file", help="Path to file containing the prompt (UTF-8)")
    parser.add_argument("--out", required=True, type=Path, help="Output directory")
    parser.add_argument("--name", default="image", help="Base name for output files")
    parser.add_argument(
        "--size", type=parse_size, default="1920x1088", help="WxH in pixels (multiples of 16)"
    )
    parser.add_argument(
        "--seeds", type=int, nargs="+", default=[4101, 4102, 4103], help="Seed values"
    )
    parser.add_argument("--steps", type=int, default=8, help="Sampling steps")
    parser.add_argument(
        "--no-claim", action="store_true", help="Skip GPU claim step"
    )
    args = parser.parse_args()

    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    else:
        prompt = args.prompt

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_claim:
        claim_gpu()

    render(prompt, out_dir, args.name, args.size, args.seeds, args.steps)


if __name__ == "__main__":
    main()
