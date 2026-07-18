#!/usr/bin/env python3
"""Generate per-room narration WAVs for the avatar presenter using XTTS-v2.

Clones Karen's voice from a short sample (assets/karen-voice-sample.wav) and
renders one 48 kHz mono WAV per room defined in room_scripts.json, written to
<model_dir>/video/presenters/<ImageStem>.wav so build_tour.py can find them.

Run inside the dedicated venv (see README):
    tools/avatar/.venv/Scripts/python.exe tools/avatar/make_narration.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.environ.get("AVATAR_CONFIG", os.path.join(HERE, "room_scripts.json"))


def load_config() -> dict:
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve(base: str, path: str) -> str:
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base, path))


def main() -> int:
    cfg = load_config()
    voice = resolve(HERE, cfg["voice_sample"])
    if not os.path.exists(voice):
        sys.exit(f"Voice sample not found: {voice}\nRecord a ~20s clean WAV of Karen first (see README).")

    out_dir = os.path.join(cfg["model_dir"], "video", "presenters")
    os.makedirs(out_dir, exist_ok=True)

    # Import here so the missing-sample check above fails fast without loading torch.
    import torch
    from TTS.api import TTS

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading XTTS-v2 on {device} ...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    lang = cfg.get("language", "en")
    for room in cfg["rooms"]:
        stem = os.path.splitext(os.path.basename(room["image"]))[0]
        out = os.path.join(out_dir, f"{stem}.wav")
        print(f"  -> {stem}.wav")
        tts.tts_to_file(
            text=room["script"],
            speaker_wav=voice,
            language=lang,
            file_path=out,
        )
    print(f"\nDone. {len(cfg['rooms'])} narration file(s) in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
