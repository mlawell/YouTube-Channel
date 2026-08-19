"""Download the public-record source data the Latitude phase map is built from.

Everything here is Bay County FL open GIS. No third-party basemap, no imagery, and
nothing read out of a developer site plan — those are transcribed by hand into
`street_index.json` / `landmarks.json` instead, so this script stays reproducible.

  Property/MapServer/2          recorded subdivision plats -> phase outlines + plat book/page
  Property/MapServer/0          subdivision lots           -> lot outlines + county LOTID
  Basic_Layers/MapServer/2      road centerlines w/ names  -> street names (Phases 1-3 only)
  Basic_Layers/MapServer/1      highways                   -> Hwy 79 / Hwy 388 corridor
  Basic_Layers/MapServer/0      address points             -> street names (Phases 1-3 only)
  TEST_Parcels/MapServer/1      parcel SITE ADDRESSES ONLY -> street names for Phases 4B-10
  PhysicalTopography/1, /2      creeks, waterbodies        -> Intracoastal + ponds

Note on parcels: only OBJECTID / DSITEADDR / ASTNAME are requested. Owner names and
sale history are deliberately NOT downloaded — this map is about active for-sale
inventory, which comes from Karen's own listings, not from county sale records.

Run:
    python tools/map/fetch_data.py
    python tools/map/fetch_data.py --only phases lots
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"

PROPERTY = "https://gis.baycountyfl.gov/arcgis/rest/services/Property/MapServer"
BASIC = "https://gis.baycountyfl.gov/arcgis/rest/services/Basic_Layers/MapServer"
TOPO = "https://gis.baycountyfl.gov/arcgis/rest/services/PhysicalTopography/MapServer"
PARCELS = "https://gis.baycountyfl.gov/arcgis/rest/services/TEST_Parcels/MapServer/1"

SUBDIVISION_LIKE = "%LATITUDE AT WATERSOUND%"

# Padded past the recorded plats so Hwy 79 and the Intracoastal read as context.
BBOX = (-85.9200, 30.2900, -85.8400, 30.3560)

UA = {"User-Agent": "nwfl-beach-homes-phase-map/1.0 (Karen@nwflbeachhomes.com)"}
PAGE = 400
TIMEOUT = 240


class ArcGisError(RuntimeError):
    """The service answered HTTP 200 with an error payload."""


def _post(url: str, params: dict) -> dict:
    # POST, not GET: objectId batches blow past the server's URL length cap.
    r = requests.post(url, data=params, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    out = r.json()
    if "error" in out:
        raise ArcGisError(out["error"].get("message", "query failed"))
    return out


def _envelope() -> dict:
    minlon, minlat, maxlon, maxlat = BBOX
    return {
        "geometry": f"{minlon},{minlat},{maxlon},{maxlat}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
    }


def _by_ids(url: str, fields: str) -> dict:
    """Fetch every feature in the bbox.

    These services cap each response and reject `resultOffset` paging, so object
    ids are pulled first and geometry is fetched in explicit id batches. A batch
    the server rejects gets bisected, so one bad record can't lose 400 good ones.
    """
    ids = _post(url, {"where": "1=1", "returnIdsOnly": "true", "f": "json", **_envelope()})
    ids = ids.get("objectIds") or []
    print(f"    {len(ids)} object ids")

    features: list[dict] = []
    dropped: list[int] = []

    def pull(batch: list[int]) -> None:
        try:
            page = _post(
                url,
                {
                    "objectIds": ",".join(str(x) for x in batch),
                    "outFields": fields,
                    "returnGeometry": "true",
                    "outSR": 4326,
                    "f": "geojson",
                },
            )
        except ArcGisError:
            if len(batch) == 1:
                dropped.append(batch[0])
                return
            mid = len(batch) // 2
            pull(batch[:mid])
            pull(batch[mid:])
            return
        features.extend(page.get("features", []))

    for i in range(0, len(ids), PAGE):
        pull(ids[i : i + PAGE])
        time.sleep(0.3)

    print(f"    {len(features)} fetched" + (f", {len(dropped)} rejected: {dropped}" if dropped else ""))
    return {"type": "FeatureCollection", "features": features}


def fetch_phases() -> dict:
    out = _post(
        f"{PROPERTY}/2/query",
        {
            "where": f"SUBDIVID LIKE '{SUBDIVISION_LIKE}'",
            "outFields": "SUBDIVID,PLATTBOOK,BOOKPAGE",
            "returnGeometry": "true",
            "outSR": 4326,
            "f": "geojson",
        },
    )
    print(f"    {len(out['features'])} recorded plats")
    return out


# The lot layer has no subdivision key, so lots come back by envelope and are
# attributed to a recorded phase by point-in-polygon in build_features.py.
def fetch_lots() -> dict:
    return _by_ids(f"{PROPERTY}/0/query", "OBJECTID,LOTID")


def fetch_roads() -> dict:
    return _by_ids(f"{BASIC}/2/query", "OBJECTID,FULL_NAME,NAME,CLASS,STRTE,OWNER")


def fetch_highways() -> dict:
    return _by_ids(f"{BASIC}/1/query", "OBJECTID,FULL_NAME,NAME,CLASS,STRTE,OWNER")


def fetch_addresses() -> dict:
    return _by_ids(f"{BASIC}/0/query", "OBJECTID,ADDRESS,ST_NAME,ST_TYPE,RESIDENTIAL")


def fetch_street_points() -> dict:
    return _by_ids(f"{PARCELS}/query", "OBJECTID,DSITEADDR,ASTNAME")


def fetch_waterbodies() -> dict:
    return _by_ids(f"{TOPO}/2/query", "OBJECTID")


def fetch_creeks() -> dict:
    return _by_ids(f"{TOPO}/1/query", "OBJECTID")


JOBS = {
    "phases": ("phases.geojson", fetch_phases),
    "lots": ("lots.geojson", fetch_lots),
    "roads": ("roads.geojson", fetch_roads),
    "highways": ("highways.geojson", fetch_highways),
    "addresses": ("addresses.geojson", fetch_addresses),
    "streetpoints": ("street_points.geojson", fetch_street_points),
    "waterbodies": ("waterbodies.geojson", fetch_waterbodies),
    "creeks": ("creeks.geojson", fetch_creeks),
}


def write(name: str, payload: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    print(f"    -> data/{name} ({path.stat().st_size / 1024:.0f} KB)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="+", choices=sorted(JOBS), help="run a subset")
    args = ap.parse_args()

    for key in args.only or list(JOBS):
        name, fn = JOBS[key]
        print(key)
        write(name, fn())

    print("\ndone. Next: python tools/map/build_features.py")


if __name__ == "__main__":
    main()
