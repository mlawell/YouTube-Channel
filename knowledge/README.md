# Knowledge Library

The shared, platform-agnostic knowledge base for **Beach Homes Social Studio** —
training and reference material distilled into searchable, action-oriented notes
for real-estate social media marketing. Each **volume** captures one source
program or body of knowledge as raw transcripts plus a synthesized playbook.

This library is platform-neutral: it feeds the per-platform playbooks and content
in [`../platforms/`](../platforms/README.md). Where a lesson applies to a specific
channel, the platform folder cross-links back to the relevant volume here.

## Volumes

| Volume | Source | Primary platform | Status |
| --- | --- | --- | --- |
| [Channel Junkies](channel-junkies/README.md) | YouTube-for-realtors training (14 Day Sprint + Billion Dollar Channel Method) | YouTube | Complete |

## How this library is built

1. **Transcribe** — Audio/video is transcribed locally with `faster-whisper`
   (see [`tools/transcribe`](../tools/transcribe/README.md)) into timestamped
   Markdown and `.srt` subtitles.
2. **Index** — Each volume's `README.md` links every source file to its transcript.
3. **Synthesize** — Transcripts are distilled into a realtor playbook organized by
   theme (strategy, content/SEO, lead generation, scripts, action plans).

> Raw transcripts and subtitles are derived from paid training content and are kept
> local (git-ignored). The synthesized playbooks are the shareable deliverable.
