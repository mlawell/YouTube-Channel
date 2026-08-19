# `tools/map` — Latitude Margaritaville Watersound phase map

A regenerating map of every recorded phase at Latitude Margaritaville
Watersound, built from Bay County, Florida public records.

It is code, not a drawing. When a phase sells out, edit one JSON file and
re-render — the map never goes stale, and every boundary on it can be traced
back to a recorded plat with a book and page number anyone can look up.

## Outputs

| File | Size | Use |
| --- | --- | --- |
| `output/latitude-phase-map.png` | 4000 × 2400 | Poster / lead magnet / printing |
| `output/latitude-phase-map.pdf` | vector | Print one-pager, open-house handout |
| `output/latitude-phase-map-thumbnail.png` | 1280 × 720 | Thumbnail plate — drop Karen's cutout and headline on top |
| `output/frames/00_all-phases.png` | 1920 × 1080 | Video: the whole community |
| `output/frames/01…16_phase-*.png` | 1920 × 1080 | Video: one frame per phase, that phase highlighted, everything else dimmed |
| `output/streets_by_phase.md` / `.json` | — | Street index per phase, with the county house-number range on every street |

The map covers **Area 1 — Phases 1 through 10, all 16 recorded plats**. Every
plat carries `AREA 1` in its subdivision name, and Phase 10 (PB 33/98) is the
last of them. **Area 2 has no recorded plat yet**, so how its phases will be
numbered is not public — do not call the next one "Phase 11".

The frame sequence is the video engine: talk about a phase, cut to its frame.
Each phase frame zooms to that phase but keeps the Sales Center and Town
Center on screen, plus a locator inset showing where you are in the community,
so viewers never lose their bearings.

## Running it

```powershell
python fetch_data.py         # download from Bay County ArcGIS  (~2 min, re-run monthly)
python build_features.py     # attribute lots + streets to phases -> data/features.json
python render_map.py         # poster, PDF, thumbnail, 17 frames
python export_streets.py     # streets_by_phase.md / .json
python make_preview.py       # the small committed preview PNGs
```

On record day, additionally:

```powershell
python inventory_report.py --csv <Karen's listings export>
```

Useful flags:

```powershell
python fetch_data.py  --only phases lots
python render_map.py  --only sequence
python render_map.py  --overlays hwy79 towncenter bandshell   # off by default
```

Dependencies: `requests`, `shapely`, `matplotlib`, `pillow`.

`data/` and `output/` are git-ignored — they regenerate. One downscaled
preview PNG is committed so the map is visible in the repo and in pull
requests.

## Where the data comes from

Everything geographic is Bay County, Florida public record, pulled live from
the county's own ArcGIS REST services.

| Layer | Endpoint | Used for |
| --- | --- | --- |
| Recorded subdivision plats | `Property/MapServer/2` | Phase boundaries + plat book/page |
| Subdivision lots | `Property/MapServer/0` | The 3,229 individual homesites |
| Road centerlines | `Basic_Layers/MapServer/2` | Street names (Phases 1–3) |
| Address points | `Basic_Layers/MapServer/0` | Street names, Sales Center anchor |
| Parcel site addresses | `TEST_Parcels/MapServer/1` | Street names (Phases 4B–10) |
| Highways | `Basic_Layers/MapServer/1` | Highway 79 |
| Waterbodies / creeks | `PhysicalTopography/MapServer/2` and `/1` | West Bay, ponds, drainage |

Base URL: `https://gis.baycountyfl.gov/arcgis/rest/services/`

Server quirks, all handled in `fetch_data.py`:

- `resultOffset` paging silently returns zero rows — use `returnIdsOnly=true`,
  then fetch by `objectIds` in batches.
- Object-id lists blow past the URL length cap, so every query is a POST.
- The service returns HTTP 200 with an `{"error": …}` body; that is checked
  explicitly.
- One record in the lots layer (`OBJECTID 4295276`) always errors. A recursive
  bisect isolates and drops it rather than losing the whole batch.
