# Phase Deep Dives — one video per phase

**Status:** drafts generated, none recordable yet.

The flagship [`latitude-phases-explained`](../latitude-phases-explained/) covers all ten phases in one 19–22 minute video at about thirty seconds each. This series is the other half: one video per phase, 8–12 minutes, with the two things thirty seconds cannot hold — **a cart time Karen actually drove**, and **what the people who live there say**.

| Episode | Video | Recorded plats | Homesites | Acres |
| --- | --- | --- | --- | --- |
| 1 | [Phase 1](phase-1.md) | PB 27/73 | 59 | 34.3 |
| 2 | [Phase 2](phase-2.md) | PB 28/8 | 213 | 103.3 |
| 3 | [Phase 3](phase-3.md) | PB 28/34, PB 28/63, PB 30/8 | 394 | 212.0 |
| 4 | [Phase 4](phase-4.md) | PB 29/23, PB 29/76 | 537 | 225.8 |
| 5 | [Phase 5](phase-5.md) | PB 30/14, PB 30/27 | 345 | 218.5 |
| 6 | [Phase 6](phase-6.md) | PB 30/39, PB 30/80 | 484 | 283.7 |
| 7 | [Phase 7](phase-7.md) | PB 31/14 | 234 | 363.3 |
| 8 | [Phase 8 ★](phase-8.md) | PB 31/71 | 204 | 180.2 |
| 9 | [Phase 9](phase-9.md) | PB 33/57 | 306 | 203.4 |
| 10 | [Phase 10](phase-10.md) | PB 33/98 | 355 | 236.8 |

★ Karen lives here. That episode is the anchor of the series.

## Humor

These are produced with HeyGen and ElevenLabs, so **nothing can be ad-libbed** — an avatar reads what it is given. Every beat is therefore written into the generator and marked `[HUMOR]` or `[MIKE]` so Karen can strike it. Doctrine, the banned-phrase list and the full line bank are in [`karen-voice-and-humor.md`](../karen-voice-and-humor.md).

Phases 5 and 9 carry **no beat on purpose**. A forced bit is worse than none.

The `[MIKE]` beats were reviewed line by line with Mike on 2026-08-23 and most of the earlier set was cut, several of them because they were **factually wrong** rather than unfunny. Two survived: *bring a cart* in Phase 6, and *the Hawaiian shirt* in Phase 8. The rule his choices revealed is the one to script against: **the joke is on the place, on paperwork, or on ourselves, never on the theme and never on residents.** Do not add a third without asking him.

## Files

| File | What it is |
| --- | --- |
| `phase-1.md` … `phase-10.md` | One shot-by-shot script per episode |
| [`metadata.md`](metadata.md) | Titles, chapters, descriptions, tags and pinned comments for all ten |
| [`thumbnail-brief.md`](thumbnail-brief.md) | One template, ten thumbnails, with the per-episode hook |
| [`photo-shot-list.md`](photo-shot-list.md) | What Karen photographs in each phase, and which beat each shot covers |
| [`drive-sheet.md`](drive-sheet.md) | **The blocker.** Cart times and resident quotes — the only source for the two things here that are not public record |

## Why grouped this way

Phase 3 is **three** separately recorded plats; Phases 4, 5 and 6 are two each. Grouping them per video makes the flagship's central correction visible instead of asserted: a viewer who came looking for "Phase 3" gets all three plats, each with its own book and page.

## The two things that are not public record

Everything in these drafts comes from Bay County recorded plats except two, and neither can be derived:

**The cart time cannot be computed.** County road centrelines cover only Phases 1, 2, 3A, 3B & 3C and 3D. Ten of the sixteen plats have no interior centreline, and only 12% of the road network connects to the Town Center — most phases sit 1–5 km from any routable road, Phase 10 nearly 5 km. So the drafts carry a **straight-line floor at 30 mph**, labelled as a floor, and a `[CART]` gate for the driven time. See [`drive-sheet.md`](drive-sheet.md).

**There is no resident feedback here at all.** So the drafts carry a prompt and a gate, never a sentence. If a phase has nobody interviewed yet, that section gets cut — it does not get filled in from imagination.

## The redirect loop

Every episode ends with **one** spoken redirect naming **one** next video, placed after the close and never before it. Characteristic 8 says point them at the next video the instant the payoff lands (`D3-GS` 00:44:45); Jesse marks the reverse order *"slightly wrong"* on air (`D3-GS` 00:54:16); and *"if you tell them to do three things they'll do zero"* (`D3-GS` 00:36:16) is why it is one card and not four.

It is a tail feeding a cycle, so no episode dead-ends:

```mermaid
flowchart LR
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
    P6 --> P7
    P7 --> P8
    P8 --> P9
    P9 --> P10
    P10 --> MAP[flagship map video]
    MAP --> P8
```

| This video ends | Points at | Because |
| --- | --- | --- |
| Phase 1 | **Phase 2** | P1 is the Sales Center and the model park, so the obvious next question is where anybody actually lives. |
| Phase 2 | **Phase 3** | Continues the Highway 79 thread the chapter just opened. |
| Phase 3 | **Phase 4** | Same trap, next instance: 4A and 4B interlock and get mixed up the same way 3A, 3B & 3C and 3D do. |
| Phase 4 | **Phase 5** | Ends the which-plat-am-I-in thread on the community's single biggest myth. |
| Phase 5 | **Phase 6** | 6A and 6B & 6C are the two density extremes, a direct contrast with the amenity core this chapter just covered. |
| Phase 6 | **Phase 7** | 6A's low-density story runs straight into the largest phase. |
| Phase 7 | **Phase 8** | The strongest handoff in the series: one street, two phases, and the destination is the residency proof. |
| Phase 8 | **Phase 9** | Established phase to the genuinely new one, which is the real resale-versus-new-build decision. |
| Phase 9 | **Phase 10** | Newest to newest-and-largest. |
| Phase 10 | **the flagship phase map video** | P10 is the end of Area 1, so the only place left to go is the whole map. Closes the loop back to the hub. |
| The flagship map video | **Phase 8** | The hub's traffic is the best on the channel, so it goes to the residency proof rather than to Phase 1, which is mostly the Sales Center and the model park. |

The last 15 to 20 seconds are reserved for it and **carry no facts**. Anything checkable said there is said to a viewer already reaching for the next video.

## Regenerating

```powershell
python tools\scripts\build_phase_scripts.py
```

Rebuilds every draft from `tools/map/data/features.json`, so homesite counts, acreages, streets, address ranges and distances cannot drift from the map.
