# `tools/map` — Latitude Margaritaville Watersound phase map

A regenerating map of every recorded phase at Latitude Margaritaville
Watersound, built from Bay County, Florida public records.

It is code, not a drawing. When a phase sells out, edit one JSON file and
re-render — the map never goes stale, and every boundary on it can be traced
back to a recorded plat with a book and page number anyone can look up.

## Outputs

| File | Size | Use |
| --- | --- | --- |
| `output/latitude-phase-map.png` | 8000 × 4800 | Screen-shaped poster, lead magnet |
| `output/latitude-phase-map-print-36x24.pdf` / `.svg` | vector, 36 × 24 in | **The main print deliverable.** Full street + address index |
| `output/latitude-phase-map-print-48x32.pdf` / `.svg` | vector, 48 × 32 in | Office wall |
| `output/latitude-phase-map-giant-raster.png` | 16,200 × 10,800 | 300 dpi at 54 in wide, for anyone who can't take a PDF |
| `output/latitude-phase-map-thumbnail.png` | 1280 × 720 | Thumbnail plate — drop Karen's cutout and headline on top |
| `output/frames/00_all-phases.png` | 3840 × 2160 | Video: the whole community |
| `output/frames/01…16_phase-*.png` | 3840 × 2160 | Video: one per phase, that phase highlighted |
| `output/streets_by_phase.md` / `.json` | — | Street index per phase, with county house-number ranges |

**Vector is the canonical master for print.** PDF and SVG are
resolution-independent, which is what actually solves "we need it bigger" — a
print shop can scale a PDF to any size without it going soft. Fonts are
embedded as subsets in the PDF (`pdf.fonttype 42`) and converted to outlines in
the SVG (`svg.fonttype path`), so nothing substitutes at the print shop. Line
widths are in points, so they scale with the page instead of turning into
hairlines. The giant PNG exists only for workflows that can't take vector.

**Zoom frames are rendered natively at their own extent**, never cropped or
upscaled from the wide render, so the lot linework is genuinely sharp when the
video pushes in on a phase. 4K gives the editor room for pan-and-zoom moves
before exporting at 1080p.

The map covers **Area 1 — Phases 1 through 10, all 16 recorded plats**. Every
plat carries `AREA 1` in its subdivision name, and Phase 10 (PB 33/98) is the
last of them. **Area 2 has no recorded plat yet**, so how its phases will be
numbered is not public — do not call the next one "Phase 11".

## Running it

```powershell
python fetch_data.py         # download from Bay County ArcGIS  (~2 min, re-run monthly)
python extract_plan_features.py water   # pond positions off the builder's site plan
python build_features.py     # attribute lots + streets to phases -> data/features.json
python render_map.py         # poster, print PDF, thumbnail, 17 frames
python export_streets.py     # streets_by_phase.md / .json
python make_preview.py       # committed previews + the print master
```

`extract_plan_features.py` only needs re-running if the builder publishes a new
site plan; its output and the solved transform are cached in `data/`.

Large formats are opt-in because they're slower and much larger:

```powershell
python render_map.py --preset print-36x24                    # the main print master
python render_map.py --preset print-48x32 giant-raster
python render_map.py --size 30 20 --dpi 300                  # any one-off size
python render_map.py --check-palette                         # phase colour separation
```

Large formats are opt-in because they're slower and much larger:

```powershell
python render_map.py --preset print-36x24                    # the main print master
python render_map.py --preset print-48x32 giant-raster
python render_map.py --size 30 20 --dpi 300                  # any one-off size
python render_map.py --check-palette                         # phase colour separation
```

On record day, additionally:

```powershell
python inventory_report.py --csv <Karen's listings export>
```

Useful flags:

```powershell
python fetch_data.py  --only phases lots
python render_map.py  --only sequence
python render_map.py  --detail clean                          # drop the dense layer
python render_map.py  --overlays hwy79 towncenter bandshell   # off by default
```

Whole pipeline including every preset runs in well under two minutes.

Dependencies: `requests`, `shapely`, `matplotlib`, `pillow`.

