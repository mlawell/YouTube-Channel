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

from shapely.geometry import mapping, shape
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


def split_town_center(lots_geoms: list[dict]) -> dict:
    """Separate the Town Center plat into the amenity tract and the cottages.

    The plat recorded as PH 5A3 is two quite different things sharing one
    boundary: one 48-acre tract carrying the Bandshell, Paradise Pool and the
    rest of the amenity core, and a pocket of cottage-sized homesites.  Drawn
    as a single 'phase' it reads as a neighbourhood, which is exactly the
    confusion Karen is trying to clear up, so it is split here.
    """
    polys = [(shape(g), g) for g in lots_geoms]
    polys = [(p, g) for p, g in polys if not p.is_empty]
    if not polys:
        return {}
    tract, tract_geom = max(polys, key=lambda t: t[0].area)
    cottages = [g for p, g in polys if acres(p) * 4046.86 <= COTTAGE_MAX_M2]
    hull = unary_union([shape(g) for g in cottages]).convex_hull if cottages else None
    return {
        "tract": tract_geom,
        "tract_acres": round(acres(tract), 1),
        "cottage_lots": cottages,
        "cottage_count": len(cottages),
        "cottage_hull": mapping(hull) if hull is not None and not hull.is_empty else None,
        "cottage_centroid": [hull.centroid.x, hull.centroid.y] if hull is not None else None,
    }


