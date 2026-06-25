# Realtor Knowledge Library

A growing library of training and reference material distilled into searchable
knowledge for real estate agents. Each **volume** captures one source program or
body of knowledge as raw transcripts plus a synthesized, action-oriented playbook.

## Volumes

| Volume | Source | Status |
| --- | --- | --- |
| [Channel Junkies](channel-junkies/README.md) | YouTube-for-realtors training (14 Day Sprint + Billion Dollar Channel Method) | In progress |

## How this library is built

1. **Transcribe** — Audio/video is transcribed locally with `faster-whisper`
   (see [`tools/transcribe`](../../tools/transcribe/README.md)) into timestamped
   Markdown and `.srt` subtitles.
2. **Index** — Each volume's `README.md` links every source file to its transcript.
3. **Synthesize** — Transcripts are distilled into a realtor playbook organized by
   theme (strategy, content/SEO, lead generation, scripts, action plans).

> Raw transcripts and subtitles are derived from paid training content and are kept
> local (git-ignored). The synthesized playbooks are the shareable deliverable.
