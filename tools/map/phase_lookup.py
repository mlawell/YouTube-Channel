"""Which phase is this address in?

Geometric lookup: lat/lon -> point-in-recorded-plat -> phase. It works for
every phase including the newest ones, because it needs nothing but the
recorded plat polygons -- no street list, no site plan.

Three ways in:

    # a coordinate
    python phase_lookup.py --latlon 30.312154 -85.863968

    # a street address, the way it appears on a listing
    python phase_lookup.py --address "9502 Escape Ave"

    # a Minto lot number -- NOT an address, see the warning below
    python phase_lookup.py --lot 8042

    # a CSV of listings exported from Karen's dashboard
    python phase_lookup.py --csv listings.csv --out listings_tagged.csv

The CSV needs latitude/longitude columns (any of lat/latitude/Lat and
lon/lng/longitude/Long). A `phase` column is added to every row. This is how
active for-sale inventory gets tagged to a phase -- Karen exports from
BoldTrail, this tags it, no scraping and no MLS redistribution.

TWO NUMBER SERIES -- do not confuse them
----------------------------------------
Minto **lot numbers** are phase-prefixed from Phase 4 onward (4xxx ... 10xxx).
County **house numbers** -- the searchable street address -- are a completely
different series. Minto lot 8042 is in Phase 8, but every Escape Avenue address
is 9xxx: the county range is 9201-9499 in Phase 7 and 9502-9667 in Phase 8.
Searching "8042 Escape Ave" finds nothing. `--lot` takes a lot number and
`--address` takes an address; they are not interchangeable.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from fmt import ident, ident_range, ident_runs, qty

HERE = Path(__file__).parent
FEATURES = HERE / "data" / "features.json"

LAT_KEYS = ("latitude", "lat", "y", "geo_lat", "map_lat")
LON_KEYS = ("longitude", "long", "lon", "lng", "x", "geo_lon", "map_lon")

STREET_ABBREV = {
    "avenue": "ave", "boulevard": "blvd", "circle": "cir", "court": "ct",
    "drive": "dr", "lane": "ln", "parkway": "pkwy", "place": "pl",
    "road": "rd", "street": "st", "way": "way", "terrace": "ter",
}


def norm_street(name: str) -> str:
    """'Escape Avenue' == 'ESCAPE AVE' == 'escape ave.'"""
    words = re.findall(r"[a-z0-9]+", name.lower())
    return " ".join(STREET_ABBREV.get(w, w) for w in words)


def load_phases() -> list[dict]:
    if not FEATURES.exists():
        raise SystemExit("data/features.json missing -- run build_features.py first")
    return json.loads(FEATURES.read_text(encoding="utf-8"))["phases"]


class Lookup:
    def __init__(self) -> None:
        from shapely.geometry import shape

        self.phases = load_phases()
        self.polys = []
        for p in self.phases:
            g = shape(p["geometry"])
            if not g.is_valid:
                g = g.buffer(0)
            self.polys.append((p, g, g.bounds))

    def by_latlon(self, lat: float, lon: float) -> dict | None:
        from shapely.geometry import Point

        pt = Point(lon, lat)
        for p, g, (x0, y0, x1, y1) in self.polys:
            if x0 <= lon <= x1 and y0 <= lat <= y1 and g.contains(pt):
                return p
        return None

    def by_lot(self, lot: int) -> list[dict]:
        """Lot numbers are only unique from Phase 4 up; 1-381 spans Phase 1-3.

        Matched against the runs a phase actually owns, not its outer span:
        Phase 4A runs 4001-4317 and 4510-4515, so lot 4400 belongs to Phase 4B
        alone even though it falls inside 4A's first and last number.
        """
        hits = []
        for p in self.phases:
            runs = p.get("lot_number_runs")
            if not runs:
                rng = p.get("lot_number_range")
                runs = [rng] if rng else []
            if any(lo <= lot <= hi for lo, hi in runs):
                hits.append(p)
        return hits

    def by_address(self, addr: str) -> list[tuple[dict, dict]]:
        """Match '9502 Escape Ave' against the county house-number range each
        street occupies in each phase. Returns (phase, street) pairs."""
        m = re.match(r"^\s*(\d+)\s+(.+)$", addr)
        if not m:
            return []
        num, street = int(m.group(1)), norm_street(m.group(2))
        hits = []
        for p in self.phases:
            for st in p.get("streets", []):
                if norm_street(st["name"]) != street:
                    continue
                rng = st.get("address_range")
                if rng and rng[0] <= num <= rng[1]:
                    hits.append((p, st))
        return hits

    def street_everywhere(self, street: str) -> list[tuple[dict, dict]]:
        """Every phase a street appears in, whatever the number."""
        want = norm_street(street)
        return [
            (p, st)
            for p in self.phases
            for st in p.get("streets", [])
            if norm_street(st["name"]) == want
        ]


def describe(p: dict) -> str:
    lines = [
        f"{p['label']}  ({p['subdivid']})",
        f"  recorded plat     PB {p['plat_book']}/{p['plat_page']}",
        f"  platted homesites {qty(p['lot_count'])}   ({p['acres']:,.1f} acres)",
    ]
    runs = p.get("lot_number_runs") or ([p["lot_number_range"]]
                                        if p.get("lot_number_range") else [])
    if runs:
        lines.append(f"  lot numbers       {ident_runs(runs, dash='-')}"
                     "   (Minto lot numbers, not addresses)")
    for st in p.get("streets", []):
        r = st.get("address_range")
        lines.append(f"  street            {st['name']}"
                     + (f"   {ident_range(r[0], r[1], dash='-')}" if r
                        else "   (no county addresses)"))
    return "\n".join(lines)


def pick(row: dict, keys: tuple[str, ...]) -> str | None:
    lowered = {k.strip().lower(): k for k in row if k}
    for want in keys:
        if want in lowered:
            return lowered[want]
    return None


def tag_csv(lk: Lookup, src: Path, dst: Path) -> None:
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
    if not rows:
        raise SystemExit(f"{src} has no rows")
    lat_col = pick(rows[0], LAT_KEYS)
    lon_col = pick(rows[0], LON_KEYS)
    if not lat_col or not lon_col:
        raise SystemExit(
            f"could not find latitude/longitude columns in {src}\n"
            f"  columns present: {', '.join(k for k in rows[0] if k)}"
        )

    tagged = missing = outside = 0
    for r in rows:
        try:
            lat, lon = float(r[lat_col]), float(r[lon_col])
        except (TypeError, ValueError):
            r["phase"] = ""
            r["phase_note"] = "no coordinate"
            missing += 1
            continue
        p = lk.by_latlon(lat, lon)
        if p:
            r["phase"] = p["label"]
            r["phase_plat"] = f"PB {p['plat_book']}/{p['plat_page']}"
            r["phase_note"] = ""
            tagged += 1
        else:
            r["phase"] = ""
            r["phase_note"] = "outside every recorded plat"
            outside += 1

    fields = list(rows[0].keys())
    for extra in ("phase", "phase_plat", "phase_note"):
        if extra not in fields:
            fields.append(extra)
    with dst.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"{dst}  ({len(rows)} rows)")
    print(f"  tagged to a phase   {tagged}")
    if outside:
        print(f"  outside every plat  {outside}  (check the coordinate, or it is not in LMWS)")
    if missing:
        print(f"  no coordinate       {missing}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--latlon", nargs=2, type=float, metavar=("LAT", "LON"))
    ap.add_argument("--address", metavar="ADDR",
                    help="a street address, e.g. \"9502 Escape Ave\"")
    ap.add_argument("--lot", type=int,
                    help="a MINTO LOT number -- not an address")
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    if not (a.latlon or a.address or a.lot is not None or a.csv):
        ap.print_help()
        sys.exit(1)

    lk = Lookup()

    if a.latlon:
        lat, lon = a.latlon
        p = lk.by_latlon(lat, lon)
        print(f"{lat}, {lon}")
        print(describe(p) if p else "  not inside any recorded Latitude plat")

    if a.address:
        hits = lk.by_address(a.address)
        print(a.address)
        if hits:
            for p, st in hits:
                rng = st["address_range"]
                print(describe(p))
                print(f"  matched on       {st['name']} {ident_range(rng[0], rng[1], dash='-')} "
                      f"(county record)")
            if len(hits) > 1:
                print("  NOTE: more than one phase matched -- check the "
                      "coordinate to be certain.")
        else:
            m = re.match(r"^\s*\d+\s+(.+)$", a.address)
            everywhere = lk.street_everywhere(m.group(1)) if m else []
            if everywhere:
                print("  that street exists, but no phase covers that house "
                      "number in county record:")
                for p, st in everywhere:
                    rng = st.get("address_range")
                    print(f"    {p['label']:<15}{st['name']}"
                          + (f"  {ident_range(rng[0], rng[1], dash='-')}" if rng else "  (no county addresses)"))
                print("  Either the number is newer than the county data, or "
                      "check the spelling. Do not guess -- use --latlon.")
            else:
                print("  no county record for that street in any phase")

    if a.lot is not None:
        hits = lk.by_lot(a.lot)
        print(f"Minto lot {ident(a.lot)}  (a lot number, NOT a street address)")
        if not hits:
            print("  no phase carries that lot number")
        elif len(hits) > 1:
            print("  ambiguous -- lot numbers repeat across these phases; "
                  "use the coordinate lookup instead:")
            for p in hits:
                print(f"    {p['label']}")
        else:
            print(describe(hits[0]))

    if a.csv:
        out = a.out or a.csv.with_name(a.csv.stem + "_with_phase.csv")
        tag_csv(lk, a.csv, out)


if __name__ == "__main__":
    main()
