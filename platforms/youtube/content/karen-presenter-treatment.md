# Karen's presenter treatment

**How Karen appears on screen.** The companion to
[`karen-voice-and-humor.md`](karen-voice-and-humor.md), which covers what she
says. This one covers what the viewer looks at while she says it.

Everything here is a **documented constraint with the reasoning attached**, not a
style preference. The findings behind it are the kind that get forgotten and then
rediscovered expensively in an edit.

---

## ⭐ The constraint that drives all of this

**Mike Lawell, 2026-08-23:** *"I don't have real Karen for the first shot. We
have to try to generate her at the desk."*

There is **no real video footage of Karen, and none is coming.** Every single
appearance on this channel is synthetic. That is the starting condition, not a
temporary gap.

Now stack it against what the HeyGen documentation actually says
([`HEYGEN.md`](../../../tools/avatar/HEYGEN.md), checked 2026-08-23):

- **No API parameter makes an avatar smile, laugh or emote on cue.** No emotion presets. The only expression-adjacent parameter is `expressiveness` (`high`/`medium`/`low`), it is **Avatar IV photo avatars only**, and it is an **energy dial** rather than an emotion selector.
- The engine is **speech-to-mouth**. It re-animates the **mouth region** against the waveform. **Cheeks, eyes and brow stay in the avatar's default neutral.**

Put those together and the arithmetic is unforgiving:

> ### A full-frame avatar for twenty minutes is twenty minutes of a neutral face with a moving mouth.

The reaction problem solved for one giggle in beat 9 is not a one-beat problem.
**It is the whole runtime.** Everything below is the response to that.

### The rule that falls out of it

Neutral is not a *wrong* expression. It is wrong **for comedy** and completely
fine **for sincerity**. A neutral face delivering a hard fact reads as composed.
A neutral face delivering a joke reads as broken.

> ## ⭐ Spend the synthetic face on sincerity. Spend the cutaways on comedy.

That single line resolves most placement questions on this page. Full-frame
Karen belongs on the candour beat, the authority beats and the CTA. It does not
belong on the punchlines.

---

## ⭐ The treatment hierarchy

**The avatar is the fallback, not the default.** Karen's library turned out to
hold far more real material than the scripts were written against, and that
inverts the assumption. Work down this list and only reach the bottom when the
tiers above genuinely have nothing.

> ### This is no longer a map video with narration over it.
> ### It is a filmed community tour with the map as its navigational spine.

That is not a rebrand, it is a format change with a citation behind it. The
playbook says voiceover-over-B-roll *"rarely clears 10 min AVD; a live filmed
walk-through does"* (`D1-QA` 00:48:32), and names the walk-through as the thing
**AI cannot replicate**: *"AI can't disrupt truth. AI can't disrupt demonstration
of content"* (`D1-QA` 00:36:57). The channel now has 1:25 of exactly that.

| | Treatment | Available for | Why it ranks here |
| ---: | --- | --- | --- |
| **1** | **Live 8K footage**, presenter **absent** | Phases **1, 2, 6B & 6C, 8, 9, 10** and the **Town Center** | The format the playbook says clears AVD and AI cannot replicate |
| **2** | **Karen's own geotagged photographs**, with motion applied | Every other plat, and 3A–7 especially richly | Proof of presence, 1,182 already indexed by phase |
| **3** | **Map frames** with the presenter **corner-inset** | Everywhere, as connective tissue | The playbook's prescribed map-video format |
| **4** | **Full-frame synthetic presenter**, over a real photograph | Hook and candour/CTA only | The weakest visual the channel has |

### ⭐ Every one of the sixteen plats now has ground-level material

There is no longer a phase anywhere in the community that has to be carried by a
map frame and a synthetic face alone.

**The video column is where a clip *starts*.** Actual coverage is broader and
unmapped: every long clip crosses into neighbouring plats, and a dash means *"no
clip begins here,"* **not** *"no footage exists."*

| Plat | Cart-tour photos | Clip **starts** here |
| --- | ---: | --- |
| 1 | 5 | **40:54** |
| 2 | 30 | 5:39 |
| 3A | 151 | — `[KAREN — confirm]` |
| 3B & 3C | 59 | — `[KAREN — confirm]` |
| 3D | 59 | — `[KAREN — confirm]` |
| 4A | 25 | — |
| 4B | 53 | — |
| **Town Center (5A3)** | 174 | ~4:01 day + 3:21 **evening** |
| 5B | 53 | — |
| 5C | 108 | — |
| 6A | 25 | — |
| 6B & 6C | 11 | **11:17** |
| 7 | 244 | — |
| 8 | 146 | 7:54 |
| **9** | **0** | **10:50** |
| **10** | **0** | within the Phase 9 clips (Mike) |

