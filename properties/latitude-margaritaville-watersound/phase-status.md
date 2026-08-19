# Phase status & community facts — Latitude Margaritaville Watersound

Two kinds of fact live here, and the distinction matters.

**Permanent.** Phase boundaries, acreage, homesite counts, plat book and page,
street names, house-number ranges, distances. All Bay County public record.
Publishable as-is, on camera or in print, and they do not go stale.

**Volatile.** What is actually for sale. In Karen's words:

> "when we talk about it we'll say, as of this moment there are x number of
> resales listed and x number of lots, but that will certainly change in the
> next 5 minutes."

So **availability is never printed on the map or quoted from this file.** It is
a spoken, dated snapshot taken on record day. That volatility is not a
weakness to apologise for — it is the single best reason for a viewer to
contact Karen instead of relying on a video, and it converts an evergreen asset
into a lead generator every time it's watched.

## The permanent table

| Phase | Plat book/page | Acres | Platted homesites | Minto lot numbers |
| --- | --- | ---: | ---: | --- |
| Phase 1 | PB 27/73 | 34.3 | 59 | 1–48 |
| Phase 2 | PB 28/8 | 103.3 | 213 | 1–200 |
| Phase 3A | PB 28/34 | 91.5 | 172 | 1–167 |
| Phase 3B & 3C | PB 28/63 | 95.7 | 178 | 168–339 |
| Phase 3D | PB 30/8 | 24.8 | 44 | 340–381 |
| Phase 4A | PB 29/23 | 142.2 | 332 | 4,001–4,515 |
| Phase 4B | PB 29/76 | 83.6 | 205 | 4,318–4,509 |
| Phase 5A3 | PB 32/81 | 62.2 | 98 | not yet in county data |
| Phase 5B | PB 30/14 | 34.5 | 97 | 5,001–5,092 |
| Phase 5C | PB 30/27 | 184.0 | 248 | 5,093–5,335 |
| Phase 6A | PB 30/39 | 189.6 | 138 | 6,001–6,132 |
| Phase 6B & 6C | PB 30/80 | 94.1 | 346 | 6,201–6,538 |
| Phase 7 | PB 31/14 | 363.3 | 234 | 7,001–7,226 |
| Phase 8 | PB 31/71 | 180.2 | 204 | 8,001–8,200 |
| Phase 9 | PB 33/57 | 203.4 | 306 | 9,001–9,288 |
| Phase 10 | PB 33/98 | 236.8 | 355 | 10,001–10,343 |
| **Total** | **16 plats** | **2,123** | **3,229** | |

**Scope.** These are all 16 recorded plats, and **every one of them carries
`AREA 1`** in its subdivision name — the distinct AREA values in Bay County
record are exactly `['1']`. **Area 1 is Phases 1 through 10**, with Phase 10
(PB 33/98) the last of them, both the highest phase number and the highest
plat book/page.

**Area 2 has no recorded plat yet**, so how its phases will be numbered is not
public. **Do not say "Phase 11"** on camera or in writing — the record does not
support the name. "Area 2" is the safe term.

**Plat order is not phase order.** PH 5A3 is PB 32/81, recorded *after* Phase 7
(PB 31/14) and Phase 8 (PB 31/71) — a late infill plat, which is why it still
has no lot numbers in county data. That single counterexample is why
availability can never be inferred from recording order.

**Only PH 5A3 is recorded** — there is no 5A1 or 5A2 plat. Ask Karen whether
they were replatted or folded into another plat.

> **Minto lot numbers are not house numbers.** They are a plan-and-plat
> convention. Every house on Escape Avenue has an address in the 9000s even
> though its lot number starts with a 7 or an 8. Searchable house numbers per
> street are in [`streets_by_phase.md`](streets_by_phase.md); quote those.

## Karen's first-hand calls

Her own experience as a resident of Phase 8. Not measurements, and attributed
that way on camera.

### Highway 79 noise — the real discriminator

**Phases 1, 2, and 3B & 3C.** Three phases out of sixteen, all on the highway
frontage. This is a short, specific, genuinely useful filter — and almost
nobody thinks to ask about it.

