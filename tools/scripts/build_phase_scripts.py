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
One of the things Karen asked for cannot be derived from public record, and this
tool does not write it:

* RESIDENT FEEDBACK. There is no resident feedback in this repository. Not a
  little, none. So the draft carries a gate and a prompt, never a sentence.
  Inventing a neighbour's opinion would be the worst thing this channel could
  do, and it is exactly the sort of thing that happens by accident when a
  template wants filling.

THE GOLF CART TIME used to be on that list. It is not any more: the drafts carry
an ESTIMATE from routed road distance scaled at CART_MPH, calibrated against the
one real measurement available -- Mike drove Phase 8's 4.14 road miles in 10
minutes. Estimates are always spoken as "about N minutes", never as a stopwatch
reading, and driving a run is now optional rather than blocking. Cart times are
an orientation detail, not the substance of any video.

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
CART_MPH = 24.8          # calibrated: Mike drove Phase 8's 4.14 road mi in 10 min

# Road miles from each plat's centroid to the Bandshell anchor, routed on the
# road network (OSRM), keyed by plat label. Cart minutes are miles / CART_MPH,
# rounded, and always spoken as "about N minutes" -- they are estimates.
ROAD_MI = {
    "Town Center": 0.33,
    "Phase 2": 0.71,
    "Phase 3A": 1.00,
    "Phase 1": 1.21,
    "Phase 3B & 3C": 1.27,
    "Phase 4A": 1.39,
    "Phase 4B": 1.56,
    "Phase 3D": 1.59,
    "Phase 5B": 1.60,
    "Phase 5C": 2.07,
    "Phase 6B & 6C": 2.23,
    "Phase 6A": 2.32,
    "Phase 7": 2.90,
    "Phase 9": 3.80,
    "Phase 10": 4.04,
    "Phase 8": 4.14,
}

# Resident Facebook groups, published to LMWS residents. Keyed by the phase
# number this script groups by. The community organises itself BY PHASE, which
# is the whole premise of this series: a phase is a real social unit, not just
# a plat number. That is a structural answer to "what are people like here",
# and it is better than an anecdote because it is checkable.
PHASE_GROUPS = {
    "3": ["Carefree in Phase 3 LMWS"],
    "5": ["LMWS Fabulous Phase Five"],
    "6": ["6BC Flip Flops"],
    "7": ["L.M.W.S. Lucky 7's"],
    "9": ["LMWS Phase 9 Residents", "The Salty Side | Phase 9BC"],
    "10": ["LMWS Hang 10 (Phase 10 Residents)"],
}

# It goes deeper than phases -- individual streets have their own pages.
STREET_GROUPS = {
    "6": [("Cool Breeze Drive 6A LMWS-Owners Page", "Cool Breeze Dr, 6A")],
    "8": [("LMWS Hang Loose Court", "Hang Loose Ct \u2014 one of Karen and Mike's "
                                    "own three Phase 8 streets")],
}
# Not tied to a phase group above, but real and worth naming where the street
# comes up: FINS UP CT - LMWS (Fins Up Ct, Phase 3) and Sandbar Lane Neighbors
# LMWS (Sandbar Ln, Phase 4).
STREET_GROUPS_BY_STREET = {
    "Fins Up Ct": "FINS UP CT - LMWS",
    "Sandbar Ln": "Sandbar Lane Neighbors LMWS",
    "Hang Loose Ct": "LMWS Hang Loose Court",
    "Cool Breeze Dr": "Cool Breeze Drive 6A LMWS-Owners Page",
}

PHASE_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

# ---------------------------------------------------------------------------
# The end-screen redirect loop
# ---------------------------------------------------------------------------
# Characteristic 8 is "the instant the price lands, point them at the next video
# or a playlist" (`D3-GS` 00:44:45), and channel-setup-config.md still has
# "Add end screens to videos" unticked. The drafts previously broke three rules
# of it at once, so all three are fixed here rather than in the markdown, which
# this tool overwrites:
#
#   1. ORDER. The redirect goes AFTER the close, never before it. Jesse marks
#      the reverse "slightly wrong" on air (`D3-GS` 00:54:16). The last thing
#      the viewer hears should be the answer they came for, not an ask. The old
#      draft opened its close with "the full phase map video is linked below"
#      and then asked for the message, which is exactly backwards.
#   2. ONE ELEMENT. "If you tell them to do three things they'll do zero"
#      (`D3-GS` 00:36:16). One video. Not video + playlist + subscribe + icon,
#      which is what the old `[END SCREEN]` line and the metadata table asked
#      for.
#   3. SAY IT ALOUD while it is on screen. Every top performer analysed does.
#      So it is spoken copy here, not a bracketed direction.
#
# Shape. Not a straight line and not ten spokes into the hub -- a tail feeding
# a cycle, so every video has exactly one next and nothing dead-ends:
#
#     1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> flagship -> 8
#                                          ^                          |
#                                          +--------------------------+
#
# Each edge is chosen because the video that is ending just raised the question
# the next one answers, which is the only reason a redirect ever gets taken.
# The flagship points at Phase 8 rather than Phase 1 because Phase 1 is mostly
# the Sales Center and the model park -- sending the hub's audience to the
# weakest episode in the series would waste the best traffic on the channel.
#
# No facts live in this block. It is the last 15 seconds and nothing checkable
# belongs there. No em-dashes either: this copy is read by ElevenLabs, and the
# em-dash is a named AI tell (`D1-QA` 00:05:11).
REDIRECT: dict[str, tuple[str, str, str]] = {
    "1": ("Phase 2", "Phase 1 is where you park to look at the models. Phase 2 "
          "is where people actually started living, and that one is on the "
          "screen right now. Go and watch that next.",
          "P1 is the Sales Center and the model park, so the obvious next "
          "question is where anybody actually lives."),
    "2": ("Phase 3", "Phase 2 is one of only three phases that can hear "
          "Highway 79. Phase 3 is another one of them, and that video is on "
          "the screen right now.",
          "Continues the Highway 79 thread the chapter just opened."),
    "3": ("Phase 4", "And if three separate plats pretending to be one phase "
          "bothered you, wait until you meet Phase 4. That one is on the "
          "screen right now.",
          "Same trap, next instance: 4A and 4B interlock and get mixed up the "
          "same way 3A, 3B & 3C and 3D do."),
    "4": ("Phase 5", "Phase 5 is where the numbering gets genuinely strange, "
          "because there is no Phase 5A. That video is on the screen right "
          "now.",
          "Ends the which-plat-am-I-in thread on the community's single "
          "biggest myth."),
    "5": ("Phase 6", "Phase 6 is next, and it holds both the emptiest and the "
          "busiest streets out here. That one is on the screen right now.",
          "6A and 6B & 6C are the two density extremes, a direct contrast "
          "with the amenity core this chapter just covered."),
    "6": ("Phase 7", "If it is space you are after, Phase 7 is the biggest "
          "footprint in the community. That video is on the screen right now.",
          "6A's low-density story runs straight into the largest phase."),
    "7": ("Phase 8", "And here is the one I would watch next. Escape Avenue "
          "runs out of Phase 7 and straight into Phase 8, which is where I "
          "live. That video is on the screen right now.",
          "The strongest handoff in the series: one street, two phases, and "
          "the destination is the residency proof."),
    "8": ("Phase 9", "Phase 8 is settled and built. If you want something "
          "newer, Phase 9 is on the screen right now.",
          "Established phase to the genuinely new one, which is the real "
          "resale-versus-new-build decision."),
    "9": ("Phase 10", "Phase 10 is the newest plat on the books and the "
          "biggest one by homesite count. It is on the screen right now.",
          "Newest to newest-and-largest."),
    "10": ("the flagship phase map video",
           "And that is the end of Area 1. If you want all ten phases laid "
           "out on one map, with every plat book and page, that video is on "
           "the screen right now.",
           "P10 is the end of Area 1, so the only place left to go is the "
           "whole map. Closes the loop back to the hub."),
}


