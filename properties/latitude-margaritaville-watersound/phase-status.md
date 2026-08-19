# Phase status — Latitude Margaritaville Watersound

**Every row below is PROVISIONAL. Nothing here is confirmed.**

The geometry, acreage, homesite counts and plat citations are hard facts from
Bay County public record and can be published as-is. The **availability column
is an inference**, not a verified fact — it was derived from plat recording
order (newest plats are most likely to still have new-build homesites) because
we have no public data source for live inventory.

Karen must confirm every availability value before any of it goes on camera or
into a lead magnet. Set `confirmed: true` in
[`tools/map/phase_meta.json`](../../tools/map/phase_meta.json) and re-render;
the PROVISIONAL banner disappears on its own once all 16 are confirmed.

## The table

| Phase | Plat book/page | Acres | Platted homesites | Lot numbers | Availability (provisional) | Confirmed |
| --- | --- | ---: | ---: | --- | --- | --- |
| Phase 1 | PB 27/73 | 34.3 | 59 | 1–48 | resale only | ❌ |
| Phase 2 | PB 28/8 | 103.3 | 213 | 1–200 | resale only | ❌ |
| Phase 3A | PB 28/34 | 91.5 | 172 | 1–167 | resale only | ❌ |
| Phase 3B & 3C | PB 28/63 | 95.7 | 178 | 168–339 | resale only | ❌ |
| Phase 3D | PB 30/8 | 24.8 | 44 | 340–381 | resale only | ❌ |
| Phase 4A | PB 29/23 | 142.2 | 332 | 4,001–4,515 | resale only | ❌ |
| Phase 4B | PB 29/76 | 83.6 | 205 | 4,318–4,509 | resale only | ❌ |
| Phase 5A3 | PB 32/81 | 62.2 | 98 | not yet in county data | new-build | ❌ |
| Phase 5B | PB 30/14 | 34.5 | 97 | 5,001–5,092 | resale only | ❌ |
| Phase 5C | PB 30/27 | 184.0 | 248 | 5,093–5,335 | resale only | ❌ |
| Phase 6A | PB 30/39 | 189.6 | 138 | 6,001–6,132 | resale only | ❌ |
| Phase 6B & 6C | PB 30/80 | 94.1 | 346 | 6,201–6,538 | resale only | ❌ |
| Phase 7 | PB 31/14 | 363.3 | 234 | 7,001–7,226 | new-build | ❌ |
| Phase 8 | PB 31/71 | 180.2 | 204 | 8,001–8,200 | new-build | ❌ |
| Phase 9 | PB 33/57 | 203.4 | 306 | 9,001–9,288 | new-build | ❌ |
| Phase 10 | PB 33/98 | 236.8 | 355 | 10,001–10,343 | new-build | ❌ |
| **Total** | **16 plats** | **2,123** | **3,229** | | | |

## What is solid vs what is not

**Solid — publishable now.** Phase boundaries, plat book and page, acreage,
homesite counts and lot-number ranges. All from Bay County recorded plats and
the county lot layer. Anyone can verify them at the Clerk's office.

**Not solid — do not publish.** Every value in the availability column.

## Karen — please confirm

### 1. Availability, all 16 phases

For each phase: does Minto still have **new-build homesites** there, or is the
only way in a **resale**? That is the whole question. Guessing is worse than
leaving it blank.

### 2. The three livability calls

These drive the map overlays and a whole section of the script.

- **Highway 79 noise** — which phases can genuinely hear it?
- **Town Center** — which phases are a comfortable walk or cart ride, and which
  are really a drive?
- **Bandshell** — how far does the music actually carry on a Saturday night?

### 3. Map points still missing

| Landmark | Status |
| --- | --- |
| Sales Center | ✅ confirmed — 9201 Highway 79 → 30.319131, −85.856248 (county address point) |
| **Town Center** | ⚠️ **contested.** The amenity complex reads at ≈ 30.30725, −85.86556 from the air; a county address point for 8520 Latitude Blvd sits ≈ 700 m north at 30.312154, −85.863968. Which is the point you'd tell a buyer to walk to? |
| Bandshell | ❌ needs a pin — it drives the live-music ring |
| Paradise Pool / fitness | ❌ needs a pin |
| Barkaritaville Dog Park | ❌ no coordinate |
| Getaway Cottages | ❌ no coordinate |
| Port of Indecision kayak launch | ❌ no coordinate |
| Future commercial / grocery | ❌ confirm the parcel, and whether the tenant can be named on screen |

### 4. Two data oddities

- **Phase 4A (#4001–4515) and Phase 4B (#4318–4509) overlap.** Either Minto
  interleaved the numbering, or some lots sit across the plat line in county
  data. Does 4B genuinely start at 4318?
- **Phase 5A3 lots have no lot numbers in county data yet** — it's the newest
  plat and the county hasn't populated them. Do you know the range?

### 5. Content questions from the competitor's comment section

Proven demand, and all three are in the script:

- Is a **second Town Square** planned when Area 2 starts? We found no public
  confirmation of it.
- **Which phase releases next**, and what's the realistic build timeline from
  contract to closing?
- What should a buyer **two years out** from relocating be doing now?

## Sources

- Bay County FL ArcGIS `Property/MapServer/2` — recorded subdivision plats
- Bay County FL ArcGIS `Property/MapServer/0` — subdivision lots
- Karen Lawell — first-hand, resident of Phase 8

*Illustrative only — not a survey. Phase availability changes; confirm current
inventory before relying on it.*
