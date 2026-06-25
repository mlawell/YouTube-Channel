#!/usr/bin/env python3
"""Transcribe audio/video files into timestamped Markdown + SRT using faster-whisper.

Walks an input directory for media files, transcribes each with Whisper, and writes
two outputs per file into the output directory (mirroring the input tree):

  - <name>.md  : metadata header + [HH:MM:SS] timestamped segments
  - <name>.srt : standard subtitle file (useful for syncing back to video)

The run is RESUMABLE: files whose .md output already exists are skipped, so the
script can be safely re-run after an interruption.

Usage (from repo root):
  python tools/transcribe/transcribe.py \
      --input "C:/path/to/media" \
      --output "docs/library/channel-junkies/transcripts/14-day-sprint" \
      --srt-output "docs/library/channel-junkies/srt/14-day-sprint"
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys
from pathlib import Path

MEDIA_EXTENSIONS = {".mp4", ".mp3", ".wav", ".m4a", ".mov", ".mkv", ".aac", ".flac", ".webm"}


def register_cuda_dlls() -> None:
    """On Windows, add the pip-installed NVIDIA DLL folders to the search path.

    ctranslate2 needs cuBLAS/cuDNN DLLs at import time; the `nvidia-*-cu12`
    wheels ship them under site-packages/nvidia/**/bin but don't register them.
    """
    if os.name != "nt":
        return
    try:
        import nvidia  # type: ignore
    except ImportError:
        return
    dll_dirs: list[str] = []
    for base in nvidia.__path__:
        for dll_dir in Path(base).glob("*/bin"):
            if dll_dir.is_dir():
                os.add_dll_directory(str(dll_dir))
                dll_dirs.append(str(dll_dir))
    # ctranslate2 resolves CUDA libs (cublas64_12.dll, cudnn64_9.dll) via PATH,
    # so add_dll_directory alone is not enough — prepend them to PATH too.
    if dll_dirs:
        os.environ["PATH"] = os.pathsep.join(dll_dirs) + os.pathsep + os.environ.get("PATH", "")


register_cuda_dlls()


def pad_numbers(name: str) -> str:
    """Zero-pad standalone integer runs to 2 digits so files sort naturally.

    'Channel Junkies Day 1' -> 'Channel Junkies Day 01'
    """
    return re.sub(r"\d+", lambda m: m.group(0).zfill(2), name)


def format_timestamp(seconds: float, *, srt: bool = False) -> str:
    """Format a time in seconds as HH:MM:SS (md) or HH:MM:SS,mmm (srt)."""
    if seconds < 0:
        seconds = 0
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    if srt:
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def find_media(input_dir: Path) -> list[Path]:
    return sorted(
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS
    )


def resolve_device(requested: str) -> tuple[str, str]:
    """Return (device, compute_type). 'auto' prefers CUDA, falls back to CPU."""
    if requested == "cpu":
        return "cpu", "int8"
    if requested == "cuda":
        return "cuda", "float16"
    # auto-detect
    try:
        import ctranslate2  # noqa: WPS433 (local import is intentional)

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:  # noqa: BLE001 - any failure means no usable CUDA
        pass
    return "cpu", "int8"


def write_outputs(
    *,
    segments: list,
    info,
    source: Path,
    md_path: Path,
    srt_path: Path | None,
    model_name: str,
) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    title = pad_numbers(source.stem)
    duration = format_timestamp(getattr(info, "duration", 0.0))
    generated = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    md_lines = [
        f"# {title}",
        "",
        f"- **Source file:** `{source.name}`",
        f"- **Duration:** {duration}",
        f"- **Language:** {getattr(info, 'language', 'unknown')}",
        f"- **Model:** faster-whisper `{model_name}`",
        f"- **Generated:** {generated}",
        "",
        "---",
        "",
        "## Transcript",
        "",
    ]

    srt_lines: list[str] = []
    for idx, seg in enumerate(segments, start=1):
        text = seg.text.strip()
        start = format_timestamp(seg.start)
        md_lines.append(f"**[{start}]** {text}")
        md_lines.append("")
        if srt_path is not None:
            srt_lines.append(str(idx))
            srt_lines.append(
                f"{format_timestamp(seg.start, srt=True)} --> "
                f"{format_timestamp(seg.end, srt=True)}"
            )
            srt_lines.append(text)
            srt_lines.append("")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    if srt_path is not None:
        srt_path.parent.mkdir(parents=True, exist_ok=True)
        srt_path.write_text("\n".join(srt_lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Directory of media files.")
    parser.add_argument("--output", required=True, type=Path, help="Directory for .md transcripts.")
    parser.add_argument("--srt-output", type=Path, default=None, help="Directory for .srt files.")
    parser.add_argument("--model", default="large-v3", help="Whisper model name.")
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    parser.add_argument("--language", default="en", help="Language code, or 'auto' to detect.")
    parser.add_argument("--beam-size", type=int, default=5)
    args = parser.parse_args()

    if not args.input.is_dir():
        print(f"ERROR: input directory not found: {args.input}", file=sys.stderr)
        return 2

    media = find_media(args.input)
    if not media:
        print(f"No media files found under {args.input}")
        return 0

    device, compute_type = resolve_device(args.device)
    print(f"Loading model '{args.model}' on {device} ({compute_type}) ...")

    from faster_whisper import WhisperModel  # imported here so --help works without deps

    model = WhisperModel(args.model, device=device, compute_type=compute_type)
    language = None if args.language == "auto" else args.language

    total = len(media)
    transcribed = 0
    skipped = 0
    for n, source in enumerate(media, start=1):
        rel = source.relative_to(args.input)
        out_stem = pad_numbers(rel.stem)
        md_path = (args.output / rel.parent / out_stem).with_suffix(".md")
        srt_path = (
            (args.srt_output / rel.parent / out_stem).with_suffix(".srt")
            if args.srt_output is not None
            else None
        )

        if md_path.exists():
            print(f"[{n}/{total}] SKIP (exists): {rel}")
            skipped += 1
            continue

        print(f"[{n}/{total}] Transcribing: {rel}")
        segments, info = model.transcribe(
            str(source),
            language=language,
            beam_size=args.beam_size,
            vad_filter=True,
        )
        # segments is a generator; materialize it so we can write md + srt.
        segments = list(segments)
        write_outputs(
            segments=segments,
            info=info,
            source=source,
            md_path=md_path,
            srt_path=srt_path,
            model_name=args.model,
        )
        transcribed += 1
        print(f"    -> {md_path}")

    print(f"\nDone. Transcribed {transcribed}, skipped {skipped}, total {total}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