# ---------------------------------------------------------------------------
# Humor beats
# ---------------------------------------------------------------------------
# These videos are produced with HeyGen and ElevenLabs, so nothing can be
# ad-libbed. An avatar reads what it is given, which makes humor a SCRIPTING
# deliverable rather than a performance note -- if it is not written here it
# will not exist. And it matters: YouTube throttles content that indexes high on
# AI detection (`D1-QA` 00:03:34), and the "AI 20" rule says human intelligence
# has to do 20% of the work (`D1-QA` 00:04:07). On a machine-narrated channel,
# specific local humor IS that 20%.
#
# Doctrine and the full line bank:
#   platforms/youtube/content/karen-voice-and-humor.md
#
# Rules enforced here:
#   * At most 3 beats per deep dive, one every 90-120 seconds, never two in a
#     row, and never in the last 20 seconds, which belongs to the redirect.
#     The three slots are ~2:00 (where), ~4:00 (cart) and ~5:30 (noise), plus
#     ~9:00 in Phase 8 only.
#   * A beat is the EXIT from a chapter, never the entrance, so it never stands
#     between a viewer and the thing they scrubbed to find.
#   * NEVER on top of a hard fact -- not a plat book and page, not an address
#     range, not an acreage, not an inventory number. The map's authority is the
#     product and a joke sharing a breath with a plat citation devalues it.
#   * If a phase has no good joke it gets none. Phases 5 and 9 are empty on
#     purpose; a forced bit is worse than silence.
#   * No em-dashes: ElevenLabs reads the cadence and the em-dash is a named tell
#     (`D1-QA` 00:05:11).
#
# Every street fact below is a CONFIRMED row in
# properties/latitude-margaritaville-watersound/street-names-buffett.md, or is
# an explicit CORRECTION of one of the three traps on that page. Nothing here
# attributes a song to Buffett that was not verified, and nothing claims Buffett
# density climbs by phase -- it does not, r = +0.064.
#
# ---------------------------------------------------------------------------
# MIKE'S EDITORIAL RULE, 2026-08-23
# ---------------------------------------------------------------------------
# Mike Lawell reviewed every beat that referenced him, line by line, and cut
# most of them. What the surviving set has in common is worth more than any
# style note, because it predicts the next beat:
#
#   THE JOKE IS ON THE PLACE, ON PAPERWORK, OR ON OURSELVES.
#   NEVER ON THE THEME, AND NEVER ON RESIDENTS.
#
# Beats where Mike was a generic sitcom husband were rejected as not funny.
# Beats where a normal person reacts to an absurd PLACE were approved. Mocking
# the theme mocks the people who chose to live inside it, which is the whole
# audience.
#
# Two registers, and they never compete:
#   KAREN  first person, warm, she is the one caught out (bingo, Phase 8's
#          streets, the cats)
#   MIKE   third person, deadpan, short flat sentences (bring a cart, the
#          Hawaiian shirt)
#
# Doctrine, the nine approved beats, what was cut and why:
#   platforms/youtube/content/karen-voice-and-humor.md
HUMOR: dict[str, list[tuple[str, str]]] = {
    "1": [("where", "Phase 1 is one street long, and that street is "
                    "Margaritaville Boulevard. When you name the very first "
                    "road in the community after the song, you are telling "
                    "people exactly what they are buying.")],
    "2": [("where", "Flip Flop Court is a line out of Margaritaville. I blew "
                    "out my flip flop, stepped on a pop top. Somebody read the "
                    "lyrics and started handing out street names."),
          ("noise", "And Coral Reef Way is named for the Coral Reefer Band, "
                    "except a syllable went missing somewhere between the band "
                    "and the street sign.")],
    "3": [("where", "Phase 3 has more Jimmy Buffett in it than any other phase "
                    "out here. Seven streets I can trace to a real song. It is "
                    "also the phase nobody can agree is one phase. Make of "
                    "that what you will."),
          ("noise", "Breathe Out Way is from a song he wrote after Hurricane "
                    "Katrina. Breathe in, breathe out, move on. Out of every "
                    "street name in this community, that is the one I think "
                    "about.")],
    "4": [("where", "Seaplane Drive is named after his actual seaplane. He "
                    "owned a Grumman Albatross called the Hemisphere Dancer. "
                    "And Cheeseburger Drive runs into Coral Reef Way, so if "
                    "you cannot find the house, follow the food.")],
    "5": [],           # 5B is two streets and there is nothing to say. Say nothing.
    "6": [("where", "Attitude Avenue is out here in Phase 6 and Latitude "
                    "Boulevard is back in Phase 2. Changes in latitudes, "
                    "changes in attitudes. Different phases entirely, and I "
                    "refuse to believe that is an accident."),
          ("noise", "Also on this plat, Pencil Thin Avenue. That is a 1974 "
                    "song about a moustache. Somebody proposed it as a street "
                    "name and the county wrote it down.")],
    "7": [("where", "Gypsy Palace Court comes from a song Jimmy Buffett wrote "
                    "with Glenn Frey from the Eagles. That is the sort of "
                    "thing you find out living here and then cannot stop "
                    "telling people.")],
    "8": [("where", "Phase 3 has seven Buffett street names. We live in Phase "
                    "8, which has zero. We're on Cool Water Way, which sounds "
                    "like a Buffett song, and isn't. It's a 1936 cowboy song "
                    "by the Sons of the Pioneers. I try not to take it "
                    "personally."),
          ("cart", "I said I'd never play bingo. I'm too young for bingo. It "
                   "is now one of my favorite things about Tuesdays.")],
    "9": [],           # Nine streets, and no beat good enough to earn the slot.
    "10": [("where", "Phase 10 has a Concoction Court and a Daiquiri Drive on "
                     "the same plat. Somebody at that naming meeting was "
                     "having a very good afternoon."),
           ("noise", "Lone Palm is a real song, off Fruitcakes in 1994. "
                     "Chill Street is License to Chill. They were still going "
                     "strong by the last plat. And before anybody tells me the "
                     "street names get more Buffett as the phases go on, I "
                     "counted them. They do not. Phase 3 wins and it is not "
                     "close.")],
}

