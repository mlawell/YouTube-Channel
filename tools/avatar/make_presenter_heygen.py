#!/usr/bin/env python3
"""Generate Karen presenter clips with HeyGen (paid, natural motion + gestures).

Alternative to make_presenter.py (SadTalker). HeyGen produces a waist-up avatar
with natural head/body motion from a single photo -- the quality target from the
reference tour. This script drives the HeyGen v2 API and, like the local path,
writes clips to <model_dir>/video/presenters/<ImageStem>.<ext> so build_tour.py
picks them up unchanged.

Setup (do NOT paste the key in chat / commit it):
    setx HEYGEN_API_KEY "your-key"          # or set for the session
    # Optional, if you pre-create them in the HeyGen dashboard:
    setx HEYGEN_TALKING_PHOTO_ID "..."      # Karen photo avatar id
    setx HEYGEN_AVATAR_ID "..."             # or a studio avatar id
    setx HEYGEN_VOICE_ID "..."              # Karen voice-clone id (else uses the room WAV)

Docs: https://docs.heygen.com/reference/create-an-avatar-video-v2

Run:
    tools/avatar/.venv/Scripts/python.exe tools/avatar/make_presenter_heygen.py
(any Python 3.9+ with `requests` works; no GPU needed).
"""
from __future__ import annotations

import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.environ.get("AVATAR_CONFIG", os.path.join(HERE, "room_scripts.json"))
API = "https://api.heygen.com"
UPLOAD = "https://upload.heygen.com"

API_KEY = os.environ.get("HEYGEN_API_KEY", "")
TALKING_PHOTO_ID = os.environ.get("HEYGEN_TALKING_PHOTO_ID", "")
AVATAR_ID = os.environ.get("HEYGEN_AVATAR_ID", "")
VOICE_ID = os.environ.get("HEYGEN_VOICE_ID", "")
# "transparent" (needs a plan that supports it) or a hex like "#00FF00" for green
# screen (build_tour / rembg can key it). Default green for broad compatibility.
BACKGROUND = os.environ.get("HEYGEN_BACKGROUND", "#00FF00")


def hdr(json_ct: bool = True) -> dict:
    h = {"X-Api-Key": API_KEY}
    if json_ct:
        h["Content-Type"] = "application/json"
    return h


def load_config() -> dict:
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve(base: str, path: str) -> str:
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base, path))


def upload_talking_photo(image_path: str) -> str:
    """Upload Karen's photo -> talking_photo_id."""
    ext = os.path.splitext(image_path)[1].lower()
    ctype = "image/png" if ext == ".png" else "image/jpeg"
    with open(image_path, "rb") as f:
        r = requests.post(f"{UPLOAD}/v1/talking_photo",
                          headers={"X-Api-Key": API_KEY, "Content-Type": ctype},
                          data=f.read(), timeout=120)
    r.raise_for_status()
    data = r.json().get("data", {})
    tp = data.get("talking_photo_id") or data.get("id")
    if not tp:
        sys.exit(f"talking_photo upload returned no id: {r.text[:300]}")
    print(f"  uploaded talking_photo_id={tp}")
    return tp


def upload_audio(wav_path: str) -> str:
    """Upload a narration WAV -> audio asset id (used when no VOICE_ID is set)."""
    with open(wav_path, "rb") as f:
        r = requests.post(f"{UPLOAD}/v1/asset",
                          headers={"X-Api-Key": API_KEY, "Content-Type": "audio/wav"},
                          data=f.read(), timeout=120)
    r.raise_for_status()
    data = r.json().get("data", {})
    aid = data.get("id") or data.get("asset_id")
    if not aid:
        sys.exit(f"audio upload returned no id: {r.text[:300]}")
    return aid


def character(talking_photo_id: str) -> dict:
    if AVATAR_ID:
        return {"type": "avatar", "avatar_id": AVATAR_ID, "avatar_style": "normal"}
    return {"type": "talking_photo", "talking_photo_id": talking_photo_id}


def voice_block(script: str, wav_path: str) -> dict:
    if VOICE_ID:
        return {"type": "text", "voice_id": VOICE_ID, "input_text": script}
    # Fall back to our XTTS narration WAV as an audio asset.
    return {"type": "audio", "audio_asset_id": upload_audio(wav_path)}


def background() -> dict:
    if BACKGROUND.lower() == "transparent":
        return {"type": "transparent"}
    return {"type": "color", "value": BACKGROUND}


def generate(talking_photo_id: str, script: str, wav_path: str) -> str:
    body = {
        "video_inputs": [{
            "character": character(talking_photo_id),
            "voice": voice_block(script, wav_path),
            "background": background(),
        }],
        "dimension": {"width": 720, "height": 1280},
    }
    r = requests.post(f"{API}/v2/video/generate", headers=hdr(),
                      data=json.dumps(body), timeout=60)
    r.raise_for_status()
    vid = r.json().get("data", {}).get("video_id")
    if not vid:
        sys.exit(f"generate returned no video_id: {r.text[:300]}")
    return vid


def wait_and_download(video_id: str, out_path: str, poll_s: int = 10, timeout_s: int = 900):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = requests.get(f"{API}/v1/video_status.get", headers=hdr(False),
                         params={"video_id": video_id}, timeout=30)
        r.raise_for_status()
        d = r.json().get("data", {})
        status = d.get("status")
        if status == "completed":
            url = d.get("video_url")
            vid = requests.get(url, timeout=300)
            vid.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(vid.content)
            return
        if status in ("failed", "error"):
            sys.exit(f"HeyGen job failed: {d.get('error') or r.text[:300]}")
        time.sleep(poll_s)
    sys.exit(f"HeyGen job timed out after {timeout_s}s (video_id={video_id})")


def main() -> int:
    if not API_KEY:
        sys.exit("Set HEYGEN_API_KEY (see the module docstring). Not provided.")
    cfg = load_config()
    portrait = resolve(HERE, cfg["portrait"])
    if not os.path.exists(portrait):
        sys.exit(f"Portrait not found: {portrait}")

    out_dir = os.path.join(cfg["model_dir"], "video", "presenters")
    os.makedirs(out_dir, exist_ok=True)

    ext = "webm" if BACKGROUND.lower() == "transparent" else "mp4"
    talking_photo_id = TALKING_PHOTO_ID or upload_talking_photo(portrait)

    made = 0
    for room in cfg["rooms"]:
        stem = os.path.splitext(os.path.basename(room["image"]))[0]
        wav = os.path.join(out_dir, f"{stem}.wav")
        if not VOICE_ID and not os.path.exists(wav):
            print(f"  skip {stem}: no narration WAV and no HEYGEN_VOICE_ID set")
            continue
        out = os.path.join(out_dir, f"{stem}.heygen.{ext}")
        print(f"  presenter -> {os.path.basename(out)}")
        vid = generate(talking_photo_id, room["script"], wav)
        wait_and_download(vid, out)
        made += 1

    print(f"\nDone. {made} HeyGen clip(s) in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
