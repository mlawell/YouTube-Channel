# Latitude Margaritaville Watersound

Bay County → Panama City Beach → West Bay & Hwy 79 Corridor → **Latitude
Margaritaville Watersound**

Minto's 55+ active-adult community off Highway 79. **16 recorded phases ·
3,229 platted homesites · ~2,123 acres**, all verifiable in Bay County public
record.

Karen and her husband live in **Phase 8**.

## In this folder

| File | What it is |
| --- | --- |
| [`phase-status.md`](phase-status.md) | Per-phase new-build vs resale-only table, with everything unverified flagged |
| [`streets_by_phase.md`](streets_by_phase.md) | Every street in every phase, each name tagged with the public record it came from |
| `streets_by_phase.json` | Same, machine-readable |

Both `streets_by_phase` files are **generated** — run
`python tools/map/export_streets.py` rather than editing them by hand.

## Related

- **The map generator:** [`tools/map`](../../tools/map) — poster, print PDF,
  thumbnail plate and a per-phase reveal sequence, all rebuilt from Bay County
  ArcGIS. Also holds `phase_meta.json`, the file to edit when a phase sells out.
- **Which phase is this address in?** `python tools/map/phase_lookup.py
  --latlon <lat> <lon>` — geometric point-in-recorded-plat lookup that works
  for every phase, including the newest ones with no county street coverage.
- **Models and collections:** [`../README.md`](../README.md) — 37 models across
  Conch cottages, Caribbean villas, Beach 50', Island 60' and Vista.
- **Video package:**
  [`platforms/youtube/content/latitude-phases-explained`](../../platforms/youtube/content/latitude-phases-explained/README.md)

## Standing accuracy rules

- Phases are **not priced differently.** Price follows model, collection and
  homesite premium. Never publish a price-by-phase tier.
- **Most phases are resale-only.** Availability is the headline buyer fact and
  it changes — always re-confirm against live inventory before publishing.
- Nothing gets added to the map or these documents unless it is in public
  record or Karen has confirmed it first-hand.
