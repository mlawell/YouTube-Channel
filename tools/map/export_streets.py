"""Emit the per-phase street index as Markdown + JSON.

Reads `data/features.json` (produced by build_features.py) and writes
`output/streets_by_phase.md` and `output/streets_by_phase.json`.

Every street name here came out of Bay County public record -- road
centerlines, address points, or parcel site addresses -- so each one is
citable. Names Bay County has no data for are listed as gaps for Karen to
fill in from her own knowledge rather than guessed at.

    python export_streets.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "features.json"
OUT = HERE / "output"
# Committed copy: the street index is a reference document, not a build artefact.
DOCS = HERE.parent.parent / "properties" / "latitude-margaritaville-watersound"

SOURCE_LABEL = {
    "county road centerline": "road centerline",
    "county address point": "address point",
    "county parcel site address": "parcel site address",
    "curated": "curated (needs Karen)",
}


def load() -> dict:
    if not DATA.exists():
        raise SystemExit("data/features.json missing -- run build_features.py first")
    return json.loads(DATA.read_text(encoding="utf-8"))


def build(d: dict) -> dict:
    phases = []
    for p in d["phases"]:
        streets = [
            {
                "name": st["name"],
                "sources": [SOURCE_LABEL.get(s, s) for s in st.get("sources", [])],
            }
            for st in p.get("streets", [])
        ]
        phases.append(
            {
                "phase": p["label"],
                "subdivision_name": p["subdivid"],
                "plat_book": p["plat_book"],
                "plat_page": p["plat_page"],
                "acres": p["acres"],
                "platted_lots": p["lot_count"],
                "lot_number_range": p.get("lot_number_range"),
                "streets": streets,
                "street_count": len(streets),
            }
        )
    return {
        "community": "Latitude Margaritaville Watersound",
        "county": "Bay County, Florida",
        "generated": date.today().isoformat(),
        "sources": [
            "Bay County FL ArcGIS -- Property/MapServer/2 (recorded subdivision plats)",
            "Bay County FL ArcGIS -- Property/MapServer/0 (subdivision lots)",
            "Bay County FL ArcGIS -- Basic_Layers/MapServer/2 (road centerlines)",
            "Bay County FL ArcGIS -- Basic_Layers/MapServer/0 (address points)",
            "Bay County FL ArcGIS -- TEST_Parcels/MapServer/1 (parcel site addresses)",
        ],
        "method": (
            "Streets are attributed to a phase geometrically: every county road "
            "centreline, address point and parcel site address inside a recorded "
            "plat polygon contributes its street name to that phase. Nothing is "
            "inferred from a site plan or from a neighbouring phase."
        ),
        "lot_numbering": (
            "From Phase 4 onward the lot number carries a phase prefix "
            "(4xxx, 5xxx ... 10xxx), so a lot number alone identifies its phase. "
            "Phases 1-3 use one unprefixed run of 1-381 across 3A, 3B & 3C and 3D. "
            "Phase 5A3 lots have no LOTID in the county data yet -- it is the "
            "newest plat."
        ),
        "phases": phases,
        "totals": {
            "phases": len(phases),
            "platted_lots": d["total_lots"],
            "acres": d["total_acres"],
            "distinct_streets": len(
                {st["name"] for p in phases for st in p["streets"]}
            ),
        },
    }


def markdown(idx: dict) -> str:
    L: list[str] = []
    a = L.append
    a("# Streets by phase - Latitude Margaritaville Watersound")
    a("")
    a(f"*Generated {idx['generated']} from Bay County, Florida public records.*")
    a("")
    a(idx["method"])
    a("")
    a("**Lot numbering.** " + idx["lot_numbering"])
    a("")
    a("> Illustrative only - not a survey. Street names are transcribed from")
    a("> county records, never invented or inferred. Where the county has no")
    a("> coverage the entry is left blank and flagged rather than guessed.")
    a("")
    a("## Summary")
    a("")
    a("| Phase | Plat | Acres | Platted lots | Lot numbers | Streets |")
    a("| --- | --- | ---: | ---: | --- | ---: |")
    for p in idx["phases"]:
        rng = p["lot_number_range"]
        rng_s = f"{rng[0]:,}-{rng[1]:,}" if rng else "not yet in county data"
        a(
            f"| {p['phase']} | PB {p['plat_book']}/{p['plat_page']} | {p['acres']:,.1f} "
            f"| {p['platted_lots']:,} | {rng_s} | {p['street_count']} |"
        )
    t = idx["totals"]
    a(
        f"| **Total** | **{t['phases']} recorded plats** | **{t['acres']:,.0f}** "
        f"| **{t['platted_lots']:,}** | | **{t['distinct_streets']} distinct** |"
    )
    a("")
    a("## Per phase")
    a("")
    for p in idx["phases"]:
        a(f"### {p['phase']}")
        a("")
        a(f"`{p['subdivision_name']}` - plat book {p['plat_book']}, page {p['plat_page']}")
        a("")
        if not p["streets"]:
            a("_No street names in Bay County public data for this phase - **needs Karen**._")
            a("")
            continue
        a("| Street | Public-record source |")
        a("| --- | --- |")
        for st in p["streets"]:
            a(f"| {st['name']} | {', '.join(st['sources'])} |")
        a("")
    a("## Sources")
    a("")
    for s in idx["sources"]:
        a(f"- {s}")
    a("")
    return "\n".join(L)


def main() -> None:
    idx = build(load())
    js = json.dumps(idx, indent=2, ensure_ascii=False)
    md = markdown(idx)
    for folder in (OUT, DOCS):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "streets_by_phase.json").write_text(js, encoding="utf-8")
        (folder / "streets_by_phase.md").write_text(md, encoding="utf-8")
        print(f"streets_by_phase.json / .md -> {folder}")
    print(f"  {idx['totals']['phases']} phases, "
          f"{idx['totals']['distinct_streets']} distinct streets")
    empty = [p["phase"] for p in idx["phases"] if not p["streets"]]
    if empty:
        print("  NEEDS KAREN (no county street data): " + ", ".join(empty))


if __name__ == "__main__":
    main()
