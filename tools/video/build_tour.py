#!/usr/bin/env python3
"""Build a crystal-clear Ken Burns real-estate tour (1080p) for a model.

Structure (Trinidad Bay):
  1. Disclaimer (held)
  2. Golden Hour AI Transition.mp4
  3. Karen AI Avatar Intro.mp4  (keeps its voiceover audio, timed correctly)
    4. Hero exterior w/ title -> beat-synced room tour -> readable Floor Plan pan
  5. Contact Card (held)

Quality: Lanczos scaling, 2x supersampled Ken Burns canvas, very gentle slow
zoom, light unsharp. All segments normalized to 1920x1080 / 30fps / yuv420p and
crossfaded. ffmpeg / ffprobe must be on PATH. No external Python deps.
"""
import json
import os
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------- configuration
DOCS = r"C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents"
MODEL_DIR = os.path.join(
    DOCS, r"Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Latitude Margaritaville Watersound\Models\Island Collection - Single-Family Homes\Trinidad Bay"
)
GALLERY = os.path.join(MODEL_DIR, "gallery")
VIDEO_DIR = os.path.join(MODEL_DIR, "video")
CONTACT_CARD = os.path.join(DOCS, r"Marketing\Contact Cards\Contact Card 1920 x 1080.jpg")
DISCLAIMER = os.path.join(DOCS, r"Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Latitude Margaritaville Watersound\Disclaimer 1080.png")
GOLDEN = os.path.join(VIDEO_DIR, "Golden Hour AI Transition.mp4")
KAREN = os.path.join(VIDEO_DIR, "Karen AI Avatar Intro.mp4")
MUSIC = os.path.join(VIDEO_DIR, "music", "Ragga L Cool Island.mp3")

OUT_FILE = os.path.join(VIDEO_DIR, "Trinidad Bay - Home Tour.mp4")

# In-room AI presenter overlays (see tools/avatar/). For any TOUR image whose
# stem has a matching presenters/<stem>.mov (+ .wav), Karen is composited over
# the room and her narration plays (music ducks) instead of a plain Ken Burns pass.
PRESENTER_DIR = os.path.join(VIDEO_DIR, "presenters")
PRESENTER_CONFIG = os.path.join(os.path.dirname(__file__), "..", "avatar", "room_scripts.json")
PRESENTER_MARGIN_X = 48
PRESENTER_MARGIN_Y = 0
PRESENTER_DEFAULT_SCALE = 0.62
PRESENTER_DEFAULT_POS = "bottom-right"
PRESENTER_DUCK_VOL = 0.08

W, H, FPS = 1920, 1080, 30
SS = 2                       # supersample factor for smooth Ken Burns
CW, CH = W * SS, H * SS      # working canvas 3840x2160
HOLD_DISCLAIMER = 5.0
HOLD_CONTACT = 5.0
XFADE = 0.75
ZOOM_MAX = 1.06             # gentle
BEAT_SECONDS = 0.483481     # detected from the CC0 track (124.10 BPM)
MUSIC_BEAT_PHASE = 0.297341
BEATS_PER_PHOTO = 8
PHOTO_STEP = BEAT_SECONDS * BEATS_PER_PHOTO
PHOTO_DUR = PHOTO_STEP + XFADE
FLOOR_PLAN_STEP = BEAT_SECONDS * 16
FLOOR_PLAN_DUR = FLOOR_PLAN_STEP + XFADE
FONT = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"

TITLE_MAIN = "Trinidad Bay"
TITLE_SUB = "Latitude Margaritaville Watersound  |  Island Collection"

