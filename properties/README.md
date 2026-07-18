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
| Breakwater at Ward Creek | Toll Brothers | Builder | Placeholder |
| Salt Grass at Ward Creek | Kolter Homes; Fischer Homes | Builder | Placeholder |
| Bayside at Ward Creek | D.R. Horton | Builder | Placeholder |

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

### Breakwater at Ward Creek

Builder: Toll Brothers. M365:
`Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Breakwater at Ward Creek\Toll Brothers\<Model>\`.

### Salt Grass at Ward Creek (Kolter Homes & Fischer Homes)

Two builders — organize by builder, then model:
`Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Salt Grass at Ward Creek\<Kolter Homes | Fischer Homes>\<Model>\`.

### Bayside at Ward Creek (D.R. Horton)

Single builder:
`Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Bayside at Ward Creek\D.R. Horton\<Model>\`.

## Individual listings (resale / specific homes)

Specific addresses follow `County \ City \ [Area] \ Community \ [Phase] \ Address`.
Examples currently at the `Properties\` root to be relocated:

| Address | Proposed path (County \ City \ [Area] \ Community \ [Phase] \ Address) |
| --- | --- |
| 109 Seabreeze Ct | `Walton County \ Seacrest Beach \ Seabreeze \ 109 Seabreeze Ct` |
| 138 Pond Cypress Cv | `Gulf County \ Port Saint Joe \ WindMark \ North WindMark \ 138 Pond Cypress Cv` |
| 917 Watermark Way | `Bay County \ Panama City \ East Bay \ Laird Point \ 917 Watermark Way` |
