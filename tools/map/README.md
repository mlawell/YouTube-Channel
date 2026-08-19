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
| `output/streets_by_phase.md` / `.json` | — | Street index per phase, each name tagged with its public-record source |

The frame sequence is the video engine: talk about a phase, cut to its frame.
Each phase frame zooms to that phase but keeps the Sales Center and Town
Center on screen, plus a locator inset showing where you are in the community,
so viewers never lose their bearings.

## Running it

```powershell
python fetch_data.py        # download from Bay County ArcGIS  (~2 min, re-run monthly)
python build_features.py    # attribute lots + streets to phases -> data/features.json
python render_map.py        # poster, PDF, thumbnail, 17 frames
python export_streets.py    # streets_by_phase.md / .json
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

### `phase_meta.json` — the one to keep current

Per phase: `availability` (`new-build` / `resale-only` / `unconfirmed`),
`confirmed`, `karen_says`, `note`, `availability_basis`.

**Every phase currently has `confirmed: false`.** The availability values are
provisional inferences from plat recording order, not verified inventory.
Until Karen sets `confirmed: true`, the poster carries a PROVISIONAL banner and
each phase frame carries a "confirm current inventory" caption. That is
deliberate — the map should refuse to look authoritative until it is.

When a phase sells out of new-build homesites:

```jsonc
"Phase 8": {
  "availability": "resale-only",
  "confirmed": true,
  "availability_basis": "Karen, 2026-09-01 — last new-build homesite closed"
}
```

then `python render_map.py`. Done.

### `landmarks.json`

Landmark coordinates, each with `confirmed`, `source` and `needs`.
Unconfirmed landmarks render with a `?` after the label so nothing unverified
sneaks onto screen looking certain. Several still have `null` coordinates and
simply do not draw until Karen drops a pin.

Only the **Sales Center** (9201 Highway 79 → 30.319131, −85.856248) is
confirmed, from a county address point.

### `street_index.json`

Curated gap-filler and the list of labels that could not be verified. Only
touch it for names Karen confirms from her own knowledge.

## Which phase is this address in?

`phase_lookup.py` answers it geometrically — lat/lon → point-in-recorded-plat
→ phase. It needs no street list, so it works for the newest phases where the
county has no address coverage at all.

```powershell
python phase_lookup.py --latlon 30.319131 -85.856248
python phase_lookup.py --lot 8042
python phase_lookup.py --csv listings.csv --out listings_with_phase.csv
```

The CSV mode is how active for-sale inventory gets tagged to a phase: Karen
exports her listings from BoldTrail with latitude/longitude columns, this adds
a `phase` column. No scraping, no MLS redistribution.

Lot numbers are a useful secondary index because Minto prefixes them by phase
from Phase 4 onward (4xxx … 10xxx), so a lot number alone usually identifies
its phase. Phases 1–3 share one unprefixed run of 1–381, so `--lot` is
ambiguous down there and the tool says so instead of guessing.

### Automating listings later

Karen's site (`karenlawell.countspcb.com`) is BoldTrail/kvCORE. Search results
are rendered client-side, so there is no server-side URL that returns
subdivision-filtered listings. The supported route is the kvCORE Feeds API —
`https://api.kvcore.com/export/listings/{zapKey}/17` — which needs a `zapKey`
from Karen's BoldTrail dashboard. Until then, the CSV export path above is the
one to use.

## Design notes

- **The map is rotated.** The community runs north-west to south-east, so a
  north-up map wastes most of a 16:9 frame. A PCA fit finds the long axis and
  rotates the whole scene onto it; the north arrow rotates to match. This was
  the single biggest legibility win.
- **Inactive phases keep their lots.** Dimmed, but drawn. The lot-and-street
  texture is what makes the map read as a real place; hide it and the frame
  looks empty.
- **Web Mercator inflates distance** by `1/cos(latitude)`. Every mile figure on
  the map is corrected for it, so the scale bar and the "2.6 mi to Town Center"
  numbers are true ground distances.
- **Context is clipped** to a padded community extent. Bay County's creek layer
  otherwise fills the frame with drainage that has nothing to do with Latitude.

## Accuracy rules this tool follows

1. **Nothing is invented.** Every phase boundary, lot, road and water body on
   the map came from a county layer. No amenity, phase, homesite or future
   feature is drawn unless it exists in public record or Karen confirms it.
2. **No street is renamed or inferred.** A street name only attaches to a phase
   when a county feature carrying that name physically sits inside that phase's
   recorded plat. Where the county has no coverage the entry stays blank and is
   flagged for Karen — never filled in by guessing from a neighbouring phase.
3. **Unverified things look unverified.** Provisional availability, `?` on
   unconfirmed landmarks, a PROVISIONAL banner while any phase is unconfirmed.
4. **Every render prints a NEEDS CONFIRMATION list** of what is still
   unverified, so it cannot quietly ship.

## Disclaimer carried on every export

> Phase boundaries & lots: Bay County, FL recorded plats (public record), plat
> book/page shown per phase · retrieved *date* | Illustrative only — not a
> survey. Phase availability changes; confirm current inventory before relying
> on it.

## Still needs Karen

- [ ] Confirm new-build vs resale-only for all 16 phases — all provisional.
- [ ] Resolve the Town Center point. The amenity complex reads at
      ≈ 30.30725, −85.86556 from the air; a county address point for
      8520 Latitude Blvd sits ≈ 700 m north at 30.312154, −85.863968.
- [ ] Drop pins: Barkaritaville Dog Park, the Getaway Cottages, the Port of
      Indecision kayak launch.
- [ ] Confirm the Bandshell point — it drives the live-music proximity ring.
- [ ] Confirm the noise / Highway 79 / Town Center calls per phase.
- [ ] Confirm the future-commercial parcel and whether the grocery tenant can
      be named on screen.
- [ ] Phase 4A (#4001–4515) and Phase 4B (#4318–4509) have overlapping lot
      numbers in county data. Interleaved numbering, or lots sitting across a
      plat line? Karen or a plat read can settle it.