TOUR = [
    ("web-trinidad-bay-ext-by-rob-harris-10369-1618602378.jpg", "Welcome Home"),   # hero/title
    ("trinidadbay-ws-13576-1713973919.jpg", "3 Bedrooms  |  3.5 Baths  |  Den  |  3-Car Garage"),
    ("web-trinidad-bay-rhett-foyer-by-rob-harris-10379-1618602380.jpg", "Welcoming Foyer"),
    ("Atrium.jpg", "Private Atrium"),
    ("Atrium Great Room.jpg", "Atrium-to-Great-Room View"),
    ("Great Room.jpg", "Sunlit Great Room"),
    ("web-trinidad-bay-great-room-by-rob-harris-10375-1618602380.jpg", "Open Living & Dining"),
    ("web-trinidad-bay-rhett-living-by-rob-harris-10371-1618602379.jpg", "Comfortable Living Area"),
    ("Great Room from Kitchen.jpg", "Kitchen-to-Great-Room View"),
    ("Kitchen.jpg", "Chef-Inspired Kitchen"),
    ("web-trinidad-bay-kitchen-by-rob-harris-10367-1618602377.jpg", "Generous Island & Storage"),
    ("Kitchen to Back Bedroom.jpg", "Kitchen-to-Guest-Wing View"),
    ("web-trinidad-bay-rhett-den-by-rob-harris-10377-1618602380.jpg", "Flexible Den or Home Office"),
    ("Great Room to Master Suite.jpg", "Private Owner's-Suite Entry"),
    ("web-trinidad-bay-rhett-master-bed-by-rob-harris-10373-1618602380.jpg", "Spacious Owner's Suite"),
    ("Master Bedroom from Bath.jpg", "Owner's-Suite Retreat"),
    ("Master Bath.jpg", "Owner's Bath"),
    ("Great Room to Bedroom.jpg", "Separate Guest Wing"),
    ("2nd Bedroom.jpg", "Bedroom 2"),
    ("Atrium to Bedroom2.jpg", "Atrium Access from Bedroom 2"),
    ("3rd Bedroom.jpg", "Bedroom 3"),
    ("3rd Bedroom and Bath.jpg", "Bedroom 3 with Private Bath"),
    ("Laundry Room.jpg", "Dedicated Laundry Room"),
    ("Laundry Room to Garage.jpg", "Direct Access to the 3-Car Garage"),
    ("web-trinidad-bay-odl-by-rob-harris-10380-1618602380.jpg", "Seamless Indoor-Outdoor Living"),
    ("Lanai.jpg", "Covered Lanai"),
    ("Lanai 2.jpg", "Space to Relax & Entertain"),
    ("Trinidad Bay-floorplan-1.jpg", "Floor Plan"),
]


def esc(path):
    return path.replace("\\", "/").replace(":", "\\:")


def cap_esc(text):
    return text.replace(":", "\\:").replace("'", "\u2019")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2500:])
        raise SystemExit(f"ffmpeg failed ({r.returncode})")


def probe_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", "--", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def caption_filter(caption):
    return (
        f"drawtext=fontfile='{esc(FONT)}':text='{cap_esc(caption)}':"
        f"fontcolor=white:fontsize=54:x=90:y=h-th-90:"
        f"box=1:boxcolor=black@0.45:boxborderw=22"
    )


def kenburns_vf(dur, zoom_in, caption=None, hero=False):
    """Build the Ken Burns video-filter chain (ends in format=yuv420p)."""
    frames = int(round(dur * FPS))
    inc = round((ZOOM_MAX - 1.0) / frames, 6)
    if zoom_in:
        z = f"min(zoom+{inc},{ZOOM_MAX})"
    else:
        z = f"if(eq(on,0),{ZOOM_MAX},max(zoom-{inc},1.0))"
    vf = (
        f"scale={CW}:{CH}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={CW}:{CH},"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={CW}x{CH}:fps={FPS},"
        f"scale={W}:{H}:flags=lanczos,unsharp=3:3:0.5:3:3:0.0,setsar=1,format=yuv420p"
    )
    if hero:
        vf += (
            f",drawbox=x=0:y=0:w=iw:h=ih:color=black@0.32:t=fill"
            f",drawtext=fontfile='{esc(FONT_BOLD)}':text='{TITLE_MAIN}':"
            f"fontcolor=white:fontsize=120:x=(w-tw)/2:y=(h/2)-130:"
            f"shadowcolor=black@0.6:shadowx=3:shadowy=3"
            f",drawtext=fontfile='{esc(FONT)}':text='{cap_esc(TITLE_SUB)}':"
            f"fontcolor=white:fontsize=44:x=(w-tw)/2:y=(h/2)+20:"
            f"shadowcolor=black@0.6:shadowx=2:shadowy=2"
        )
    elif caption:
        vf += "," + caption_filter(caption)
    return vf


def make_kenburns(src, caption, out, dur, zoom_in, hero=False):
    vf = kenburns_vf(dur, zoom_in, caption, hero)
    # Single-image input: zoompan (d=frames) emits the whole clip. Do NOT use
    # -loop/-t here or zoompan multiplies frames (input_frames x d).
    run(["ffmpeg", "-y", "-i", src, "-vf", vf,
         "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "16",
         "-pix_fmt", "yuv420p", out])