**Phase 3 is marked for confirmation on purpose.** Mike says he drove it, and the
40:54 clip is demonstrably nowhere near its start point by minute 30, so the
footage may be in there. Do not record Phase 3 as photographs-only.

**Phases 9 and 10 stopped being the hard case.** They have no photographs at all,
but they now have the video, and a 33-megapixel frame extract is a better still
than a phone photo. **They need no shoot.**

**Phase 6A and 4A look thinnest** at 25 photos and no clip starting in them —
though again, that is a floor rather than a finding.

---

## 1. ⛔ Not at a desk

**The desk is the single most recognisable "this is synthetic" composition
available.** It is the default output of practically every avatar tool, and it
sits on top of generic realtor stock framing, so it reads as two clichés at once.

It also spends the AI-detection budget that the em-dash rule and the
no-synthesised-reactions rule exist to protect. `win-with-youtube-challenge.md`
records that YouTube runs **built-in AI language and imagery detection and
throttles content that indexes too high** (`D1-QA` 00:03:34, `D1-GS` 00:13:44).
**Imagery**, not just language. A synthetic presenter at a synthetic desk is the
imagery half of that test, failed on the opening frame.

### The existing desk plates, examined

These already exist in the Microsoft 365 library under `Marketing\Karen\Office\`:
`Karen at Desk with Latitude Margaritaville.png`, `…Closeup.png`,
`Karen at Desk full room.png`, plus empty-room variants (`Desk Clean.png`,
`Desk with Neon Sign.png`, `Desk Wall Space.png`).

They were looked at rather than assumed, and there are **three separate problems**
beyond the format objection:

| Problem | Detail |
| --- | --- |
| **Heavy magenta cast** | The room reads pink across the whole frame. It does not match any other Karen asset, and it does not look like anywhere in Northwest Florida |
| **Invented interior** | It is a generated room. Nothing in it is checkable, which is the opposite of everything else this channel does |
| **Wrong brand scope** | The neon reads *"Living in Latitude Margaritaville Watersound with Karen."* This channel covers the **whole Northwest Florida beaches market**, not one community. A Latitude-branded set caps every video shot on it |

### What the desk plates are still good for

Not nothing. **Keep them, use them narrowly:** a static end card, a contact-card
background, a thumbnail element, or anything Latitude-specific where the neon is
an asset rather than a cap. What they should not be is **the format** for a
twenty-minute video.

---

## 2. The corner inset is the prescribed format, not a workaround

Two independent sources land on the same answer, which is worth recording
because the convergence is the argument.

**The playbook prescribes it for this exact video type.** From
[`realtor-playbook.md`](../../../knowledge/channel-junkies/playbook/realtor-playbook.md),
Day 10:

> *"Map videos — record Google Maps via Zoom/Loom screen-share, **put yourself in
> the corner**, narrate neighborhoods using Street View and personal stories, end
> with 'call me — I know exactly where you'll want to live.'"*

The flagship and all ten deep dives **are map videos.** Corner-inset is the
format they are supposed to be in.

**The repo's own avatar tooling reached the same conclusion independently**, for
an unrelated reason. From [`tools/avatar/README.md`](../../../tools/avatar/README.md):

> *"these free models are strongest on **head-and-shoulders**. That's why the
> presenter is composited as a lower-corner 'on-camera guide,' not a full-length
> standing figure."*

One arrived at it from **audience retention**, the other from **render quality**.
Neither knew about the HeyGen expression limit, which is now a **third** reason
pointing the same way: a corner inset is small, peripheral and never the focus,
which is the most forgiving possible framing for a face that cannot change
expression.

**Three independent reasons, one answer. Put her in the corner.**

---

## 3. Composite over real photographs, never an invented interior

A synthetic figure in front of a **real, checkable location** reads far better
than a synthetic figure in an invented office, because **the place is verifiable
even when the render is not.** The viewer's eye lands on the Bandshell, the gate,
the street sign, and those are all real.

It also honours *"green screens are played out, shoot talking heads on location"*
(WWYT, Aug 2026, in the playbook's gear update) in spirit. We cannot shoot on
location. We can put her **on** the location.

**Composite her over:**

- Her own **278 geotagged Phase 7 and 8 photographs** (`Latitude Margaritaville Photo Map.kml` in the M365 library)
- The four anchors from [`photo-shot-list.md`](phase-deep-dives/photo-shot-list.md): the Bandshell, the Town Center, the Highway 79 frontage, the Sales Center
- Cool Water Way, the gate, drive footage

**Never over:** a generated room, a stock office, a blank wall, or a gradient.

---

## 4. Verified asset inventory

Checked on disk 2026-08-23, with `ffprobe` where it mattered.

### ⭐ Tier 1 — the 8K tour footage

**1:25:23 of 8K, across two folders**, all shot on a phone. Every duration was
verified with `ffprobe`. **The plat column is where each clip *begins*, not what
it covers** — see the caveat below, which is load-bearing.

| Folder | Clip | Duration | Plat at **start** |
| --- | --- | ---: | --- |
| `Phases\Videos\` | `20260822_105457.mp4` | **40:54** | **Phase 1** |
| `Phases\Videos\` | `20260822_104302.mp4` | 7:54 | **Phase 8** |
| `Phases\Videos\` | `20260822_121813.mp4` | 5:54 | **Phase 9** |
| `Phases\Videos\` | `20260822_122522.mp4` | 4:56 | **Phase 9** |
| `Phases\Videos\` | `20260822_123852.mp4` | 0:01 | **discard** |
| `video\` | `20260822_120642.mp4` | **11:17** | **Phase 6B & 6C** |
| `video\` | `20260822_120031.mp4` | 5:39 | **Phase 2** |
| `video\` | ×3 daytime clips | 4:01 | **Town Center** |
| `video\` | ×10 evening clips, 19:01–19:32 | 3:21 | **Town Center**, evening |
| `Town Center\Bandshell\Music\` | ×7 clips | 1:26 | **Town Center**, live music |

**7680×4320 HEVC, 30 fps, ~96 Mbps, AAC 48 kHz stereo.**

> ⚠️ **The second folder is easy to miss.** `video\` at the community root holds
> **24 minutes** including the two longest non-tour clips. Anyone inventorying
> `Phases\Videos\` alone will undercount by a third.

#### ⛔ Start points are a floor, not an inventory

The GPS comes from each file's single `location` tag. **Samsung phone recordings
carry one start-point tag and no telemetry track**, so the table says where a
clip *began* and nothing about where it went. The community is contiguous, and
every long clip necessarily crosses into neighbouring plats.

**This was tested on the 40:54 clip, and the clip travels a long way:**

| Timestamp | What the frame shows |
| --- | --- |
| **30:00** | Undeveloped lots, a walking trail, new utility pedestals, **no houses**. That is **not Phase 1** — Phase 1 is the oldest plat (PB 27/73) and is built out |
| **40:00** | **The Town Center** — the golf-cart parking bays and the amenity building |

So a single clip tagged "Phase 1" demonstrably covers Phase 1, undeveloped land
somewhere else entirely, and the Town Center.

> ### ⛔ Never read this table as "phase X has no footage."
> It only supports *"no clip starts in phase X."* Recording the stronger claim
> would tell an editor not to scrub 41 minutes of 8K looking for a phase, and
> usable footage would be left on the floor.

**Mike's own account is broader than the metadata:** *"I did a video tour of
phase 1, 2, 3, and town center yesterday."* He is ground truth for his own drive,
and throughout this project his recollection has beaten the paperwork. He also
confirms the **Phase 9 clips continue into Phase 10**, which is exactly the
coverage a start-point tag cannot show.

**On Phase 3 specifically:** Phase 3 has **269 photographs** and **no clip that
starts inside it**. The 40:54 clip beginning in Phase 1 travels well beyond its
start point, so **Phase 3 footage may well exist inside the longer clips.**
`[KAREN — confirm on review]`

#### 📋 The correct method, when someone has time for it

Start-point guesses can be converted into a real per-minute phase index:

1. **Sample a frame every 30 seconds** from the long clips.
2. **Read the street-name signs** and look them up in [`streets_by_phase.md`](../../../properties/latitude-margaritaville-watersound/streets_by_phase.md), which already maps every street to its plat.
3. Write out a per-minute index of which plat each clip is in.

> **Feasibility was checked, and the honest answer is "yes, with a caveat."**
> A native-resolution crop from the 30:00 frame is **sharp enough to read
> mounting bolts and an asset-tag sticker on a sign**, so 8K resolution is not
> the constraint. **Sign orientation is.** The sign in that particular frame was
> facing away — a stop sign seen from behind. Expect a meaningful fraction of
> 30-second samples to catch sign backs, and sample more densely, or step
> forward a few seconds, when one does.

This is real work rather than something to do in passing, but it is the correct
method and it belongs to whoever builds the edit.

#### ⭐ Extract frames instead of shooting stills

**A 7680×4320 frame is a 33-megapixel still** — larger than most stills cameras
produce.

> ### Standing method: any phase with video and no photographs gets its stills extracted from the video.
> That is what closes **Phases 9 and 10**, which have zero cart-tour photographs.
> **They do not need a photo shoot.**

The folder also holds **16 huge stills** already: seven at **8160×4592** (37 MP)
and nine at **16320×9180** (150 MP). At that size a single frame crops to several
distinct 1080p shots.

#### Working rules for the 8K

- **⛔ Delivery stays 1080p.** The playbook is explicit: shoot 1080p/60, *"the only reason you would ever need 4K is if you were going to start playing these videos at the movie theater"* (`D2-GS` 00:19:43), citing storage burden and slow transfers to offshore editors. A 27.5 GB file is exactly that problem. **The 8K is justified only as reframing headroom, never as a delivery format.**
- **⭐ 8K is a virtual camera operator.** A 1920-wide window inside a 7680-wide frame can pan, punch in and reframe, so one static drive-by yields several distinct shots with real camera moves at full delivery quality. That is the single biggest reduction in how much the avatar has to carry.
- **⚠️ The cart's windscreen post is in shot.** It appears as a dark vertical bar at **frame right** in some of the drive footage, though not all — it depends where the phone was mounted. **It has to be cropped out**, and 8K is exactly what makes that free: cropping the right ~8% of a 7680-wide frame still leaves well over 1080p. **Check every selected shot for it**, because it is easy to miss on a proxy and obvious on delivery.
- **The picture quality is good.** Sharp, well exposed. A native-resolution crop resolves the mounting bolts and asset-tag sticker on a roadside sign. This is genuinely usable B-roll, not just reference.
- **⛔ Proxies are mandatory, not optional.** 8K HEVC at 96 Mbps **will not scrub in real time** on most machines. Cut against 1080p proxies and conform back only for shots that need reframing. Discovering this on edit day costs a day.
- **Frame rate mismatch, minor.** This is **30 fps** and the playbook prefers 1080p/**60**. Fine for delivery, but 30 cannot be conformed up, so do not plan slow motion from it.

### ⛔ Strip the location audio

**Mike's instruction:** *"we need to remove all of the sound from the videos, not
important when Karen is talking."*

Correct, and there is a **second reason that is stronger than convenience** and
must be recorded, because otherwise somebody will be tempted to keep "just a
little" ambience under the Bandshell shots.

> ### The evening Town Center clips are Bandshell footage with live music playing.
> Publishing recorded live performance of copyrighted songs invites a **YouTube
> Content ID claim**, and in a **Jimmy Buffett community** the live material is
> very likely to be Buffett covers.

The playbook is unambiguous about the stakes. *"Never use footage or photos you
don't own"* — one agent had to **wire a creator ~$14,000** to get a channel
restored (`D4-GS` 00:54:38–00:55:43) — and the strike policy is **one strike a
warning, two a 30-day penalty box, three permanent removal** (`D4-GS`
00:54:13–00:54:33).

So muting is not housekeeping. **It removes a real channel risk.**

It was also measured before being decided: eight samples across the 41-minute
tour showed levels of **−24 to −31 LUFS** with the 1–4 kHz speech band sitting
**8 to 15 dB below** the low band on most of them. Wind and cart rumble
dominant, occasionally something with real mid-band content. **Neither uniformly
unusable nor reliably usable**, which is another reason not to build on it.

### ⭐ Stills for the performance, muted video for the setting

Mike, refining the above: *"I would just post images instead of music for the
bandshell music."*

**Keep the distinction rather than applying a blanket rule.** It is the
*performance* material that becomes stills. The evening clips also hold
non-performance content — carts arriving, the venue at dusk, people walking in,
the empty stage before a show — and that stays usable as **muted video**. A slow
push on an empty Bandshell at sunset is a strong shot carrying no risk at all.

> ## The rule, and it generalises
> **Where the missing sound would be conspicuous, use a still. Where it would
> not, muted video is fine.**
>
> Muted video of a live band is **dissonant**: the viewer sees people dancing,
> hears only narration, and *notices the absence.* A photograph creates no such
> expectation. This is a better rule than "mute everything," and it applies
> anywhere in the library with performance, crowds, or an obvious sound source.

**There is no shortage of stills for it — 33 for a beat that needs three or four:**

| Source | Count |
| --- | ---: |
| `Town Center\Bandshell\Music\` | **26 photographs** (plus the 7 videos) |
| `Town Center\Bandshell\` | 6 photographs |
| `Bandshell Music - Golf carts.jpg` (community root) | ⭐ carts lined up outside — the whole thing in one frame |

**This resolves the open `[KAREN]` question** about what a Saturday night is
actually like. The answer is now: **stills of the crowd and the carts, narrated,
over the music bed.** No location audio, no Content ID exposure, and the beat
still lands.

### What replaces the stripped audio

A fully silent picture under narration reads as dead, and the playbook is blunt
that production value is forgiving but **audio quality is not** (`D1-VIP`
00:57:28). **Bed plus ducked narration, never bare.**

Already in the library, so nothing needs sourcing:

| Asset | What it is |
| --- | --- |
| `LM Island Breeze - Tour Bed.mp3` | ⭐ The intended bed |
| `LM Island Breeze - Mix QA (narration+duck).m4a` | ⭐ A reference mix **with ducking already applied** |
| `video\music\shared\Bed 1.mp3` … `Bed 5.mp3` | Five more shared beds |
| `Clubs\_reel\reel_beat.mp3` | A sixth |

### ⭐ Tier 2 — the geotagged photo library

Karen photographed a **golf-cart tour of the whole community on 2026-08-09**:
**1,193 photos, 1,182 with GPS EXIF (99%)**, every one assigned to a plat by
point-in-polygon against `tools/map/`'s polygons.

Index: `…\session-state\…\latitude-phase-map\golfcart_byphase.json`
(counts verified against the file).

| Phase | Photos | | Phase | Photos |
| --- | ---: | --- | --- | ---: |
| 7 | 244 | | 5B | 53 |
| **5A3 (Town Center)** | 174 | | 4B | 53 |
| 3A | 151 | | 2 | 30 |
| 8 | 146 | | 4A | 25 |
| 5C | 108 | | 6A | 25 |
| 3D | 59 | | 6B & 6C | 11 |
| 3B & 3C | 59 | | 1 | 5 |
| | | | **9 and 10** | **0** |

Plus **39 outside any plat** — approach roads, Highway 79, the entrance. Useful
for the "getting here" and Highway 79 beats, which currently have no visual at
all.

This is **in addition to** the 278 geotagged Phase 7 and 8 photographs already
noted on the shot list.

### Amenity and activity sets, none of them in any script

All under `…\Latitude Margaritaville Watersound\`:

| Set | Contents |
| --- | --- |
| `Activities\` | ⭐ **`bingo.jpg`** and **`Hawaiian Bingo.png`** · kayaking |
| `Town Center\Bandshell\Music` | 26 photos, 7 videos |
| `Town Center\Workin' N' Playin' Center\` | ⭐ the **Barkaritaville** plate |
| `West Bay Center\` | ⭐ `West Bay Center 001.JPG`, `002.MP4`, `Watersound Retail.JPG`, `Aerial Retail Center - Existing.jpg`, `West-Bay-Map.jpg`/`.avif`, `Publix .JPG`, `Publix West Bay Center 01.MP4` |
| `Bar & Chill\Sunsets` | 46 |
| `Pool` 16 · `Kayak Launch` 10 · `Intercoastal` 10 · `Bocce Ball` 7 · `Fins Up! Fitness Center` 6 | plus Putting Green, Cornhole, Tennis and Pickleball, Walking Trails, Trails |
| `Building Features\` | 21 |
| `Events\` | `Ladies of Latitude Breast Cancer Run 5k.jpg` |
| `Clubs\` | `Retirement Community Reel.mp4` + `reel_beat.mp3` |

**Audio beds already exist:** `LM Island Breeze - Tour Bed.mp3`, and a mix-QA
reference with ducking already applied.

### 🏥 FSU Health Panama City Beach — drone footage

`…\West Bay & HWY 79 Corridor\FSU Health Panama City Beach\FSU Health Panama City Beach 01.MP4`

**2:24 · 3840×2160 · HEVC Main 10 · 59.94 fps · ~67 Mbps · 1.4 GB · aerial drone.**

Karen's own footage of the hospital going up, and it is good: sharp, well
exposed, showing a topped-out five-level concrete structure with a finished,
occupied building beside it. **It is the proof that beat 3's "the hospital is
still being built" is first-hand rather than repeated.** What it does and does
not support on camera is set out in
[`karen-voice-and-humor.md`](karen-voice-and-humor.md).

> ⚠️ **This clip matches nothing else in the library and must be conformed
> before intercutting.** Two separate mismatches:
>
> | | This clip | Everything else |
> | --- | --- | --- |
> | **Bit depth** | **10-bit** (`yuv420p10le`, Main 10) | The Pier Park plates are **8-bit** |
> | **Frame rate** | **59.94 fps** | The 8K community footage is **30 fps** |
>
> Dropped into a 30 fps 8-bit timeline untouched, the grade will not match and
> the motion will judder. **Pick one working space and one frame rate and
> conform everything into it before the edit starts**, in the same pass as the
> proxies below.

### 🐈 The cats — the one asset that lives outside the library

**48 photographs**, foldered per cat, supplied by Mike:

| Folder | Photos |
| --- | ---: |
| `Bella\` | 17 |
| `Buddy\` | 17 |
| `Cinder\` | 10 |
| root, loose | 4 |

File dates run **2023 through 2026-08-18**, so there is recent material as well
as older, and sizes are **1.0–8.8 MB** — full-resolution phone photography, ample
for a cutaway.

> ⚠️ **These are the one exception to "everything is in the M365 library."**
> They live at **`C:\Users\mikel\Pictures\Cats\`** — Mike's **personal** Pictures
> folder, not `NWFL Beach Homes - Documents` — and they are **personal
> photographs rather than brokerage assets**. Anyone looking for them in the
> shared library will not find them.
>
> ⛔ **Do not commit them**, same rule as every other media asset. Reference by
> path only.

**Editorial note for whoever places the beat: name and show all three.**
*"Bella, Cinder and Buddy"* is funnier than *"our cats"* because **the
specificity is the joke**, and three separate faces on screen sell *"we're
staff"* far better than one does. With 10–17 shots of each, three can be picked
that **match tonally** rather than taking whatever exists — so choose for
consistency of light and mood, not just the cutest frame.

### Stills

Paths relative to `…\NWFL Beach Homes - Documents\Marketing\Karen`.

| Asset | Notes |
| --- | --- |
| `Headshots\Portraits\Karen High Res no BG.jpg` | ⭐ **Background already removed.** The workhorse still. A 1k version sits beside it |
| `Headshots\Portraits\Karen-transparent.png` | Transparent PNG alternative |
| `Headshots\Portraits\Karen Full Length Portrait.png` + `.psd` | Full length, layered source available |
| `Full Length\Karen - Sunset - 16-9.png` | Full length, 16:9, sunset grade |
| `AI Avatars\Karen Gestures 44 hands up.png` | Gesture plate, plus a `-lighting` variant and a 4k version |
| `AI Avatars\heygen_brand_glossary.csv` | Brand glossary for HeyGen |

### Expression plates

| Asset | Notes |
| --- | --- |
| `Headshots\Karen Wow.png` | ⭐ **A genuine big expression** — mouth open, hands up, surprised. The thing the avatar cannot do |
| `Headshots\Surprised Karen.png` | Same family |

> ⚠️ **Wardrobe continuity.** The expression plates are in a **pink striped
> shirt**. The alpha video plates below are in a **beige linen blazer over
> white**. They **cannot be intercut inside one video** without reading as two
> different days. Pick a wardrobe per video and stay in it, or re-render the
> expression plate in the blazer.

### Existing alpha video plates

Both are **ProRes 4444 with a real alpha channel** (`yuva444p12le`) — already
keyed, no green-screen work needed.

| Asset | Spec | Figure |
| --- | --- | --- |
| `…\Latitude Margaritaville Watersound\Karen - Coastal Subscribe Outro - Alpha.mov` | 1080×1920, 10.0 s | ⭐ Waist-up, **large in frame**, gesturing. The highest-resolution alpha figure available |
| `…\Karen - LM Subscribe Outro - GreenKey Master.mov` | 1920×1080, 12.2 s | Waist-up, small and centred |

> ### 📌 Correction worth recording
> These two are commonly written off as "unusable — vertical, and
> Latitude-branded." That is true of them **as finished outros** and false of
> them **as mattes.**
>
> The frames were extracted and looked at. **Both figures are visually
> brand-neutral** — the Latitude branding in the LM one lives in its graphics and
> audio, not in the plate. And a **1080×1920 vertical frame is irrelevant when
> you are compositing a cutout**: the alpha lets the figure be lifted onto any
> canvas at any size.
>
> So **`Karen - Coastal Subscribe Outro - Alpha.mov` is the single best existing
> source for a corner-inset composite**, because its figure is the largest and
> therefore carries the most resolution when scaled down into a corner.
>
> New **spoken content** still needs new renders. The **mattes** do not.

---

## 5. Face-time budget

Given the mouth-only constraint, **minimising sustained full-frame exposure is
the main lever available.** Budget it deliberately rather than defaulting to
full-frame.

**Read this as the ceiling, not the target.** The
[treatment hierarchy](#-the-treatment-hierarchy) comes first: where tier 1 live
footage or tier 2 photographs exist, the presenter should be **absent**, and the
numbers below shrink further.

| Segment | Treatment | Why |
| --- | --- | --- |
| **Hook, ~30 s** | Full-frame, composited over a **real community photograph** | The one place a face earns full frame. Establishes a person, over a checkable place |
| **Body** | **Map full-screen**, presenter corner-inset or absent — **or live footage with her absent entirely** where it exists | The playbook's prescribed map-video format, and the map is the product |
| **Candour beat and CTA** | Full-frame again, over a real photograph | Sincerity is exactly where a neutral face is *correct* |
| **Close** | Subscribe outro | Existing plate, re-rendered |

That is **at most one minute of full-frame synthetic face in a twenty-minute
video.** Every other second is live footage, map, photographs, or drive footage
with her voice over it.

**Note how this interacts with the sincerity rule.** The two full-frame blocks
are the hook and the candour/CTA — both sincere registers. Every comedic beat
falls in the body, where she is corner-inset or absent. The budget and the
register rule agree, which is a good sign that both are right.

**Phases 1, 2, 3 and the Town Center should now run well under the ceiling**,
because tier 1 footage covers their bodies outright. **Phases 9 and 10 will sit
at it**, because they have neither footage nor photographs.

---

## 6. The cutaway rule, generalised

The giggle in beat 9 was the first instance, not the whole rule.

> ## ⛔ Any moment requiring visible emotion cuts away from the avatar.
> A laugh, a wry look, mock indignation, a raised eyebrow. If the face has to do
> something the engine cannot render, **the picture is somewhere else.**

The cutaway has to be **planned**, and the image has to **exist**. That makes it
a scripting and shot-list constraint, not an editing decision.

### Per-beat cutaway assignments

Checked against
[`photo-shot-list.md`](phase-deep-dives/photo-shot-list.md).

| # | Beat | Face needs to | Cutaway image | Status |
| ---: | --- | --- | --- | --- |
| 1 | Bring a cart | Nothing — Mike is third person, deadpan | The cart in Karen's driveway, **or** the Town Center cart bays at ~40:00 in the 40:54 clip | ✅ Phase 8 shot 5. **Reuse it in the flagship's Q3.** The Town Center bays are the stronger image: dozens of carts says everybody does it |
| 2 | The cats | Warm, smiling | **Bella, Cinder and Buddy**, and the Barkaritaville plate | ✅ **Fully resourced.** 48 photographs at `C:\Users\mikel\Pictures\Cats\` (Bella 17, Buddy 17, Cinder 10, 4 loose), plus `Town Center\Workin' N' Playin' Center\high-res-bark-aritaville-…jpg`. **Lacks a script slot, not assets** |
| 3 | The dermatologist | Wry | West Bay Center storefronts, and the hospital site | ✅ **Fully resourced.** `West Bay Center\` has `West Bay Center 001.JPG`, `002.MP4`, `Watersound Retail.JPG`, `Aerial Retail Center - Existing.jpg`, `Publix .JPG` and more. **Lacks a script slot, not assets** |
| 4 | Lawn care | Nothing — **stay full-frame** | The lawns, including a poor one | ✅ Phase 8 shot 4. See note below |
| 5 | Bingo | Self-deprecating smile | Bingo at the Town Center | ✅ **Solved.** `Activities\bingo.jpg` **and** `Activities\Hawaiian Bingo.png` |
| 6 | Hawaiian shirt | Nothing — Mike, deadpan | The shirts on the rail, no face | ✅ Phase 8 shot 6 |
| 7 | Escape Avenue | Nothing — authority | The address-range graphic, and the Escape Ave sign | ✅ Phase 8 shot 1 + on-screen graphic |
| 8 | Phase 8 zero Buffett | Wry, self-deprecating | The **Cool Water Way** sign | ✅ Phase 8 shot 2 |
| 9 | No Shoes Court | **Giggle** | The **No Shoes Ct** sign, clean 4-second hold | ✅ Phase 5 block shot 3 |

**Every beat now has its images.** With the cat photographs supplied, **the
cutaway audit is closed** — nothing on this list is waiting on a shoot.

> ### 🎁 A free callback nobody planned
> `Activities\` contains **`Hawaiian Bingo.png`**, and beats 5 and 6 are **bingo**
> and **the Hawaiian shirt**. If both land in the same episode — and they do, both
> are in the **Phase 8 deep dive** — the bingo cutaway can be the *Hawaiian* bingo
> frame, which quietly sets up Mike's shirt beat five minutes before it arrives.
>
> Use it **only if it stays invisible.** The moment it looks like a constructed
> callback it becomes a comedy routine, which is the thing Karen is not doing.
> Play the image straight and let the few who notice enjoy it.

> **Beat 4 is the deliberate exception.** The lawn-care beat is the honesty
> moment, and honesty is delivered *to* the viewer. **Stay on the face.** Its
> shot-list entry is support B-roll, not a cutaway. This is the sincerity rule
> doing its job.

### ➡️ Beats 2 and 3 are waiting on a video, not on assets

Both are **fully resourced and unplaced.** Beat 2 has 48 cat photographs and the
Barkaritaville plate; beat 3 has the whole West Bay Center set. Neither has a
script slot, and that is **correct** — they are not phase-map beats:

- **The cats** are a pets-and-HOA beat. Nothing in a plat-by-plat video is about pets.
- **The dermatologist** is a **West Bay Center** beat, and neither the flagship nor any deep dive covers the commercial centre at all.

> **That points somewhere.** Two approved beats with complete assets and no home
> is a reasonable signal that **the amenities / day-in-the-life video is the next
> content package**, rather than something to be wedged into the existing one.
> The library backs that up: `Pool`, `Kayak Launch`, `Bocce Ball`,
> `Fins Up! Fitness Center`, `Putting Green`, `Cornhole`,
> `Tennis and Pickleball`, `Walking Trails`, `Bar & Chill\Sunsets`,
> `Barkaritaville` and the West Bay Center set are all shot and all unused.
>
> Recorded here as a **forward reference** so the two beats are parked against a
> plan rather than left in limbo.

---

## 7. Render and prep batch

Both existing subscribe outros need new renders for **content** reasons — one is
vertical and one is Latitude-branded, and this channel is Northwest Florida wide.
Since the renders have to happen anyway, **batch everything in one pass** rather
than paying the setup cost three times:

- [ ] **Subscribe outro, 16:9, brand-neutral** — replaces both existing ones for general use
- [ ] **Hook plate** — full-frame, alpha, long enough for a 30-second hook
- [ ] **Candour / CTA plate** — full-frame, alpha
- [ ] **Corner-inset plate** — waist-up, alpha, neutral gesturing, long enough to loop under map narration
- [ ] Confirm a **single wardrobe** across the batch, and decide whether the expression plates get re-rendered to match

**Render on alpha, always.** Every plate above should come out with a real alpha
channel, the way `Karen - Coastal Subscribe Outro - Alpha.mov` already does. A
flattened plate can only be used on the background it was rendered against; an
alpha plate can be composited over any photograph in the library, which is the
entire treatment on this page.

### ⛔ Before any edit session: build 8K proxies

**Do this first, not on edit day.** 8K HEVC at 96 Mbps will not scrub in real
time on most machines, and finding that out with an editor waiting costs a day.

> ⭐ **Stripping the audio and building proxies is one operation, not two.**
> `-an` while transcoding to 1080p ProRes or DNxHR gives muted proxies in a
> single pass, and the 8K originals stay untouched as reframing source.

- [ ] Transcode **all keeper 8K clips in both folders** — `Phases\Videos\` **and** `video\` — to **muted 1080p ProRes or DNxHR** proxies, `-an` in the same pass
- [ ] Cut against the proxies
- [ ] **Conform back to 8K only for shots that need reframing** — the pan, punch-in and reposition moves
- [ ] Deliver **1080p**. The 8K is headroom, never a delivery format
- [ ] **Conform the FSU Health clip** — it is **10-bit at 59.94 fps** against 8-bit 30 fps everywhere else. One working space, one frame rate, decided before the edit starts
- [ ] **Extract stills for Phases 9 and 10** from their clips, at full 7680×4320
- [ ] **Every selected shot checked for the cart windscreen post** at frame right, and cropped out where present
- [ ] **No location audio in the final mix.** Bed plus ducked narration, using `LM Island Breeze - Tour Bed.mp3` against the `Mix QA (narration+duck)` reference
- [ ] **Bandshell performance is stills only.** Muted video is fine for the setting — arrivals, dusk, the empty stage
- [ ] Check `Phases\Phase 1\Phase 1-1.mp4` — modified 2026-08-23 11:21, so a Phase 1 segment may already be in progress

---

## Checklist

- [ ] **The treatment hierarchy was worked top-down.** Live footage where it exists, then Karen's photographs, then map with corner-inset, and only then a full-frame avatar
- [ ] No shot in the final cut places Karen at a desk, or in any generated interior
- [ ] Every full-frame appearance is composited over a **real photograph**
- [ ] Full-frame face time is **at most one minute** in a twenty-minute video, and less where tier 1 or tier 2 material covers the body
- [ ] Every full-frame block is a **sincere** register — hook, candour, CTA. No punchline is delivered full-frame
- [ ] Every beat requiring visible emotion **cuts away**, and the cutaway image exists
- [ ] Beat 9's giggle plays over the No Shoes Ct sign, held clean for at least 4 seconds
- [ ] Wardrobe is consistent across every plate used in one video
- [ ] All plates rendered with a real alpha channel
- [ ] **8K proxies built before the edit session**, muted in the same pass, and delivery is 1080p
- [ ] **No location audio anywhere in the final mix.** Bed plus ducked narration, never bare and never live
- [ ] **No live-performance video.** Bandshell music is stills; muted video only for arrivals, dusk and the empty stage
- [ ] Phases 9 and 10 stills are **frame extracts**, not a re-shoot