# Referenced but never interviewed. The Ken pattern (`D3-GS` 00:25:27): a
# recurring character who never shows his face. Mike is a neighbour, not an
# authority -- the moment he answers a question about plats or pricing the
# credibility has transferred and it stops working.
#
# These two are the ONLY Mike beats Mike approved. Everything else that used to
# be here he cut himself: the fitness-center-versus-pool beat as generic, the
# nine-minute-walk beat as factually wrong (Phase 8 is 4.14 miles by road, not
# a nine minute walk -- nine minutes is Phase 3A), the concert-night beat as
# false (you cannot hear the Bandshell from Phase 8), the Escape Avenue
# speeding beat as the wrong street, and the "street names are ridiculous" beat
# because he does not think they are. Do not add a third without asking him.
#
# (phase -> (slot, line)). Slot-aware so a Mike beat sits where it is actually
# funny rather than always in the cart run.
MIKE: dict[str, tuple[str, str]] = {
    "6": ("cart", "I asked Mike what he'd tell somebody thinking about moving "
                  "here. He said, bring a cart. That was the entire answer."),
    "8": ("mine", "Mike said he'd never own a Hawaiian shirt. Mike owns "
                  "several. Mike has a favorite."),
}

# The one street that runs through two phases and is worth the airtime in both.
# Beat 7 of the approved set: an AUTHORITY beat with no joke in it. County
# parcel site addresses, via streets_by_phase.md -- Phase 7 is 9201-9499 and
# Phase 8 is 9502-9667, with nothing interleaved.
ESCAPE_SPLIT = {"7", "8"}


def humor(kind: str, num: str) -> list[str]:
    """The optional beats for one slot, formatted so Karen can strike them.

    At most one beat is emitted per slot, and no phase puts a HUMOR beat and a
    MIKE beat in the same slot, so nothing is ever read back to back.
    """
    out: list[str] = []
    for slot, line in HUMOR.get(num, []):
        if slot != kind:
            continue
        out += ["`[HUMOR \u2014 optional, cut freely]`", "", f"> {line}", ""]
    mike = MIKE.get(num)
    if mike and mike[0] == kind:
        out += ["`[MIKE \u2014 approved by Mike 2026-08-23. Third person, deadpan, "
                "flat, short sentences. Read it straight: any repetition of "
                "his name is deliberate flat escalation with no signalled "
                "punchline, so do not smooth it. He is a character, never a "
                "source: if he answers a question about plats or pricing, cut "
                "it.]`", "",
                f"> {mike[1]}", ""]
    return out


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


def cart_min(miles: float) -> int:
    """Estimated cart minutes for a road distance, rounded, spoken as "about N".

    24.8 mph is calibrated from the one real measurement available: Mike drove
    Phase 8's 4.14 road miles in 10 minutes. That is the cart's average WITH
    stop signs, turns and slowing for other carts, not its speed on a clear
    straight. Erring slow is also the safer way round for a buyer -- told seven
    minutes and experiencing six is a pleasant surprise; the reverse is not.
    """
    return max(1, round(miles / CART_MPH * 60.0))