> "Phases 1, 2, and 3b & C all could hear 79"

### Bandshell noise — *not* a discriminator

> "you know where the bandshell is, anything within a few miles could hear a
> loud concert, 6bc, 4a, 3D… and maybe more"

The naive assumption is "far from the Bandshell = quiet." That is **false**.
A loud concert carries a couple of miles, and Karen has heard it in 6B & 6C,
4A and 3D — and probably more. Most of the community hears a big show
sometimes.

**Design consequence:** never render a hard noise ring and never print a
radius. Sound varies with event volume, wind, season and tree cover, and Karen
is speaking approximately. The map draws a soft gradient with no edge, and the
"and maybe more" hedge stays in the script — the honesty is why it lands.

## The Town Center anchor

**30.30734, −85.86556 — the centre of the Bandshell.** Confirmed by Karen.

It is the middle of the amenity core: Fins Up! Fitness immediately north,
Latitude Bar and Chill plus Paradise Pool immediately south, amphitheater and
Bandshell west of the main parking. Every "distance to Town Center" on the map
is measured from here.

**Retired:** 8520 Latitude Blvd (30.312154, −85.863968). It is 554 m / 0.34 mi
NNE and is a mailing-address reference only, not the point a buyer walks to.

## Confirmed amenities

All on Minto's amenity site plan, safe to name on screen:

Bandshell · Town Square Amphitheater (with dance floor) · Fins Up! Fitness
Center · Workin' N' Playin' Center · Latitude Bar and Chill Restaurant ·
Paradise Pool · Community Services Building · Pickleball · Tennis ·
Multi-Purpose Court · Bocce · Lawn Games / Park Area · Port of Indecision
Kayak Launch · Barkaritaville Dog Park · Intracoastal Waterway on the west
edge · trail network with two marked overlooks.

## Second Town Square

- **Confirmed:** yes, planned, in Area 2.
- **Unknown:** what goes in it. Do not speculate about tenants or amenities.
- **Timing:** a ways out. Area 2 isn't recorded yet, so any specific timing is
  a guess and must be labelled as one on camera.
- **Do not say "Phase 11."** The record does not support the name.

"It's planned, nobody knows what's in it yet, and it's a ways out" is the
accurate and sufficient answer, and it beats the competitor, who doesn't
mention it at all.

## Record-day workflow

```powershell
python tools\map\inventory_report.py --csv <Karen's BoldTrail export>
```

Prints a read-on-camera block:

```
AS OF 2026-08-19
                  resales  new lots
Phase 1                 2         0
Phase 2                 5         0
...
```

…and writes the same numbers into `tools/map/phase_meta.json` so the script
prep and the spoken numbers cannot drift apart. Say it as **"as I'm recording
this, in [Month Year]…"** so the video ages gracefully, and repeat the caveat
in the description and the pinned comment — that's where a viewer six months
out will land.

## Still open

Nothing is blocking the script. Remaining items are map polish:

- [ ] Pins for Barkaritaville Dog Park, the Getaway Cottages, the Port of
      Indecision kayak launch, and confirmation of the Paradise Pool pin.
- [ ] The future-commercial parcel — confirm construction status and whether
      the grocery tenant can be named on screen.
- [ ] Phase 4A (#4,001–4,515) and 4B (#4,318–4,509) have overlapping Minto lot
      numbers in county data. Interleaved numbering, or lots sitting across a
      plat line?
- [ ] Were **5A1 and 5A2** ever platted? Only PH 5A3 exists in the record.
- [ ] One clipped label on Minto's Phase 4/5 panel still reads only "…IK DR".
      Shell Sink Dr is the nearest county match but it's not close enough to
      call. Left `UNVERIFIED` in `tools/map/street_index.json`.

## Sources

- Bay County FL ArcGIS `Property/MapServer/2` — recorded subdivision plats
- Bay County FL ArcGIS `Property/MapServer/0` — subdivision lots
- Bay County FL ArcGIS `TEST_Parcels/MapServer/1` — parcel site addresses
- Karen Lawell — first-hand, resident of Phase 8

*Illustrative only — not a survey. For what is actually for sale today, ask
Karen.*