def make_kenburns_presenter(src, caption, out, dur, zoom_in, clip, scale, position):
    """Ken Burns of the room with a transparent presenter clip overlaid."""
    bg = kenburns_vf(dur, zoom_in, caption)
    ox = f"W-w-{PRESENTER_MARGIN_X}" if position == "bottom-right" else f"{PRESENTER_MARGIN_X}"
    oy = f"H-h-{PRESENTER_MARGIN_Y}"
    filt = (
        f"[0:v]{bg}[bg];"
        f"[1:v]scale=-1:{int(round(scale * H))}:flags=lanczos[pv];"
        f"[bg][pv]overlay=x='{ox}':y='{oy}':eof_action=pass:format=auto,"
        f"setsar=1,format=yuv420p[v]"
    )
    # Single-image room input (see make_kenburns note); the presenter clip (a
    # ProRes 4444 mov with alpha) on input 1 supplies its own frames.
    # eof_action=pass keeps the room after she ends.
    run(["ffmpeg", "-y", "-i", src, "-i", clip,
         "-filter_complex", filt, "-map", "[v]", "-an", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "slow", "-crf", "16",
         "-pix_fmt", "yuv420p", out])


def load_presenter_placement():
    """Read per-room overlay position/scale from tools/avatar/room_scripts.json."""
    placement = {}
    try:
        with open(PRESENTER_CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return placement
    d = cfg.get("defaults", {})
    for room in cfg.get("rooms", []):
        stem = os.path.splitext(os.path.basename(room["image"]))[0]
        placement[stem] = {
            "position": room.get("position", d.get("position", PRESENTER_DEFAULT_POS)),
            "scale": room.get("scale", d.get("scale", PRESENTER_DEFAULT_SCALE)),
        }
    return placement


def find_presenter(image_name):
    """Return (mov, wav) for a TOUR image if a presenter clip exists, else None."""
    stem = os.path.splitext(os.path.basename(image_name))[0]
    mov = os.path.join(PRESENTER_DIR, f"{stem}.mov")
    wav = os.path.join(PRESENTER_DIR, f"{stem}.wav")
    if os.path.exists(mov):
        return mov, (wav if os.path.exists(wav) else mov)
    return None



def make_fit_hold(src, caption, out, dur, pad_color):
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={pad_color},setsar=1,format=yuv420p"
    )
    if caption:
        vf += "," + caption_filter(caption)
    run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur}", "-i", src, "-vf", vf,
         "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "16",
         "-pix_fmt", "yuv420p", out])


def make_floor_plan(src, out, dur):
    """Pan down the tall plan at a readable scale instead of shrinking it."""
    vf = (
        f"scale=1500:-2:flags=lanczos,"
        f"pad={W}:ih:(ow-iw)/2:0:color=white,"
        f"crop={W}:{H}:0:'(ih-oh)*min(t/{dur},1)',"
        f"unsharp=3:3:0.45:3:3:0.0,setsar=1,format=yuv420p,"
        + caption_filter("Floor Plan  |  2,549 A/C sq. ft.")
    )
    run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur}", "-i", src, "-vf", vf,
         "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "16",
         "-pix_fmt", "yuv420p", out])


def make_video_clip(src, out):
    """Normalize an existing video to 1920x1080/30fps/yuv420p (video only)."""
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS},setsar=1,format=yuv420p"
    )
    run(["ffmpeg", "-y", "-i", src, "-an", "-vf", vf, "-r", str(FPS),
         "-c:v", "libx264", "-preset", "slow", "-crf", "16",
         "-pix_fmt", "yuv420p", out])


