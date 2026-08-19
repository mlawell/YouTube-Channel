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

from fmt import ident_range

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
                **({"address_range": st["address_range"],
                    "addressed_parcels": st["addressed_parcels"]}
                   if st.get("address_range") else {}),
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
            "Two different number series exist and they are easy to confuse. "
            "MINTO LOT NUMBERS carry a phase prefix from Phase 4 onward "
            "(4xxx ... 10xxx), so a lot number identifies its phase; phases 1-3 "
            "use one unprefixed run of 1-381. COUNTY HOUSE NUMBERS -- the "
            "searchable street address -- are an entirely different series. On "
            "Escape Avenue, Minto lot 8042 is not house number 8042: the county "
            "address range on that street is 9201-9499 in Phase 7 and 9502-9667 "
            "in Phase 8. Quote house numbers to buyers, not lot numbers."
        ),
        "cross_phase_streets": cross_phase(phases),
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


def cross_phase(phases: list[dict]) -> list[dict]:
    """Streets that run through more than one recorded phase.

    These are the ones that confuse buyers: two homes on the same street can
    sit in two different phases. Where the county has house numbers on both
    sides, the number range tells you which phase you are looking at.
    """
    where: dict[str, list[dict]] = {}
    for p in phases:
        for st in p["streets"]:
            where.setdefault(st["name"], []).append(
                {"phase": p["phase"], "address_range": st.get("address_range")}
            )
    rows = [
        {"street": name, "phases": segs, "phase_count": len(segs)}
        for name, segs in where.items()
        if len(segs) > 1
    ]
    return sorted(rows, key=lambda r: (-r["phase_count"], r["street"]))


def markdown(idx: dict) -> str:
    L: list[str] = []
    a = L.append
    a("# Streets by phase - Latitude Margaritaville Watersound")
    a("")
    a(f"*Generated {idx['generated']} from Bay County, Florida public records.*")
    a("")
    a(idx["method"])
    a("")
    a("**Lot numbers are not house numbers.** " + idx["lot_numbering"])
    a("")
    a("> Illustrative only - not a survey. Street names are transcribed from")
    a("> county records, never invented or inferred. Where the county has no")
    a("> coverage the entry is left blank and flagged rather than guessed.")
    a("")
    a("## Streets that cross a phase boundary")
    a("")
    a("These are the ones that catch buyers out: two homes on the same street,")
    a("two different phases. Where the county has house numbers on both sides,")
    a("the address range tells you which phase you are looking at.")
    a("")
    a("| Street | Phases | Address range per phase (county record) |")
    a("| --- | ---: | --- |")
    for r in idx["cross_phase_streets"]:
        segs = []
        for s in r["phases"]:
            rng = s["address_range"]
            segs.append(f"{s['phase']} {ident_range(rng[0], rng[1])}" if rng else f"{s['phase']} (no county addresses)")
        a(f"| {r['street']} | {r['phase_count']} | {' · '.join(segs)} |")
    a("")
    a("## Summary")
    a("")
    a("| Phase | Plat | Acres | Platted lots | Minto lot numbers | Streets |")
    a("| --- | --- | ---: | ---: | --- | ---: |")
    for p in idx["phases"]:
        rng = p["lot_number_range"]
        rng_s = ident_range(rng[0], rng[1]) if rng else "not yet in county data"
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
        a("| Street | House numbers (county record) | Public-record source |")
        a("| --- | --- | --- |")
        for st in p["streets"]:
            rng = st.get("address_range")
            rng_s = ident_range(rng[0], rng[1]) if rng else "—"
            a(f"| {st['name']} | {rng_s} | {', '.join(st['sources'])} |")
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
