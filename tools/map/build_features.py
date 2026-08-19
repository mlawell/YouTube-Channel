"""Turn the raw county downloads into one tidy feature set for the renderer.

Two independent phase lookups fall out of this, and they cross-check each other:

  geometric   any lat/lon -> point-in-plat-polygon -> phase. Works everywhere,
              including phases with no address or street coverage at all.
  lot number  Minto numbers lots with a phase prefix from Phase 4 on (7001-7226 =
              Phase 7, 8001-8200 = Phase 8, and so on). Bay County carries those
              same numbers in LOTID, so the county data confirms the scheme
              without anyone having to read them off a site plan.

Inputs   tools/map/data/*.geojson  (see fetch_data.py)
         tools/map/phase_meta.json, landmarks.json, street_index.json
Output   tools/map/data/features.json

Run:
    python tools/map/build_features.py
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

REF_LAT = 30.323
M_PER_DEG_LAT = 110_574.0
M_PER_DEG_LON = 111_320.0 * math.cos(math.radians(REF_LAT))
SQ_M_PER_ACRE = 4046.8564224

STREET_TYPES = {
    "AVE": "Ave", "BLVD": "Blvd", "CIR": "Cir", "CT": "Ct", "DR": "Dr",
    "LN": "Ln", "PKWY": "Pkwy", "PL": "Pl", "RD": "Rd", "ST": "St",
    "TRL": "Trl", "WAY": "Way",
}


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_cfg(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def phase_label(subdivid: str) -> str:
    """'LATITUDE AT WATERSOUND AREA 1 PHASE  6B & 6C' -> 'Phase 6B & 6C'."""
    tail = subdivid.upper().split("AREA 1", 1)[-1]
    tail = re.sub(r"\bPHASE\b|\bPH\b", " ", tail)
    return "Phase " + " ".join(tail.split())


def sort_key(label: str) -> tuple:
    body = label.replace("Phase ", "")
    head = body.split("&")[0].strip()
    num = ""
    for ch in head:
        if ch.isdigit():
            num += ch
        else:
            break
    return (int(num) if num else 99, head[len(num):])


def acres(geom) -> float:
    return geom.area * M_PER_DEG_LAT * M_PER_DEG_LON / SQ_M_PER_ACRE


def titlecase_street(raw: str) -> str:
    """'LOST SHAKER  WAY' -> 'Lost Shaker Way'. Never renames, only re-cases."""
    parts = [p for p in re.split(r"\s+", raw.strip()) if p]
    out = []
    for i, p in enumerate(parts):
        up = p.upper()
        if i == len(parts) - 1 and up in STREET_TYPES:
            out.append(STREET_TYPES[up])
        elif up.startswith("HIGHWAY") or up.isdigit():
            out.append(up.title() if not up.isdigit() else up)
        else:
            out.append(p.title())
    return " ".join(out)


class PhaseIndex:
    """Point-in-polygon phase lookup. The one source of truth for 'which phase?'."""

    def __init__(self, features: list[dict]):
        self.items = []
        for f in features:
            g = shape(f["geometry"])
            if not g.is_valid:
                g = g.buffer(0)
            self.items.append((phase_label(f["properties"]["SUBDIVID"]), g, g.bounds))
        self.items.sort(key=lambda t: sort_key(t[0]))

    def labels(self) -> list[str]:
        return [lab for lab, _, _ in self.items]

    def lookup(self, lon: float, lat: float) -> str | None:
        from shapely.geometry import Point

        pt = Point(lon, lat)
        for lab, poly, (x0, y0, x1, y1) in self.items:
            if x0 <= lon <= x1 and y0 <= lat <= y1 and poly.contains(pt):
                return lab
        return None

    def lookup_geom(self, geom: dict) -> str | None:
        g = shape(geom)
        if not g.is_valid:
            g = g.buffer(0)
        if g.is_empty:
            return None
        p = g.representative_point()
        return self.lookup(p.x, p.y)


def build_lot_ranges(lot_ids: list[str]) -> dict:
    """Lot-number span for a phase, ignoring stray misfiled lot numbers.

    From Phase 4 onward Minto prefixes lot numbers with the phase (4xxx ...
    10xxx), so a phase's lots cluster in one thousands band. A handful of
    county records carry a number from a different band -- keeping them would
    stretch the printed range far past reality (Phase 6B & 6C reads 6201-9400
    on the raw data). Report the dominant band and count the strays.
    """
    nums = sorted(int(x) for x in lot_ids if x and str(x).isdigit())
    if not nums or len(nums) < max(5, 0.25 * len(lot_ids)):
        # Too few county records carry a number to state a range honestly.
        return {"lot_number_range": None, "numbered_lots": len(nums),
                "lot_number_outliers": 0}
    bands = Counter(n // 1000 for n in nums)
    if len(bands) > 1 and max(nums) >= 1000:
        band, count = bands.most_common(1)[0]
        # Only trust the band if it clearly dominates; otherwise report as-is.
        if count / len(nums) >= 0.9:
            kept = [n for n in nums if n // 1000 == band]
            return {
                "lot_number_range": [kept[0], kept[-1]],
                "numbered_lots": len(nums),
                "lot_number_outliers": len(nums) - len(kept),
            }
    return {"lot_number_range": [nums[0], nums[-1]], "numbered_lots": len(nums),
            "lot_number_outliers": 0}


def centroid_of(geom: dict) -> tuple[float, float] | None:
    g = shape(geom)
    if not g.is_valid:
        g = g.buffer(0)
    if g.is_empty:
        return None
    p = g.representative_point()
    return (p.x, p.y)


def principal_angle_deg(pts: list[tuple[float, float]]) -> float:
    """Direction a run of parcels lies along, so a street label can follow it."""
    n = len(pts)
    if n < 3:
        return 0.0
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    # Latitude compression: a degree of longitude is shorter than a degree of
    # latitude, so compare in locally-equal units or every angle comes out wrong.
    k = math.cos(math.radians(my))
    sxx = sum(((p[0] - mx) * k) ** 2 for p in pts)
    syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum(((p[0] - mx) * k) * (p[1] - my) for p in pts)
    ang = math.degrees(0.5 * math.atan2(2 * sxy, sxx - syy))
    return round(ang, 2)


def street_key(name: str) -> str:
    """Group spellings of the same street: 'Flipflop Ct' == 'Flip Flop Ct' == 'Flip Flop'."""
    words = [w for w in re.split(r"\s+", name.upper()) if w]
    if words and words[-1] in STREET_TYPES:
        words = words[:-1]
    return "".join(words)


def collect_streets(idx: PhaseIndex) -> dict:
    """Street names per phase, from three county layers, each tagged with its source.

    Nothing is inferred: a street only lands in a phase if a county feature carrying
    that name physically sits inside that phase's recorded plat. Spellings that
    differ between layers are grouped, and the fullest form (the one that still has
    its street type) becomes the display name.
    """
    found: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"names": set(), "sources": set(), "numbers": [], "pts": []}))

    def add(label: str | None, raw: str, source: str, number: int | None = None,
            pt: tuple[float, float] | None = None) -> None:
        if not label:
            return
        name = titlecase_street(raw)
        if not name or len(name) < 3:
            return
        rec = found[label][street_key(name)]
        rec["names"].add(name)
        rec["sources"].add(source)
        if number is not None:
            rec["numbers"].append(number)
        if pt is not None:
            rec["pts"].append(pt)

    for f in load("roads.geojson")["features"]:
        name = (f["properties"].get("FULL_NAME") or "").strip()
        if not name or name == "?":
            continue
        p = shape(f["geometry"]).interpolate(0.5, normalized=True)
        add(idx.lookup(p.x, p.y), name, "county road centerline")

    for f in load("addresses.geojson")["features"]:
        pr = f["properties"]
        name = " ".join(x for x in (pr.get("ST_NAME"), pr.get("ST_TYPE")) if x).strip()
        if not name:
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        num = pr.get("ADDRNUM") or pr.get("HOUSENUM")
        add(idx.lookup(lon, lat), name, "county address point",
            int(num) if str(num).isdigit() else None, (lon, lat))

    for f in load("street_points.geojson")["features"]:
        pr = f["properties"]
        addr = (pr.get("DSITEADDR") or "").strip()
        # Skip metes-and-bounds descriptions like '12 2S 17W -2-'.
        if not addr or " -" in addr or re.match(r"^\d+\s+\d+[NS]\s", addr):
            continue
        # DSITEADDR keeps the street type ('8482  MARGARITAVILLE BLVD'); ASTNAME drops it.
        m = re.match(r"^(\d+)\s+(.+)$", addr)
        name = (m.group(2) if m else addr).strip() or (pr.get("ASTNAME") or "").strip()
        if not re.search(r"[A-Z]{3}", name.upper()):
            continue
        add(idx.lookup_geom(f["geometry"]), name, "county parcel site address",
            int(m.group(1)) if m else None, centroid_of(f["geometry"]))

    out = {}
    for label, streets in found.items():
        rows = []
        for rec in streets.values():
            # Prefer the spelling that kept its street type, then the longest.
            display = sorted(rec["names"], key=lambda n: (n.split()[-1].upper() not in {v.upper() for v in STREET_TYPES.values()}, -len(n)))[0]
            row = {"name": display, "sources": sorted(rec["sources"])}
            nums = sorted(rec["numbers"])
            if nums:
                # Real, searchable house numbers from county record -- not Minto
                # lot numbers, which are a different series entirely.
                row["address_range"] = [nums[0], nums[-1]]
                row["addressed_parcels"] = len(nums)
            pts = rec["pts"]
            if pts:
                # Where to write the street name on a detailed map. County road
                # centrelines only cover Phases 1-3, so for the newer phases the
                # only way to place a label is the centre of the parcels that
                # carry the name -- which is real data, not a guess.
                row["label_lonlat"] = [
                    round(sum(p[0] for p in pts) / len(pts), 6),
                    round(sum(p[1] for p in pts) / len(pts), 6),
                ]
                row["label_angle"] = principal_angle_deg(pts)
            variants = sorted(rec["names"] - {display})
            if variants:
                row["also_spelled"] = variants
            rows.append(row)
        out[label] = sorted(rows, key=lambda d: d["name"])
    return out


def simplify(geom, tol: float = 0.000012):
    """Shave vertices the renderer will never resolve. ~1.2 m — well under a pixel."""
    g = shape(geom) if isinstance(geom, dict) else geom
    if not g.is_valid:
        g = g.buffer(0)
    return g.simplify(tol, preserve_topology=True).__geo_interface__


def main() -> None:
    raw_phases = load("phases.geojson")["features"]
    idx = PhaseIndex(raw_phases)
    meta = load_cfg("phase_meta.json")

    by_id = {phase_label(f["properties"]["SUBDIVID"]): f for f in raw_phases}

    print("lots")
    lots_by_phase: dict[str, list] = defaultdict(list)
    lotids: dict[str, list] = defaultdict(list)
    orphans = 0
    for f in load("lots.geojson")["features"]:
        if not f.get("geometry"):
            continue
        lab = idx.lookup_geom(f["geometry"])
        if not lab:
            orphans += 1
            continue
        lots_by_phase[lab].append(simplify(f["geometry"]))
        lotids[lab].append(f["properties"].get("LOTID"))
    print(f"  {sum(len(v) for v in lots_by_phase.values())} attributed, {orphans} outside the plats")

    print("streets")
    streets = collect_streets(idx)
    curated = load_cfg("street_index.json")["phases"]

    phases = []
    for lab in idx.labels():
        pr = by_id[lab]["properties"]
        geom = shape(by_id[lab]["geometry"])
        county = streets.get(lab, [])
        extra = curated.get(lab, {}).get("streets", [])
        known = {street_key(s["name"]) for s in county}
        merged = county + [
            {"name": s["name"], "sources": [s.get("source", "site plan, read visually")]}
            for s in extra
            if street_key(s["name"]) not in known
        ]
        phases.append(
            {
                "label": lab,
                "short": lab.replace("Phase ", "Ph "),
                "subdivid": pr["SUBDIVID"],
                "plat": f"PB {pr['PLATTBOOK']}/{pr['BOOKPAGE']}",
                "plat_book": pr["PLATTBOOK"],
                "plat_page": pr["BOOKPAGE"],
                "acres": round(acres(geom), 1),
                "lot_count": len(lots_by_phase[lab]),
                **build_lot_ranges(lotids[lab]),
                "centroid": [geom.centroid.x, geom.centroid.y],
                "bounds": list(geom.bounds),
                "streets": sorted(merged, key=lambda d: d["name"]),
                "geometry": simplify(by_id[lab]["geometry"]),
                **meta["phases"].get(lab, {}),
            }
        )
        p = phases[-1]
        rng = p["lot_number_range"]
        print(f"  {lab:<15}{p['plat']:<10}{p['acres']:>7.1f} ac{p['lot_count']:>5} lots  "
              f"{'#' + str(rng[0]) + '-' + str(rng[1]) if rng else 'unnumbered':<14}"
              f"{len(p['streets'])} streets")

    print("context")
    hwy = [
        {
            "name": titlecase_street(f["properties"].get("FULL_NAME") or ""),
            "route": (f["properties"].get("STRTE") or "").strip(),
            "geometry": simplify(f["geometry"], 0.00002),
        }
        for f in load("highways.geojson")["features"]
    ]
    water = [simplify(f["geometry"], 0.00003) for f in load("waterbodies.geojson")["features"]]
    creeks = [simplify(f["geometry"], 0.00002) for f in load("creeks.geojson")["features"]]
    roads = [
        {
            "name": titlecase_street(f["properties"].get("FULL_NAME") or ""),
            "owner": f["properties"].get("OWNER"),
            "geometry": simplify(f["geometry"], 0.00001),
        }
        for f in load("roads.geojson")["features"]
    ]
    print(f"  {len(hwy)} highway, {len(roads)} road, {len(water)} waterbody, {len(creeks)} creek features")

    footprint = unary_union([shape(p["geometry"]) for p in phases])
    out = {
        "generated_from": "Bay County FL public GIS (recorded plats, lots, roads, addresses, hydrology)",
        "reference_lat": REF_LAT,
        "bounds": list(footprint.bounds),
        "total_acres": round(acres(footprint), 1),
        "total_lots": sum(p["lot_count"] for p in phases),
        "phases": phases,
        "lots_by_phase": lots_by_phase,
        "highways": hwy,
        "roads": roads,
        "waterbodies": water,
        "creeks": creeks,
        "landmarks": load_cfg("landmarks.json")["landmarks"],
        "meta": {**meta["map"], "scope": meta.get("scope", {}),
                 "karen_first_hand": meta.get("karen_first_hand", {})},
    }
    path = DATA / "features.json"
    path.write_text(json.dumps(out), encoding="utf-8")
    print(f"\n{len(phases)} recorded phases · {out['total_lots']:,} platted lots · "
          f"{out['total_acres']:,.0f} acres -> data/features.json "
          f"({path.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
