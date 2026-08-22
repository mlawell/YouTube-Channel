# Reference Videos

A working catalog of real, high-performing YouTube videos from relocation
realtors, scored against the Channel Junkies framework documented in
[`knowledge/channel-junkies/`](../channel-junkies/).

This exists to answer one question Karen asked: *how do these videos match what
Channel Junkies is presenting, so we can produce the same result?*

The short answer is that they mostly do — and the places where they **don't**
are the most useful thing in here.

## Start here

| If you are… | Read |
| --- | --- |
| About to script a video and want a model to copy | [`catalog.md`](catalog.md) — jump to your format |
| Deciding how long a video should be, or where to put the price | [`framework-vs-practice.md`](framework-vs-practice.md) |
| Sizing up a channel or looking for who to watch | [`channels.md`](channels.md) |
| Re-scoring this data or adding videos | [`catalog.json`](catalog.json) |

## How to use the catalog

[`catalog.md`](catalog.md) is grouped **by format**, not by channel, because
format is what determines structure. When Karen is making a map tour, the useful
comparison is other map tours — not other videos by the same person. Every entry
carries a clickable link, the measured numbers, and a short **what to steal**
note.

The one rule for using it: **watch the video before copying the note.** These
notes are compressed judgements about other people's work. They are a reason to
go and look, not a substitute for looking.

## Ground rules

These are the same rules as [`knowledge/competitors/`](../competitors/), and
they are not negotiable:

- **Link and summarize. Never republish.** No transcripts, no descriptions
  copied wholesale, no downloaded media in this repo. Every video is referenced
  by URL so the source gets the view.
- **Quote sparingly and attribute.** Short fragments, to make a specific
  analytical point, always naming whose video it is. If a quote is long enough
  to be worth reading on its own, it is too long.
- **No caption or transcript files are committed.** The `.vtt` files this
  analysis was built from stay in the research session folder. `.gitignore`
  blocks them from this directory.
- **Correct the claim, not the human.** Where a video diverges from the
  framework that is an observation about a technique, not a criticism of the
  person. Several of these people are better at this than we are.

## Data provenance

Everything here traces to a research pass run **2026-08-21** in session
`d9ad2b5f-0191-4756-a1ef-478cb074fd3a`. Source files live in that session's
`files/reference-videos/` folder and are deliberately **not** in the repo.

| Source | What it gave us | Reliability |
| --- | --- | --- |
| `exemplars.json` | yt-dlp metadata for 18 videos: title, channel, duration, views, likes, comments, upload date, subscriber count, chapter count | **Exact.** Every duration, view and chapter figure in this catalog comes from here |
| `caps/*.vtt` | Auto-generated captions for 16 of the 18 | Timestamps exact, wording approximate — see caveat below |
| `scored.json` | A first regex pass over the captions | **Used only as a candidate generator.** Its own classifications were not trusted — see below |
| `*.txt` channel listings | 45–60 recent videos per channel: id, duration, views, title | Durations exact; **view counts rounded by YouTube** (e.g. `11000` for 11K) |

### ⚠️ The auto-caption caveat

The captions are YouTube's automatic transcription. **Timestamps are reliable.
Wording is not.** Observed failures in this very dataset:

- *Avimor* → "Avonmore"
- *Margaritaville* → "Margaritavville"
- *"Mr. Beach here"* → "your Beach here"
- *Brevard County* → "Bvard County"
- *McWiggan* → "McWigan"

Consequently: **no quote in this catalog is presented as verbatim unless the
wording was read back and judged sound.** Proper nouns have been silently
corrected to their real spellings; everything else is left as transcribed.
Anything genuinely uncertain is marked as an impression rather than asserted.

### ⚠️ Why `scored.json` was re-done

The original regex pass answered "when is the first number that looks like
money?" That is not the same question as "when is the first price?" Checking
each hit against its surrounding sentence found these false positives:

| Video | Regex called it the first price | It was actually |
| --- | --- | --- |
| Mr. Beach — *Inside Margaritaville PCB* | 7:58 | a **$2 McDonald's biscuit** in a joke about retirement |
| Cunha — *Cape Coral's Biggest Dealbreaker* | 2:35 | a **population of 100,000** |
| *Margaritaville Daytona Beach* | 0:07 | **500,000 people registered** for information |
| Rachel — *Shockingly Affordable* | 5:00 | a **$3 million contrast** about other videos, not this home |

It also **missed** prices spoken as words rather than digits — Mr. Beach's real
first price is *"these start in the 350s"* at **1:38**, six minutes earlier than
the regex thought, and it changes that video's reading completely.

Every price position in [`catalog.json`](catalog.json) was therefore re-derived
by reading the surrounding sentence. `scored.json` is superseded; do not cite it.

### What is *not* measured

Honesty about the edges of the data matters more than coverage:

- **No retention or watch-time data.** Those are private to the channel owner.
  Views are a weak proxy and are treated as one throughout.
- **No lead data.** Every one of these is a lead-generation video and we cannot
  see whether any of them generates leads. This is the single biggest limit on
  every conclusion here, and it is why "more views" is never treated as "better."
- **Two videos have no captions** (`NOSAZ2h7UUY`, `H3jUbpNT2Zw`) and are
  metadata-only. They are flagged in the JSON with `captions_available: false`.
- **The sample is selected, not random.** These videos were chosen *because*
  they perform well. Any statement of the form "videos that do X get more views"
  is therefore describing this sample, not proving a rule, and is written that
  way.

## Re-scoring later

[`catalog.json`](catalog.json) carries the full record per video, including
`first_price_s`, `first_price_kind` (`band` vs `number`), `price_reveal_s`,
`has_callout`, `co_host` and `chapters`. To refresh:

1. Re-pull metadata with yt-dlp into a new `exemplars.json`.
2. Re-run the caption pass **in a scratch folder**, never in the repo.
3. Re-verify each price hit by reading its sentence. The regex alone is not
   sufficient — that is the whole lesson of the first pass.