`data/` and `output/` are git-ignored — they regenerate. `preview/` is
committed: downscaled rasters so the map is visible in the repo and in pull
requests, plus **the 36 × 24 print master verbatim**, so the file Karen hands a
print shop doesn't require running Python to obtain. `python make_preview.py`
populates it.

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
| Waterbodies / creeks | `PhysicalTopography/MapServer/2` and `/1` | West Bay, the Intracoastal, drainage |

Base URL: `https://gis.baycountyfl.gov/arcgis/rest/services/`

### The one thing the county does not have: the ponds

`PhysicalTopography/MapServer/2` returns exactly **one** waterbody across the
whole community, `Basic_Layers/MapServer/20` (Water) returns none, and
`Basic_Layers/MapServer/21` (Building Footprints) returns **zero** features
inside the Town Center. OpenStreetMap has nothing inside the amenity core
either. So the eighty-odd lakes and stormwater ponds are not obtainable from
any public dataset.

They come instead from the builder's own June 2026 site plan, via
`extract_plan_features.py` — and the important part is *how*:

- The sheet is not traced, recoloured, cropped or republished. What is taken is
  factual: **where the water is**. The outlines are simplified well past the
  drawn linework and redrawn in our own styling.
- The plan is **georeferenced by solving for it**, not by assuming. A similarity
  transform is fitted by aligning the plan's drawn lot fabric against the 3,151
  recorded homesites we already hold from the county.
- The fit is then **measured**: the map is cut into tiles and each tile's own
  residual shift is solved independently. Current fit is +0.77°, median residual
  **0 m** and 90th percentile **12.5 m** across 28 tiles — comfortably finer
  than a pond.
- Below `--max-error` the script **writes nothing at all**. Geometry placed by a
  fit nobody checked is a guess with extra steps.

IoU is deliberately *not* the acceptance test. The sheet is an artist's
rendering that draws homesites as tidy uniform rectangles nowhere near the
recorded parcel outlines, so overlap is capped well below 1 even when the
registration is perfect. Local residual displacement is what actually decides
whether a pond lands in the right place, so that is what is measured.

### Ponds are then reconciled against the recorded plats

A 12 m fit is fine for a map and still enough to float a pond onto somebody's
back yard. Worse, the Caribbean Collection's villa pods are drawn in a pale cyan
that passes any blue-dominant water test, so a handful of "ponds" were never
water at all. `build_features.reconcile_ponds()` lets the public record arbitrate,
because between an artist's rendering and a recorded plat the plat wins:

| Rule | Why |
| --- | --- |
| **Drop** a pond ≥85% inside recorded homesites | Not a pond. That is a lot pod that happened to be cyan. |
| **Nudge** the rest, 16-direction spiral in 3 m steps, **capped at 15 m** | 15 m is the fit's own measured error. Past that we would not be correcting a fit, we would be inventing a position. |
| **Trim** whatever still overlaps, always | Cheaper than a wrong outline, and the residual is dust. |

Current pass over 87 extracted ponds: kept 57, nudged 16, trimmed 14, **dropped
14**, median shift 15.0 m → **73 rendered**. Total pond-on-homesite overlap goes
from **93,359 m² to zero**. Fourteen ponds still share a boundary with a
homesite, which is exactly what a retention pond behind a lot row does; none of
them sit on one.

Two things learned the hard way:

- **Simplify before reconciling, not after.** Shaving a vertex off an outline
  that was just trimmed to a lot line pushes it straight back over the line.
- **Do not fix this upstream by excluding developed area from the water mask.**
  That was tried; it over-corrects badly (pond acreage 223 → 70) because it also
  strips real shallows and every anti-aliased pond edge. The reconcile step is
  the right place — it can see the plats.

Google Maps satellite imagery would settle every one of these instantly and is
**not** usable here: it is licensed imagery going into a commercial product,
which is the same trap as the builder's site plan.

