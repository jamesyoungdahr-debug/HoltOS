"""Render HoltOS wallpapers on the local ComfyUI (RTX 4090) from wallpapers.json.

    python render.py --ids rain forest               every seed listed for these wallpapers
    python render.py --ids rain --size 2560x1440     same seeds at another size
    python render.py --ids nebula --seeds 3137 3138  extra seeds (wallpapers.json is not changed)
    python render.py --chosen                        (re)render each approved wallpaper's chosen render

Claims the GPU through the local LLM scheduler first (comfy_hook.py), queues every
missing render at once, waits for them and saves renders/<id>-<w>x<h>-s<seed>.png.
Renders that already exist are skipped.
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "wallpapers.json"
RENDERS = HERE / "renders"
HOOK = Path(r"C:\projects\llm-scheduler\comfy_hook.py")
JOB_TIMEOUT = 600.


def graph(prompt: str, width: int, height: int, seed: int, prefix: str) -> dict:
    """Return the Z-Image-Turbo ComfyUI API graph."""
    return {
        "28": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "30": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}},
        "29": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "11": {"class_type": "ModelSamplingAuraFlow", "inputs": {"shift": 3, "model": ["28", 0]}},
        "27": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["30", 0]}},
        "33": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["27", 0]}},
        "13": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1, "model": ["11", 0], "positive": ["27", 0], "negative": ["33", 0], "latent_image": ["13", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["29", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["8", 0]}}
    }


def http_json(url: str, body: dict | None = None, timeout: float = 30) -> dict:
    """GET when body is None, else POST json with Content-Type application/json; return parsed JSON."""
    if body is None:
        req = urllib.request.Request(url)
    else:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def claim_gpu() -> None:
    """Claim the GPU through the local LLM scheduler."""
    r = subprocess.run([sys.executable, str(HOOK)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Could not claim the GPU for ComfyUI: " + (r.stderr or r.stdout).strip())


def load_config() -> dict:
    """Load and return the wallpapers configuration."""
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def build_targets(cfg: dict, ids: list[str] | None, size: str | None, chosen: bool, seeds: list[int] | None) -> list[tuple[str, int, int, int, str]]:
    """Build the list of (id, width, height, seed, prompt) targets to render."""
    entries = cfg["wallpapers"]
    known_ids = {e["id"] for e in entries}

    if ids is not None:
        unknown = [i for i in ids if i not in known_ids]
        if unknown:
            sys.exit("unknown ids: " + ", ".join(unknown))

    def prompt_for(e):
        return e["prompt"] + " " + cfg["style"] if e.get("use_style", True) else e["prompt"]

    targets = []

    if chosen:
        for e in entries:
            if ids is not None and e["id"] not in known_ids:
                continue
            if ids is not None and e["id"] not in set(ids):
                continue
            if e.get("status") != "approved":
                continue
            chosen_dict = e.get("chosen")
            if not isinstance(chosen_dict, dict):
                continue
            targets.append((e["id"], chosen_dict["width"], chosen_dict["height"], chosen_dict["seed"], prompt_for(e)))
    else:
        if ids is None:
            sys.exit("use --ids or --chosen")

        if size is not None:
            w, h = (int(v) for v in size.split("x"))
        else:
            w = cfg["render"]["width"]
            h = cfg["render"]["height"]

        selected_ids = set(ids)
        for e in entries:
            if e["id"] not in selected_ids:
                continue
            seed_list = seeds if seeds is not None else e.get("seeds", [])
            for seed in seed_list:
                targets.append((e["id"], w, h, seed, prompt_for(e)))

    return targets


def main() -> None:
    """Parse args, claim GPU, queue missing renders, wait and download."""
    parser = argparse.ArgumentParser(description="Render HoltOS wallpapers on the local ComfyUI")
    parser.add_argument("--ids", nargs="+", help="Wallpaper IDs to render")
    parser.add_argument("--size", help="Size like '2560x1440'")
    parser.add_argument("--chosen", action="store_true", help="(Re)render each approved choice")
    parser.add_argument("--seeds", nargs="+", type=int, help="Extra seeds to use instead of those in wallpapers.json")
    args = parser.parse_args()

    cfg = load_config()
    comfy = cfg.get("comfy_url", "http://127.0.0.1:8188").rstrip("/")
    RENDERS.mkdir(parents=True, exist_ok=True)

    targets = build_targets(cfg, args.ids, args.size, args.chosen, args.seeds)

    todo = []
    for id_, w, h, seed, prompt in targets:
        name = f"{id_}-{w}x{h}-s{seed}"
        if (RENDERS / f"{name}.png").exists():
            print(f"have {name}")
        else:
            todo.append((name, w, h, seed, prompt))

    if not todo:
        print("nothing to render")
        return

    claim_gpu()

    jobs = {}
    for name, w, h, seed, prompt in todo:
        pid = http_json(f"{comfy}/prompt", {"prompt": graph(prompt, w, h, seed, f"holtos-{name}")})["prompt_id"]
        jobs[pid] = name
        print(f"queued {name}", flush=True)

    start = time.monotonic()
    deadline = start + JOB_TIMEOUT * len(jobs)
    failures = 0

    while jobs and time.monotonic() < deadline:
        for pid, name in list(jobs.items()):
            h = http_json(f"{comfy}/history/{pid}").get(pid)
            if not h:
                continue
            status = h.get("status", {})
            if status.get("completed"):
                img = h["outputs"]["9"]["images"][0]
                q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
                with urllib.request.urlopen(f"{comfy}/view?{q}", timeout=60) as r:
                    (RENDERS / f"{name}.png").write_bytes(r.read())
                print(f"saved {name} ({time.monotonic() - start:.0f}s)", flush=True)
                del jobs[pid]
            elif status.get("status_str") == "error":
                failures += 1
                print(f"FAILED {name}: {json.dumps(status.get('messages', []))[:300]}", flush=True)
                del jobs[pid]
        time.sleep(1)

    for name in jobs.values():
        failures += 1
        print(f"TIMED OUT {name}")

    print("next: python qa.py")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
