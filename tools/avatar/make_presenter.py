#!/usr/bin/env python3
"""Generate transparent-background presenter clips with SadTalker + rembg.

For each room in room_scripts.json (that has a narration WAV from
make_narration.py), lip-syncs Karen's still portrait to the narration using
SadTalker, then mattes out the background per frame with rembg, producing a
ProRes 4444 (.mov, alpha) at <model_dir>/video/presenters/<ImageStem>.mov.

build_tour.py overlays that .webm on the matching room photo.

Prereqs (see README): dedicated venv, SadTalker cloned to tools/avatar/SadTalker
with checkpoints downloaded, and narration WAVs already generated.

Run:
    tools/avatar/.venv/Scripts/python.exe tools/avatar/make_presenter.py
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.environ.get("AVATAR_CONFIG", os.path.join(HERE, "room_scripts.json"))
SADTALKER_DIR = os.environ.get("SADTALKER_DIR", os.path.join(HERE, "SadTalker"))
FPS = 30


def load_config() -> dict:
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve(base: str, path: str) -> str:
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base, path))


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-2000:])
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"command failed ({r.returncode}): {cmd[0]}")
    return r


def register_cuda_dlls():
    """Put torch's bundled CUDA libs on PATH so onnxruntime-gpu (rembg) can find
    cublasLt64_12.dll etc. and matte on the GPU instead of falling back to CPU."""
    try:
        import torch
        libdir = os.path.join(os.path.dirname(torch.__file__), "lib")
        if os.path.isdir(libdir):
            try:
                os.add_dll_directory(libdir)
            except (AttributeError, OSError):
                pass
            os.environ["PATH"] = libdir + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass


def run_sadtalker(portrait: str, audio: str, result_dir: str, preprocess: str,
                  batch_size: int = 8) -> str:
    """Run SadTalker inference and return the path to the generated mp4."""
    py = sys.executable
    inference = os.path.join(SADTALKER_DIR, "inference.py")
    if not os.path.exists(inference):
        sys.exit(f"SadTalker not found at {SADTALKER_DIR} (set SADTALKER_DIR or clone it — see README).")
    os.makedirs(result_dir, exist_ok=True)
    run([
        py, inference,
        "--source_image", portrait,
        "--driven_audio", audio,
        "--result_dir", result_dir,
        "--preprocess", preprocess,
        "--still",
        "--enhancer", "gfpgan",
        "--size", "512",
        "--batch_size", str(batch_size),
    ], cwd=SADTALKER_DIR)
    mp4s = glob.glob(os.path.join(result_dir, "**", "*.mp4"), recursive=True)
    if not mp4s:
        sys.exit("SadTalker produced no mp4.")
    return max(mp4s, key=os.path.getmtime)


def matte_to_mov(src_mp4: str, out_mov: str, work: str):
    """Remove background per frame with rembg -> ProRes 4444 (alpha) mov at FPS."""
    register_cuda_dlls()  # let onnxruntime-gpu find CUDA -> matte on GPU
    from rembg import new_session, remove
    from PIL import Image

    raw = os.path.join(work, "raw")
    cut = os.path.join(work, "cut")
    os.makedirs(raw, exist_ok=True)
    os.makedirs(cut, exist_ok=True)

    run(["ffmpeg", "-y", "-i", src_mp4, "-vf", f"fps={FPS}",
         os.path.join(raw, "%05d.png")])

    session = new_session("u2net_human_seg")
    frames = sorted(glob.glob(os.path.join(raw, "*.png")))
    if not frames:
        sys.exit("No frames extracted from SadTalker output.")
    for f in frames:
        img = Image.open(f)
        out = remove(img, session=session, post_process_mask=True)
        out.save(os.path.join(cut, os.path.basename(f)))

    # Encode the matted frames as ProRes 4444 with alpha. NOTE: this ffmpeg
    # build's libvpx/libvpx-vp9 silently drops the alpha channel (transparent ->
    # black), so VP9/webm is unusable here; ProRes 4444 (.mov) preserves alpha
    # reliably and ffmpeg overlays it directly. Narration audio lives in the
    # sibling .wav (build_tour.py mixes it), so this clip is video-only.
    run([
        "ffmpeg", "-y",
        "-framerate", str(FPS), "-i", os.path.join(cut, "%05d.png"),
        "-an", "-c:v", "prores_ks", "-profile:v", "4444",
        "-pix_fmt", "yuva444p10le",
        out_mov,
    ])


def main() -> int:
    cfg = load_config()
    portrait = resolve(HERE, cfg["portrait"])
    if not os.path.exists(portrait):
        sys.exit(f"Portrait not found: {portrait}")
    preprocess = cfg.get("defaults", {}).get("preprocess", "full")
    batch_size = int(cfg.get("defaults", {}).get("batch_size", 8))

    out_dir = os.path.join(cfg["model_dir"], "video", "presenters")
    os.makedirs(out_dir, exist_ok=True)

    made = 0
    for room in cfg["rooms"]:
        stem = os.path.splitext(os.path.basename(room["image"]))[0]
        audio = os.path.join(out_dir, f"{stem}.wav")
        out_mov = os.path.join(out_dir, f"{stem}.mov")
        if not os.path.exists(audio):
            print(f"  skip {stem}: no narration WAV (run make_narration.py first)")
            continue
        print(f"  presenter -> {stem}.mov")
        # Stage heavy frame I/O locally, not on the network share.
        with tempfile.TemporaryDirectory(prefix=f"pres_{stem}_") as work:
            talk = run_sadtalker(portrait, audio, os.path.join(work, "sadtalker"), preprocess, batch_size)
            matte_to_mov(talk, out_mov, work)
        made += 1

    print(f"\nDone. {made} presenter clip(s) in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
