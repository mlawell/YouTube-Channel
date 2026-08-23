# Media map — Five Kinds of Life in Panama City Beach

Every frame this video draws on, by segment, with the exact source path.

> 🚫 **Nothing in this file is committed to the repo.** All of it lives in the
> Microsoft 365 / OneDrive library and is referenced by path, per
> [`properties/README.md`](../../../../properties/README.md). Do not copy media
> into `platforms/youtube/assets/` either — see
> [the media rule](README.md#the-media-rule).

**M365 root** (called `PCB` below):

```
C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents\Properties\Bay County\Panama City Beach
```

---

## ⚠️ Read this before you cut anything: what the "Virtual Tour" files actually are

The 15 `- Virtual Tour.mp4` files are **not filmed walk-throughs.** They are
auto-generated Ken Burns slideshows built from the same gallery JPEGs that sit
next to them. This was measured, not assumed:

| Evidence | Finding |
| --- | --- |
| Runtime | **13 of 15 are 123.1 s to the frame.** The two exceptions are the two smallest galleries |
| The fit | 34 photos → 105.7 s; 37 photos → 114.4 s. That is **2.84 s per photo + 9.5 s of cards**, capped at 40 photos. Every one of the 15 fits this formula exactly |
| Cut cadence | A hard cut every ~2.8 s with a slow zoom between cuts |
| Frame matching | Sampled frames match specific gallery JPEGs at **0.99 correlation** (`783783-3`, `783783-28`, `783783-38`) |

**Three consequences.**

1. **They add no motion the gallery does not already have.** The plan's premise
   was that these files supply ~10 minutes of genuine filmed footage. They do
   not. See [the README](README.md#-the-finding-that-changes-the-plan-the-virtual-tours-are-slideshows).
2. **They only ever show the first 40 photos.** Bahama Beach has **172** photos
   and the tour file shows **40** of them. Treasure Cove has **152** and shows
   **40**. The best material in the two deepest galleries is *not in the tour
   file at all*.
3. **The price is burned into frame one.** See below. This is the one that
   breaks the structure if it is missed.

### Anatomy of every tour file — measured, all five confirmed identical

| Block | In | Out | Length | Contents |
| --- | --- | --- | --- | --- |
| **Title card** | 0:00.0 | **0:04.1** | 4.1 s | Address, city, **and the price, burned in** |
| **Body** | **0:04.1** | **1:57.7** | **113.6 s** | Up to 40 gallery photos, 2.84 s each, with burned-in caption chips bottom-left ("Built 1987", "0.23 Acres Lot") |
| **Outro card** | **1:57.7** | 2:03.1 | 5.4 s | Counts logo, Karen's headshot, 2104 Navy Blvd, 850-517-8528, `Karen@nwflbeachhomes.com`, and the strip *"Listing courtesy of Counts Real Estate Group \| Data from CPAR MLS \| Information deemed reliable but not guaranteed"* |

Measured per file (seconds):

| Address | Duration | Title out | Outro in | Usable body |
| --- | --- | --- | --- | --- |
| 249 Oxford Ave | 123.0 | 4.00 | 117.73 | 113.7 |
| 13003 Oleander Dr | 123.0 | 4.20 | 117.63 | 113.4 |
| 263 Lullwater Dr | 123.0 | 4.10 | 117.73 | 113.6 |
| 1722 Wahoo Cir | 123.0 | 4.00 | 117.63 | 113.6 |
| 2601 Oak St | 123.0 | 4.00 | 117.73 | 113.7 |

### 🔴 The trim rule — non-negotiable

```
Trim IN at 0:04.5   (drop the title card — it has the price on it)
Trim OUT at 1:57.5  (drop the outro card — it is a hard stop mid-video)
```

**Why the in-point matters more than it looks.** The whole segment structure
holds each home's number to the *end* of its segment — five micro-reveals, one
per neighborhood. If the tour file is dropped in whole, **the price appears
burned into the first frame of every segment** and the structure is gone. The
title card is 4.1 seconds and it costs nothing to lose.

There is a second reason. **These prices move.** Bay Point has been cut five
times and Treasure Cove four. A burned-in number is stale the day it changes,
and it is stale *permanently*, because it is baked into the frame.

**The outro card is not waste — reuse it.** It is a finished, on-brand end card
carrying the brokerage name next to the contact details, which is exactly what
[Florida rule 61J2-10.025](README.md#brokerage-disclosure--verified) requires.
Take it from **any one** file and use it as the video's own end card under the
final redirect. Do not use it five times.

### Audio

Every tour file carries an **AAC stereo music bed** for its full 123 s. Karen
narrates over all of it. **Mute the tour audio entirely** — do not duck it. Five
different fragments of the same library track fading in and out is worse than
silence, and the video already has its own music plan.

---

## ⭐ The real motion footage: Pier Park drone plates

**`PCB\Pier Park\`** — this is the asset the plan was missing, and it is the
answer to the "no filmed footage" problem.

| File | Duration | Format |
| --- | --- | --- |
| `Pier Park 001.MP4` | 0:43.9 | 3840×2160 @ 59.94 HEVC |
| `Pier Park 002.MP4` | 1:47.1 | 3840×2160 @ 59.94 HEVC |
| `Pier Park 003.MP4` | 1:04.3 | 3840×2160 @ 59.94 HEVC |
| `Pier Park 004.MP4` | 4:33.9 | 3840×2160 @ 59.94 HEVC |
| `Pier Park 005.MP4` | 3:11.8 | 3840×2160 @ 59.94 HEVC |
| `Pier Park 006.MP4` | 5:59.8 | 3840×2160 @ 59.94 HEVC |
| `Pier Park 007.MP4` | 4:02.4 | 3840×2160 @ 59.94 HEVC |
| **Total** | **21:23** | ~13 GB |

Plus four 4K stills: `Pier Park 007.JPG`, `008.JPG`, `009.JPG`, `010.JPG`.

**21 minutes of real aerial motion, against roughly 30 minutes of finished
video.** Budget it deliberately — this is the only genuinely moving,
genuinely-shot material in the package, and it is the thing that stops the video
reading as a slideshow with a voice on top.

**Where it goes.** Not all in the anchor segment. Spread it:

- The whole cold open and anchor block (0:00–3:30)
- **Every neighborhood transition** — the "now we're driving east" beat between
  segments. Five transitions, ~10–15 s each. This is the highest-value use:
  motion between static segments is what makes a slideshow feel like a vlog
- Under the Palmetto Trace segment, which is *across the street from Pier Park*
  and therefore the one place the footage is literally on-topic
- Under the close

**Two production notes.**

- **Downscale to 1080p on ingest.** It is 4K60 HEVC; the channel delivers 1080p
  and the framework is explicit that 4K buys nothing here (`D2-GS` 00:19:43).
  Transcode once to 1080p ProRes or DNxHR and edit from that — scrubbing 13 GB
  of HEVC will be miserable.
- **Slow it down.** 59.94 fps conformed to 23.976 or 29.97 gives clean 40–50%
  slow motion, which suits aerial establishing shots and stretches 21 minutes of
  plates further.

⚠️ **`PCB\DJI_001\` is empty.** If Karen believes there is drone footage of the
*neighborhoods* (not Pier Park), it has not landed in the library. Worth asking —
neighborhood aerials would materially improve segments 2–5.

---

## Segment 1 — Palmetto Trace · 249 Oxford Ave

**MLS 790701** · `PCB\Palmetto Trace Phase 2\249 Oxford Ave\`

| Asset | Path | Notes |
| --- | --- | --- |
| Detail sheet | `listing-details.md` | Source of every number in this segment |
| Gallery | `gallery\790701-1.jpg` … `790701-41.jpg` | 41 photos, **2048×1368** |
| Tour | `video\249 Oxford Ave - Virtual Tour.mp4` | Trim 0:04.5–1:57.5 |

**Gallery is 41 photos and the tour uses 40 — so the tour is effectively the
whole gallery.** There is almost no unused material here. Lean on the Pier Park
plates for this segment's B-roll instead; it is the one neighborhood where they
are geographically honest.

**Verified route** (MLS Directions, listing 790701): *"the Front entrance of
Palmetto Trace Neighborhood located across the street From Pier Park. From Back
Beach Road, turn into Cambridge Blvd. Take your 1st Left onto Biltmore Pl., then
your 1st Right."*

---

## Segment 2 — Bahama Beach · 13003 Oleander Dr

**MLS 781232** · `PCB\Bahama Beach\13003 Oleander Dr\`

| Asset | Path | Notes |
| --- | --- | --- |
| Detail sheet | `listing-details.md` | |
| Gallery | `gallery\781232-1.jpg` … `781232-172.jpg` | **172 photos, 3000×2250** — the deepest and highest-resolution set in the package |
| Tour | `video\13003 Oleander Dr - Virtual Tour.mp4` | Trim 0:04.5–1:57.5 |

⭐ **The tour file shows 40 of 172 photos. 132 photos are unused.** This is the
single richest vein of material in the whole package and the tour file barely
touches it. At 3000×2250 these take a 1.5× Ken Burns push without softening.

**Build this segment's B-roll by hand from the gallery**, not from the tour file.
The tour file is the fallback, not the plan. Photos worth finding in the back
half of the set: the second-floor heated pool, the Gulf-front deck, the private
boardwalk to the sand, the elevator, and the seven bedroom suites.

---

## Segment 3 — El Centro Beach · 263 Lullwater Dr

**MLS 782720** · `PCB\El Centro Beach\263 Lullwater Dr\`

| Asset | Path | Notes |
| --- | --- | --- |
| Detail sheet | `listing-details.md` | |
| Gallery | `gallery\782720-1.jpg` … `782720-63.jpg` | 63 photos, 3000×1687 (16:9 — no reframing needed) |
| Tour | `video\263 Lullwater Dr - Virtual Tour.mp4` | Trim 0:04.5–1:57.5 |

**23 photos unused by the tour file.** The segment turns on the lot — 0.66 acres,
the biggest in the package by a factor of nearly three — and on the water being a
*lake*, not the Gulf. Prioritise any photo that shows the lot line, the water
frontage, or the tree cover. If those are only in the unused 23, cut to them
directly rather than relying on the tour file.

**Verified route** (MLS Directions, listing 782720): *"79 South, left on Panama
City Beach Parkway (Hwy 98), right on Lullwater Dr."*

---

## Segment 4 — Bay Point Unit 1 · 1722 Wahoo Cir

**MLS 783783** · `PCB\Bay Point Unit 1\1722 Wahoo Cir\`

| Asset | Path | Notes |
| --- | --- | --- |
| Detail sheet | `listing-details.md` | |
| Gallery | `gallery\783783-1.jpg` … `783783-48.jpg` | 48 photos, **1763×1202 — the lowest resolution in the package** |
| Tour | `video\1722 Wahoo Cir - Virtual Tour.mp4` | Trim 0:04.5–1:57.5 |

⚠️ **Resolution warning.** 1763×1202 clears 1080p by only 11%. **Do not push in
more than ~1.1× on these**, or they will visibly soften on a 1080p master. The
tour file's own Ken Burns moves are already at the edge of what this set
supports. Where this segment needs movement, take it from the Pier Park plates
or hold the frame still.

**This segment is about the community, not the house** — gate, guard, Jack
Nicklaus course, marina, canals, on-site restaurant — and almost none of that is
in a gallery of the interior. ⚠️ **There is no Bay Point community photography in
this library.** Either Karen shoots the gate and the marina herself, or the
segment carries on narration plus the interior stills, which is the weakest
configuration in the video. Flag this before the shoot, not during the edit.

---

## Segment 5 — Treasure Cove · 2601 Oak St

**MLS 785430** · `PCB\Treasure Cove\2601 Oak St\`

| Asset | Path | Notes |
| --- | --- | --- |
| Detail sheet | `listing-details.md` | |
| Gallery | `gallery\785430-1.jpg` … `785430-152.jpg` | **152 photos, 3000×1687** — second-deepest set |
| Tour | `video\2601 Oak St - Virtual Tour.mp4` | Trim 0:04.5–1:57.5 |

⭐ **112 photos unused by the tour file.** Like Bahama Beach, build this segment
by hand. It closes the video, it is the affordability answer, and it deserves
better than the first 40 frames the generator happened to pick.

Prioritise anything showing the **0.36-acre lot** — it is the second-largest in
the package and it is the segment's whole argument: the cheapest house here sits
on more land than the $5.3 million one.

**Verified route** (MLS Directions, listing 785430): *"From US Hwy. 98 (Back
Beach Rd) turn onto Navy Blvd./Thomas Dr.; turn right onto Sunset Dr.; Sunset
Dr. becomes Oak St. and the home will be on the left."*

---

## Not used, and why

The ten listings left on the shelf. Recorded so the next video does not have to
re-derive it — and so the reasoning is checkable.

| Neighborhood / address | Price | DOM | Photos | Why not this time |
| --- | --- | --- | --- | --- |
| Bare Footin Condominium · 13906 Front Beach Rd | $2,450,000 | 182 | 55 | **Not a condo.** MLS type is Single Family. Duplicates Bahama Beach's beach-plus-rental story at half the spectacle |
| Hollywood Beach · 123 Dupree St | $2,299,000 | 52 | 70 | Also duplicates Bahama Beach — 2022 build, pool, STR-allowed. Strong on its own; redundant here |
| Royal Palms Of Laguna Beach · 19906 Front Beach Rd | $1,450,000 | **533** | 51 | **Not a condo either.** The 533-day narrative is the best in the set and is being *saved* — see [the README](README.md#what-the-next-video-should-be) |
| Bid-A-Wee Beach 1st Add · 407 Petrel St | $1,248,000 | 172 | 75 | Good set, but a third Gulf-view beach house. No new *kind* of life |
| Suntime Beach U-1 · 125 Cobb Rd | $935,000 | 72 | 41 | 6bd/3,335 sqft, no HOA, no view, no community features. Hard to characterise as a lifestyle |
| The Glades · 124 Hombre Cir | $689,000 | 43 | **34** | Golf duplicates Bay Point, which also has a marina and a gate. Weakest gallery in the package, and its tour file is only 1:45 |
| Laguna Beach Estates 5th Add · 105 Granger Ln | $684,500 | 91 | 45 | 978 sqft, built 1959 — the *actual* classic beach cottage. A genuinely good segment, cut only for time |
| No Named Subdivision · 22611 Hilltop Ave | $669,000 | 143 | 43 | "No Named Subdivision" cannot carry a neighborhood segment |
| No Named Subdivision · 21915 Lakeview Dr | $649,000 | **15** | 37 | Same problem. 2024 build, 15 days on market — a fine *home tour*, not a neighborhood |
| Summer Breeze Phase I · 109 Summer Breeze Rd | $575,000 | 86 | 50 | Overlaps Palmetto Trace: inland, small HOA, family-oriented. Palmetto Trace wins on the Pier Park adjacency |

---

## Totals

| | |
| --- | --- |
| Neighborhoods in the video | 5 of 15 available |
| Gallery photos across the five | **476** |
| Of those, reachable via the tour files | 200 (five × 40) |
| **Unused by the tour files** | **276** |
| Slideshow footage after trimming | 5 × 1:53.6 = **9:28** |
| Pier Park aerial plates | **21:23** |
| Target runtime | 28–32 min |

The arithmetic that matters: **9½ minutes of slideshow against a 30-minute
video.** Even used in full, the tour files cover under a third of the runtime.
The other two thirds is Karen, the Pier Park plates, hand-cut gallery stills, and
whatever she shoots herself. Plan it that way from the start.
