# Properties & Communities

Index and organization standard for the real-estate inventory Karen markets across
every platform. The **media** (models, floor plans, galleries, tour video, community
photos) lives in the M365 / OneDrive library — see
[`../brand/README.md`](../brand/README.md#asset-library-microsoft-365) — and is
referenced from here, not duplicated into the repo.

M365 roots (under `C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents`):

- `Properties\` — model floor plans, galleries, tour video, and specific-home listings.
- `Images\Communities\` — community/lifestyle photography.

Both trees use the **same geographic prefix**: `County \ City \ [Area] \ Community \ …`.

## ✅ Permission to market this media is settled

**Karen is a Counts agent marketing Counts properties.** There is no outstanding
permission question on any listing media in this library, and no video, script or
plan should carry one. Mike, 2026-08-23:

> *"Stop worrying about Counts marketing policy and please don't ask me again…
> this is the third time I've said it. WE HAVE PERMISSION TO MARKET THEIR
> PROPERTIES. Karen works for Counts and is helping her friends market. PERIOD."*

It is recorded here, at the index for the media itself, **so no future session
re-derives it as an open question.** It had already cost three separate
exchanges before it was written down.

**Do not confuse this with disclosure**, which is a different thing and does
still apply: Florida Administrative Code **61J2-10.025** requires the licensed
brokerage name adjacent to the point of contact information in advertising. That
is a formatting requirement on the published piece, not a permission question,
and the video packages already satisfy it by keeping
`Brokered by Counts Real Estate Group` directly under the phone/email block.

## Organization standard

Everything is filed under one geographic prefix, then branches by what it is:

```
<County> \ <City> \ [<Area>] \ <Community> \ …
   new-build models:  … \ <Community> \ <Collection | Builder> \ <Model> \ { gallery, video, floorplan }
   specific homes:    … \ <Community> \ [<Phase>] \ <Address> \
   community photos:   … \ <Community> \                 (in Images\Communities)
```

| Level | Meaning | When it applies |
| --- | --- | --- |
| **County** | County | Always (e.g., *Bay County*, *Walton County*) |
| **City** | City / town | Always (e.g., *Panama City Beach*, *Seacrest Beach*) |
| **Area** | Corridor / submarket grouping | Optional (e.g., *West Bay & HWY 79 Corridor*) |
| **Community** | The named development / subdivision | Always (e.g., *Latitude Margaritaville Watersound*, *Seabreeze*) |
| **Collection** | A builder's product tier within one community | New builds: single-builder communities with tiers (Margaritaville's Conch / Caribbean / Beach / Island / Vista) |
| **Builder** | The homebuilder | New builds: multi-builder communities — use the builder instead of Collection (Salt Grass = Kolter + Fischer) |
| **Model** | The individual floor plan / model | New-build leaf |
| **Phase** | A build phase within a community | Optional, for specific homes in phased communities (e.g., *Phase 4*) |
| **Address** | A specific home | Specific-home leaf (e.g., *109 Seabreeze Ct*, *8656 Weekend Dr*) |
| **Leaf contents** | `gallery/` (photos), `video/` (tour + `music/`, `presenters/`), floor-plan files | Per model or address |

**Rules of thumb**

- **New build, single builder + product tiers** → middle level is **Collection**
  (Margaritaville / Minto).
- **New build, multiple builders in one community** → middle level is **Builder**;
  models (and any builder-specific collections) nest under each builder (Salt Grass).
- **New build, single builder, no tiers** → models nest under a single builder folder
  for consistency (Bayside / D.R. Horton).
- **Specific home / resale** → file by address under its community, with an optional
  **Phase** level for phased communities.
- **Area** is optional — include it where a corridor grouping is useful (West Bay & HWY
  79 Corridor); skip it where the community sits directly under the city.

## Area: West Bay & HWY 79 Corridor

Geographic path: `Bay County \ Panama City Beach \ West Bay & HWY 79 Corridor`.

| Community | Builder(s) | Middle level | Status |
| --- | --- | --- | --- |
| Latitude Margaritaville Watersound | Minto | Collection (5) | Cataloged (37 models) |
| Breakwater at Ward Creek | Toll Brothers | Collection (3) | Cataloged (14 models) |
| Salt Grass at Ward Creek | Kolter Homes; Fischer Homes | Builder | Cataloged (13 models) |
| Bayside at Ward Creek | D.R. Horton | Builder | Cataloged (7 plans) |

### Latitude Margaritaville Watersound (Minto)

9201 Highway 79, Panama City Beach FL. M365:
`Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Latitude Margaritaville Watersound\Models\<Collection>\<Model>\`.

| Collection | Type | Models |
| --- | --- | --- |
| Conch Collection | Cottages | Aloha, Bamboo, Camellia, Dreamsicle, Hula, Mango |
| Caribbean Collection | Villas | Antigua, Barbuda, Barbuda Bay, Jamaica, Lucia, Nevis, Tortola |
| Beach Collection | Single-Family | Breeze, Breeze Bay, Cabana, Cabana Bay, Cabana Tandem, Cabana Bay Tandem, Coconut, Escape, Escape Bay, Parrot, Seashell, Seashell Bay |
| Island Collection | Single-Family | Aruba, St. Bart, Trinidad, Trinidad Bay |
| Vista Collection | Single-Family (luxury) | Mainsail, Mainsail Bay, Spinnaker, Wayfarer, Grand Mainsail, Grand Mainsail Bay, Grand Spinnaker, Grand Wayfarer |

> Verified model specs and pricing are tracked separately; advertised model prices are
> home-only (homesite cost is extra) and set by Minto (non-negotiable).

### Breakwater at Ward Creek (Toll Brothers)

Single builder with three collections (tiers) — organize by collection, then model:
`Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Breakwater at Ward Creek\<Collection>\<Model>\`.

| Collection | Sq ft (a/c) | Models |
| --- | --- | --- |
| Coastal Collection | 1,665–2,548 | Frankford (2BR), Bellview (3BR), Cain (3BR), Hathaway (3–4BR) |
| Oasis Collection | 2,114–2,565 | Summerwood (3BR), West Bay (3BR), Palmetto (4BR), Sandestin (4BR), Delwood (3–4BR) |
| Vista Collection | 2,455–3,242 | Caswell (3BR), Sandy (4BR), Grayton (4BR), Callaway (4–5BR), Killian (4–5BR) |

### Salt Grass at Ward Creek (Kolter Homes & Fischer Homes)

Two builders — organize by builder, then model:
`Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Salt Grass at Ward Creek\<Kolter Homes | Fischer Homes>\<Model>\`.

**Fischer Homes — Designer Collection (7 plans):**

| Model | Beds | Sq ft |
| --- | --- | --- |
| Edenton | 2–3 | 1,501–2,645 |
| Amelia | 2–4 | 1,683–3,020 |
| Wilmington | 2–4 | 1,725–3,322 |
| Camden | 2–4 | 1,859–2,811 |
| Linden | 3–5 | 2,064–3,219 |
| Olive | 3–6 | 2,417–3,097 |
| Ivy | 4–6 | 2,692–2,756 |

**Kolter Homes — Carson Collection (6 plans; living-area sq ft):**

| Model | Beds | Living sq ft |
| --- | --- | --- |
| Erika | 2–3 | 1,811 |
| Julia | 2–4 | 1,958 |
| Lila | 3–5 | 2,134 |
| Madison | 3–5 | 2,281 |
| Natasha | 3–4 | 2,402 |
| Olivia | 3–5 | 2,750 |

### Bayside at Ward Creek (D.R. Horton)

Single builder (Tradition Series) — townhomes + single-family:
`Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Bayside at Ward Creek\D.R. Horton\<Model>\`.

| Model | Type | Beds / Baths | Sq ft |
| --- | --- | --- | --- |
| Palm | Townhome | 3BR / 2.5BA | ~1,459 |
| Delray | Single-family | 4BR / 2BA | 2,044 |
| Kennedy | Single-family | 5BR / 3BA | 2,145 |
| Carol | Single-family | 5BR / 3BA | 2,550 |
| Rhett | Single-family | — | — |
| Oakland | Single-family | — | — |

> D.R. Horton lists 7 floor plans; 6 confirmed above (one plan name not yet captured).
> Range 1,459–2,550 sq ft.

## Individual listings (resale / specific homes)

Specific addresses follow `County \ City \ [Area] \ Community \ [Phase] \ Address`.
Examples currently at the `Properties\` root to be relocated:

| Address | Proposed path (County \ City \ [Area] \ Community \ [Phase] \ Address) |
| --- | --- |
| 109 Seabreeze Ct | `Walton County \ Seacrest Beach \ Seabreeze \ 109 Seabreeze Ct` |
| 138 Pond Cypress Cv | `Gulf County \ Port Saint Joe \ WindMark \ North WindMark \ 138 Pond Cypress Cv` |
| 917 Watermark Way | `Bay County \ Panama City \ East Bay \ Laird Point \ 917 Watermark Way` |
