# Local AI-avatar presenter pipeline

Generate **Karen presenter clips** — her talking, on a transparent background —
so she can appear *inside* room photos narrating the space. 100% local and free:
runs on the workstation GPU (RTX 3060 12 GB, CUDA), no API keys, no per-clip cost.

```
Karen portrait (still) ─┐
                        ├─► SadTalker ─► talking clip ─► rembg matte ─► Karen.webm (alpha)
per-room script ─► XTTS ─┘ (voice clone + narration wav)                       │
                                                                                ▼
                                        tools/video/build_tour.py overlays her on the room
```

## What each piece does

| Stage | Tool | Output |
|---|---|---|
| Voice | **XTTS-v2** (coqui-tts) | Clones Karen's voice from a ~20 s sample, renders a narration `.wav` per room |
| Avatar | **SadTalker** | Lip-syncs the still portrait to each narration `.wav` → talking `.mp4` |
| Matte | **rembg** (`u2net_human_seg`) | Removes the background per frame → transparent `.webm` (VP9 + alpha) |
| Composite | **ffmpeg** (in `build_tour.py`) | Overlays the transparent clip onto the Ken Burns room shot, ducks the music under her voice |

Quality note: these free models are strongest on **head-and-shoulders**. That's
why the presenter is composited as a lower-corner "on-camera guide," not a
full-length standing figure (which needs paid tools like HeyGen).

For the paid, higher-quality HeyGen path — REST API and the remote MCP server —
see [HEYGEN.md](HEYGEN.md). The `make_presenter_heygen.py` script writes clips to
the same `presenters/` folder so `build_tour.py` picks them up unchanged.

## One-time setup

Use a **dedicated venv** (SadTalker + coqui pin conflicting deps that clash with
the `transcribe` `.venv`). The recipe below is the **verified working set** — the
version pins matter (SadTalker predates numpy 2 and modern transformers).

```powershell
cd R:\YouTube-Channel
$py = "tools\avatar\.venv\Scripts\python.exe"
py -3.10 -m venv tools\avatar\.venv

# 1) CUDA torch FIRST (cu121 wheels; CUDA verified on the RTX 3060)
& $py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 2) This pipeline's deps (coqui-tts, rembg[gpu], onnxruntime-gpu, soundfile)
& $py -m pip install -r tools\avatar\requirements.txt

# 3) SadTalker (not on PyPI). Do NOT install its requirements.txt verbatim — its
#    torch/numpy/librosa pins would downgrade the working stack. Install only its
#    extra deps UNPINNED so the coqui-compatible versions are kept:
git clone --depth 1 https://github.com/OpenTalker/SadTalker.git tools\avatar\SadTalker
& $py -m pip install face_alignment imageio-ffmpeg kornia yacs basicsr facexlib gfpgan av pydub resampy

# 4) Repair the known version clashes (order matters):
& $py -m pip install "transformers>=4.57,<5.0"   # 5.x removed isin_mps_friendly (coqui tortoise needs it)
& $py -m pip uninstall -y opencv-python opencv-python-headless
& $py -m pip install "opencv-python==4.11.0.86"  # single cv2 provider, numpy-1.26 compatible
& $py -m pip install "numpy==1.26.4"             # SadTalker uses np.VisibleDeprecationWarning (gone in numpy 2)
```

**Required source patch** (torchvision >= 0.17 removed `functional_tensor`, which
`basicsr`/`gfpgan` import). Edit
`tools\avatar\.venv\Lib\site-packages\basicsr\data\degradations.py` line ~8:

```python
try:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale
except ImportError:  # torchvision >= 0.17
    from torchvision.transforms.functional import rgb_to_grayscale
```

**Model checkpoints** (~1.7 GB) — download with resumable `curl.exe` to a *local*
staging folder, then robocopy onto the share (the R: share can drop mid-write; see
`/memories/repo/notes.md`). `make_presenter.py` uses `--size 512 --enhancer gfpgan`,
so fetch these into `SadTalker\checkpoints\` and `SadTalker\gfpgan\weights\`:

- checkpoints: `mapping_00109-model.pth.tar`, `mapping_00229-model.pth.tar`,
  `SadTalker_V0.0.2_512.safetensors`
- gfpgan/weights: `alignment_WFLW_4HG.pth`, `detection_Resnet50_Final.pth`,
  `GFPGANv1.4.pth`, `parsing_parsenet.pth`

URLs are in `SadTalker\scripts\download_models.sh`.

> `pip check` will warn that `rembg` wants `opencv-python-headless` — harmless; the
> single `opencv-python` build provides `cv2` and works at runtime.

**Verify:** `& $py -c "import torch; print(torch.cuda.is_available())"` → `True`,
and `cd tools\avatar\SadTalker; & $py inference.py --help` prints usage.

### Record Karen's voice sample

Put a clean ~15–30 s mono WAV of Karen speaking at
`tools\avatar\assets\karen-voice-sample.wav` (no music/background). This is the
voice XTTS clones. A snippet lifted from an existing narration works.

## Usage

Everything is driven by [`room_scripts.json`](room_scripts.json) — the model,
the portrait, the voice sample, and the per-room narration lines.

```powershell
tools\avatar\.venv\Scripts\Activate.ps1

# 1) Generate narration WAVs (one per room) into <model>\video\presenters\
python tools\avatar\make_narration.py

# 2) Generate transparent presenter clips (SadTalker + matte)
python tools\avatar\make_presenter.py

# 3) Build the tour — presenter rooms are picked up automatically
python tools\video\build_tour.py
```

`build_tour.py` looks in `<model>\video\presenters\` and, for any TOUR image
that has a matching `<ImageStem>.webm` + `<ImageStem>.wav`, overlays Karen and
plays her narration instead of the plain Ken Burns pass. Rooms without a
presenter clip are unchanged.

## Files

| File | Purpose |
|---|---|
| `requirements.txt` | Python deps (dedicated venv) |
| `room_scripts.json` | Model, portrait, voice sample, per-room scripts + overlay placement |
| `make_narration.py` | XTTS-v2 → per-room narration WAVs |
| `make_presenter.py` | SadTalker → rembg matte → transparent WEBM per room |
| `assets/` | `karen-voice-sample.wav` (you provide) |
| `SadTalker/` | Cloned repo + checkpoints (git-ignored) |
| `.venv/` | Dedicated environment (git-ignored) |