- `Basic_Layers/MapServer/3` (Parcels) is stale for this community.
  `TEST_Parcels/MapServer/1` is the current one, despite the name.

## The files you edit

### `phase_meta.json` — narrative + the inventory snapshot

Per phase: `role`, `karen_says`, `note`, `karen_lives_here`, `hwy79_audible`,
and `inventory_snapshot`.

**Availability is deliberately NOT rendered.** Karen's framing:

> "as of this moment there are x number of resales listed and x number of lots,
> but that will certainly change in the next 5 minutes."

Baking a number that volatile into a printed asset guarantees it goes stale,
and it is the one thing on an otherwise hard-public-record map that would make
the whole thing look untrustworthy. So live inventory is spoken and dated at
record time instead, and that volatility becomes the call to action — it is the
reason a viewer contacts Karen rather than relying on the video.

The file also carries `karen_first_hand` (her Highway 79 and Bandshell noise
calls, with her exact quotes) and `scope`, which records that the map covers
**Area 1 — Phases 1 through 10, all 16 recorded plats** and that Area 2 has no
recorded plat yet. It also notes that **plat order is not phase order**: PH 5A3
is PB 32/81, recorded *after* Phases 7 and 8. That single counterexample is why
availability can never be inferred from recording order.

### `landmarks.json`

Landmark coordinates, each with `confirmed`, `source` and `needs`.
Unconfirmed landmarks render with a `?` after the label so nothing unverified
sneaks onto screen looking certain. Entries with `null` coordinates simply do
not draw.

Confirmed:

- **Sales Center** — 9201 Highway 79 → 30.319131, −85.856248 (county address point)
- **Town Center & Bandshell** — 30.30734, −85.86556, the centre of the
  Bandshell, confirmed by Karen. It is the middle of the amenity core, so it is
  the origin for every "distance to Town Center" on the map.

### `street_index.json`

Curated gap-filler, the `unverified` clipped-label list, and the two-number-series
warning. Only touch it for names Karen confirms from her own knowledge.

## Record day — the inventory snapshot

```powershell
python inventory_report.py --csv <Karen's BoldTrail export>
```

Assigns every listing to a phase geometrically, then prints a block to read
straight off the screen:

```
AS OF 2026-08-19
                  resales  new lots
Phase 1                 2         0
Phase 2                 5         0
...
```

It writes the same numbers into `phase_meta.json` so the script prep and the
spoken numbers cannot drift apart. Use `--no-write` to print only.

## Which phase is this address in?

`phase_lookup.py` answers it three ways.

```powershell
python phase_lookup.py --address "9502 Escape Ave"     # by county house number
python phase_lookup.py --latlon 30.319131 -85.856248   # by coordinate
python phase_lookup.py --lot 8042                      # by MINTO LOT number
python phase_lookup.py --csv listings.csv --out tagged.csv
```

The coordinate path is the robust one — point-in-recorded-plat needs no street
list, so it works for the newest phases where the county has no address
coverage at all. The CSV mode is how active for-sale inventory gets tagged:
Karen exports her listings from BoldTrail with latitude/longitude columns, this
adds a `phase` column. No scraping, no MLS redistribution.

### Two number series — do not confuse them

**Minto lot numbers** are phase-prefixed from Phase 4 onward (4xxx … 10xxx);
phases 1–3 use one unprefixed run of 1–381. They identify a phase but are
useless for searching.

**County house numbers** are the searchable street address, and they are a
completely different series. On Escape Avenue the county range is **9201–9499
in Phase 7** and **9502–9667 in Phase 8** — so Minto lot 8042 is in Phase 8,
but there is no *8042 Escape Avenue*. Quote house numbers to buyers, never lot
numbers.

`streets_by_phase.md` publishes the house-number range for every street in
every phase, and calls out the **12 streets that cross a phase boundary** —
those are the ones that catch buyers out.

### Automating listings later