def group_road_mi(c: "Community", num: str) -> tuple[float | None, float | None]:
    """(nearest, farthest) road miles across the plats in one phase group."""
    vals = [ROAD_MI[p["label"]] for p in c.groups[num] if p["label"] in ROAD_MI]
    return (min(vals), max(vals)) if vals else (None, None)


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
    rd_near, rd_far = group_road_mi(c, num)
    add("### How far it is")
    add("")
    add("| Measure | Value |")
    add("| --- | --- |")
    if near is not None:
        if multi and far and quarter_mi(far) != quarter_mi(near):
            add(f"| Straight line to the Town Center | {fmt_miles_range(near, far)} "
                f"(varies by plat) |")
        else:
            add(f"| Straight line to the Town Center | {fmt_miles(near)} |")
    if rd_near is not None:
        if rd_far and cart_min(rd_far) != cart_min(rd_near):
            add(f"| By road to the Town Center | {rd_near:.1f}\u2013{rd_far:.1f} mi |")
            add(f"| Cart ride, estimated | about {cart_min(rd_near)}\u2013"
                f"{cart_min(rd_far)} min |")
        else:
            add(f"| By road to the Town Center | {rd_near:.1f} mi |")
            add(f"| Cart ride, estimated | about {cart_min(rd_near)} min |")
    if g["hwy79_mi"] is not None:
        add(f"| Straight line to Highway 79 | {fmt_miles(g['hwy79_mi'])} |")
    add("")
    add("Straight-line distances are from the middle of the phase, **rounded to "
        "the nearest quarter mile** \u2014 a phase is not a point, so a second decimal "
        "would be claiming a survey.")
    add("")
    add("**Cart times are estimates, so say \"about.\"** Road distance routed to "
        "the Bandshell, scaled at roughly 25 mph \u2014 calibrated from Mike's "
        "measured Phase 8 run. They are times **to the Town Center from the "
        "middle of the phase**, not phase-to-phase, and someone at the far edge "
        "of a big phase will see something different.")
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
    # Whether this phase has anything real to say in the resident chapter.
    # Computed HERE rather than in that section, because the cold open makes a
    # promise about it and the two have to agree. Phases 1 and 2 have no
    # recorded group, so their cold open must not promise resident voices.
    groups = PHASE_GROUPS.get(num, [])
    streets = STREET_GROUPS.get(num, [])
    named = [s for s in g["streets"] if s in STREET_GROUPS_BY_STREET]
    has_residents = bool(groups or streets or named)
    L: list[str] = []
    add = L.append

    add("## How to read this")
    add("")
    add("- `[FRAME nn_name]` \u2014 cut to that PNG from `tools/map/output/frames/`")
    add("- `[KAREN]` \u2014 Karen must supply or confirm this. Do not read it as-is.")
    add("- `[CART]` \u2014 an **estimated** cart time: road distance scaled at "
        "roughly 25 mph. Say \"about N minutes\", never a precise figure.")
    add("- `[RESIDENT]` \u2014 a real quote from a real neighbour, captured on the "
        "drive sheet, used with permission. Never paraphrase one into existence.")
    add("- `[INVENTORY]` \u2014 today's snapshot, spoken and dated, from "
        "`inventory_report.py`.")
    add("- Spoken copy is the plain text. Brackets are direction.")
    if mine or has_residents:
        add("- `[TEASER]` \u2014 a short forward promise at a section exit, naming "
            "what is coming next. Its job is to carry the viewer across the "
            "cut. **Every teaser must be paid off by the thing it named.**")
    add("")
    add("## Rules this script follows")
    add("")
    add("Same five as the flagship \u2014 no price-by-phase, inventory spoken and "
        "dated, plat book and page on screen, no invented amenities, lot numbers "
        "are never addresses \u2014 plus two this series adds:")
    add("")
    add("6. **Cart times are estimates and are spoken as \"about N minutes.\"** "
        "Never a precise figure, and never presented as a stopwatch reading.")
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
        # The cold open may only promise what the video actually delivers. The
        # resident chapter is empty for any phase with no recorded group, so
        # the clause about residents is conditional on there being one.
        if has_residents:
            add(f"> This is Phase {num}. And by the end of this video you'll know "
                f"exactly where it is, what's in it, how long it takes to get to the "
                f"Town Center on a cart \u2014 because I timed it \u2014 and what the people "
                f"who actually live here say about it.")
        else:
            add(f"> This is Phase {num}. And by the end of this video you'll know "
                f"exactly where it is, what's in it, and how long it takes to get "
                f"to the Town Center on a cart, because I timed it.")
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
    if num in ESCAPE_SPLIT:
        add("`[on-screen graphic: ESCAPE AVENUE \u00b7 9201\u20139499 \u2192 PHASE 7 \u00b7 "
            "9502\u20139667 \u2192 PHASE 8]`")
        add("")
        add("> One thing before we move on, because it catches people out. "
            "Escape Avenue runs through both phases. Nine four nine nine and "
            "below is Phase 7, nine five oh two and up is Phase 8. If you see "
            "two houses on the same street listed in different phases, that's "
            "not a mistake.")
        add("")
        add("**Direction:** this is an authority beat, not a joke. Say the "
            "numbers cleanly and move on. Karen does **not** live on Escape "
            "Avenue \u2014 she and Mike are on Cool Water Way \u2014 so there is no "
            "\"my end of the street\" line here. Source: "
            "`streets_by_phase.md`, county parcel site addresses.")
        add("")
    L.extend(humor("where", num))

    # ---- the cart run -------------------------------------------------------
    add("## THE CART RUN \u2014 2:00\u20134:00")
    add("")
    add("**Direction:** this is the segment nobody else has. Film it in one take "
        "from the driveway to the Town Center. If Karen times the run, use her "
        "real number and say so; otherwise the estimate below is fine.")
    add("")
    add("`[B-ROLL: cart POV, start of run]`")
    add("")
    rd_near, rd_far = group_road_mi(c, num)
    if rd_near is not None:
        mins = cart_min(rd_near)
        spread = rd_far and cart_min(rd_far) != mins
        if spread:
            add(f"> `[ON SCREEN: {rd_near:.1f}\u2013{rd_far:.1f} mi by road \u00b7 about "
                f"{mins}\u2013{cart_min(rd_far)} min on a cart]`")
        else:
            add(f"> `[ON SCREEN: {rd_near:.1f} mi by road \u00b7 about {mins} min "
                f"on a cart]`")
        add("")
        if spread:
            add(f"> So here's the question everybody actually asks: how far is "
                f"it to the Town Center? By road it's about {rd_near:.1f} to "
                f"{rd_far:.1f} miles depending which plat you're on, so call it "
                f"{spoken(mins)} to {spoken(cart_min(rd_far))} minutes on a cart.")
        else:
            add(f"> So here's the question everybody actually asks: how far is "
                f"it to the Town Center? By road it's about {rd_near:.1f} miles, "
                f"which is about a {spoken(mins)} minute cart ride.")
        add("")
        add("**Say \"about.\"** This is road distance scaled at roughly 25 mph, "
            "calibrated from Mike's measured Phase 8 run, not a stopwatch "
            "reading. It is also a time **to the Town Center from the middle of "
            "the phase**, not phase-to-phase, and the far edge of a big phase "
            "will differ.")
        add("")
    add("`[KAREN: and then the honest part \u2014 is that a walk, a cart trip, or do "
        "you take the car? Say which one you actually do.]`")
    add("")
    L.extend(humor("cart", num))

    # ---- highway 79 / bandshell --------------------------------------------
    add("## NOISE AND CONVENIENCE \u2014 4:00\u20136:00")
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
    if num == "8":
        add("`[KAREN \u2014 first-hand: the Bandshell. Mike confirms you do NOT hear "
            "concerts from Phase 8, and that is worth saying plainly because it "
            "is the honest answer, not the flattering one. Your own line is that "
            "a loud show carries for miles, so it is not how you pick a phase. "
            "No distances, no radius \u2014 it varies too much.]`")
    else:
        add("`[KAREN \u2014 first-hand: the Bandshell. Your own line is that a loud "
            "show carries for miles, so it is not how you pick a phase. Say "
            "whether you hear it here, and whether that is a plus or a minus for "
            "you. No distances, no radius \u2014 it varies too much.]`")
    add("")
    add("**Picture for the Bandshell beat:** **stills, not video.** There are 26 "
        "photographs in `Town Center\\Bandshell\\Music`, 6 more in "
        "`Town Center\\Bandshell`, and `Bandshell Music - Golf carts.jpg` at the "
        "community root. \u26d4 The 8K clips of the bands playing must **not** be "
        "published: recorded live performance of copyrighted songs invites a "
        "Content ID claim, and in a Jimmy Buffett community the set list is "
        "very likely Buffett covers. Muted video is still fine for the "
        "**setting** \u2014 carts arriving, dusk, the empty stage. See "
        "[`karen-presenter-treatment.md`](../karen-presenter-treatment.md).")
    add("")
    add("### How far the Gulf is")
    add("")
    add("**This community is inland, and \"how far is the beach?\" is the single "
        "most common objection a Florida 55+ buyer raises.** Every episode "
        "answers it, because every episode may be someone's first.")
    add("")
    add("`[on-screen: Front Beach Rd west end 8.5 mi ~15 min \u00b7 Pier Park "
        "13.6 mi ~25 min \u00b7 free-flow, add time in summer]`")
    add("")
    add("> We are not on the beach. Let me be straight about that, because the "
        "name does a lot of work. The closest Gulf access is about fifteen "
        "minutes. Pier Park, where you probably actually want to go, is "
        "twenty-five. And in July, add to that.")
    add("")
    add("\u26d4 **Do not round down, and never drop the summer caveat.** Mike's "
        "own \"10 to 15 minutes\" is correct but it is the **floor** \u2014 it holds "
        "for the nearest access only. These are OSRM free-flow routings from the "
        "Town Center with no traffic model, and summer traffic on Front Beach "
        "Road will exceed them materially. A buyer told \"ten minutes to the "
        "beach\" who tours in July and sits on Front Beach Road for forty "
        "re-evaluates everything else in the video. Table and method: "
        "[`phase-status.md`](../../../../properties/latitude-margaritaville-watersound/phase-status.md).")
    add("")
    add("\u26a0\ufe0f **Drive time, not a sight line.** No part of this community "
        "can see the Gulf.")
    add("")
    add("\u26d4 **Say \"the Gulf.\"** Not \"Gulf of Mexico,\" not \"Gulf of "
        "America.\" It is what locals say, both formal names are currently "
        "politically loaded in opposite directions, and the training is "
        "explicit about keeping charged terms off a relocation channel "
        "(`D4-GS` 00:12:35). This beat runs in all ten deep dives and the "
        "flagship, so the term is spoken eleven times across the series and "
        "consistency matters. Channel-wide rule: "
        "[`karen-voice-and-humor.md`](../karen-voice-and-humor.md).")
    add("")
    L.extend(humor("noise", num))

    # ---- teaser into the next section --------------------------------------
    # Characteristic 5: plant a question, answer it late (`framework-vs-practice`
    # marks re-hooks as one of the characteristics that holds). This one is
    # short-range: it carries the viewer over the cut into the chapter that pays
    # the biggest promise.
    #
    # It is emitted ONLY where there is something to pay it with. A teaser that
    # names a chapter the video then does not deliver is worse than no teaser,
    # because the viewer stayed for it. Phases 1 and 2 have no recorded resident
    # group, so they get no resident teaser and no resident promise in the cold
    # open either.
    if mine or has_residents:
        add("`[TEASER \u2014 the exit of this section, carries the viewer across "
            "the cut]`")
        add("")
        if mine:
            add("> And then the part that isn't on any map and isn't in any "
                "county record, which is why the two of us picked this one out "
                "of all ten.")
        else:
            add("> And then something you can actually check for yourself, "
                "which is how the people who already live in this phase "
                "organise themselves.")
        add("")

    # ---- residents ----------------------------------------------------------
    add("## WHAT PEOPLE WHO LIVE HERE SAY \u2014 6:00\u20138:00")
    add("")
    if groups or streets or named:
        add("**Direction:** the strongest answer here is structural, not "
            "anecdotal. **This community organises itself by phase** \u2014 which "
            "is the entire premise of this series. A phase is a real social "
            "unit, not just a plat number, and that is exactly what a buyer is "
            "trying to work out when they ask which phase they should be in.")
        add("")
        if groups:
            add("**Resident Facebook group"
                + ("s" if len(groups) > 1 else "") + " for this phase:**")
            add("")
            for gname in groups:
                add(f"- **{gname}**")
            add("")
            lead = groups[0]
            add(f"> The people here have their own Facebook group. It's called "
                f"**{lead}**. That's not something Minto set up, that's the "
                f"residents.")
            add("")
        for sname, where in streets:
            add(f"- **{sname}** \u2014 {where}")
            add("")
        extra = [(s, STREET_GROUPS_BY_STREET[s]) for s in named
                 if STREET_GROUPS_BY_STREET[s] not in [x[0] for x in streets]]
        for street, gname in extra:
            add(f"- **{gname}** \u2014 {street} has its own page")
            add("")
        add("> And it goes further than the phase. Individual streets out here "
            "have their own pages.")
        add("")
        add("**Why this earns the chapter:** it is checkable, it is not an "
            "anecdote, and it doubles as a natural CTA \u2014 somebody who buys "
            "here has somewhere to go on day one. Name the group, do not read "
            "out its posts, and do not screenshot member names.")
        add("")
    else:
        add("**Direction:** no resident group is recorded for this phase. Say "
            "nothing rather than implying one exists. If Karen knows of one, "
            "it goes in the generator.")
        add("")
    add("`[KAREN \u2014 optional: anything first-hand you know about the people in "
        "this phase. Never summarise what you imagine they would say.]`")
    add("")

    # ---- Karen's own phase --------------------------------------------------
    if mine:
        add("## WHY I LIVE HERE \u2014 8:00\u20139:00")
        add("")
        add("`[CUT TO KAREN, walking her own street]`")
        add("")
        add("`[KAREN: this is the emotional centre of the whole series and the one "
            "thing that cannot be copied. Why you and your husband picked Phase 8 "
            "over the other nine. What the trip to the Bandshell is really like "
            "day to day: it is 4.14 miles by road, roughly a ten minute cart "
            "ride, and you cannot hear the concerts from here. Speak from "
            "experience, not from notes.]`")
        add("")
        add("`[KAREN: one real trade-off about your own phase.]`")
        add("")
        add("**Direction: the lawn-care question.** Mike's one real complaint is "
            "the standard of the HOA-included lawn care, and it is the thing "
            "residents talk about most. Say it as buyer instruction and never as "
            "an accusation: *\"lawn care is included in your HOA dues, and as "
            "I'm recording this the quality of it is what residents talk about "
            "most. When you come tour, look at the lawns, and ask the HOA what's "
            "being done about it.\"* **Never name the landscaping contractor or "
            "the management company.** Describe the condition, not the culprit. "
            "There is an unconfirmed rumour that another landscaper is being "
            "added: do **not** state a fix on camera, because an unconfirmed "
            "rumour becomes a correction. The instruction form stays true "
            "whether the situation is bad, improving or fixed.")
        add("")
        add("`[B-ROLL: Karen's geotagged Phase 8 photo set]`")
        add("")
        L.extend(humor("mine", num))

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
    # The close ends on the answer. The redirect is a separate block AFTER it,
    # because the old order put "the map video is linked below" first and the
    # ask second, which is the thing Jesse marks wrong at `D3-GS` 00:54:16.
    add("## CLOSE \u2014 10:00\u201310:30")
    add("")
    add("> And if you want today's actual list for Phase " + num + ", message "
        "me. I live here.")
    add("")

    # ---- the redirect -------------------------------------------------------
    nxt, line, why = REDIRECT[num]
    add("## END SCREEN REDIRECT \u2014 10:30\u201310:45")
    add("")
    add(f"**One element: {nxt}.** Nothing else on the card. No playlist, no "
        f"subscribe button competing with it, no channel icon \u2014 *\"if you tell "
        f"them to do three things they'll do zero\"* (`D3-GS` 00:36:16). Say it "
        f"out loud while it is on screen; every top performer does.")
    add("")
    add(f"**Why {nxt}:** {why}")
    add("")
    add(f"> {line}")
    add("")
    add(f"`[END SCREEN: {nxt}. One element only. Last 15 seconds.]`")
    add("")
    add("**Put no facts in this block.** It is the last fifteen seconds, the "
        "viewer is already reaching for the next thing, and anything checkable "
        "said here is said to nobody.")
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
    add("- [ ] **Every promise is paid off.** Walk the cold open and every "
        "`[TEASER]` and confirm the video delivers what each one named. A "
        "promise the video does not keep costs more than never having made it")
    add("- [ ] End screen card set to **one element only** \u2014 "
        f"{REDIRECT[num][0]} \u2014 and the redirect line spoken over it")
    add("- [ ] No em-dashes left in any spoken line. ElevenLabs reads the "
        "cadence, and the em-dash is a named AI detection tell "
        "(`D1-QA` 00:05:11). Use a comma, a full stop, or \"and\".")
    add("- [ ] Every mention of the water says **\"the Gulf\"** \u2014 never "
        "\"Gulf of Mexico\" or \"Gulf of America\", in spoken copy, titles, "
        "descriptions or tags.")
    add("- [ ] Every `[HUMOR]` and `[MIKE]` beat is either kept or struck. The "
        "approved set is nine beats and one held, listed in "
        "[`karen-voice-and-humor.md`](../karen-voice-and-humor.md). **Do not "
        "add a new Mike beat without asking Mike.**")
    add("- [ ] No laughter, sigh or breath is synthesised. Any reaction in a "
        "spoken line is dropped in from Karen's own recorded reaction library "
        "on the edit. A synthesised laugh is one of the clearest AI tells "
        "there is, and YouTube throttles content indexing high on AI detection "
        "(`D1-QA` 00:03:34).")
    add("- [ ] Every `[...]` cue is stripped before the script goes to "
        "ElevenLabs. They are edit instructions, not TTS input: on a v2-family "
        "voice the model **speaks the cue aloud** and nothing warns you. "
        "`<break time=\"0.5s\" />` tags are the one exception, and they stay "
        "in.")
    add("- [ ] The picture cuts away from the avatar for the full duration of "
        "any recorded reaction. HeyGen exposes no expression control and "
        "cannot render a laugh, so a real laugh over the avatar is a laughing "
        "voice on a neutral face. See "
        "[`HEYGEN.md`](../../../../tools/avatar/HEYGEN.md).")
    add("- [ ] Presenter treatment followed: **map full-screen, Karen "
        "corner-inset or absent** through the body, full-frame only over a "
        "real photograph and only on a sincere beat. Never at a desk, never in "
        "a generated interior. There is no real footage of Karen, so every "
        "appearance is composited. See "
        "[`karen-presenter-treatment.md`](../karen-presenter-treatment.md).")
    add("- [ ] **No narrated sight lines.** Nothing says \"you can see X from "
        "here\" unless Karen or Mike has stood there and confirmed it. Aerials "
        "and satellite basemaps show what a drone sees, not what a resident "
        "sees, and a sight line that fails on a tour is a trust failure at the "
        "worst possible moment.")
    add("- [ ] **No location audio in the final mix.** All camera sound is "
        "stripped; the bed is `LM Island Breeze - Tour Bed.mp3` with narration "
        "ducked over it. Never bare picture, because production value is "
        "forgiving and audio quality is not (`D1-VIP` 00:57:28).")
    add("- [ ] **No live-performance video published.** Bandshell music is "
        "**stills**; muted video only for the setting. Recorded live "
        "performance of copyrighted songs invites a Content ID claim, and the "
        "strike policy is one warning, two a 30-day penalty box, three "
        "permanent removal (`D4-GS` 00:54:13).")
    add("- [ ] 8K sources cut via **muted 1080p proxies** (`-an` in the same "
        "transcode), conformed back only for reframing, and **delivered at "
        "1080p** (`D2-GS` 00:19:43).")
    add("- [ ] Nothing on camera names the landscaping contractor or the "
        "management company. Describe the condition, ask the question, never "
        "identify the culprit.")
    return "\n".join(L)


