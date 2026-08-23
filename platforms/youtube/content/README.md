# YouTube content packages

One folder per video (or per series). Each package is self-contained: the script,
the metadata, the thumbnail brief, and a map of the media it draws on.

**No media lives here.** Photos, video and thumbnails stay in the Microsoft 365
library and are referenced by path, per
[`properties/README.md`](../../../properties/README.md). See
[the media rule](#the-media-rule) below.

## Packages

### Living in Panama City Beach FL \| The Lawell Team

`@LivinginPanamaCityBeachFLtheLT` · the driver-city channel

| Package | What it is | Status |
| --- | --- | --- |
| [**Five Kinds of Life in Panama City Beach**](pcb-five-neighborhoods/README.md) | ~30 min vlog tour of five neighborhoods, built from Counts-held listing media and 21 min of Pier Park aerials | Ready to record — [3 blocking `[KAREN]` items](pcb-five-neighborhoods/README.md#before-you-record) |

This channel has **one published video**, so this is effectively its launch.
Against the four permanent assets every relocation channel needs — pros and cons,
cost of living, a driver-city vlog tour, and a map tour — it covers **the vlog
tour**. Cost of living and the map tour are still missing, and the vlog video
[redirects to cost of living](pcb-five-neighborhoods/README.md#what-the-next-video-should-be),
so that one is next.

### Living in Latitude Margaritaville Watersound

`@LivingMargaritavillewithKaren` · the niche 55+ channel

| Package | What it is | Status |
| --- | --- | --- |
| [Every Phase Explained](latitude-phases-explained/README.md) | The flagship. 19–22 min, all 16 phases from recorded plats | Script ready, awaiting Karen's confirmations · [runtime under review](latitude-phases-explained/README.md#-1-runtime--1922-minutes-is-below-every-comparable-channel) |
| [Phase Deep Dives](phase-deep-dives/README.md) | Ten spokes, one per phase | Drafts + metadata + thumbnails generated. **Blocked on the [drive sheet](phase-deep-dives/drive-sheet.md)** |

Hub and spokes: the flagship answers *"how do the phases work"*, each deep dive
answers *"should I buy in this one"*. Both are generated from the same public
record as the map by
[`tools/scripts/build_phase_scripts.py`](../../../tools/scripts/build_phase_scripts.py),
so they cannot drift from it.

## What a package contains

| File | Always | What it is |
| --- | --- | --- |
| `README.md` | ✅ | Why this video, the decisions made and the evidence for them, what is still blocking |
| `script.md` | ✅ | Timecoded script with frame cues. Spoken copy blockquoted, direction in brackets |
| `metadata.md` | ✅ | Title variants, description, tags, chapters, end screen, pinned comment |
| `thumbnail-brief.md` | ✅ | Concepts and what to test |
| `media-map.md` | when the video uses library media | Every source file by segment, with measurements and trim points |
| `drive-sheet.md` | when the video makes distance claims | Drive times to be filled in from actual drives, never estimated |

## Conventions

- **`[KAREN]` marks anything unverified.** It is never a guess dressed as a fact.
  Drive times, HOA rules, school-quality claims, flood-zone claims and insurance
  figures are marked by default.
- **Every number traces to a source** — a recorded plat, an MLS detail sheet with
  a snapshot date, or a measurement someone actually took.
- **Volatile facts are spoken as volatile**: *"as I'm recording this, in
  [Month Year]…"*. Prices and inventory change and the video does not.
- **No em-dashes in spoken copy** — a named AI-detection tell (`D1-QA` 00:05:11).
  Prose in these markdown files is not read aloud and is not subject to the rule.
- **No price and no "for sale" in a title or thumbnail** (`D1-QA` 00:15:37).

## The media rule

Images and video are **referenced, never committed**. They live in the M365
library at `C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents` and are
addressed by path from a package's `media-map.md`.

`.gitignore` carries a rule covering image and video extensions under
`platforms/**/content/` and `platforms/**/assets/`, so an accidental `git add`
fails closed rather than committing a multi-gigabyte drone plate. Verify before
committing:

```powershell
git status --short          # expect *.md only
```
