# Phase Deep Dives — one video per phase

**Status:** drafts generated, none recordable yet.

The flagship [`latitude-phases-explained`](../latitude-phases-explained/) covers all ten phases in one 19–22 minute video at about thirty seconds each. This series is the other half: one video per phase, 8–12 minutes, with the two things thirty seconds cannot hold — **a cart time Karen actually drove**, and **what the people who live there say**.

| Episode | Video | Recorded plats | Homesites | Acres |
| --- | --- | --- | --- | --- |
| 1 | [Phase 1](phase-1.md) | PB 27/73 | 59 | 34 |
| 2 | [Phase 2](phase-2.md) | PB 28/8 | 213 | 103 |
| 3 | [Phase 3](phase-3.md) | PB 28/34, PB 28/63, PB 30/8 | 394 | 212 |
| 4 | [Phase 4](phase-4.md) | PB 29/23, PB 29/76 | 537 | 226 |
| 5 | [Phase 5](phase-5.md) | PB 30/14, PB 30/27 | 345 | 218 |
| 6 | [Phase 6](phase-6.md) | PB 30/39, PB 30/80 | 484 | 284 |
| 7 | [Phase 7](phase-7.md) | PB 31/14 | 234 | 363 |
| 8 | [Phase 8 ★](phase-8.md) | PB 31/71 | 204 | 180 |
| 9 | [Phase 9](phase-9.md) | PB 33/57 | 306 | 203 |
| 10 | [Phase 10](phase-10.md) | PB 33/98 | 355 | 237 |

★ Karen lives here. That episode is the anchor of the series.

## Why grouped this way

Phase 3 is **three** separately recorded plats; Phases 4, 5 and 6 are two each. Grouping them per video makes the flagship's central correction visible instead of asserted: a viewer who came looking for "Phase 3" gets all three plats, each with its own book and page.

## The two things that are not public record

Everything in these drafts comes from Bay County recorded plats except two, and neither can be derived:

**The cart time cannot be computed.** County road centrelines cover only Phases 1, 2, 3A, 3B & 3C and 3D. Ten of the sixteen plats have no interior centreline, and only 12% of the road network connects to the Town Center — most phases sit 1–5 km from any routable road, Phase 10 nearly 5 km. So the drafts carry a **straight-line floor at 30 mph**, labelled as a floor, and a `[CART]` gate for the driven time. See [`drive-sheet.md`](drive-sheet.md).

**There is no resident feedback here at all.** So the drafts carry a prompt and a gate, never a sentence. If a phase has nobody interviewed yet, that section gets cut — it does not get filled in from imagination.

## Regenerating

```powershell
python tools\scripts\build_phase_scripts.py
```

Rebuilds every draft from `tools/map/data/features.json`, so homesite counts, acreages, streets, address ranges and distances cannot drift from the map.
