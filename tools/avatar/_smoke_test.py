"""Smoke-test build_tour's presenter compositing + multi-voice audio mix
using synthetic placeholder assets (no real gallery / SadTalker needed)."""
import importlib.util
import os
import subprocess
import sys
import tempfile

BT_PATH = r"R:\YouTube-Channel\tools\video\build_tour.py"


def ff(args):
    r = subprocess.run(["ffmpeg", "-y", *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit("ffmpeg asset gen failed")


def main():
    work = tempfile.mkdtemp(prefix="pres_test_")
    gallery = os.path.join(work, "gallery")
    pres = os.path.join(work, "video", "presenters")
    os.makedirs(gallery, exist_ok=True)
    os.makedirs(pres, exist_ok=True)

    # two room photos
    ff(["-f", "lavfi", "-i", "color=c=slateblue:s=1600x1000:d=1", "-frames:v", "1",
        os.path.join(gallery, "Great Room.jpg")])
    ff(["-f", "lavfi", "-i", "color=c=seagreen:s=1600x1000:d=1", "-frames:v", "1",
        os.path.join(gallery, "Kitchen.jpg")])

    # transparent presenter webm (opaque box padded with a transparent border) + audio
    ff(["-f", "lavfi", "-i", "color=c=orange:s=200x360:d=3:r=30",
        "-f", "lavfi", "-i", "sine=frequency=330:duration=3",
        "-vf", "format=yuva420p,pad=260:420:30:30:color=black@0.0",
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30",
        "-c:a", "libopus", os.path.join(pres, "Great Room.webm")])
    ff(["-f", "lavfi", "-i", "sine=frequency=330:duration=3",
        os.path.join(pres, "Great Room.wav")])

    # music bed
    music_dir = os.path.join(work, "video", "music")
    os.makedirs(music_dir, exist_ok=True)
    music = os.path.join(music_dir, "test.mp3")
    ff(["-f", "lavfi", "-i", "sine=frequency=220:duration=30", music])

    # load build_tour and redirect its constants at the synthetic set
    spec = importlib.util.spec_from_file_location("build_tour", BT_PATH)
    bt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bt)

    bt.GALLERY = gallery
    bt.VIDEO_DIR = os.path.join(work, "video")
    bt.PRESENTER_DIR = pres
    bt.MUSIC = music
    bt.DISCLAIMER = os.path.join(work, "nope-disclaimer.png")
    bt.GOLDEN = os.path.join(work, "nope-golden.mp4")
    bt.KAREN = os.path.join(work, "nope-karen.mp4")
    bt.CONTACT_CARD = os.path.join(work, "nope-contact.jpg")
    bt.OUT_FILE = os.path.join(work, "test-tour.mp4")
    bt.TOUR = [("Great Room.jpg", "Sunlit Great Room"), ("Kitchen.jpg", "Chef Kitchen")]

    bt.main()

    out = bt.OUT_FILE
    ok = os.path.exists(out) and os.path.getsize(out) > 0
    if ok:
        info = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=codec_type,codec_name", "-of", "default=nw=1", out],
            capture_output=True, text=True).stdout
        print("\n=== OUTPUT OK ===")
        print(out)
        print(info)
    else:
        raise SystemExit("no output produced")


if __name__ == "__main__":
    main()