Karen's site (`karenlawell.countspcb.com`) is BoldTrail/kvCORE. Search results
are rendered client-side, so there is no server-side URL that returns
subdivision-filtered listings. The supported route is the kvCORE Feeds API —
`https://api.kvcore.com/export/listings/{zapKey}/17` — which needs a `zapKey`
from Karen's BoldTrail dashboard. Until then, the CSV export path is the one to
use.

## Design notes

- **The map is rotated.** The community runs north-west to south-east, so a
  north-up map wastes most of a 16:9 frame. A PCA fit finds the long axis and
  rotates the whole scene onto it; the north arrow rotates to match. This was
  the single biggest legibility win.
- **Phases are coloured by plat book**, oldest to newest. It is permanent
  public record and it tells a real story — Phase 5A3 sits in book 32, so it
  visibly reads as one of the newest parts of the community despite carrying a
  "5". The map proves the correction without a word of commentary.
- **Inactive phases keep their lots.** Dimmed, but drawn. The lot-and-street
  texture is what makes the map read as a real place; hide it and the frame
  looks empty.
- **The Bandshell overlay has no hard edge and no printed radius.** Karen says
  a loud concert carries "a few miles" and she has heard it in 6B & 6C, 4A and
  3D "and maybe more". Sound varies with event volume, wind, season and tree
  cover, so a crisp ring with a number on it would be an invented measurement.
  It is an impression, and it is drawn like one. The Town Center half-mile walk
  ring *is* a hard ring, because that one is genuinely measurable.
- **Web Mercator inflates distance** by `1/cos(latitude)`. Every mile figure on
  the map is corrected for it, so the scale bar and the "0.6 mi to Town Center"
  numbers are true ground distances.
- **Context is clipped** to a padded community extent. Bay County's creek layer
  otherwise fills the frame with drainage that has nothing to do with Latitude.

## Accuracy rules this tool follows

1. **Nothing is invented.** Every phase boundary, lot, road and water body on
   the map came from a county layer. No amenity, phase, homesite or future
   feature is drawn unless it exists in public record or Karen confirms it.
   Area 2 has no recorded plat, so nothing of it is drawn or named.
2. **No street is renamed or inferred.** A street name only attaches to a phase
   when a county feature carrying that name physically sits inside that phase's
   recorded plat. Where the county has no coverage the entry stays blank and is
   flagged for Karen — never filled in by guessing from a neighbouring phase.
3. **Nothing volatile is printed.** Live inventory changes by the hour, so it
   never goes on the map. Everything rendered is either public record or a
   confirmed first-hand call from Karen, attributed as such.
4. **Approximate things look approximate.** No hard edge or number on the
   Bandshell overlay; `?` on unconfirmed landmarks.
5. **Every render prints a NEEDS CONFIRMATION list** of what is still
   unverified, so it cannot quietly ship.

## Disclaimer carried on every export

> Phase boundaries & lots: Bay County, FL recorded plats (public record), plat
> book/page shown per phase · retrieved *date* | Illustrative only — not a
> survey. Boundaries, homesite counts and street data are public record; for
> what is actually for sale today, ask Karen.
> Area 1 is Phases 1 through 10 — all 16 plats recorded, Phase 10 (PB 33/98)
> the last of them. Area 2 has no recorded plat yet, so how its phases will be
> numbered is not public.

## Still needs Karen

Nothing blocking — these are map polish.

- [ ] Pins for Barkaritaville Dog Park, the Getaway Cottages and the Port of
      Indecision kayak launch; confirm the Paradise Pool pin.
- [ ] The future-commercial parcel — confirm construction status and whether
      the grocery tenant can be named on screen.
- [ ] Phase 4A (#4,001–4,515) and Phase 4B (#4,318–4,509) have overlapping
      Minto lot numbers in county data. Interleaved numbering, or lots sitting
      across a plat line?
- [ ] One clipped label on Minto's Phase 4/5 panel still reads only "…IK DR".
