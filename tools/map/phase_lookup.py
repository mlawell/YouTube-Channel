"""Which phase is this address in?

Geometric lookup: lat/lon -> point-in-recorded-plat -> phase. It works for
every phase including the newest ones, because it needs nothing but the
recorded plat polygons -- no street list, no site plan.

Three ways in:

    # a coordinate
    python phase_lookup.py --latlon 30.312154 -85.863968

    # a lot number (Phase 4 onward carries a phase prefix)
    python phase_lookup.py --lot 8042

    # a CSV of listings exported from Karen's dashboard
    python phase_lookup.py --csv listings.csv --out listings_tagged.csv

The CSV needs latitude/longitude columns (any of lat/latitude/Lat and
lon/lng/longitude/Long). A `phase` column is added to every row. This is how
active for-sale inventory gets tagged to a phase -- Karen exports from
BoldTrail, this tags it, no scraping and no MLS redistribution.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
FEATURES = HERE / "data" / "features.json"

LAT_KEYS = ("latitude", "lat", "y", "geo_lat", "map_lat")
LON_KEYS = ("longitude", "long", "lon", "lng", "x", "geo_lon", "map_lon")


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
        """Lot numbers are only unique from Phase 4 up; 1-381 spans Phase 1-3."""
        hits = []
        for p in self.phases:
            rng = p.get("lot_number_range")
            if rng and rng[0] <= lot <= rng[1]:
                hits.append(p)
        return hits


def describe(p: dict) -> str:
    lines = [
        f"{p['label']}  ({p['subdivid']})",
        f"  recorded plat     PB {p['plat_book']}/{p['plat_page']}",
        f"  platted homesites {p['lot_count']:,}   ({p['acres']:,.1f} acres)",
    ]
    rng = p.get("lot_number_range")
    if rng:
        lines.append(f"  lot numbers       {rng[0]:,}-{rng[1]:,}")
    status = p.get("availability", "unconfirmed")
    flag = "" if p.get("confirmed") else "   [PROVISIONAL - confirm before quoting]"
    lines.append(f"  availability      {status}{flag}")
    streets = [st["name"] for st in p.get("streets", [])]
    if streets:
        lines.append(f"  streets           {', '.join(streets)}")
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
    ap.add_argument("--lot", type=int)
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    if not (a.latlon or a.lot is not None or a.csv):
        ap.print_help()
        sys.exit(1)

    lk = Lookup()

    if a.latlon:
        lat, lon = a.latlon
        p = lk.by_latlon(lat, lon)
        print(f"{lat}, {lon}")
        print(describe(p) if p else "  not inside any recorded Latitude plat")

    if a.lot is not None:
        hits = lk.by_lot(a.lot)
        print(f"lot {a.lot:,}")
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
