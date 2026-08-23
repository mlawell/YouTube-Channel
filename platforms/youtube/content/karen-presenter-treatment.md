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

Checked on disk 2026-08-23, with `ffprobe` where it mattered. Paths are relative
to `C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents\Marketing\Karen`.

### Stills

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

| Segment | Treatment | Why |
| --- | --- | --- |
| **Hook, ~30 s** | Full-frame, composited over a **real community photograph** | The one place a face earns full frame. Establishes a person, over a checkable place |
| **Body** | **Map full-screen**, presenter corner-inset or absent | The playbook's prescribed map-video format, and the map is the product |
| **Candour beat and CTA** | Full-frame again, over a real photograph | Sincerity is exactly where a neutral face is *correct* |
| **Close** | Subscribe outro | Existing plate, re-rendered |

That is roughly **one minute of full-frame synthetic face in a twenty-minute
video.** Every other second is map, photographs, or drive footage with her voice
over it.

**Note how this interacts with the sincerity rule.** The two full-frame blocks
are the hook and the candour/CTA — both sincere registers. Every comedic beat
falls in the body, where she is corner-inset or absent. The budget and the
register rule agree, which is a good sign that both are right.

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
| 1 | Bring a cart | Nothing — Mike is third person, deadpan | The cart in Karen's driveway | ✅ Phase 8 shot 5. **Reuse it in the flagship's Q3** |
| 2 | The cats | Warm, smiling | **Bella, Cinder and Buddy**, and the Barkaritaville sign | ❌ **Needs adding** |
| 3 | The dermatologist | Wry | West Bay Center storefronts, and the hospital site | ❌ **Needs adding** |
| 4 | Lawn care | Nothing — **stay full-frame** | The lawns, including a poor one | ✅ Phase 8 shot 4. See note below |
| 5 | Bingo | Self-deprecating smile | Town Center, ideally the activity room | ⚠️ Town Center is an anchor shot, but a **bingo-specific frame is better** |
| 6 | Hawaiian shirt | Nothing — Mike, deadpan | The shirts on the rail, no face | ✅ Phase 8 shot 6 |
| 7 | Escape Avenue | Nothing — authority | The address-range graphic, and the Escape Ave sign | ✅ Phase 8 shot 1 + on-screen graphic |
| 8 | Phase 8 zero Buffett | Wry, self-deprecating | The **Cool Water Way** sign | ✅ Phase 8 shot 2 |
| 9 | No Shoes Court | **Giggle** | The **No Shoes Ct** sign, clean 4-second hold | ✅ Phase 5 block shot 3 |

**Three gaps: beats 2, 3 and 5.** Beats 2 and 3 have no script slot yet anyway,
so their images can wait for the amenities video that will carry them. **Beat 5
is the live one** — it is scripted into the Phase 8 deep dive and its cutaway is
currently a generic Town Center anchor.

> **Beat 4 is the deliberate exception.** The lawn-care beat is the honesty
> moment, and honesty is delivered *to* the viewer. **Stay on the face.** Its
> shot-list entry is support B-roll, not a cutaway. This is the sincerity rule
> doing its job.

---

## 7. Render batch

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

---

## Checklist

- [ ] No shot in the final cut places Karen at a desk, or in any generated interior
- [ ] Every full-frame appearance is composited over a **real photograph**
- [ ] Full-frame face time totals roughly **one minute** in a twenty-minute video
- [ ] Every full-frame block is a **sincere** register — hook, candour, CTA. No punchline is delivered full-frame
- [ ] Every beat requiring visible emotion **cuts away**, and the cutaway image exists on the shot list
- [ ] Beat 9's giggle plays over the No Shoes Ct sign, held clean for at least 4 seconds
- [ ] Wardrobe is consistent across every plate used in one video
- [ ] All plates rendered with a real alpha channel