def drive_sheet(c: Community) -> str:
    """CLOSED. Kept as a short record so existing links do not break.

    Both halves resolved: cart times by calculation, resident colour by the
    per-phase Facebook groups Mike supplied. Nothing on this sheet is
    outstanding, so it no longer asks for anything.
    """
    L: list[str] = []
    add = L.append
    add("# Drive sheet \u2014 \u2705 CLOSED")
    add("")
    add("Generated by `tools/scripts/build_phase_scripts.py`.")
    add("")
    add("**This sheet is finished. Nothing here is blocking any episode.** It "
        "is kept as a record of how each half was resolved.")
    add("")
    add("| What it asked for | How it closed |")
    add("| --- | --- |")
    add("| **Cart times**, to be driven and stopwatched | **By calculation.** "
        "Routed road distance scaled at roughly 25 mph, calibrated from Mike's "
        "measured Phase 8 run (4.14 road miles in 10 minutes). Every draft now "
        "says \"about N minutes\". Driving one is optional |")
    add("| **Resident quotes**, to be collected with permission | **By the "
        "per-phase Facebook groups.** The community organises itself by phase, "
        "which answers \"what are people like here\" structurally rather than "
        "anecdotally, and is checkable rather than a single voice |")
    add("")
    add("## Cart times, for reference")
    add("")
    add("Estimates, already in the drafts. Listed so a driven run has something "
        "to check against, not because anything waits on them.")
    add("")
    add("| Phase | By road | Estimated cart ride |")
    add("| --- | --- | --- |")
    for num in PHASE_ORDER:
        g = c.group_stats(num)
        rd_near, rd_far = group_road_mi(c, num)
        if rd_near is None:
            continue
        if rd_far and cart_min(rd_far) != cart_min(rd_near):
            dist = f"{rd_near:.1f}\u2013{rd_far:.1f} mi"
            est = f"about {cart_min(rd_near)}\u2013{cart_min(rd_far)} min"
        else:
            dist = f"{rd_near:.1f} mi"
            est = f"about {cart_min(rd_near)} min"
        star = " \u2605" if g["karen_lives_here"] else ""
        add(f"| **Phase {num}**{star} | {dist} | {est} |")
    add("")
    add("\u2605 = Karen's own phase, and the calibration point.")
    add("")
    add("## Resident groups, for reference")
    add("")
    add("Published to LMWS residents on Facebook. Named in each phase's episode "
        "in `WHAT PEOPLE WHO LIVE HERE SAY`.")
    add("")
    add("| Group | Phase |")
    add("| --- | --- |")
    for numk in PHASE_ORDER:
        for gname in PHASE_GROUPS.get(numk, []):
            add(f"| {gname} | {numk} |")
    add("| LMWS Hang Loose Court | street-level, Phase 8 |")
    add("| FINS UP CT - LMWS | street-level |")
    add("| Sandbar Lane Neighbors LMWS | street-level |")
    add("| Cool Breeze Drive 6A LMWS-Owners Page | street-level, Phase 6A |")
    add("")
    add("**Name the group. Do not read out its posts and do not screenshot "
        "member names.**")
    add("")
    add("If a first-hand resident quote ever does turn up, it is welcome \u2014 it "
        "is just no longer required for an episode to be recordable.")
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
    _rd_near, _rd_far = group_road_mi(c, num)
    if _rd_near is not None:
        add(f"\u2022 How far it is to the Town Center by road, and roughly how long "
            f"that is on a golf cart")
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
        ("4:00", "Highway 79, the Bandshell and how far the Gulf is"),
        ("6:00", "What people who live here say"),
    ]
    if g["karen_lives_here"]:
        ch.append(("8:00", "Why I live in this phase \u2014 and the honest trade-off"))
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
    add("| End screen | **One element per video**, per the redirect loop below. Not subscribe *and* next *and* the map |")
    add("")
    add("### The redirect loop")
    add("")
    add("One video per end screen, spoken aloud while the card is up, placed "
        "**after** the close and never before it. The chain is a tail feeding a "
        "cycle, so nothing dead-ends:")
    add("")
    add("| This video ends | Points at | Because |")
    add("| --- | --- | --- |")
    for n in PHASE_ORDER:
        nxt, _, why = REDIRECT[n]
        add(f"| Phase {n} | **{nxt}** | {why} |")
    add("| The flagship map video | **Phase 8** | Karen's own phase. The hub's "
        "traffic is the best on the channel, so it goes to the residency proof "
        "rather than to Phase 1, which is mostly the Sales Center. |")
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
    add("## Humor")
    add("")
    add("These are produced with HeyGen and ElevenLabs, so **nothing can be "
        "ad-libbed** \u2014 an avatar reads what it is given. Every beat is "
        "therefore written into the generator and marked `[HUMOR]` or `[MIKE]` "
        "so Karen can strike it. Doctrine, the banned-phrase list and the full "
        "line bank are in "
        "[`karen-voice-and-humor.md`](../karen-voice-and-humor.md).")
    add("")
    add("Phases 5 and 9 carry **no beat on purpose**. A forced bit is worse "
        "than none.")
    add("")
    add("The `[MIKE]` beats were reviewed line by line with Mike on "
        "2026-08-23 and most of the earlier set was cut, several of them "
        "because they were **factually wrong** rather than unfunny. Two "
        "survived: *bring a cart* in Phase 6, and *the Hawaiian shirt* in "
        "Phase 8. The rule his choices revealed is the one to script against: "
        "**the joke is on the place, on paperwork, or on ourselves, never on "
        "the theme and never on residents.** Do not add a third without "
        "asking him.")
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
    add("| [`photo-shot-list.md`](photo-shot-list.md) | What Karen photographs "
        "in each phase, and which beat each shot covers |")
    add("| [`drive-sheet.md`](drive-sheet.md) | Resident quotes \u2014 the one thing "
        "in these videos that cannot be derived from a file |")
    add("")
    add("## Why grouped this way")
    add("")
    add("Phase 3 is **three** separately recorded plats; Phases 4, 5 and 6 are "
        "two each. Grouping them per video makes the flagship's central "
        "correction visible instead of asserted: a viewer who came looking for "
        "\"Phase 3\" gets all three plats, each with its own book and page.")
    add("")
    add("## The one thing that is not public record")
    add("")
    add("**There is no resident feedback here at all.** So the drafts carry a "
        "prompt and a gate, never a sentence. If a phase has nobody interviewed "
        "yet, that section gets cut \u2014 it does not get filled in from "
        "imagination.")
    add("")
    add("Cart times used to sit beside it as a blocker. They no longer do: the "
        "drafts carry an **estimate** from routed road distance at roughly "
        "25 mph, calibrated from Mike's measured Phase 8 run, always spoken as "
        "\"about N minutes\". Driving one is optional. They are an orientation "
        "detail, not the substance of any video.")
    add("")
    add("## The redirect loop")
    add("")
    add("Every episode ends with **one** spoken redirect naming **one** next "
        "video, placed after the close and never before it. Characteristic 8 "
        "says point them at the next video the instant the payoff lands "
        "(`D3-GS` 00:44:45); Jesse marks the reverse order *\"slightly wrong\"* "
        "on air (`D3-GS` 00:54:16); and *\"if you tell them to do three things "
        "they'll do zero\"* (`D3-GS` 00:36:16) is why it is one card and not "
        "four.")
    add("")
    add("It is a tail feeding a cycle, so no episode dead-ends:")
    add("")
    add("```mermaid")
    add("flowchart LR")
    for i, n in enumerate(PHASE_ORDER[:-1]):
        add(f"    P{n} --> P{PHASE_ORDER[i + 1]}")
    add("    P10 --> MAP[flagship map video]")
    add("    MAP --> P8")
    add("```")
    add("")
    add("| This video ends | Points at | Because |")
    add("| --- | --- | --- |")
    for n in PHASE_ORDER:
        nxt, _, why = REDIRECT[n]
        add(f"| Phase {n} | **{nxt}** | {why} |")
    add("| The flagship map video | **Phase 8** | The hub's traffic is the best "
        "on the channel, so it goes to the residency proof rather than to Phase "
        "1, which is mostly the Sales Center and the model park. |")
    add("")
    add("The last 15 to 20 seconds are reserved for it and **carry no facts**. "
        "Anything checkable said there is said to a viewer already reaching for "
        "the next video.")
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
