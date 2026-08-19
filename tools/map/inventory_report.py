"""Record-day inventory snapshot.

Availability is not a map attribute. Karen's own framing:

    "when we talk about it we'll say, as of this moment there are x number of
     resales listed and x number of lots, but that will certainly change in
     the next 5 minutes."

So live inventory is never printed on the map. It is spoken, dated, and handed
off to a conversation -- which is the whole call to action. This script turns
Karen's BoldTrail export into a block she can read straight off the screen on
record day, and writes the same numbers into `phase_meta.json` so the script
prep and the spoken numbers cannot drift apart.

    python inventory_report.py --csv export.csv
    python inventory_report.py --csv export.csv --as-of 2026-08-19
    python inventory_report.py --csv export.csv --no-write   # print only

The CSV needs latitude/longitude columns; phase is assigned geometrically by
point-in-recorded-plat, exactly like phase_lookup.py. A `status` or `type`
column splits resales from new-build lots -- anything containing "lot",
"land", "vacant" or "homesite" counts as a lot, everything else as a resale.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from phase_lookup import LAT_KEYS, LON_KEYS, Lookup, pick

HERE = Path(__file__).parent
META = HERE / "phase_meta.json"

STATUS_KEYS = ("status", "listing_status", "mls_status")
TYPE_KEYS = ("type", "listing_type", "property_type", "listing_type_label", "propertysubtype")
LOT_WORDS = re.compile(r"\b(lot|land|vacant|homesite|home site|acreage)\b", re.I)
DATE_KEYS = ("as_of", "date", "export_date", "generated")


def is_lot(row: dict, type_col: str | None) -> bool:
    return bool(type_col and LOT_WORDS.search(str(row.get(type_col) or "")))


def is_active(row: dict, status_col: str | None) -> bool:
    """Default to counting the row; only exclude an explicit non-active status."""
    if not status_col:
        return True
    v = str(row.get(status_col) or "").strip().lower()
    if not v:
        return True
    return not any(w in v for w in ("sold", "closed", "expired", "withdrawn", "cancel"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True,
                    help="listings export with latitude/longitude columns")
    ap.add_argument("--as-of", help="snapshot date; defaults to a date column, else today")
    ap.add_argument("--no-write", action="store_true",
                    help="print the block but leave phase_meta.json alone")
    a = ap.parse_args()

    rows = list(csv.DictReader(a.csv.open(encoding="utf-8-sig")))
    if not rows:
        raise SystemExit(f"{a.csv} has no rows")

    lat_col, lon_col = pick(rows[0], LAT_KEYS), pick(rows[0], LON_KEYS)
    if not lat_col or not lon_col:
        raise SystemExit(
            f"could not find latitude/longitude columns in {a.csv}\n"
            f"  columns present: {', '.join(k for k in rows[0] if k)}"
        )
    status_col, type_col = pick(rows[0], STATUS_KEYS), pick(rows[0], TYPE_KEYS)
    date_col = pick(rows[0], DATE_KEYS)

    as_of = a.as_of or (str(rows[0].get(date_col) or "").strip() if date_col else "")
    as_of = as_of or date.today().isoformat()

    lk = Lookup()
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"resales_listed": 0, "new_lots": 0})
    skipped = outside = 0

    for r in rows:
        if not is_active(r, status_col):
            continue
        try:
            lat, lon = float(r[lat_col]), float(r[lon_col])
        except (TypeError, ValueError):
            skipped += 1
            continue
        p = lk.by_latlon(lat, lon)
        if not p:
            outside += 1
            continue
        key = "new_lots" if is_lot(r, type_col) else "resales_listed"
        counts[p["label"]][key] += 1

    print()
    print(f"AS OF {as_of}")
    print(f"{'':<15}{'resales':>9}{'new lots':>10}")
    tot_r = tot_l = 0
    for p in lk.phases:
        c = counts.get(p["label"], {"resales_listed": 0, "new_lots": 0})
        tot_r += c["resales_listed"]
        tot_l += c["new_lots"]
        print(f"{p['label']:<15}{c['resales_listed']:>9}{c['new_lots']:>10}")
    print(f"{'TOTAL':<15}{tot_r:>9}{tot_l:>10}")
    print()
    print("Read it as: \"As I'm recording this, in "
          f"{date.fromisoformat(as_of).strftime('%B %Y')}, Phase X has N resales")
    print("listed and N new lots. By the time you watch this that will be")
    print("different -- message me and I'll send you today's actual list.\"")
    print()
    if skipped:
        print(f"  {skipped} rows had no usable coordinate")
    if outside:
        print(f"  {outside} rows fell outside every recorded plat (not in LMWS)")
    if not status_col:
        print("  no status column found -- every row was counted as active")
    if not type_col:
        print("  no type column found -- every row was counted as a resale")

    if a.no_write:
        return

    meta = json.loads(META.read_text(encoding="utf-8"))
    for label, m in meta.get("phases", {}).items():
        c = counts.get(label, {"resales_listed": 0, "new_lots": 0})
        m["inventory_snapshot"] = {"as_of": as_of, **c}
        m.pop("availability", None)
        m.pop("confirmed", None)
        m.pop("availability_basis", None)
    META.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  wrote the snapshot into {META.name}")


if __name__ == "__main__":
    main()