Bay County's `CityStormwater` / `CountyStormwater` services do publish a
**Retention Ponds** layer. It returns zero features for this community. Checked
so nobody checks again.

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
**Area 1 — ten phases across sixteen recorded plats** and that Area 2 has no
recorded plat yet. It also notes that **plat order is not phase order**: the
Town Center plat is PB 32/81, recorded *after* Phases 7 and 8. That single
counterexample is why availability can never be inferred from recording order.

### There is no Phase 5A — and the map has to say so

Karen: *"There isn't a phase 5A."* A plat named `PH 5A3` **is** recorded at PB
32/81. Both statements are true, and the resolution is the most useful fact on
the map.

Point-in-polygon against the county's own parcel layer shows that **48.3 of that
plat's 62.2 acres are one single tract**, and that both the Bandshell
(30.30734, −85.86556) and Paradise Pool (30.30630, −85.86578) fall inside it.
That tract is the Town Center. The plat's only homesites are the Stay & Play
cottages.

So `build_features.py` labels this plat **Town Center**, not "Phase 5A3", splits
it into the amenity tract plus the cottages, and gives it a warm neutral fill
outside every phase hue — because drawing it as a phase would put it right back
into the sequence the map exists to take it out of. The `PB 32/81` citation is
kept in the legend.

This also means two counts, both correct and constantly confused:
`phase_count` = **10** and `plat_count` = **16**. Phase 3 was recorded as
3A / 3B & 3C / 3D and Phase 4 as 4A / 4B, and the sixteenth plat is the Town
Center rather than an eleventh phase.

> **Superseded.** An earlier version of this project used *"5A3 is a recorded
> plat, so the claim that 5A was skipped is wrong"* as an authority beat in the
> video. That was wrong on the substance. Do not reintroduce it.

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

- **The map is rotated.** The community runs north-west to south-east and is
  about **3.1 : 1** — a north-up map wastes most of any frame. A PCA fit finds
  the long axis and rotates the whole scene onto it; the north arrow rotates to
  match. This was the single biggest legibility win.
- **That 3.1 : 1 shape drives the print layout.** On a 3:2 sheet a full-width
  map only fills the top third. Rather than pad that with whitespace or distort
  the geometry to fill it, the space below carries the street and address
  index — which is what makes a big map worth printing in the first place.
- **One hue per phase number, one tint per sub-phase.** 3A / 3B & 3C / 3D are
  three shades of one colour, 4A / 4B two shades of another. A viewer learns
  ten colours instead of sixteen and the map teaches the numbering scheme
  without narration. Every polygon still carries a printed label, because
  sixteen categories is past what colour alone can safely carry.
- **The palette is measured, not eyeballed.** Hues avoid the pale cyan of water
  and the coral of the landmark pins, which leaves only ~245° for ten families —
  five of them would otherwise pile into the greens. So each family carries its
  own hue, lightness *and* saturation, including one deep navy that reads
  nothing like pale water. `--check-palette` reports CIE Lab separation three
  ways and fails loudly on any of them:

  | Check | Threshold | Why |
  | --- | --- | --- |
  | vs the paper | ΔE ≥ 30 | A washed-out fill reads as empty land, not as a phase |
  | cross-family | ΔE ≥ 20 | Different phase numbers must be unmistakable |
  | within-family | ΔE ≥ 8 | Sub-phases *should* look related, just tellable apart |

  Phase fills are held inside a legibility band (lightness 0.34–0.62, saturation
  ≥ 0.42) so nothing can wash into the cream background. That costs some
  separation between siblings, which is the right trade — a viewer has to see
  that a phase *is* there before they can tell which sibling it is, and the
  label and legend carry the fine distinction. Siblings ramp in saturation as
  well as lightness to claw some of it back.
- **Identifiers are never formatted as numbers.** `fmt.py` splits `ident()` /
  `ident_range()` from `qty()`. A house number is `9201 Escape Ave`, never
  `9,201`; a lot number is `8001–8200`, never `8,001–8,200`. Counts and
  acreages keep their separators, because those are genuine quantities. A
  single-parcel span prints as a lone number rather than `8939–8939`. On a
  sheet whose whole purpose is matching an address to a listing, a stray comma
  is wrong in the one place it cannot afford to be.