def reconcile_ponds(ponds: list, homesites: list, tol: float = 0.02,
                    drop_at: float = 0.85, max_shift_m: float = 15.0):
    """Settle pond geometry against the recorded homesites, which outrank it.

    Ponds are measured off a builder's rendering; homesites are recorded plats.
    Where the two disagree the plat wins, and there are two quite different
    kinds of disagreement:

    a blob sitting almost entirely on homesites is not a pond at all - it is
    lot ink the colour mask misread - so it is dropped rather than moved;

    a pond clipping the edge of a lot row is a real pond a few metres out of
    register, so it is nudged to the offset that clears the houses, which keeps
    its shape instead of gnawing a bite out of it.

    The nudge is capped at the georeference's own measured error (the fit's 90th
    percentile local residual is about 12 m). Moving further than the error bar
    would not be correcting registration, it would be inventing a position -
    so anything still overlapping after a bounded nudge is trimmed instead.

    Between them these take the total pond-on-house overlap from roughly
    93,000 square metres to zero. Fourteen ponds still *touch* a homesite
    boundary after trimming, which is what a retention pond behind a lot row
    actually does; none of them overlap one.
    """
    from shapely.affinity import translate
    from shapely.strtree import STRtree

    if not ponds or not homesites:
        return ponds, {"kept": len(ponds), "nudged": 0, "trimmed": 0, "dropped": 0}

    tree = STRtree(homesites)

    def overlap(poly):
        a = 0.0
        for j in tree.query(poly):
            try:
                a += poly.intersection(homesites[j]).area
            except Exception:
                pass
        return a

    def trim(poly):
        """Cut any recorded homesite back out of a pond."""
        for j in tree.query(poly):
            try:
                poly = poly.difference(homesites[j])
            except Exception:
                pass
        if poly.geom_type == "MultiPolygon" and not poly.is_empty:
            poly = max(poly.geoms, key=lambda g: g.area)
        return poly

    dx_deg = 1.0 / M_PER_DEG_LON
    dy_deg = 1.0 / M_PER_DEG_LAT
    stats = {"kept": 0, "nudged": 0, "trimmed": 0, "dropped": 0}
    shifts = []
    out = []

    for p in ponds:
        if not p.is_valid:
            p = p.buffer(0)
        if p.is_empty:
            continue
        frac = overlap(p) / p.area if p.area else 0.0
        if frac <= tol:
            # Below the tolerance a pond is not worth moving, but a sliver of
            # it may still sit on a house, and that is never acceptable.
            stats["kept"] += 1
            out.append(trim(p) if frac > 0 else p)
            continue
        if frac >= drop_at:
            stats["dropped"] += 1
            continue

        # Prefer the smallest shift that clears the houses, not the globally
        # lowest overlap. Chasing the global minimum walks the pond tens of
        # metres to shave a fraction of a percent, which is a bigger lie than
        # the error it fixes.
        best, best_frac, best_d = p, frac, 0.0
        for radius in range(3, int(max_shift_m) + 1, 3):
            cand_best, cand_frac = None, best_frac
            for k in range(16):
                ang = 2 * math.pi * k / 16
                cand = translate(p, radius * math.cos(ang) * dx_deg,
                                 radius * math.sin(ang) * dy_deg)
                f = overlap(cand) / cand.area if cand.area else 1.0
                if f < cand_frac - 1e-9:
                    cand_best, cand_frac = cand, f
            if cand_best is not None:
                best, best_frac, best_d = cand_best, cand_frac, float(radius)
            if best_frac <= tol:
                break

        if best_d:
            stats["nudged"] += 1
            shifts.append(best_d)

        # Always take the final trim, even for the slivers left inside `tol`.
        # The tolerance decides whether a pond is worth *moving*; it should not
        # decide whether a pond is allowed to sit on a house. Leaving a 2%
        # overlap in place would make the invariant a slogan rather than a fact.
        residual = overlap(best)
        if residual > 0:
            best = trim(best)
            if residual / p.area > tol:
                stats["trimmed"] += 1
        if best.is_empty or best.area < 0.25 * p.area:
            stats["dropped"] += 1
            continue
        out.append(best)

    if shifts:
        stats["median_shift_m"] = round(sorted(shifts)[len(shifts) // 2], 1)
    return out, stats


def load_ponds(footprint=None, homesites=None, buffer_m: float = 150.0) -> list[dict]:
    """Pond outlines measured off Minto's site plan, if they have been built.

    The county's hydrology layers return a single feature across the whole
    community, so the ponds have to come from somewhere else; see
    extract_plan_features.py for how they are georeferenced and checked.

    The builder's sheet covers more than the recorded plats, so ponds are kept
    only where they touch the platted footprint.  Otherwise the map sprouts
    water in Area 2 and on neighbouring land, which we are not describing.
    """
    path = DATA / "plan_water.geojson"
    if not path.exists():
        print("  no plan_water.geojson - run extract_plan_features.py water")
        return []
    fc = json.loads(path.read_text(encoding="utf-8"))
    ponds = [f for f in fc["features"] if f["properties"].get("kind") == "pond"]
    kept = ponds
    if footprint is not None:
        near = footprint.buffer(buffer_m / M_PER_DEG_LON)
        kept = [f for f in ponds if near.intersects(shape(f["geometry"]))]
    print(f"  {len(kept)} of {len(ponds)} ponds inside the community "
          f"(fit residual {fc.get('fit', {}).get('median_residual_m', '?')} m)")

    # Simplify before reconciling, not after: shaving a vertex by up to a metre
    # can push a trimmed edge back over a lot line, which would leave slivers
    # of pond on top of houses and quietly break the invariant this is for.
    geoms = [shape(simplify(f["geometry"], 0.000008)) for f in kept]
    if homesites:
        geoms, stats = reconcile_ponds(geoms, homesites)
        print("  vs recorded homesites: " + ", ".join(f"{k} {v}" for k, v in stats.items()))
    return [mapping(g) for g in geoms]


def load_cfg(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


TOWN_CENTER_PLAT = "5A3"
TOWN_CENTER_LABEL = "Town Center"
COTTAGES_LABEL = "Stay & Play Cottages"

# A homesite is a few hundred square metres; anything far larger inside a plat
# is a tract - stormwater, preserve, right-of-way, or the amenity parcel itself.
COTTAGE_MAX_M2 = 1500.0


def phase_label(subdivid: str) -> str:
    """'LATITUDE AT WATERSOUND AREA 1 PHASE  6B & 6C' -> 'Phase 6B & 6C'.

    The plat recorded as 'PH 5A3' is the exception, and it is why buyers are
    told there is no Phase 5A to buy in: 48 of its 62 acres are the single
    tract that holds the Town Center, and its only homesites are the Stay &
    Play cottages.  Calling it 'Phase 5A3' on the map would invent a
    neighbourhood that does not exist, so it carries its real name and keeps
    its plat citation.
    """
    tail = subdivid.upper().split("AREA 1", 1)[-1]
    tail = re.sub(r"\bPHASE\b|\bPH\b", " ", tail)
    body = " ".join(tail.split())
    if body == TOWN_CENTER_PLAT:
        return TOWN_CENTER_LABEL
    return "Phase " + body


def is_phase(label: str) -> bool:
    return label.startswith("Phase ")


def sort_key(label: str) -> tuple:
    if not is_phase(label):
        return (98, label)
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

    print("town center")
    tc = split_town_center(lots_by_phase.get(TOWN_CENTER_LABEL, []))
    if tc:
        print(f"  amenity tract {tc['tract_acres']} acres · "
              f"{tc['cottage_count']} {COTTAGES_LABEL.lower()}")
    # The plat's parcel count includes the amenity tract itself and a second
    # common-area tract. Neither is a homesite, and reporting them as such puts
    # two houses on the map that do not exist.
    tc_homesites = tc.get("cottage_count") if tc else None

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
                "short": lab.replace("Phase ", "Ph ") if is_phase(lab) else lab,
                "kind": "phase" if is_phase(lab) else "town_center",
                "subdivid": pr["SUBDIVID"],
                "plat": f"PB {pr['PLATTBOOK']}/{pr['BOOKPAGE']}",
                "plat_book": pr["PLATTBOOK"],
                "plat_page": pr["BOOKPAGE"],
                "acres": round(acres(geom), 1),
                "lot_count": (tc_homesites if lab == TOWN_CENTER_LABEL and tc_homesites is not None
                              else len(lots_by_phase[lab])),
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
        kind = "homesites" if p["kind"] == "phase" else "cottages"
        print(f"  {lab:<15}{p['plat']:<10}{p['acres']:>7.1f} ac{p['lot_count']:>5} {kind:<10}"
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

    print("ponds")
    footprint = unary_union([shape(p["geometry"]) for p in phases])
    # Only true homesites arbitrate. A pond legitimately sits inside a
    # common-area tract, so testing against every parcel would reject the
    # ponds for being exactly where ponds belong.
    homesites = []
    for lab, geoms in lots_by_phase.items():
        for g in geoms:
            s = shape(g)
            if not s.is_valid:
                s = s.buffer(0)
            if not s.is_empty and acres(s) * SQ_M_PER_ACRE <= COTTAGE_MAX_M2:
                homesites.append(s)
    ponds = load_ponds(footprint, homesites)

    # Ten phases, but fifteen residential plats: Phase 3 was recorded as 3A,
    # 3B & 3C and 3D, Phase 4 as 4A and 4B, and so on.  Both numbers are true
    # and they get confused constantly, so both are carried explicitly.
    phase_numbers = {re.match(r"Phase (\d+)", p["label"]).group(1)
                     for p in phases if p["kind"] == "phase"}
    homesites = sum(p["lot_count"] for p in phases)

    footprint = unary_union([shape(p["geometry"]) for p in phases])
    out = {
        "generated_from": "Bay County FL public GIS (recorded plats, lots, roads, addresses, hydrology)",        "reference_lat": REF_LAT,
        "bounds": list(footprint.bounds),
        "total_acres": round(acres(footprint), 1),
        "total_lots": homesites,
        "phase_count": len(phase_numbers),
        "residential_plat_count": sum(1 for p in phases if p["kind"] == "phase"),
        "plat_count": len(phases),
        "phases": phases,
        "lots_by_phase": lots_by_phase,
        "town_center": {
            "label": TOWN_CENTER_LABEL,
            "cottages_label": COTTAGES_LABEL,
            "plat": next((p["plat"] for p in phases if p["label"] == TOWN_CENTER_LABEL), None),
            "tract": tc.get("tract"),
            "tract_acres": tc.get("tract_acres"),
            "cottage_lots": tc.get("cottage_lots", []),
            "cottage_count": tc.get("cottage_count", 0),
            "cottage_hull": tc.get("cottage_hull"),
            "cottage_centroid": tc.get("cottage_centroid"),
        },
        "ponds": ponds,
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
    print(f"\n{out['phase_count']} phases across {out['residential_plat_count']} plats, "
          f"plus the Town Center = {out['plat_count']} recorded plats · "
          f"{out['total_lots']:,} platted homesites · {out['total_acres']:,.0f} acres "
          f"-> data/features.json ({path.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
