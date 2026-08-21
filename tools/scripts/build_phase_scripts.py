"""Build one script draft per phase, from public record.

Karen: "lets start working on the script to go through each of the phases, we
need a good detailed YouTube video about the phase, including how long on a golf
cart going 30 will take, resident feedback, etc."

She said "a good detailed video about THE PHASE", singular, so this builds a
SERIES -- one video per phase number, not another single video. The existing
19-22 minute flagship stays as the hub and gives each phase about 30 seconds,
which is nowhere near enough to hold a cart time and resident feedback.

Ten videos, one per phase number, with the sub-plats grouped:

    Phase 3 = 3A + 3B & 3C + 3D          Phase 5 = 5B + 5C  (and the 5A story)
    Phase 4 = 4A + 4B                    Phase 6 = 6A + 6B & 6C

That grouping is not a convenience -- it is the correction the flagship leads
with. "Phase 3" is three separate recorded plats, and a video called Phase 3
that shows all three makes the argument rather than asserting it.

WHAT THIS TOOL WILL NOT DO
--------------------------
Two of the things Karen asked for cannot be derived from public record, and this
tool writes neither:

* THE GOLF CART TIME. It cannot be computed. County road centrelines cover only
  Phases 1, 2, 3A, 3B & 3C and 3D; ten of the sixteen plats have no interior
  centreline at all, and only 12% of the road network connects to the Town
  Center -- most phases sit 1-5 km from any routable road, Phase 10 nearly 5 km.
  So there is no street-following distance to be had. What goes in the draft is
  the straight-line FLOOR at 30 mph, clearly labelled as a floor, plus a gate
  for the time Karen measures by driving it. She lives there; the drive sheet
  this tool also writes is how that gets captured.

* RESIDENT FEEDBACK. There is no resident feedback in this repository. Not a
  little, none. So the draft carries a gate and a prompt, never a sentence.
  Inventing a neighbour's opinion would be the worst thing this channel could
  do, and it is exactly the sort of thing that happens by accident when a
  template wants filling.

Everything else in the draft is public record, printed with its plat book and
page so a viewer can check it.

Run:
    python tools/scripts/build_phase_scripts.py
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FEATURES = ROOT / "tools" / "map" / "data" / "features.json"
OUT = ROOT / "platforms" / "youtube" / "content" / "phase-deep-dives"

MI_PER_M = 1 / 1609.344
CART_MPH = 30.0          # Karen's number, taken literally

PHASE_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


def load() -> dict:
    return json.loads(FEATURES.read_text(encoding="utf-8"))


def phase_number(label: str) -> str | None:
    """'Phase 3B & 3C' -> '3'. The Town Center is not a phase and returns None."""
    m = re.match(r"Phase (\d+)", label)
    return m.group(1) if m else None


def frame_slug(label: str) -> str:
    return (label.lower().replace("phase ", "phase-")
            .replace(" & ", "-").replace(" ", ""))


def merc(lon: float, lat: float) -> tuple[float, float]:
    R = 6378137.0
    return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def ground_mi(a, b, lat_deg: float) -> float:
    """Ground miles between two Web Mercator points.

    Mercator inflates distance by 1/cos(lat); undo it, or every number here is
    about 15% too large at this latitude.
    """
    return math.hypot(a[0] - b[0], a[1] - b[1]) * math.cos(math.radians(lat_deg)) * MI_PER_M


def quarter_mi(miles: float) -> float:
    """Round to the nearest quarter mile. Karen's call, and the honest precision.

    Every distance here is a straight line from a phase CENTROID, and a phase is
    not a point -- the second decimal was never real. Printing "1.79 mi" claims a
    survey. Quarter-mile buckets also absorb the small differences that come from
    measuring against slightly different geometry, so the map and these scripts
    cannot drift apart over a rounding choice.

    Kept identical to `render_map.fmt_miles` on purpose: one claim, one number,
    wherever it appears.
    """
    return round(miles * 4) / 4


def fmt_miles(miles: float) -> str:
    """A quarter-rounded distance, written the way it is said."""
    q = quarter_mi(miles)
    if q <= 0:
        return "under \u00bc mile"
    whole, frac = int(q), q - int(q)
    glyph = {0.0: "", 0.25: "\u00bc", 0.5: "\u00bd", 0.75: "\u00be"}[round(frac, 2)]
    unit = "mile" if q == 1 else "miles"
    if whole and glyph:
        return f"{whole}{glyph} {unit}"
    if whole:
        return f"{whole} {unit}"
    return f"{glyph} mile"


def miles_num(miles: float) -> str:
    """Just the quantity, no unit -- for building ranges."""
    q = quarter_mi(miles)
    if q <= 0:
        return "0"
    whole, frac = int(q), round(q - int(q), 2)
    glyph = {0.0: "", 0.25: "\u00bc", 0.5: "\u00bd", 0.75: "\u00be"}[frac]
    return f"{whole}{glyph}" if whole else glyph


def fmt_miles_range(a: float, b: float) -> str:
    """A quarter-rounded range with the unit said once: '1/4-3/4 mile'."""
    if quarter_mi(a) == quarter_mi(b):
        return fmt_miles(a)
    unit = "miles" if quarter_mi(b) > 1 else "mile"
    return f"{miles_num(a)}\u2013{miles_num(b)} {unit}"


def spoken_miles(miles: float) -> str:
    """The same distance as words, for reading aloud."""
    q = quarter_mi(miles)
    if q <= 0:
        return "under a quarter of a mile"
    whole, frac = int(q), round(q - int(q), 2)
    words = {0.0: "", 0.25: "a quarter", 0.5: "a half", 0.75: "three quarters"}[frac]
    if whole and frac:
        return f"{spoken(whole)} and {words.replace('a ', '')} miles"
    if whole:
        return f"{spoken(whole)} mile" + ("" if whole == 1 else "s")
    return f"{words} of a mile"


def fmt_range(r) -> str:
    """House numbers, printed the way they appear on a mailbox.

    No thousands separator: the number on the house is 8401, never "8,401".
    A single-value range is not a range -- several parcels share one number,
    usually a shared entrance -- so it is said that way instead.
    """
    if not r:
        return "\u2014"
    if r[0] == r[1]:
        return f"{r[0]} (one shared number)"
    return f"{r[0]}\u2013{r[1]}"


def spoken(n: int) -> str:
    """Numbers get read aloud, so give Karen the words as well as the digits."""
    ones = ["zero", "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
            "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
            "eighty", "ninety"]

    def u1000(v: int) -> str:
        if v < 20:
            return ones[v]
        if v < 100:
            return tens[v // 10] + ("-" + ones[v % 10] if v % 10 else "")
        return ones[v // 100] + " hundred" + (" and " + u1000(v % 100) if v % 100 else "")

    if n < 1000:
        return u1000(n)
    return u1000(n // 1000) + " thousand" + (" " + u1000(n % 1000) if n % 1000 else "")


class Community:
    """Everything the drafts need, measured once."""

    def __init__(self, d: dict):
        self.d = d
        self.phases = [p for p in d["phases"] if phase_number(p["label"])]
        self.tc = next((p for p in d["phases"] if p["label"] == "Town Center"), None)
        self.landmarks = {l["name"]: l for l in d.get("landmarks", [])}
        self.groups: dict[str, list[dict]] = {}
        for p in self.phases:
            self.groups.setdefault(phase_number(p["label"]), []).append(p)

        # The reveal frames are numbered by their position in features.json --
        # render_sequence does `for i, p in enumerate(s.phases, 1)` -- so the
        # filename is derived here the same way rather than guessed. Guessing is
        # how the flagship script ended up citing 14_phase-8 for a file that is
        # actually 13_phase-8.
        self.frame_name = {
            p["label"]: f"{i:02d}_{frame_slug(p['label'])}"
            for i, p in enumerate(d["phases"], 1)
        }

        tsa = self.landmarks.get("Town Square Amenity")
        self.tc_xy = merc(tsa["lon"], tsa["lat"]) if tsa else None
        # The Bandshell is that same confirmed pin -- it is labelled "Bandshell"
        # on the map and "Town Square Amenity" in the data.
        self.bandshell_xy = self.tc_xy
        self.hwy79 = [h for h in d.get("highways", [])
                      if (h.get("name") or "") == "Highway 79"]

    def centroid_xy(self, p: dict):
        lon, lat = p["centroid"]
        return merc(lon, lat), lat

    def to_town_center_mi(self, p: dict) -> float | None:
        if not self.tc_xy:
            return None
        xy, lat = self.centroid_xy(p)
        return ground_mi(xy, self.tc_xy, lat)

    def to_hwy79_mi(self, p: dict) -> float | None:
        """Nearest approach from the phase centroid to the Highway 79 centreline.

        This is the number behind Karen's road-noise point, so it is measured to
        the road itself rather than to some point on it.
        """
        if not self.hwy79:
            return None
        (cx, cy), lat = self.centroid_xy(p)
        best = None
        for h in self.hwy79:
            pts = [merc(x, y) for x, y in h["geometry"]["coordinates"]]
            for a, b in zip(pts, pts[1:]):
                dx, dy = b[0] - a[0], b[1] - a[1]
                L = dx * dx + dy * dy
                t = 0.0 if L == 0 else max(0.0, min(1.0, ((cx - a[0]) * dx + (cy - a[1]) * dy) / L))
                qx, qy = a[0] + t * dx, a[1] + t * dy
                d = math.hypot(cx - qx, cy - qy)
                if best is None or d < best:
                    best = d
        return best * math.cos(math.radians(lat)) * MI_PER_M

    def group_stats(self, num: str) -> dict:
        ps = self.groups[num]
        lots = sum(p["lot_count"] for p in ps)
        acres = sum(p["acres"] for p in ps)
        d_tc = [x for x in (self.to_town_center_mi(p) for p in ps) if x is not None]
        d79 = [x for x in (self.to_hwy79_mi(p) for p in ps) if x is not None]
        streets: dict[str, list] = {}
        for p in ps:
            for st in p.get("streets", []):
                # A street with neither an address range nor an addressed parcel
                # carries no information -- "Highway 79" turns up in Phase 3 this
                # way, off a single county address point, and reading it out as a
                # street in the neighbourhood would be plainly wrong.
                if not st.get("address_range") and not st.get("addressed_parcels"):
                    continue
                streets.setdefault(st["name"], []).append(
                    (p["label"], st.get("address_range"), st.get("addressed_parcels") or 0))
        return {
            "plats": ps,
            "lots": lots,
            "acres": acres,
            "nearest_mi": min(d_tc) if d_tc else None,
            "farthest_mi": max(d_tc) if d_tc else None,
            "hwy79_mi": min(d79) if d79 else None,
            "streets": streets,
            "karen_lives_here": any(p.get("karen_lives_here") for p in ps),
        }


def cart_floor_min(miles: float) -> float:
    """The fastest a 30 mph cart could possibly do it: the straight line.

    Computed from the QUARTER-ROUNDED distance, not the raw one, so that the two
    numbers on screen agree with each other. If the card says 1 3/4 miles and a
    viewer divides by 30, they should get the minutes we printed -- showing
    1.79 mi worth of minutes beside a 1 3/4 mi caption is the kind of small
    inconsistency that makes someone doubt the rest.
    """
    return quarter_mi(miles) / CART_MPH * 60.0


def draft(c: Community, num: str) -> str:
    g = c.group_stats(num)
    plats = g["plats"]
    multi = len(plats) > 1
    L: list[str] = []
    add = L.append

    title = f"Phase {num}"
    add(f"# Script \u2014 {title}, Latitude Margaritaville Watersound")
    add("")
    add(f"**Series:** Phase Deep Dives \u00b7 episode {PHASE_ORDER.index(num) + 1} of "
        f"{len(PHASE_ORDER)}")
    add("**Channel:** Living in Latitude Margaritaville Watersound "
        "(`@LivingMargaritavillewithKaren`)")
    add("**Target runtime:** 8\u201312 minutes")
    add("**Status:** DRAFT \u2014 generated from public record. Not recordable until "
        "every `[KAREN]` gate below is filled.")
    add("")
    add("> Generated by `tools/scripts/build_phase_scripts.py` from "
        "`tools/map/data/features.json`. Re-run it after any data refresh; do not "
        "hand-edit the FACTS block, it will be overwritten. Spoken copy and "
        "Karen's answers live in the sections marked to keep.")
    add("")

    # ---- the facts, all checkable -------------------------------------------
    add("## FACTS \u2014 public record (regenerated, do not hand-edit)")
    add("")
    if multi:
        add(f"Phase {num} is **{len(plats)} separately recorded plats**, not one:")
        add("")
        add("| Plat | Recorded | Homesites | Acres | Map frame |")
        add("| --- | --- | --- | --- | --- |")
        for p in plats:
            add(f"| {p['label']} | {p['plat']} | {p['lot_count']:,} | "
                f"{p['acres']:,.1f} | `{c.frame_name[p['label']]}` |")
        add("")
        # One decimal place, because at zero the parts stop adding up to the
        # total on screen -- 91.5 + 95.7 + 24.8 rounds to 92 + 96 + 25 = 213
        # against a true 212, and a viewer doing the sum is a viewer who stops
        # trusting the rest of it.
        add(f"**Together: {g['lots']:,} homesites across {g['acres']:,.1f} acres.**")
    else:
        p = plats[0]
        add("| Field | Value |")
        add("| --- | --- |")
        add(f"| Recorded plat | **{p['plat']}** |")
        add(f"| Homesites | {p['lot_count']:,} |")
        add(f"| Acres | {p['acres']:,.1f} |")
        add(f"| Map frame | `{c.frame_name[p['label']]}` |")
    add("")

    # distance + the cart question
    near, far = g["nearest_mi"], g["farthest_mi"]
    add("### How far it is")
    add("")
    add("| Measure | Value |")
    add("| --- | --- |")
    if near is not None:
        if multi and far and quarter_mi(far) != quarter_mi(near):
            add(f"| Straight line to the Town Center | {fmt_miles_range(near, far)} "
                f"(varies by plat) |")
            add(f"| Cart floor at {CART_MPH:.0f} mph | "
                f"{cart_floor_min(near):.1f}\u2013{cart_floor_min(far):.1f} min |")
        else:
            add(f"| Straight line to the Town Center | {fmt_miles(near)} |")
            add(f"| Cart floor at {CART_MPH:.0f} mph | {cart_floor_min(near):.1f} min |")
    if g["hwy79_mi"] is not None:
        add(f"| Straight line to Highway 79 | {fmt_miles(g['hwy79_mi'])} |")
    add("")
    add("Distances are straight lines from the middle of the phase, **rounded to "
        "the nearest quarter mile** \u2014 a phase is not a point, so a second decimal "
        "would be claiming a survey.")
    add("")
    add("**The cart floor is a floor, not a drive time.** It is the straight "
        "line, so no cart can beat it. County road centrelines cover only "
        "Phases 1, 2, 3A, 3B & 3C and 3D \u2014 ten of the sixteen plats have none, "
        "and only 12% of the road network connects to the Town Center \u2014 so a "
        "street-following time cannot be calculated from public record. It has "
        "to be driven.")
    add("")

    # streets
    add("### Streets and county address ranges")
    add("")
    add("Biggest first \u2014 the ones with the most addressed parcels are the "
        "streets worth naming on camera.")
    add("")
    add("| Street | County house numbers | Addressed parcels |")
    add("| --- | --- | --- |")
    ordered = sorted(g["streets"].items(),
                     key=lambda kv: -sum(n for _, _, n in kv[1]))
    for name, entries in ordered:
        rs = [fmt_range(r) for _, r, _ in entries if r]
        shown = " \u00b7 ".join(dict.fromkeys(rs)) if rs else "\u2014"
        total = sum(n for _, _, n in entries)
        if multi and len({lab for lab, _, _ in entries}) > 1:
            where = ", ".join(sorted({lab.replace("Phase ", "") for lab, _, _ in entries}))
            add(f"| {name} *(in {where})* | {shown} | {total} |")
        else:
            add(f"| {name} | {shown} | {total} |")
    add("")
    lot_runs = []
    for p in plats:
        for r in (p.get("lot_number_runs") or []):
            lot_runs.append(f"{p['label']}: {fmt_range(r)}")
    if lot_runs:
        add(f"Minto lot numbers \u2014 **{'; '.join(lot_runs)}**. Say on camera that "
            "these are *not* addresses; the county house numbers above are what "
            "is on the mailbox.")
        add("")
    add("---")
    add("")
    add(_body(c, num, g))
    return "\n".join(L)


def _body(c: Community, num: str, g: dict) -> str:
    """The spoken draft.

    Verified facts are written as spoken lines. Everything that is not verified
    is a gate, never a sentence -- if Karen reads this cold, she should be
    unable to say anything untrue.
    """
    plats = g["plats"]
    multi = len(plats) > 1
    near, far = g["nearest_mi"], g["farthest_mi"]
    mine = g["karen_lives_here"]
    L: list[str] = []
    add = L.append

    add("## How to read this")
    add("")
    add("- `[FRAME nn_name]` \u2014 cut to that PNG from `tools/map/output/frames/`")
    add("- `[KAREN]` \u2014 Karen must supply or confirm this. Do not read it as-is.")
    add("- `[CART]` \u2014 the measured cart time from `drive-sheet.md`. Until that is "
        "filled in, this beat cannot be recorded.")
    add("- `[RESIDENT]` \u2014 a real quote from a real neighbour, captured on the "
        "drive sheet, used with permission. Never paraphrase one into existence.")
    add("- `[INVENTORY]` \u2014 today's snapshot, spoken and dated, from "
        "`inventory_report.py`.")
    add("- Spoken copy is the plain text. Brackets are direction.")
    add("")
    add("## Rules this script follows")
    add("")
    add("Same five as the flagship \u2014 no price-by-phase, inventory spoken and "
        "dated, plat book and page on screen, no invented amenities, lot numbers "
        "are never addresses \u2014 plus two this series adds:")
    add("")
    add("6. **No cart time that was not driven.** The straight-line floor may be "
        "shown on screen as a floor. A spoken \"it takes about N minutes\" must "
        "come from the stopwatch.")
    add("7. **No resident feedback that did not come from a resident.** If nobody "
        "has been asked yet, the section is cut, not filled.")
    add("")
    add("---")
    add("")

    # ---- cold open ----------------------------------------------------------
    add("## COLD OPEN \u2014 0:00\u20130:15")
    add("")
    if mine:
        add("`[KAREN on camera, on her own street]`")
        add("")
        add("> This is Phase 8. I'm not going to show you a site plan and guess \u2014 "
            "I live here. This is my street.")
    else:
        add(f"`[FRAME {c.frame_name[plats[0]['label']]}]`")
        add("")
        add(f"> This is Phase {num}. And by the end of this video you'll know "
            f"exactly where it is, what's in it, how long it takes to get to the "
            f"Town Center on a cart \u2014 because I timed it \u2014 and what the people "
            f"who actually live here say about it.")
    add("")
    if multi:
        add(f"> And the first thing to know is that Phase {num} isn't one "
            f"neighborhood. It's {spoken(len(plats))} separately recorded plats.")
        add("")

    # ---- where it is --------------------------------------------------------
    add("## WHERE IT IS \u2014 0:15\u20132:00")
    add("")
    for p in plats:
        add(f"`[FRAME {c.frame_name[p['label']]}]` \u00b7 `{p['plat']} \u00b7 "
            f"{p['lot_count']:,} homesites \u00b7 {p['acres']:,.0f} acres`")
        add("")
        add(f"> {p['label']} \u2014 plat book {p['plat_book']}, page {p['plat_page']}. "
            f"{spoken(p['lot_count']).capitalize()} homesites on "
            f"{p['acres']:,.0f} acres. `[KAREN: one sentence on where this sits "
            f"and what it feels like driving in.]`")
        add("")
    if multi:
        add(f"> Put together, that's **{g['lots']:,} homesites across "
            f"{g['acres']:,.0f} acres** \u2014 all of it Phase {num}, all of it on "
            f"separate plats you can look up.")
        add("")

    # ---- the cart run -------------------------------------------------------
    add("## THE CART RUN \u2014 2:00\u20134:00")
    add("")
    add("**Direction:** this is the segment nobody else has, and it only works "
        "if it is real. Film it in one take from the driveway to the Town "
        "Center, clock visible or timer overlaid. Say the speed out loud.")
    add("")
    add("`[B-ROLL: cart POV, start of run]`")
    add("")
    add(f"> So here's the question everybody actually asks: how far is it to the "
        f"Town Center? Let's just go. Thirty miles an hour, which is what these "
        f"carts do here.")
    add("")
    add("`[CART: measured time, from drive-sheet.md. Do NOT record this beat "
        "until it is driven.]`")
    add("")
    if near is not None:
        floor = cart_floor_min(near)
        if multi and far and quarter_mi(far) != quarter_mi(near):
            add(f"> `[ON SCREEN: straight line {fmt_miles_range(near, far)} \u00b7 "
                f"floor {floor:.1f}\u2013{cart_floor_min(far):.1f} min at 30 mph]`")
        else:
            add(f"> `[ON SCREEN: straight line {fmt_miles(near)} \u00b7 "
                f"floor {floor:.1f} min at 30 mph]`")
        add("")
        add(f"> Straight line it's about {spoken_miles(near)}, so it could never "
            f"be quicker than about {floor:.1f} minutes \u2014 and roads aren't "
            f"straight lines, so the real answer is `[CART]`.")
        add("")
    add("`[KAREN: and then the honest part \u2014 is that a walk, a cart trip, or do "
        "you take the car? Say which one you actually do.]`")
    add("")

    # ---- highway 79 / bandshell --------------------------------------------
    add("## NOISE AND CONVENIENCE \u2014 4:00\u20135:30")
    add("")
    if g["hwy79_mi"] is not None:
        d = g["hwy79_mi"]
        add(f"> Highway 79 is about **{spoken_miles(d)}** from the middle of this "
            f"phase in a straight line. `[ON SCREEN: {fmt_miles(d)} to Hwy 79]`")
        add("")
        if quarter_mi(d) <= 0.5:
            add("`[KAREN \u2014 first-hand: this is one of the close ones. Can you hear "
                "79 here? Say what it actually sounds like, and when.]`")
        else:
            add("`[KAREN \u2014 first-hand: this is one of the further ones. Is 79 a "
                "non-issue here?]`")
        add("")
    add("`[KAREN \u2014 first-hand: the Bandshell. Your own line is that a loud show "
        "carries for miles, so it is not how you pick a phase. Say whether you "
        "hear it here, and whether that is a plus or a minus for you. No "
        "distances, no radius \u2014 it varies too much.]`")
    add("")

    # ---- residents ----------------------------------------------------------
    add("## WHAT PEOPLE WHO LIVE HERE SAY \u2014 5:30\u20137:30")
    add("")
    add("**Direction:** this is the second thing no competitor can do, and it is "
        "empty until real people are asked. There is no resident feedback in "
        "this repository \u2014 none \u2014 so nothing is written here for Karen to read.")
    add("")
    add("`[RESIDENT 1: name or \"a neighbour on <street>\", with permission. Ask: "
        "why this phase over the others? What surprised you after you moved in?]`")
    add("")
    add("`[RESIDENT 2: ask for one honest trade-off. A phase with no downside is "
        "a phase nobody believes.]`")
    add("")
    add("`[KAREN: if nobody in this phase has been asked yet, CUT this section "
        "entirely and say so in the description. Do not summarise what you "
        "imagine they would say.]`")
    add("")

    # ---- Karen's own phase --------------------------------------------------
    if mine:
        add("## WHY I LIVE HERE \u2014 7:30\u20139:00")
        add("")
        add("`[CUT TO KAREN, walking her own street]`")
        add("")
        add("`[KAREN: this is the emotional centre of the whole series and the one "
            "thing that cannot be copied. Why you and your husband picked Phase 8 "
            "over the other nine. What the trip to the Bandshell is really like "
            "day to day. Whether you hear the music from your lanai. Speak from "
            "experience, not from notes.]`")
        add("")
        add("`[KAREN: one real trade-off about your own phase.]`")
        add("")
        add("`[B-ROLL: Karen's geotagged Phase 8 photo set]`")
        add("")

    # ---- availability -------------------------------------------------------
    add("## WHAT'S ACTUALLY FOR SALE \u2014 9:00\u201310:00")
    add("")
    add("`[INVENTORY]`")
    add("")
    add("> `[KAREN: say it dated \u2014 \"as I'm recording this, in [Month Year], "
        "Phase " + num + " has N resales listed and N new lots \u2014 by the time you "
        "watch this that will be different, message me and I'll send you today's "
        "actual list.\"]`")
    add("")
    add("**Never** imply this phase is priced differently from another. Price "
        "follows the model, the collection and the homesite premium.")
    add("")

    # ---- close --------------------------------------------------------------
    add("## CLOSE \u2014 10:00\u201310:45")
    add("")
    add("> If you want to see how this phase fits against the other nine, the "
        "full phase map video is linked below \u2014 every one of the sixteen "
        "recorded plats, with the book and page.")
    add("")
    add("> And if you want today's actual list for Phase " + num + ", message me. "
        "I live here.")
    add("")
    add("`[END SCREEN: flagship phase-map video + next phase in the series]`")
    add("")
    add("---")
    add("")
    add("## Production checklist")
    add("")
    add("- [ ] Cart run driven and timed, entered in `drive-sheet.md`")
    add("- [ ] At least one resident interviewed, with permission, or the "
        "section cut")
    add("- [ ] `[KAREN]` gates all answered")
    add("- [ ] `python tools/map/render_map.py --only sequence` run for fresh frames")
    add("- [ ] `python tools/map/inventory_report.py --csv <export>` run on record day")
    add("- [ ] Plat book/page on screen for every plat named")
    return "\n".join(L)


def drive_sheet(c: Community) -> str:
    """The sheet Karen takes in the cart.

    Both of the things she asked for that cannot be derived -- the cart time and
    the resident feedback -- get captured here, in one pass, on one page. The
    floor is printed beside each blank so a mistyped stopwatch is obvious: a
    measured time BELOW the floor is impossible and means something went wrong.
    """
    L: list[str] = []
    add = L.append
    add("# Drive sheet \u2014 cart times and resident feedback")
    add("")
    add("Generated by `tools/scripts/build_phase_scripts.py`. **This is the only "
        "source for the two things in the phase videos that are not public "
        "record.** Fill it in, then re-read the drafts.")
    add("")
    add("## How to run it")
    add("")
    add("1. Start at the phase, end at the Town Center. Same end point every "
        "time, or the numbers are not comparable.")
    add("2. Hold 30 mph where it is safe and legal \u2014 that is the number quoted "
        "on screen. If a phase cannot be driven at 30, write down what it can be "
        "driven at; that is itself worth saying.")
    add("3. Film it. A cart-POV run with a visible timer is the proof, and it is "
        "the B-roll.")
    add("4. **A measured time below the floor is impossible.** The floor is the "
        "straight line. If the stopwatch beats it, something is wrong \u2014 wrong "
        "start point, wrong end point, or a mistyped number.")
    add("")
    add("## Cart times")
    add("")
    add(f"| Phase | Straight line | Floor at {CART_MPH:.0f} mph | **Measured** | "
        f"Route actually taken | Notes |")
    add("| --- | --- | --- | --- | --- | --- |")
    for num in PHASE_ORDER:
        g = c.group_stats(num)
        near, far = g["nearest_mi"], g["farthest_mi"]
        if near is None:
            continue
        if far and quarter_mi(far) != quarter_mi(near):
            dist = fmt_miles_range(near, far)
            fl = f"{cart_floor_min(near):.1f}\u2013{cart_floor_min(far):.1f} min"
        else:
            dist = fmt_miles(near)
            fl = f"{cart_floor_min(near):.1f} min"
        star = " \u2605" if g["karen_lives_here"] else ""
        add(f"| **Phase {num}**{star} | {dist} | {fl} | &nbsp; | &nbsp; | &nbsp; |")
    add("")
    add("\u2605 = Karen's own phase.")
    add("")
    add("## Resident feedback")
    add("")
    add("There is **no** resident feedback in this repository yet. Every quote a "
        "video uses has to start life on this page.")
    add("")
    add("Ask the same three, so answers are comparable across phases:")
    add("")
    add("1. Why this phase over the others?")
    add("2. What surprised you after you moved in \u2014 good or bad?")
    add("3. One honest trade-off.")
    add("")
    add("| Phase | Who (name or \"neighbour on <street>\") | Permission to use? | Quote |")
    add("| --- | --- | --- | --- |")
    for num in PHASE_ORDER:
        add(f"| Phase {num} | &nbsp; | &nbsp; | &nbsp; |")
    add("")
    add("**Permission is not optional.** A quote without a yes in that column "
        "does not go in a video.")
    return "\n".join(L)


def episode_title(c: Community, num: str) -> tuple[str, list[str]]:
    """Primary title plus A/B alternates.

    Same rule as the flagship: lead with the search term, not a clever question.
    Somebody typing "latitude margaritaville watersound phase 8" has to see their
    exact words at the front. Per-phase videos are a long-tail play -- far fewer
    searches than the flagship, but far higher intent, because nobody types a
    specific phase number unless they are seriously considering it.
    """
    g = c.group_stats(num)
    base = "Latitude Margaritaville Watersound Phase " + num
    if g["karen_lives_here"]:
        primary = f"{base} | I Live Here \u2014 Honest Tour, Cart Times & What It's Really Like"
        alts = [
            f"{base} Review (2026) | From Someone Who Actually Lives In It",
            f"{base} \u2014 Worth It? A Resident Realtor's Honest Take",
        ]
    else:
        primary = f"{base} Explained (2026) | Streets, Distances & What Living There Is Like"
        alts = [
            f"{base} Tour | How Far To The Town Center, And Who Lives There",
            f"{base} \u2014 Everything You Need To Know Before You Buy",
        ]
    if len(g["plats"]) > 1:
        alts.append(f"{base} Is Actually {spoken(len(g['plats'])).capitalize()} "
                    f"Separate Plats \u2014 Here's What That Means")
    return primary, alts


def episode_description(c: Community, num: str) -> str:
    """The description, built only from what is checkable.

    No cart time and no resident quote appears here -- both are gated in the
    script and neither exists until Karen drives and asks. The description is
    written the day of upload, so the gates are marked in-line rather than left
    to memory.
    """
    g = c.group_stats(num)
    plats = g["plats"]
    L: list[str] = []
    add = L.append

    # The first two lines are all that shows above the fold, so they carry the
    # search term and the authority claim and nothing else. Everything below is
    # for the people who clicked "more".
    if g["karen_lives_here"]:
        add(f"Latitude Margaritaville Watersound Phase {num} \u2014 and this is the one "
            f"I actually live in.")
        add("I'm Karen Lawell. My husband and I bought here, so this is not a tour, "
            "it's home.")
    else:
        add(f"Latitude Margaritaville Watersound Phase {num}, walked street by "
            f"street from the recorded plats.")
        add("I'm Karen Lawell \u2014 I'm a realtor here and I live in Phase 8, so I can "
            "tell you how this one actually compares.")
    add("")
    if len(plats) > 1:
        add(f"First thing: Phase {num} is not one neighborhood. It's "
            f"{spoken(len(plats))} separately recorded plats \u2014 "
            + ", ".join(f"{p['label'].replace('Phase ', '')} ({p['plat']})" for p in plats)
            + ". You can look every one of them up at the Bay County Clerk.")
    else:
        p = plats[0]
        add(f"Recorded as {p['plat']} \u2014 {p['lot_count']:,} homesites on "
            f"{p['acres']:,.1f} acres. Checkable at the Bay County Clerk.")
    add("")
    add("\u23f1\ufe0f ABOUT THE INVENTORY NUMBERS: whatever resale and homesite counts I")
    add("give in this video were true the day I recorded it and will be different")
    add("by the time you watch. Everything else here \u2014 the plats, the streets, the")
    add("addresses, the distances \u2014 doesn't change. For today's actual numbers,")
    add("message me.")
    add("")
    add("What's in this video:")
    add(f"\u2022 Exactly where Phase {num} sits, drawn from the recorded plats")
    add(f"\u2022 How long it really takes to get to the Town Center on a golf cart at "
        f"30 \u2014 I drove it and timed it  [CART: confirm before publishing]")
    add(f"\u2022 Straight line it's about {fmt_miles(g['nearest_mi'])} to the Town Center"
        + (f" and about {fmt_miles(g['hwy79_mi'])} to Highway 79"
           if g["hwy79_mi"] is not None else ""))
    add("\u2022 Every street in the phase and the county house numbers on each")
    add("\u2022 Why Minto's lot numbers are NOT addresses")
    add("\u2022 What the people who actually live here say  [RESIDENT: cut this line if")
    add("  nobody was interviewed]")
    if g["karen_lives_here"]:
        add("\u2022 Why my husband and I picked this phase \u2014 and one honest trade-off")
    add("\u2022 Whether you can hear Highway 79 or the Bandshell from here")
    add("")
    add("\U0001F4CD WANT THE FULL PHASE MAP? Comment \"MAP\" and I'll send you the")
    add("full-size map \u2014 all 16 recorded plats with book and page, free.")
    add("")
    add("\U0001F4EC GOT AN ADDRESS? Drop it in the comments and I'll tell you which phase")
    add("it's in and which plat it was recorded under.")
    add("")
    add("\u26a0\ufe0f REGISTER BEFORE YOUR FIRST VISIT. Minto pays the buyer's agent")
    add("commission, so having me with you costs you nothing \u2014 but only if you")
    add("register with me BEFORE you walk into the Sales Center.")
    add("")
    add("\U0001F4DE Call/Text: 850-517-8528")
    add("\U0001F4E7 Email: Karen@nwflbeachhomes.com")
    add("\U0001F4C5 Schedule a call: https://karenlawell.countspcb.com/contact.php")
    add("")
    add("Karen Lawell, Realtor | License #3397366 | Brokered by Counts Real Estate Group")
    add("")
    add("Map data: Bay County, Florida recorded plats (public record), plat book and")
    add("page shown. Illustrative only \u2014 not a survey. For what is actually for sale")
    add("today, contact me. This channel is not affiliated with or endorsed by Minto")
    add("Communities.")
    add("")
    add(f"#LatitudeMargaritaville #Watersound #PanamaCityBeach #Phase{num} "
        f"#55PlusCommunity")
    return "\n".join(L)


def episode_tags(c: Community, num: str) -> list[str]:
    g = c.group_stats(num)
    tags = [
        f"Latitude Margaritaville Watersound Phase {num}",
        f"Latitude Margaritaville Phase {num}",
        f"Latitude Margaritaville Watersound Phase {num} homes for sale",
        "Latitude Margaritaville Watersound",
        "Latitude Margaritaville Watersound phases",
        "Latitude Margaritaville phase map",
        "Latitude Margaritaville Panama City Beach",
        "Latitude Margaritaville Watersound review",
        "living in Latitude Margaritaville",
        "Minto Latitude Margaritaville",
        "55 plus communities Florida",
        "active adult community Florida",
        "retiring to Panama City Beach",
        "Watersound Florida",
    ]
    # The street names are long-tail gold: somebody who has been sent a listing
    # searches the street, not the phase number.
    top = sorted(g["streets"].items(), key=lambda kv: -sum(n for _, _, n in kv[1]))
    for name, _ in top[:4]:
        tags.append(f"{name} Latitude Margaritaville")
    if g["karen_lives_here"]:
        tags.append("Latitude Margaritaville realtor who lives there")
    return tags


def episode_chapters(c: Community, num: str) -> list[str]:
    """Provisional chapters, matching the script's section times.

    Timestamps must be corrected to the final cut before publishing; the first
    one must be 0:00 or YouTube ignores the whole list.
    """
    g = c.group_stats(num)
    ch = [
        ("0:00", f"Phase {num} \u2014 what you actually want to know"),
        ("0:15", "Where it is, and how it was recorded"),
        ("2:00", "The cart run to the Town Center, at 30"),
        ("4:00", "Highway 79 and the Bandshell \u2014 what you can hear"),
        ("5:30", "What people who live here say"),
    ]
    if g["karen_lives_here"]:
        ch.append(("7:30", "Why I live in this phase \u2014 and the honest trade-off"))
    ch += [
        ("9:00", "What's actually for sale right now"),
        ("10:00", "Get the full phase map"),
    ]
    return [f"{t} {label}" for t, label in ch]


def metadata_doc(c: Community) -> str:
    L: list[str] = []
    add = L.append
    add("# Metadata \u2014 Phase Deep Dives")
    add("")
    add("Generated by `tools/scripts/build_phase_scripts.py`. One block per "
        "episode, ready to paste at upload.")
    add("")
    add("**Two things must be resolved before any of these are published:**")
    add("")
    add("- `[CART: ...]` \u2014 the description promises a timed cart run. If the run "
        "has not been driven, that line comes out of the description as well as "
        "the script.")
    add("- `[RESIDENT: ...]` \u2014 same for the resident line. Promising it in the "
        "description and not delivering it in the video is worse than not "
        "mentioning it.")
    add("")
    add("Titles lead with the search term, per the flagship's rule. A per-phase "
        "video is a long-tail play: far fewer searches than \"phases explained\", "
        "far higher intent \u2014 nobody types a specific phase number unless they are "
        "seriously considering it.")
    add("")
    for num in PHASE_ORDER:
        g = c.group_stats(num)
        primary, alts = episode_title(c, num)
        add("---")
        add("")
        add(f"## Phase {num}"
            + ("  \u2605 Karen lives here" if g["karen_lives_here"] else ""))
        add("")
        add(f"`{len(g['plats'])} plat(s)` \u00b7 `{g['lots']:,} homesites` \u00b7 "
            f"`{g['acres']:,.1f} acres` \u00b7 "
            f"`{fmt_miles(g['nearest_mi'])} to the Town Center`")
        add("")
        add("### Title")
        add("")
        add("```")
        add(primary)
        add("```")
        add("")
        add("Alternates for A/B:")
        add("")
        add("```")
        for a in alts:
            add(a)
        add("```")
        add("")
        add("### Chapters")
        add("")
        add("```")
        for line in episode_chapters(c, num):
            add(line)
        add("```")
        add("")
        add("### Description")
        add("")
        add("```")
        add(episode_description(c, num))
        add("```")
        add("")
        add("### Tags")
        add("")
        add("```")
        for t in episode_tags(c, num):
            add(t)
        add("```")
        add("")
        add("### Pinned comment")
        add("")
        add("```")
        if len(g["plats"]) > 1:
            add(f"Phase {num} is actually {spoken(len(g['plats']))} separately "
                f"recorded plats, not one:")
            add("")
            for p in g["plats"]:
                add(f"\u2022 {p['label']} \u2014 {p['plat']}, {p['lot_count']:,} homesites")
            add("")
        else:
            p = g["plats"][0]
            add(f"Phase {num} is recorded as {p['plat']} \u2014 {p['lot_count']:,} "
                f"homesites on {p['acres']:,.1f} acres. You can look it up at the "
                f"Bay County Clerk.")
            add("")
        add("Want the full-size map of all 16 recorded plats? Reply \"MAP\".")
        add("")
        add("And if you're coming to see it, text me at 850-517-8528 BEFORE your")
        add("first Sales Center visit \u2014 Minto pays my commission so I cost you")
        add("nothing, but only if you register with me first. \u2014 Karen (Phase 8)")
        add("```")
        add("")
    add("---")
    add("")
    add("## Shared publishing settings")
    add("")
    add("| Setting | Value |")
    add("| --- | --- |")
    add("| Category | People & Blogs |")
    add("| Licence | Standard YouTube Licence |")
    add("| Audience | Not made for kids |")
    add("| Subtitles | Upload a corrected SRT \u2014 auto-captions mangle the street names |")
    add("| Playlist | \"Latitude Margaritaville Watersound \u2014 Every Phase\", in phase order |")
    add("| End screen | Subscribe (left) \u00b7 next phase in the series \u00b7 the flagship map video |")
    add("")
    add("**Publish in phase order**, one a week. The playlist is the product: "
        "somebody deciding between two phases watches both, and the series only "
        "does its job once several are up.")
    return "\n".join(L)


def thumbnail_doc(c: Community) -> str:
    L: list[str] = []
    add = L.append
    add("# Thumbnail brief \u2014 Phase Deep Dives")
    add("")
    add("Generated by `tools/scripts/build_phase_scripts.py`.")
    add("")
    add("## One system, ten thumbnails")
    add("")
    add("These are a **series**, so they have to read as a set in the sidebar and "
        "still be told apart at a glance on a phone. One template, one variable: "
        "the phase number, set huge.")
    add("")
    add("| Zone | Content |")
    add("| --- | --- |")
    add("| Left third | Karen, cut out, shoulders up \u2014 same crop every episode |")
    add("| Centre | **PHASE N** in the heaviest weight available, filling the height |")
    add("| Behind | That phase's reveal frame from `tools/map/output/frames/`, "
        "desaturated so the number stays legible |")
    add("| Lower right | One short hook, 3\u20134 words max |")
    add("")
    add("The phase number is the whole thumbnail. Somebody scrolling is looking "
        "for *their* phase; make that findable from across the room.")
    add("")
    add("## Per-episode hook")
    add("")
    add("| Episode | Frame to use | Hook | Note |")
    add("| --- | --- | --- | --- |")
    for num in PHASE_ORDER:
        g = c.group_stats(num)
        frame = c.frame_name[g["plats"][0]["label"]]
        if g["karen_lives_here"]:
            hook, note = "I LIVE HERE", "The strongest hook on the channel. Use it."
        elif len(g["plats"]) > 1:
            hook = f"{len(g['plats'])} PLATS, NOT 1"
            note = "The correction is the hook."
        elif quarter_mi(g["nearest_mi"]) <= 0.5:
            hook, note = "WALK TO TOWN CENTER", "Closest phases \u2014 lead with proximity."
        elif quarter_mi(g["nearest_mi"]) >= 2.5:
            hook, note = "THE FAR END", "Be honest about it; it is also the quietest."
        else:
            hook, note = "WORTH IT?", "Generic \u2014 replace once Karen has driven it."
        add(f"| Phase {num} | `{frame}.png` | **{hook}** | {note} |")
    add("")
    add("## Rules")
    add("")
    add("- **No price, ever.** Phases are not priced differently and a thumbnail "
        "implying a tier is the fastest way to lose the channel's credibility.")
    add("- **No inventory count.** It is stale within days and the thumbnail is "
        "not re-uploadable.")
    add("- Test the number at 210 px wide. If the phase number is not readable "
        "there, it is not readable in the sidebar.")
    return "\n".join(L)


def series_readme(c: Community) -> str:
    L: list[str] = []
    add = L.append
    add("# Phase Deep Dives \u2014 one video per phase")
    add("")
    add("**Status:** drafts generated, none recordable yet.")
    add("")
    add("The flagship [`latitude-phases-explained`](../latitude-phases-explained/) "
        "covers all ten phases in one 19\u201322 minute video at about thirty seconds "
        "each. This series is the other half: one video per phase, 8\u201312 minutes, "
        "with the two things thirty seconds cannot hold \u2014 **a cart time Karen "
        "actually drove**, and **what the people who live there say**.")
    add("")
    add("| Episode | Video | Recorded plats | Homesites | Acres |")
    add("| --- | --- | --- | --- | --- |")
    for i, num in enumerate(PHASE_ORDER, 1):
        g = c.group_stats(num)
        plats = ", ".join(p["plat"] for p in g["plats"])
        star = " \u2605" if g["karen_lives_here"] else ""
        add(f"| {i} | [Phase {num}{star}](phase-{num}.md) | {plats} | "
            f"{g['lots']:,} | {g['acres']:,.1f} |")
    add("")
    add("\u2605 Karen lives here. That episode is the anchor of the series.")
    add("")
    add("## Files")
    add("")
    add("| File | What it is |")
    add("| --- | --- |")
    add("| `phase-1.md` \u2026 `phase-10.md` | One shot-by-shot script per episode |")
    add("| [`metadata.md`](metadata.md) | Titles, chapters, descriptions, tags and "
        "pinned comments for all ten |")
    add("| [`thumbnail-brief.md`](thumbnail-brief.md) | One template, ten "
        "thumbnails, with the per-episode hook |")
    add("| [`drive-sheet.md`](drive-sheet.md) | **The blocker.** Cart times and "
        "resident quotes \u2014 the only source for the two things here that are not "
        "public record |")
    add("")
    add("## Why grouped this way")
    add("")
    add("Phase 3 is **three** separately recorded plats; Phases 4, 5 and 6 are "
        "two each. Grouping them per video makes the flagship's central "
        "correction visible instead of asserted: a viewer who came looking for "
        "\"Phase 3\" gets all three plats, each with its own book and page.")
    add("")
    add("## The two things that are not public record")
    add("")
    add("Everything in these drafts comes from Bay County recorded plats except "
        "two, and neither can be derived:")
    add("")
    add("**The cart time cannot be computed.** County road centrelines cover only "
        "Phases 1, 2, 3A, 3B & 3C and 3D. Ten of the sixteen plats have no "
        "interior centreline, and only 12% of the road network connects to the "
        "Town Center \u2014 most phases sit 1\u20135 km from any routable road, Phase 10 "
        "nearly 5 km. So the drafts carry a **straight-line floor at 30 mph**, "
        "labelled as a floor, and a `[CART]` gate for the driven time. See "
        "[`drive-sheet.md`](drive-sheet.md).")
    add("")
    add("**There is no resident feedback here at all.** So the drafts carry a "
        "prompt and a gate, never a sentence. If a phase has nobody interviewed "
        "yet, that section gets cut \u2014 it does not get filled in from "
        "imagination.")
    add("")
    add("## Regenerating")
    add("")
    add("```powershell")
    add("python tools\\scripts\\build_phase_scripts.py")
    add("```")
    add("")
    add("Rebuilds every draft from `tools/map/data/features.json`, so homesite "
        "counts, acreages, streets, address ranges and distances cannot drift "
        "from the map.")
    return "\n".join(L)


def check_frame_refs() -> list[str]:
    """Every `[FRAME x]` in every script must name a file that exists.

    Worth automating because it went wrong silently and badly. The flagship
    script cited 14_phase-8 for a file that is really 13_phase-8 -- eight cues
    from Phase 5B onward were all off by one, because the frames are numbered by
    position in features.json and the Town Center sits at position 8, not last.
    A wrong frame cue is invisible on the page and obvious on camera: Karen says
    "Phase 8" while Phase 9 is on screen.
    """
    frames = ROOT / "tools" / "map" / "output" / "frames"
    content = ROOT / "platforms" / "youtube" / "content"
    if not frames.exists():
        return ["tools/map/output/frames does not exist -- run render_map.py "
                "--only sequence before trusting this check"]
    bad = []
    for md in sorted(content.rglob("*.md")):
        for m in re.finditer(r"\[FRAME ([0-9A-Za-z_-]+)\]", md.read_text(encoding="utf-8")):
            ref = m.group(1)
            if ref == "nn_name":          # the legend placeholder, not a cue
                continue
            if not (frames / f"{ref}.png").exists():
                bad.append(f"{md.relative_to(ROOT)}: [FRAME {ref}] has no such file")
    return bad


def main() -> None:
    c = Community(load())
    OUT.mkdir(parents=True, exist_ok=True)

    missing = [n for n in PHASE_ORDER if n not in c.groups]
    if missing:
        raise SystemExit(f"no plats found for phase(s) {missing} \u2014 "
                         f"has the data changed shape?")

    written = []
    for num in PHASE_ORDER:
        p = OUT / f"phase-{num}.md"
        p.write_text(draft(c, num) + "\n", encoding="utf-8", newline="\n")
        written.append(p)
        g = c.group_stats(num)
        print(f"  phase-{num}.md   {len(g['plats'])} plat(s), "
              f"{g['lots']:>4,} homesites, {g['nearest_mi']:.2f} mi to Town Center")

    for name, text in (("drive-sheet.md", drive_sheet(c)),
                       ("metadata.md", metadata_doc(c)),
                       ("thumbnail-brief.md", thumbnail_doc(c)),
                       ("README.md", series_readme(c))):
        (OUT / name).write_text(text + "\n", encoding="utf-8", newline="\n")
        written.append(OUT / name)

    print(f"\n{len(written)} files -> {OUT.relative_to(ROOT)}")

    bad = check_frame_refs()
    if bad:
        print("\nBROKEN FRAME REFERENCES:")
        for b in bad:
            print(f"  {b}")
        raise SystemExit(1)
    print("every [FRAME] reference in every script resolves to a real file.")
    print("Nothing here is recordable until the drive sheet is filled in.")


if __name__ == "__main__":
    main()