- **Inactive phases drop to one common pale value**, not a relative lightening.
  Relative shifts leave the dark phases still reading as heavy blocks when they
  should be receding.
- **Lots are tinted with their phase colour**, not drawn white. Drawn white, a
  fully platted phase reads as a white sheet while an undeveloped one reads as
  solid colour — which makes build-out look like a colour difference.
- **The coloured band along Margaritaville Blvd is not a device.** It is the
  right-of-way strip that each plat carries, so it takes the colour of whatever
  phase it runs through. It changes colour at every plat line because that is
  genuinely where the phases change.
- **Collections, not patches.** 3,229 lots drawn one patch at a time was the
  whole render time at poster size; `PolyCollection` made the poster ~2 s.
- **Street labels come from parcel data, not road lines.** County road
  centrelines only cover Phases 1–3, so for most of the community there is no
  line to hang a label off. The anchor is the centre of the parcels carrying
  that street name, and the angle is the direction that run of parcels lies
  along — both from county record, neither guessed.
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

## Printing

- **Send the PDF.** It is vector and scales to any size cleanly.
- **Fonts are embedded** (PDF subsets) or outlined (SVG), so nothing
  substitutes.
- **0.25 in bleed** on the print presets, and Karen's contact block sits inside
  the safe margin so it cannot be trimmed off.
- **Aspect is taken from the real community footprint.** Nothing is stretched
  to hit a nominal size.
- Source, retrieval date and the "illustrative, not a survey" line appear on
  every size.

If Karen has a specific print size or vendor in mind, add it to `PRESETS` in
`render_map.py` — it is one line — or render it once with
`--size <width> <height> --dpi <n>`.

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

## Copyright and watermark

Every large output carries two things.

**A copyright notice** in the footer: *© 2026 Karen Lawell · Counts Real Estate
Group. Map design and compilation.*

The wording is deliberate. It claims **our original cartography and
compilation** — the palette, the layout, the phase-to-street attribution, the
address index. It does **not** claim the underlying data, because Bay County's
recorded plats, lots and address points are public record and nobody can own
them. Overclaiming there would undercut the honesty the rest of this map is
built on.

**A tiled watermark** across the map body: `KAREN LAWELL · NWFLBEACHHOMES.COM ·
850-517-8528`. It sits above the fills but *below* every label in z-order, so
it can never cost legibility — which is the entire point of this map. It's set
at a fixed diagonal rather than aligned to the scene rotation, because an
aligned repeat reads as a data label instead of a watermark. It also does
double duty: if someone lifts the map, the phone number goes with it.

Both are configured in `phase_meta.json` under `map.copyright` and
`map.watermark`.

Watermark applies to the poster and every print/giant preset. It is **not** on
the video frames — those get Karen's own branding in the edit — or on the
thumbnail plate, which gets overlaid. For a clean copy:

```powershell
python render_map.py --preset print-36x24 --no-watermark
```

## Still needs Karen

Nothing blocking — these are map polish.

- [ ] Confirm the two pins measured off the builder's site plan: Barkaritaville
      Dog Park and the Port of Indecision kayak launch. Both render with a `?`
      until she does.
- [x] The future marina. Karen placed it herself — open ground between Phase 4
      and the Town Center tract, on the water. It renders without a `?`; the
      "(future)" in the label carries the caveat. It is deliberately a labelled
      point and **not** a basin outline: the builder's plan does not show a
      marina yet, so there is no shape anyone could stand behind.
- [ ] The future-commercial parcel — confirm construction status and whether
      the grocery tenant can be named on screen.
- [ ] Phase 4A (#4,001–4,515) and Phase 4B (#4,318–4,509) have overlapping
      Minto lot numbers in county data. Interleaved numbering, or lots sitting
      across a plat line?
- [ ] Karen says the block the builder's plan still marks "Future Development",
      just west of the Stay & Play cottages, is also Stay & Play. It is not in
      the public record, so no area is drawn for it — confirm the extent.
- [ ] One clipped label on Minto's Phase 4/5 panel still reads only "…IK DR".
- [ ] A specific print size or vendor, if she has one in mind.
