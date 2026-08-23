# Latitude Margaritaville Watersound

Bay County → Panama City Beach → West Bay & Hwy 79 Corridor → **Latitude
Margaritaville Watersound**

Minto's 55+ active-adult community off Highway 79. **Area 1 — Phases 1 through
10, 16 recorded plats · 3,229 platted homesites · ~2,123 acres**, all
verifiable in Bay County public record. Area 2 is planned but has no recorded
plat yet.

Karen and her husband live in **Phase 8**.

## In this folder

| File | What it is |
| --- | --- |
| [`phase-status.md`](phase-status.md) | Permanent per-phase facts, Karen's first-hand noise calls, and the record-day inventory workflow |
| [`streets_by_phase.md`](streets_by_phase.md) | Every street in every phase, each name tagged with the public record it came from |
| [`street-names-buffett.md`](street-names-buffett.md) | Which street names are **verified** Jimmy Buffett references and which only look like it. Read before scripting a joke about one |
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
- **Live inventory is never printed.** It changes by the hour. It is a spoken,
  dated snapshot — run `tools/map/inventory_report.py` on record day and say
  "as I'm recording this, in [Month Year]…". That volatility is the call to
  action, not a caveat.
- **Minto lot numbers are not house numbers.** Quote the county address.
- **Highway 79 noise is the real per-phase discriminator** (Phases 1, 2 and
  3B & 3C). The Bandshell is not — a loud show carries for miles.
- **Do not say "Phase 11."** Area 2 has no recorded plat.
- Nothing gets added to the map or these documents unless it is in public
  record or Karen has confirmed it first-hand, and first-hand calls are
  attributed to her as such.