def main():
    os.makedirs(VIDEO_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="tour_")
    clips, durs = [], []
    placement = load_presenter_placement()
    # voice events: narration to place on the timeline -> {path, clip_index, offset}
    voice_events = []

    def add(path, dur):
        clips.append(path)
        durs.append(dur)

    n = 0
    # 1) Disclaimer first
    if os.path.exists(DISCLAIMER):
        o = os.path.join(tmp, f"c{n:03d}.mp4"); make_fit_hold(DISCLAIMER, "", o, HOLD_DISCLAIMER, "black")
        add(o, HOLD_DISCLAIMER); print(f"  [{n+1}] Disclaimer"); n += 1

    # 2) Golden Hour transition
    if os.path.exists(GOLDEN):
        o = os.path.join(tmp, f"c{n:03d}.mp4"); make_video_clip(GOLDEN, o)
        add(o, probe_dur(o)); print(f"  [{n+1}] Golden Hour AI Transition"); n += 1

    # 3) Karen AI avatar intro (audio preserved separately)
    if os.path.exists(KAREN):
        o = os.path.join(tmp, f"c{n:03d}.mp4"); make_video_clip(KAREN, o)
        add(o, probe_dur(o))
        voice_events.append({"path": KAREN, "clip_index": len(clips) - 1, "offset": 0.0})
        print(f"  [{n+1}] Karen AI Avatar Intro"); n += 1

    # 4) Photo tour (rooms with a presenter clip get Karen overlaid + narrating)
    for i, (name, cap) in enumerate(TOUR):
        src = os.path.join(GALLERY, name)
        if not os.path.exists(src):
            print(f"      skip (missing): {name}"); continue
        o = os.path.join(tmp, f"c{n:03d}.mp4")
        presenter = None if "floorplan" in name.lower() else find_presenter(name)
        if "floorplan" in name.lower():
            make_floor_plan(src, o, FLOOR_PLAN_DUR)
            dur = FLOOR_PLAN_DUR
        elif presenter:
            mov, wav = presenter
            stem = os.path.splitext(os.path.basename(name))[0]
            place = placement.get(stem, {"position": PRESENTER_DEFAULT_POS, "scale": PRESENTER_DEFAULT_SCALE})
            dur = probe_dur(mov)
            make_kenburns_presenter(src, cap, o, dur, zoom_in=(n % 2 == 0),
                                    clip=mov, scale=place["scale"], position=place["position"])
            add(o, dur)
            voice_events.append({"path": wav, "clip_index": len(clips) - 1, "offset": 0.0})
            print(f"  [{n+1}] {cap}  <- {name}  [PRESENTER {round(dur,1)}s]"); n += 1
            continue
        else:
            make_kenburns(src, cap, o, PHOTO_DUR, zoom_in=(n % 2 == 0), hero=(i == 0))
            dur = PHOTO_DUR
        add(o, dur); print(f"  [{n+1}] {cap}  <- {name}"); n += 1

    # 5) Contact card last
    if os.path.exists(CONTACT_CARD):
        o = os.path.join(tmp, f"c{n:03d}.mp4"); make_fit_hold(CONTACT_CARD, "", o, HOLD_CONTACT, "white")
        add(o, HOLD_CONTACT); print(f"  [{n+1}] Contact Card"); n += 1

    # ---- compute timeline starts (for audio placement) ----
    starts = [0.0]
    acc = durs[0]
    for i in range(1, len(clips)):
        starts.append(round(acc - XFADE, 3))
        acc = round(acc + durs[i] - XFADE, 3)
    total = acc

    # resolve each voice event to an absolute (path, start, duration)
    voices = []
    for ev in voice_events:
        start = round(starts[ev["clip_index"]] + ev["offset"], 3)
        voices.append((ev["path"], start, probe_dur(ev["path"])))

    # ---- pass 2: crossfade video + mix voices under ducked music ----
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    filt = []
    prev = "[0:v]"
    a2 = durs[0]
    for i in range(1, len(clips)):
        off = round(a2 - XFADE, 3)
        lbl = f"[vx{i}]"
        filt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={off}{lbl}")
        prev = lbl
        a2 = round(a2 + durs[i] - XFADE, 3)

    cmd = ["ffmpeg", "-y", *inputs]
    maps = ["-map", prev]
    audio_streams = []
    extra_idx = len(clips)
    for i, (vpath, vstart, _vdur) in enumerate(voices):
        ms = int(round(vstart * 1000))
        cmd += ["-i", vpath]
        lbl = f"[voice{i}]"
        filt.append(
            f"[{extra_idx}:a]adelay={ms}|{ms},"
            f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo{lbl}"
        )
        audio_streams.append(lbl)
        extra_idx += 1

    if os.path.exists(MUSIC):
        music_idx = extra_idx
        music_start = starts[1] if len(starts) > 1 else 0.0
        photo_start = starts[3] if len(starts) > 3 else music_start
        trim = (MUSIC_BEAT_PHASE - (photo_start - music_start)) % BEAT_SECONDS
        music_len = total - music_start
        fade_out = max(0.0, music_len - 4.0)
        # duck the music under every voice window (times relative to music start)
        windows = [
            (max(0.0, vs - music_start), max(0.0, vs + vd - music_start))
            for (_vp, vs, vd) in voices
        ]
        duck = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in windows) or "0"
        cmd += ["-stream_loop", "-1", "-i", MUSIC]
        filt.append(
            f"[{music_idx}:a]atrim=start={trim}:duration={music_len},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out}:d=4,"
            f"volume='if(gt({duck},0),{PRESENTER_DUCK_VOL},0.25)':eval=frame,"
            f"adelay={int(round(music_start * 1000))}|{int(round(music_start * 1000))},"
            f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[music]"
        )
        audio_streams.insert(0, "[music]")

    if audio_streams:
        filt.append(
            f"{''.join(audio_streams)}amix=inputs={len(audio_streams)}:duration=longest:"
            f"normalize=0,alimiter=limit=0.95,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
        )
        maps += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    filter_complex = ";".join(filt)

    starts_str = ", ".join(f"{s}s" for (_p, s, _d) in voices) or "none"
    print(f"\nCombining {len(clips)} clips (total ~{round(total,1)}s); voices @ {starts_str}")
    run(cmd + ["-filter_complex", filter_complex, *maps,
               "-c:v", "libx264", "-preset", "slow", "-crf", "16",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT_FILE])
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
