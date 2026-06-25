# Transcription tool

Local, GPU-accelerated transcription of audio/video into timestamped Markdown + SRT
using [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Runs entirely on
your machine — no cloud upload of source media.

## Setup

```powershell
# From the repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r tools/transcribe/requirements.txt
```

Requires `ffmpeg` on PATH. GPU acceleration uses the bundled CUDA libraries from the
`nvidia-*-cu12` packages; on a CPU-only machine the script falls back automatically.

## Usage

```powershell
python tools/transcribe/transcribe.py `
  --input "C:/path/to/media" `
  --output "docs/library/channel-junkies/transcripts/14-day-sprint" `
  --srt-output "docs/library/channel-junkies/srt/14-day-sprint"
```

Key flags:

- `--model` — Whisper model (default `large-v3`). Use `medium` for a faster CPU run.
- `--device` — `auto` (default), `cuda`, or `cpu`.
- `--language` — language code (default `en`; use `auto` to detect).

The run is **resumable**: any file whose `.md` already exists is skipped, so you can
re-run after an interruption.
