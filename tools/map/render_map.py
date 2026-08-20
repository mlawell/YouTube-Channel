"""Render the Latitude Margaritaville Watersound phase map.

Outputs (all under tools/map/output/, all regenerable):

    poster       one high-resolution map of the whole community, legend + credits
    print        the same thing as a print-ready PDF one-pager
    thumbnail    1280x720 plate to drop a face and headline onto
    sequence     the video reveal - 1920x1080 frames, overview first, then one
                 zoomed frame per phase with a locator inset, so a phase can be
                 revealed while it is being talked about instead of scribbled on

Everything is drawn from tools/map/data/features.json, which is rebuilt from Bay
County public records. Re-run fetch_data.py -> build_features.py and every export
here updates; the map cannot go stale the way a screen recording does.

Run:
    python tools/map/render_map.py                    # everything
    python tools/map/render_map.py --only poster
    python tools/map/render_map.py --only sequence --overlays hwy79 towncenter
"""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import os
import re
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

# Vector output is the canonical master for print, so fonts must travel with the
# file -- a print shop that substitutes a font silently reflows the whole sheet.
# fonttype 42 embeds a TrueType subset in PDF; 'path' converts SVG text to
# outlines, which cannot substitute at all.
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["svg.fonttype"] = "path"

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Polygon as MPoly, Rectangle

from fmt import ident, ident_range, qty

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "output"

R = 6378137.0
MI_PER_M = 1 / 1609.344

# ---------------------------------------------------------------- brand palette
SAND = "#FAF3E4"
INK = "#12333F"
TEAL = "#20D0C4"
DEEP = "#0E4C5A"
NAVY = "#0C2A34"
GOLD = "#FFC845"
CORAL = "#FF6B5B"
PINK = "#FF4FA3"
WATER = "#A8DCE6"
WATER_EDGE = "#7CC2D0"
LAND = "#E7EFDC"
DIM_FILL = "#EDE4D2"
DIM_EDGE = "#BCAF98"
ROAD = "#8C8271"
MUTED = "#5C6B70"

# ---------------------------------------------------------------- phase palette
# One hue family per phase NUMBER, one lightness tint per lettered sub-phase, so
# 3A / 3B & 3C / 3D read as three shades of the same colour. A viewer learns ten
# colours instead of sixteen and the map teaches the numbering scheme by itself.
#
# Hues avoid the pale cyan of water (~194 deg, lightness ~0.78) and the coral of
# the landmark pins (~6 deg), which leaves little room for ten families -- five
# of them would otherwise pile into the greens. So each family carries its own
# hue, lightness AND saturation. A deep navy at lightness 0.40 is unmistakable
# against pale water even though the hues are neighbours; value and saturation
# do the work that hue alone cannot at this spacing.
#
# The assignment is deliberately NOT in phase order: consecutive phase numbers
# tend to be geographically adjacent, and adjacent regions are exactly the ones
# that have to be told apart. `--check-palette` measures the result in CIE Lab.
# Every fill has to sit clear of the cream paper, or a phase reads as empty land
# rather than as a phase -- which defeats colour-coding entirely. These bounds
# are the floor; within-family tints are derived inside them, which costs some
# separation between siblings. That is the right trade: a viewer has to see that
# a phase IS there before they can tell which sibling it is, and the label and
# legend already carry the fine distinction.
PHASE_LIGHT_MIN, PHASE_LIGHT_MAX = 0.34, 0.62
PHASE_SAT_MIN = 0.42
PHASE_STYLE = {
    #      hue   light  sat
    1:  (180, 0.42, 0.55),   # deep teal
    2:  (133, 0.56, 0.52),   # green
    3:  (305, 0.48, 0.48),   # orchid
    4:  (218, 0.40, 0.55),   # deep navy -- far from the bay, and far darker than water
    5:  (345, 0.52, 0.52),   # rose
    6:  (73,  0.56, 0.60),   # yellow-green
    7:  (20,  0.54, 0.58),   # orange
    8:  (265, 0.46, 0.50),   # purple
    9:  (155, 0.38, 0.52),   # dark green
    10: (43,  0.44, 0.58),   # bronze
}
PHASE_LIGHT_SPREAD = 0.20  # lightness spread across a family's sub-phases
PHASE_SAT_SPREAD = 0.24    # saturation ramp across them, for extra separation
MIN_BG_DELTA = 30.0        # every fill must clear the paper by at least this

# The Town Center is not a phase and must not look like one, or the map
# reintroduces exactly the "Phase 5A" confusion it exists to clear up. It takes
# a dark slate that no phase occupies - phases are held between lightness 0.34
# and 0.62, so going darker and greyer than any of them reads as "civic" rather
# than as another neighbourhood. The cottages inside it take a warm gold: they
# are a different thing from the amenity tract and need to be told apart at a
# glance, so the pair is separated by lightness, hue and saturation at once
# (deltaE 70) rather than being two tints of one brown.
TOWN_CENTER_FILL = "#4E5A52"
COTTAGE_FILL = "#F4D06B"

# The measured Town Center buildings sit on top of that dark slate tract, so
# they take a near-white warm grey: it reads as "building" at a glance and has
# the contrast to survive being 2 mm across on a 36-inch sheet. The edge is
# deliberately soft rather than a crisp survey line, because these are good to
# about 5 m and should not look sharper than they are.
BUILDING_FILL = "#EDE7DA"
BUILDING_EDGE = "#8A8578"
# Ponds take the same blue as West Bay and the Intracoastal. They are the same
# substance, and giving them a colour of their own made the map look like it
# was drawing two different kinds of thing.
POND_FILL = WATER
POND_EDGE = WATER_EDGE


def _hls(h_deg: float, light: float, sat: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h_deg % 360) / 360.0, light, sat)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def is_phase(label: str) -> bool:
    return label.startswith("Phase ")


def phase_number(label: str) -> int:
    m = re.search(r"(\d+)", label)
    return int(m.group(1)) if m else 0


def colour_family(label: str):
    """Grouping key for the palette check.

    Sub-phases of one number are *meant* to look related, so they are checked
    against a lower bar. Everything that is not a phase gets its own family -
    the Town Center and the cottages are different things and have to be
    unmistakable from each other, not merely tellable apart.
    """
    return phase_number(label) if is_phase(label) else label


def build_palette(labels: list[str]) -> dict[str, str]:
    """label -> hex. Sub-phases of one number share a hue and vary in lightness.

    The Town Center is handled outside the families: it is a recorded plat but
    not a neighbourhood, and giving it a phase hue would put it back in the
    sequence the map is trying to take it out of.
    """
    families: dict[int, list[str]] = {}
    out: dict[str, str] = {}
    for lab in labels:
        if is_phase(lab):
            families.setdefault(phase_number(lab), []).append(lab)
        else:
            out[lab] = TOWN_CENTER_FILL
    for num, members in families.items():
        hue, light, sat = PHASE_STYLE.get(num, ((num * 37) % 360, 0.50, 0.50))
        sat = max(sat, PHASE_SAT_MIN)
        light = min(max(light, PHASE_LIGHT_MIN), PHASE_LIGHT_MAX)
        if len(members) == 1:
            out[members[0]] = _hls(hue, light, sat)
            continue
        # Spread the family inside the legibility band, sliding rather than
        # clipping so the sub-phases stay evenly spaced. Saturation ramps
        # alongside lightness: the band is narrow now, so lightness alone does
        # not give siblings enough separation to be told apart.
        half = PHASE_LIGHT_SPREAD / 2
        lo = min(max(light - half, PHASE_LIGHT_MIN), PHASE_LIGHT_MAX - PHASE_LIGHT_SPREAD)
        step = PHASE_LIGHT_SPREAD / (len(members) - 1)
        sat_step = PHASE_SAT_SPREAD / (len(members) - 1)
        for i, lab in enumerate(members):
            out[lab] = _hls(hue, lo + i * step,
                            max(PHASE_SAT_MIN, sat + PHASE_SAT_SPREAD / 2 - i * sat_step))
    return out


def shade(hex_colour: str, *, light_delta: float = 0.0, sat_scale: float = 1.0) -> str:
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    return _hls(h * 360, min(1.0, max(0.0, l + light_delta)), min(1.0, sat * sat_scale))


def muted(hex_colour: str, *, light: float = 0.84, sat: float = 0.10) -> str:
    """Push a colour to a fixed pale value, keeping only a hint of its hue.

    Absolute rather than relative: a relative lightening leaves the dark phases
    (navy, deep green) still reading as heavy blocks when they should be
    receding, so every inactive phase has to land on the same value.
    """
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, _, s0 = colorsys.rgb_to_hls(r, g, b)
    return _hls(h * 360, light, min(sat, s0))


def _lab(hex_colour: str) -> tuple[float, float, float]:
    """sRGB -> CIE Lab (D65). Perceptual, so colour distance means something."""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(hex_colour[i:i + 2], 16)) for i in (1, 3, 5))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def palette_report(palette: dict[str, str]) -> None:
    """Check separation, three ways.

    Against the paper: every fill must be clearly visible, or a phase reads as
    empty land rather than as a phase. This is the check that catches a tint
    washing out into the background.
    Cross-family: different phase numbers have to be unmistakable (deltaE >= 20).
    Within-family: sub-phases are *supposed* to look related, so they only need
    to be tellable apart (deltaE >= 8).
    """
    items = list(palette.items())
    bg = _lab(SAND)
    print(f"{'phase':<14}{'hex':<10}{'vs paper':>9}   {'nearest other family':<22}deltaE")
    worst_bg, worst_cross, worst_within = 999.0, 999.0, 999.0
    problems = []
    for lab, hexa in items:
        l1 = _lab(hexa)
        fam = colour_family(lab)
        d_bg = math.dist(l1, bg)
        worst_bg = min(worst_bg, d_bg)
        if d_bg < MIN_BG_DELTA:
            problems.append(f"{lab} too pale against the paper ({d_bg:.1f})")
        cross = [(o, math.dist(l1, _lab(h))) for o, h in items if colour_family(o) != fam]
        near, d = min(cross, key=lambda t: t[1])
        worst_cross = min(worst_cross, d)
        if d < 20:
            problems.append(f"{lab} vs {near} ({d:.1f})")
        flags = ("  <-- pale" if d_bg < MIN_BG_DELTA else "") + \
                ("  <-- too close" if d < 20 else "")
        print(f"  {lab:<14}{hexa:<10}{d_bg:>9.1f}   {near:<22}{d:5.1f}{flags}")
        for o, h in items:
            if colour_family(o) == fam and o != lab:
                dw = math.dist(l1, _lab(h))
                worst_within = min(worst_within, dw)
                if dw < 8:
                    problems.append(f"{lab} vs {o} ({dw:.1f}, same family)")

    print(f"\nvs paper minimum       deltaE {worst_bg:5.1f}   (want >= {MIN_BG_DELTA})")
    print(f"cross-family minimum   deltaE {worst_cross:5.1f}   (want >= 20)")
    if worst_within < 999:
        print(f"within-family minimum  deltaE {worst_within:5.1f}   (want >= 8, "
              f"they should look related)")
    print("OK" if not problems else "RETUNE PHASE_STYLE: " + "; ".join(sorted(set(problems))))

FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"


def _font(candidates: list[str], **kw) -> FontProperties:
    for name in candidates:
        p = FONT_DIR / name
        if p.exists():
            return FontProperties(fname=str(p), **kw)
    return FontProperties(**kw)


F_BLACK = _font(["ariblk.ttf", "arialbd.ttf"])
F_BOLD = _font(["arialbd.ttf"])
F_REG = _font(["arial.ttf"])


# ---------------------------------------------------------------- projection
def merc(lon: float, lat: float) -> tuple[float, float]:
    return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def rings(geom: dict):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            yield ring


def lines(geom: dict):
    if geom["type"] == "LineString":
        yield geom["coordinates"]
    elif geom["type"] == "MultiLineString":
        yield from geom["coordinates"]


def principal_angle(points: list[tuple[float, float]]) -> float:
    """Angle of the long axis of a point cloud, via a 2x2 covariance eigenvector.

    The community is a ~4-mile ribbon running north-west to south-east. Drawn
    north-up it wastes most of a 16:9 frame; rotated onto its own long axis it
    fills the frame and every phase label gets room to breathe.
    """
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points) / n
    syy = sum((p[1] - my) ** 2 for p in points) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points) / n
    return 0.5 * math.atan2(2 * sxy, sxx - syy)


def project_ring(ring) -> list[tuple[float, float]]:
    return [merc(c[0], c[1]) for c in ring]


def bbox_of(seqs) -> tuple[float, float, float, float]:
    xs = [x for seq in seqs for x, _ in seq]
    ys = [y for seq in seqs for _, y in seq]
    return min(xs), min(ys), max(xs), max(ys)


def clip_to(seqs, box, pad_frac: float = 0.30):
    """Drop context geometry that lands far outside the community.

    County hydrology and road layers cover the whole bbox we downloaded; without
    this the map is full of creeks that have nothing to do with the community.
    """
    x0, y0, x1, y1 = box
    px, py = (x1 - x0) * pad_frac, (y1 - y0) * pad_frac
    x0, y0, x1, y1 = x0 - px, y0 - py, x1 + px, y1 + py
    keep = []
    for seq in seqs:
        if any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in seq):
            keep.append(seq)
    return keep


# ---------------------------------------------------------------- data
def load_features() -> dict:
    path = DATA / "features.json"
    if not path.exists():
        raise SystemExit("data/features.json missing - run fetch_data.py then build_features.py")
    return json.loads(path.read_text(encoding="utf-8"))


class Scene:
    """Everything projected and rotated once, so each frame is just drawing."""

    def __init__(self, f: dict):
        self.meta = f["meta"]
        self.phases = f["phases"]
        self.total_lots = f["total_lots"]
        # Ten phases, sixteen plats. Phase 3 was recorded as 3A, 3B & 3C and 3D,
        # Phase 4 as 4A and 4B, and the sixteenth plat is the Town Center rather
        # than an eleventh phase. Conflating the two numbers is the single most
        # common way this community gets described wrongly.
        self.phase_count = f.get("phase_count", 10)
        self.plat_count = f.get("plat_count", len(f["phases"]))
        self.summary = (f"{self.phase_count} phases \u00b7 {self.plat_count} recorded plats "
                        f"\u00b7 {self.total_lots:,} platted homesites")
        self.total_acres = f["total_acres"]

        raw = {
            p["label"]: [project_ring(r) for r in rings(p["geometry"])] for p in self.phases
        }
        cloud = [pt for rs in raw.values() for r in rs for pt in r]
        self.theta = -principal_angle(cloud)
        self.origin = (
            sum(p[0] for p in cloud) / len(cloud),
            sum(p[1] for p in cloud) / len(cloud),
        )
        # North ends up rotated by theta; the north arrow is drawn to match.
        self.north_deg = math.degrees(self.theta)

        self.phase_rings = {lab: [self.rot(r) for r in rs] for lab, rs in raw.items()}
        self.extent = bbox_of([r for rs in self.phase_rings.values() for r in rs])

        self.lot_rings = {
            lab: [self.rot(project_ring(r)) for g in geoms for r in rings(g)]
            for lab, geoms in f["lots_by_phase"].items()
        }
        self.water = clip_to(
            [self.rot(project_ring(r)) for g in f["waterbodies"] for r in rings(g)],
            self.extent, 0.20,
        )
        # Stormwater ponds. The county's hydrology layers return a single
        # feature across the whole community, so these are measured off the
        # builder's site plan instead; see extract_plan_features.py.
        self.ponds = [self.rot(project_ring(r)) for g in f.get("ponds", []) for r in rings(g)]

        tc = f.get("town_center") or {}
        self.tc_label = tc.get("label", "Town Center")
        self.tc_plat = tc.get("plat")
        self.tc_acres = tc.get("tract_acres")
        self.tc_tract = [self.rot(project_ring(r)) for r in rings(tc.get("tract") or {})]
        self.cottages_label = tc.get("cottages_label", "Stay & Play Cottages")
        self.cottage_count = tc.get("cottage_count", 0)
        self.cottage_lots = [self.rot(project_ring(r))
                             for g in tc.get("cottage_lots", []) for r in rings(g)]
        self.cottage_hull = [self.rot(project_ring(r)) for r in rings(tc.get("cottage_hull") or {})]
        cc = tc.get("cottage_centroid")
        self.cottage_xy = self.rot([tuple(cc)], project=True)[0] if cc else None
        self.tc_buildings = [
            (b.get("name"), b.get("confirmed_name", False),
             [self.rot(project_ring(r)) for r in rings(b["geometry"])])
            for b in tc.get("buildings", [])
        ]
        self.creeks = clip_to(
            [self.rot(project_ring(l)) for g in f["creeks"] for l in lines(g)],
            self.extent, 0.06,
        )
        self.roads = [
            (r["name"], self.rot(project_ring(l))) for r in f["roads"] for l in lines(r["geometry"])
        ]
        self.highways = [
            (h["name"], h.get("route", ""), self.rot(project_ring(l)))
            for h in f["highways"]
            for l in lines(h["geometry"])
        ]
        self.hwy79 = clip_to(
            [pts for _, route, pts in self.highways if route == "79"], self.extent, 0.12
        )

        self.landmarks = [l for l in f["landmarks"] if l.get("lat") is not None]
        self.needs_confirmation = [l for l in f["landmarks"] if not l.get("confirmed")]
        self.anchor_xy = {l["name"]: self.rot([(l["lon"], l["lat"])], project=True)[0]
                          for l in self.landmarks}
        self.centroids = {
            p["label"]: self.rot([tuple(p["centroid"])], project=True)[0] for p in self.phases
        }
        self.palette = build_palette([p["label"] for p in self.phases])

        # Street name label anchors, projected and rotated with everything else.
        # `label_angle` comes out of build_features as a bearing in lon/lat space;
        # the scene rotation has to be added on top of it.
        rot_deg = math.degrees(self.theta)
        self.street_labels = []
        for p in self.phases:
            for st in p.get("streets", []):
                ll = st.get("label_lonlat")
                if not ll:
                    continue
                ang = st.get("label_angle", 0.0) + rot_deg
                ang = (ang + 90) % 180 - 90          # keep text upright
                self.street_labels.append({
                    "phase": p["label"],
                    "name": st["name"],
                    "xy": self.rot([tuple(ll)], project=True)[0],
                    "angle": ang,
                    "address_range": st.get("address_range"),
                })

    def rot(self, pts, project: bool = False):
        c, s = math.cos(self.theta), math.sin(self.theta)
        ox, oy = self.origin
        out = []
        for pt in pts:
            x, y = merc(pt[0], pt[1]) if project else (pt[0], pt[1])
            dx, dy = x - ox, y - oy
            out.append((ox + dx * c - dy * s, oy + dx * s + dy * c))
        return out

    def landmark(self, name: str):
        return self.anchor_xy.get(name)

    def colour(self, label: str) -> str:
        return self.palette[label]

    def distance_mi(self, p: dict, target: str) -> float | None:
        """Straight-line miles from the phase centroid to a landmark."""
        t = self.landmark(target)
        if not t:
            return None
        cx, cy = self.centroids[p["label"]]
        lat = math.radians(p["centroid"][1])
        # Web Mercator inflates ground distance by 1/cos(lat); undo it.
        return math.hypot(cx - t[0], cy - t[1]) * math.cos(lat) * MI_PER_M

    def hwy79_distance_mi(self, p: dict) -> float | None:
        if not self.hwy79:
            return None
        cx, cy = self.centroids[p["label"]]
        lat = math.radians(p["centroid"][1])
        best = min(
            _point_seg_dist(cx, cy, a, b)
            for pts in self.hwy79
            for a, b in zip(pts, pts[1:])
        )
        return best * math.cos(lat) * MI_PER_M


def _point_seg_dist(px, py, a, b) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


# ---------------------------------------------------------------- drawing
def draw_base(ax, s: Scene, *, lw_scale: float = 1.0) -> None:
    for pts in s.water:
        ax.add_patch(MPoly(pts, closed=True, facecolor=WATER, edgecolor=WATER_EDGE,
                           lw=0.6 * lw_scale, zorder=1))
    for pts in s.creeks:
        ax.plot(*zip(*pts), color=WATER_EDGE, lw=0.9 * lw_scale, solid_capstyle="round", zorder=1.1)


def draw_ponds(ax, s: Scene, *, lw_scale: float = 1.0) -> None:
    """Stormwater ponds, above the lot linework so they read as water.

    Z-order matters more than it looks here. A pond is a hole in the
    developable land, so it has to sit above the lots, not just above the phase
    fill - drawn underneath, the ponds in the densely platted western phases
    disappear entirely under the lot hatching while the ones in open ground
    still show, which reads as "the west has no lakes" rather than as a
    drawing-order artefact. It stays below the roads, which really do cross it.
    """
    if not s.ponds:
        return
    ax.add_collection(PolyCollection(
        s.ponds, facecolors=POND_FILL, edgecolors=POND_EDGE,
        linewidths=0.7 * lw_scale, alpha=0.95, zorder=3.15))


def draw_town_center(ax, s: Scene, active: str | None, *, lw_scale: float = 1.0,
                     label: bool = True, fontsize: float = 8.0) -> None:
    """The amenity tract and the Stay & Play cottages inside it.

    Both come out of the plat recorded as 'PH 5A3'.  They are drawn as what
    they are rather than as a phase, because there is no Phase 5A to buy in -
    48 of the plat's 62 acres are the single tract holding the Bandshell and
    Paradise Pool, and its only homesites are the cottages.
    """
    on = active in (None, s.tc_label)
    if s.tc_tract:
        ax.add_collection(PolyCollection(
            s.tc_tract, facecolors=TOWN_CENTER_FILL if on else muted(TOWN_CENTER_FILL),
            edgecolors=shade(TOWN_CENTER_FILL, light_delta=-0.22),
            linewidths=1.6 * lw_scale, alpha=0.92 if on else 0.8, zorder=2.6))
    if s.cottage_lots:
        ax.add_collection(PolyCollection(
            s.cottage_lots, facecolors=COTTAGE_FILL if on else muted(COTTAGE_FILL),
            edgecolors=shade(COTTAGE_FILL, light_delta=-0.28),
            linewidths=0.5 * lw_scale, alpha=0.95 if on else 0.8, zorder=2.7))
    draw_tc_buildings(ax, s, on=on, lw_scale=lw_scale)
    if label and s.cottage_xy and on:
        ax.annotate(s.cottages_label, s.cottage_xy, ha="center", va="center",
                    fontsize=fontsize, fontproperties=F_BOLD, color="#4A3F2C", zorder=6,
                    path_effects=[pe.withStroke(linewidth=fontsize * 0.5, foreground="white")])


def draw_tc_buildings(ax, s: Scene, *, on: bool = True, lw_scale: float = 1.0) -> None:
    """The Town Center buildings, drawn as measured massing.

    Karen asked for these twice and noted they appear on Minto's site plan.
    They do, but that plan is licensed for use as-is and forbids derivative
    work, so these were measured off georeferenced aerial imagery instead --
    see town_center_buildings.json for the full derivation and for why no
    authoritative dataset and no automatic extraction could supply them.

    They are good to about 5 m, so they are drawn to *look* like massing: solid
    enough to read as buildings at a glance, without the crisp survey edge that
    would claim more precision than was measured. That is the same rule the
    rest of the map follows -- an unverified thing has to look unverified.
    """
    if not s.tc_buildings:
        return
    rings_ = [r for _, _, rr in s.tc_buildings for r in rr]
    if not rings_:
        return
    ax.add_collection(PolyCollection(
        rings_, facecolors=BUILDING_FILL if on else muted(BUILDING_FILL),
        edgecolors=BUILDING_EDGE, linewidths=0.9 * lw_scale,
        alpha=0.95 if on else 0.75, zorder=2.75))


def draw_phases(ax, s: Scene, active: str | None, *, lw_scale: float = 1.0,
                show_lots: str = "active") -> None:
    """Phase fills and lot linework.

    Uses PolyCollection rather than one patch per polygon -- there are 3,229
    lots, and at poster resolution per-patch drawing is the whole render time.
    """
    for p in s.phases:
        lab = p["label"]
        on = lab == active
        colour = s.colour(lab)
        if active is None or on:
            face, alpha = colour, (0.95 if on else 0.92)
            edge = shade(colour, light_delta=-0.30, sat_scale=1.1)
        else:
            # Everything that isn't being discussed drops to a common pale value
            # so the active phase reads instantly.
            face, alpha = muted(colour, light=0.86, sat=0.09), 0.85
            edge = "#B3A992"
        ax.add_collection(PolyCollection(
            s.phase_rings[lab], facecolors=face, alpha=alpha, edgecolors=edge,
            linewidths=(3.2 if on else 1.4) * lw_scale, zorder=2.5 if on else 2))

    # Inactive lots stay on screen, just quietly - the street pattern is what makes
    # the map readable, and dropping it leaves the rest of the community looking empty.
    #
    # Lots take a pale tint of their own phase colour rather than plain white.
    # Drawn white, a fully platted phase reads as a white sheet while an
    # undeveloped one reads as solid colour, which makes build-out look like a
    # colour difference. Tinting keeps every phase reading as its own colour.
    # Inactive lots stay on screen, just quietly - the street pattern is what makes
    # the map readable, and dropping it leaves the rest of the community looking empty.
    #
    # Lots take a pale tint of their own phase colour rather than plain white.
    # Drawn white, a fully platted phase reads as a white sheet while an
    # undeveloped one reads as solid colour, which makes build-out look like a
    # colour difference. Tinting keeps every phase reading as its own colour.
    if show_lots == "none":
        draw_town_center(ax, s, active, lw_scale=lw_scale, label=False)
        draw_ponds(ax, s, lw_scale=lw_scale)
        return
    for p in s.phases:
        lab = p["label"]
        if lab == s.tc_label:
            continue        # drawn by draw_town_center, as a tract plus cottages
        on = lab == active
        rings = s.lot_rings.get(lab)
        if not rings:
            continue
        colour = s.colour(lab)
        if active is not None and not on:
            ax.add_collection(PolyCollection(
                rings, facecolors=muted(colour, light=0.93, sat=0.06),
                alpha=0.85, edgecolors="#BEB3A0",
                linewidths=0.28 * lw_scale, zorder=2.8))
            continue
        if on:
            # Lots of the active phase take a deeper tint of that phase's own
            # colour, so the highlight never needs a second colour of its own.
            face = shade(colour, light_delta=0.14, sat_scale=1.05)
            edge = shade(colour, light_delta=-0.34, sat_scale=1.15)
            lw = 0.55
        else:
            face = shade(colour, light_delta=0.30, sat_scale=0.62)
            edge = shade(colour, light_delta=-0.18, sat_scale=0.75)
            lw = 0.35
        ax.add_collection(PolyCollection(
            rings, facecolors=face, alpha=0.95, edgecolors=edge,
            linewidths=lw * lw_scale, zorder=3))

    draw_town_center(ax, s, active, lw_scale=lw_scale, label=False)
    draw_ponds(ax, s, lw_scale=lw_scale)


def draw_roads(ax, s: Scene, *, lw_scale: float = 1.0, label_hwy: bool = True) -> None:
    for name, route, pts in s.highways:
        ax.plot(*zip(*pts), color="#FFFFFF", lw=5.0 * lw_scale, solid_capstyle="round", zorder=3.4)
        ax.plot(*zip(*pts), color=ROAD, lw=2.4 * lw_scale, solid_capstyle="round", zorder=3.5)
    for name, pts in s.roads:
        ax.plot(*zip(*pts), color="#FFFFFF", lw=2.2 * lw_scale, solid_capstyle="round", zorder=3.2)
        ax.plot(*zip(*pts), color=ROAD, lw=0.9 * lw_scale, alpha=0.8,
                solid_capstyle="round", zorder=3.3)

    if label_hwy and s.hwy79:
        longest = max(s.hwy79, key=len)
        i = len(longest) // 2
        (x, y), (x2, y2) = longest[i], longest[min(i + 1, len(longest) - 1)]
        ang = math.degrees(math.atan2(y2 - y, x2 - x))
        if ang > 90:
            ang -= 180
        elif ang < -90:
            ang += 180
        ax.text(x, y, "HWY 79", fontproperties=F_BOLD, fontsize=10 * lw_scale, color="#FFFFFF",
                ha="center", va="center", rotation=ang, rotation_mode="anchor", zorder=6,
                bbox=dict(boxstyle="round,pad=0.30", fc=ROAD, ec="white", lw=1.2))


def draw_overlays(ax, s: Scene, overlays: set[str], *, lw_scale: float = 1.0) -> None:
    """Optional context rings. Off by default so the map stays clean."""
    if "hwy79" in overlays and s.hwy79:
        for pts in s.hwy79:
            ax.plot(*zip(*pts), color=CORAL, lw=26 * lw_scale, alpha=0.16,
                    solid_capstyle="round", zorder=1.6)

    lat = math.radians(30.32)
    c = s.landmark("Town Square Amenity")
    if not c:
        return

    if "towncenter" in overlays:
        # A half-mile walk ring. This one is a real, defensible measurement.
        r = 0.5 / MI_PER_M / math.cos(lat)
        ax.add_patch(Circle(c, r, facecolor=TEAL, alpha=0.10, edgecolor=TEAL,
                            lw=1.6 * lw_scale, ls=(0, (5, 4)), zorder=1.7))

    if "bandshell" in overlays:
        # Deliberately soft, with no edge and no printed radius. Karen: a loud
        # concert carries "a few miles" and she has heard it in 6B & 6C, 4A and
        # 3D "and maybe more". Sound varies with event volume, wind, season and
        # tree cover, so a crisp ring with a number on it would be a made-up
        # measurement. This is an impression, drawn like one.
        for i in range(28):
            f = i / 27
            r = (0.35 + f * 2.4) / MI_PER_M / math.cos(lat)
            ax.add_patch(Circle(c, r, facecolor=PINK, alpha=0.016 * (1 - f) ** 1.4,
                                edgecolor="none", zorder=1.65))


def draw_landmarks(ax, s: Scene, *, only_anchors: bool = False, lw_scale: float = 1.0) -> None:
    """Draw landmark pins with labels. Call *after* set_view -- placement is
    collision-aware and needs the final axes limits.

    Labels are tried all round the pin, nearest position first, and any label
    that ends up off its pin gets a leader line. Both matter in the amenity
    core, where the Bandshell, Paradise Pool, the kayak launch, the cottages
    and the dog park sit within a few hundred metres of each other. The
    previous version could only push a label straight down, with nothing
    joining it back to its marker -- so the kayak launch ended up apparently
    floating in open ground well south of the water it launches into.
    """
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    span_x, span_y = x1 - x0, y1 - y0

    visible = []
    for l in s.landmarks:
        if only_anchors and not l.get("anchor"):
            continue
        x, y = s.anchor_xy[l["name"]]
        fx, fy = (x - x0) / span_x, (y - y0) / span_y
        if not (-0.01 <= fx <= 1.01 and -0.01 <= fy <= 1.01):
            continue
        visible.append((fy, fx, x, y, l))
    visible.sort(key=lambda t: -t[0])

    ext = ax.get_window_extent()
    ax_w_pt = max(ext.width / ax.figure.dpi * 72, 1.0)
    ax_h_pt = max(ext.height / ax.figure.dpi * 72, 1.0)
    fs = 11 * lw_scale
    h = fs * 1.7 / ax_h_pt

    placed: list[tuple[float, float, float, float]] = []
    for fy, fx, x, y, l in visible:
        ax.plot([x], [y], marker="o", ms=9 * lw_scale, mfc=CORAL, mec="white",
                mew=2.0 * lw_scale, zorder=7)
        label = l["short"] + ("" if l.get("confirmed") else " ?")
        w = len(label) * fs * 0.56 / ax_w_pt

        # Near the right edge a label would run off the map or under the info
        # panel, so try the left of the pin first there.
        sides = (-1, 1) if fx > 0.70 else (1, -1)
        chosen = None
        for step in range(8):
            r = 0.010 + step * 0.024
            for dy_mul in (0.0, 0.8, -0.8, 1.7, -1.7):
                for side in sides:
                    lx, ly = fx + side * r, fy + dy_mul * r
                    bx = lx - w if side < 0 else lx
                    box = (bx - 0.004, ly - h / 2, bx + w + 0.004, ly + h / 2)
                    if box[0] < 0.004 or box[2] > 0.996 or box[1] < 0.004 or box[3] > 0.996:
                        continue
                    if any(box[0] < q[2] and q[0] < box[2]
                           and box[1] < q[3] and q[1] < box[3] for q in placed):
                        continue
                    chosen = (lx, ly, side, box)
                    break
                if chosen:
                    break
            if chosen:
                break
        if chosen is None:
            lx, ly, side = fx + 0.012, fy + 0.016, 1
            chosen = (lx, ly, side, (lx, ly - h / 2, lx + w, ly + h / 2))
        lx, ly, side, box = chosen
        placed.append(box)

        # A displaced label is ambiguous without a leader; a touching one is
        # cluttered by it. Only draw the line once the label has actually moved.
        if math.hypot((lx - fx) * span_x / span_y, ly - fy) > 0.030:
            ax.plot([x, x0 + lx * span_x], [y, y0 + ly * span_y],
                    color=DEEP, lw=0.8 * lw_scale, alpha=0.75, zorder=7.2,
                    solid_capstyle="round")

        t = ax.text(
            x0 + lx * span_x, y0 + ly * span_y, label,
            fontproperties=F_BOLD, fontsize=fs, color=INK, zorder=7.5,
            ha="right" if side < 0 else "left", va="center",
            path_effects=[pe.withStroke(linewidth=3.5 * lw_scale, foreground="white")],
        )
        t.set_clip_on(True)
        t.set_clip_box(ax.bbox)


def draw_street_labels(ax, s: Scene, *, fontsize: float = 5.0,
                       with_ranges: bool = True) -> None:
    """Street names written on the map, at large sizes only.

    County road centrelines only cover Phases 1-3, so a label cannot be hung off
    the line geometry for most of the community. The anchor is instead the centre
    of the parcels carrying that street name, and the angle is the direction that
    run of parcels lies along -- both derived from county record, neither guessed.
    """
    for sl in s.street_labels:
        text = sl["name"]
        if with_ranges and sl["address_range"]:
            lo, hi = sl["address_range"]
            text += "\n" + ident_range(lo, hi)
        t = ax.text(
            sl["xy"][0], sl["xy"][1], text, fontproperties=F_BOLD, fontsize=fontsize,
            color="#2A3F47", ha="center", va="center", rotation=sl["angle"],
            rotation_mode="anchor", zorder=6.5, linespacing=1.25,
            path_effects=[pe.withStroke(linewidth=fontsize * 0.5, foreground="white")],
        )
        t.set_clip_on(True)
        t.set_clip_box(ax.bbox)


def draw_amenity_labels(ax, s: Scene, *, fontsize: float = 6.0,
                        corner: str = "auto") -> None:
    """Name the amenity core on a detailed map.

    Only one Town Center building has a confirmed identity (Google puts its own
    marker on the fitness centre), so the rest of the amenities are listed
    against the tract on a leader rather than attached to a particular roof.
    Guessing which measured block is the theatre would look authoritative and
    be a guess.

    The block is parked in a corner rather than hung off the pin. Hanging it
    off the pin put it straight over the Town Center on the zoomed frame,
    hiding the very thing being named, and the list is tall enough that no
    fixed offset stays clear at every zoom. `corner` is explicit where the
    layout already owns some corners -- the video frames carry a locator inset
    top-left and an info panel down the right, which "auto" cannot know about.
    """
    c = s.landmark("Town Square Amenity")
    if not c or not s.meta.get("amenities"):
        return
    names = s.meta["amenities"]
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()

    if corner == "auto":
        # Just below-left of the pin, clamped inside the axes. On a big sheet
        # this is the tidy option: the block sits beside what it names on a
        # short leader. It only fails when the map is zoomed right into the
        # tract, where a near-pin block covers the subject -- hence `corner`.
        ax_h_pt = ax.get_window_extent().height / ax.figure.dpi * 72
        block_frac = (len(names) + 1) * fontsize * 1.55 / max(ax_h_pt, 1)
        ly = min(max((c[1] - y0) / (y1 - y0) - 0.02, block_frac + 0.03), 0.98)
        tx, ty = c[0] - (x1 - x0) * 0.045, y0 + ly * (y1 - y0)
        ha, va = "right", "top"
    else:
        vert, horiz = corner.split("-")
        right, top = horiz == "right", vert == "top"
        lx = 0.985 if right else 0.015
        # Bottom placements clear the scale bar, which is drawn afterwards along
        # the bottom-left and would otherwise be struck through the list.
        ly = 0.975 if top else 0.075
        tx, ty = x0 + lx * (x1 - x0), y0 + ly * (y1 - y0)
        ha, va = ("right" if right else "left"), ("top" if top else "bottom")

    ax.annotate(
        "", xy=c, xytext=(tx, ty),
        arrowprops=dict(arrowstyle="-", color=DEEP, lw=0.9, alpha=0.8), zorder=7.4,
    )
    body = "\n".join("\u00b7 " + a for a in names)
    t = ax.text(
        tx, ty, "AT THE TOWN CENTER\n" + body, fontproperties=F_REG, fontsize=fontsize,
        color=INK, ha=ha, va=va, zorder=7.6, linespacing=1.55,
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=DIM_EDGE, lw=0.8, alpha=0.93),
    )
    t.set_clip_on(True)
    t.set_clip_box(ax.bbox)


def draw_phase_labels(ax, s: Scene, active: str | None, *, lw_scale: float = 1.0,
                      show_plat: bool = False) -> None:
    for p in s.phases:
        lab = p["label"]
        on = lab == active
        if active is not None and not on:
            continue
        x, y = s.centroids[lab]
        text = p["short"] if active is None else p["label"]
        if show_plat:
            text += f"\n{p['plat']}"
        if p.get("karen_lives_here"):
            text += "  \u2014 Karen lives here" if on else " \u2665"
        colour = s.colour(lab)
        if on and p.get("karen_lives_here"):
            fc, tc = PINK, "white"
        elif on:
            fc, tc = shade(colour, light_delta=-0.34, sat_scale=1.1), "white"
        else:
            fc, tc = "white", INK
        ax.text(
            x, y, text, fontproperties=F_BLACK if on else F_BOLD,
            fontsize=(15 if on else 9.5) * lw_scale, color=tc,
            ha="center", va="center", zorder=8, linespacing=1.35,
            bbox=dict(boxstyle="round,pad=0.42", fc=fc,
                      ec="white" if on else shade(colour, light_delta=-0.22),
                      lw=1.8 if on else 1.1, alpha=0.96),
        )


def set_view(ax, box, pad_frac: float, aspect: float) -> None:
    """Frame `box` at `aspect` (w/h), padded, without distorting the geometry."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * (1 + pad_frac), (y1 - y0) * (1 + pad_frac)
    if w / h < aspect:
        w = h * aspect
    else:
        h = w / aspect
    ax.set_xlim(cx - w / 2, cx + w / 2)
    ax.set_ylim(cy - h / 2, cy + h / 2)
    ax.set_aspect("equal")
    ax.axis("off")


def ax_aspect(fig, rect) -> float:
    """Width/height of an axes rectangle in real inches."""
    fw, fh = fig.get_size_inches()
    return (fw * rect[2]) / (fh * rect[3])


def phase_box(s: Scene, label: str):
    pts = [pt for r in s.phase_rings[label] for pt in r]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def scale_bar(ax, s: Scene, *, lw_scale: float = 1.0) -> None:
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    lat = math.radians(30.32)
    half_mi = 0.5 / MI_PER_M / math.cos(lat)
    if half_mi > (x1 - x0) * 0.35:
        half_mi /= 2
        label = "\u00bc mile"
    else:
        label = "\u00bd mile"
    bx = x0 + (x1 - x0) * 0.045
    by = y0 + (y1 - y0) * 0.055
    ax.plot([bx, bx + half_mi], [by, by], color=INK, lw=3.2 * lw_scale,
            solid_capstyle="butt", zorder=9)
    for x in (bx, bx + half_mi):
        ax.plot([x, x], [by - (y1 - y0) * 0.008, by + (y1 - y0) * 0.008],
                color=INK, lw=3.2 * lw_scale, zorder=9)
    ax.text(bx + half_mi / 2, by + (y1 - y0) * 0.014, label, fontproperties=F_BOLD,
            fontsize=8.5 * lw_scale, color=INK, ha="center", va="bottom", zorder=9,
            path_effects=[pe.withStroke(linewidth=3, foreground="white")])


def north_arrow(ax, s: Scene, *, lw_scale: float = 1.0) -> None:
    """North is rotated with the map, so the arrow has to be too."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    span = (y1 - y0)
    x = x1 - (x1 - x0) * 0.045
    y = y0 + span * 0.085
    ang = math.radians(90 + s.north_deg)
    dx, dy = math.cos(ang) * span * 0.05, math.sin(ang) * span * 0.05
    ax.annotate("", xy=(x + dx, y + dy), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2 * lw_scale), zorder=9)
    ax.text(x + dx * 1.5, y + dy * 1.5, "N", fontproperties=F_BLACK, fontsize=12 * lw_scale,
            color=INK, ha="center", va="center", zorder=9,
            path_effects=[pe.withStroke(linewidth=3.5, foreground="white")])


def legend(ax, s: Scene, *, lw_scale: float = 1.0, loc="lower left") -> None:
    """Phase swatch key. Sub-phases of one number share a hue, so the key also
    teaches the numbering scheme."""
    handles = [
        MPoly([(0, 0)], facecolor=s.colour(p["label"]), edgecolor=shade(s.colour(p["label"]),
              light_delta=-0.30), lw=1.0, alpha=0.8,
              label=f"{p['short']}   {p['plat']}")
        for p in s.phases
    ]
    if s.cottage_lots:
        handles.append(MPoly([(0, 0)], facecolor=COTTAGE_FILL,
                             edgecolor=shade(COTTAGE_FILL, light_delta=-0.28), lw=1.0, alpha=0.9,
                             label=f"{s.cottages_label}   (in PB 32/81)"))
    if s.ponds:
        handles.append(MPoly([(0, 0)], facecolor=POND_FILL, edgecolor=WATER_EDGE, lw=1.0,
                             alpha=0.95, label="Water \u2014 bay, lakes & ponds"))
    handles.append(
        Line2D([0], [0], marker="o", ms=8, mfc=CORAL, mec="white", mew=1.6, ls="none",
               label="Landmark  (\u201c?\u201d = awaiting confirmation)")
    )
    leg = ax.legend(handles=handles, loc=loc, frameon=True, ncol=2,
                    prop=FontProperties(fname=F_REG.get_file(), size=9.0 * lw_scale),
                    borderpad=0.8, labelspacing=0.42, handlelength=1.4,
                    columnspacing=1.4, title="Phases  \u00b7  recorded plat")
    leg.get_title().set_fontproperties(FontProperties(fname=F_BOLD.get_file(),
                                                      size=9.5 * lw_scale))
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_edgecolor(DIM_EDGE)
    leg.get_frame().set_alpha(0.95)
    leg.set_zorder(10)


def draw_watermark(ax, s: Scene, *, fontsize: float = 9.0, alpha: float = 0.115,
                   angle: float = -28.0) -> None:
    """Tile the ownership line faintly across the map body.

    Sits above the fills but *below* every label, so it can never cost
    legibility -- which is the whole point of this map. Deliberately a fixed
    diagonal rather than aligned to the scene rotation, because an aligned
    repeat reads as a data label instead of a watermark.

    It doubles as marketing: if someone lifts the map, the phone number goes
    with it.
    """
    text = (s.meta.get("watermark") or {}).get("text")
    if not text:
        return
    # Tile in axes fraction so spacing is independent of zoom and output size.
    step_x, step_y = 0.42, 0.155
    rows = int(1 / step_y) + 3
    cols = int(1 / step_x) + 3
    for r in range(-1, rows):
        for c in range(-1, cols):
            x = c * step_x + (r % 2) * step_x / 2 - 0.15
            y = r * step_y - 0.10
            t = ax.text(x, y, text, transform=ax.transAxes,
                        fontproperties=F_BOLD, fontsize=fontsize, color=INK,
                        alpha=alpha, ha="left", va="center", rotation=angle,
                        rotation_mode="anchor", zorder=5.5)
            t.set_clip_on(True)
            t.set_clip_box(ax.bbox)


def copyright_line(s: Scene) -> str:
    c = s.meta.get("copyright") or {}
    return c.get("notice", "")


def credit_line(s: Scene) -> str:
    """Four lines: sources, the standing disclaimer, scope, ownership.

    Kept as separate lines rather than one run-on: at poster width a single
    line of this length clips at both margins, and the first thing lost is the
    disclaimer, which is the one part that is not optional.
    """
    return (
        f"{s.meta['data_credit']}  \u00b7  retrieved {date.today().isoformat()}\n"
        f"{s.meta['disclaimer']}\n"
        f"{s.meta.get('scope', {}).get('note', '')}\n"
        f"{copyright_line(s)}"
    )


# ---------------------------------------------------------------- exports
POSTER_RECT = [0.025, 0.075, 0.95, 0.845]


class Preset:
    """A named output size.

    `sheet` puts the map in a band across the top and a reference index below.
    The community is ~3.1:1, so on a 3:2 sheet a full-width map only fills the
    top third -- rather than pad that with whitespace or distort the geometry,
    the space carries the street and address index that makes the big map worth
    printing.

    `panorama` is map-dominant, for the screen-shaped poster.
    """

    def __init__(self, kind, w_in, h_in, dpi, formats, detail="clean", bleed_in=0.0):
        self.kind, self.w, self.h = kind, w_in, h_in
        self.dpi, self.formats, self.detail, self.bleed = dpi, formats, detail, bleed_in

    @property
    def pixels(self):
        return round(self.w * self.dpi), round(self.h * self.dpi)

    def describe(self):
        px = f"{self.pixels[0]:,} x {self.pixels[1]:,} px" if "png" in self.formats else "vector"
        return f"{self.w:g} x {self.h:g} in @ {self.dpi} dpi  ({px})"


PRESETS = {
    "poster":       Preset("panorama", 20, 12, 400, ("png",)),
    "print-36x24":  Preset("sheet", 36, 24, 150, ("pdf", "svg"), "full", 0.25),
    "print-48x32":  Preset("sheet", 48, 32, 150, ("pdf", "svg"), "full", 0.25),
    "giant-raster": Preset("sheet", 54, 36, 300, ("png",), "full"),
}


def _flow_reference(fig, s: Scene, rect, *, min_pt: float = 3.5,
                    max_pt: float = 14.0, min_col_in: float = 2.2) -> None:
    """The street + address index, flowed to fill the space it is given.

    This is the layer that makes a printed map a reference document: point at a
    street, read off the phase and the house-number range without looking
    anything up. Type is sized up until the content just fills the band, rather
    than left small with dead space under it.
    """
    x0, y0, w, h = rect
    blocks = []
    for p in s.phases:
        lines = [("head", f"{p['label']}   {p['plat']}"),
                 ("sub", f"{p['lot_count']:,} homesites \u00b7 {p['acres']:,.0f} acres")]
        for st in p.get("streets", []):
            r = st.get("address_range")
            lines.append(("row", (st["name"], ident_range(r[0], r[1]) if r else "\u2014")))
        lines.append(("gap", ""))
        blocks.append(lines)

    fig_w_in, fig_h_in = fig.get_size_inches()

    def pack(pt):
        """Lay the blocks into columns at this type size, or None if it won't fit."""
        line_h = pt * 1.55 / (fig_h_in * 72)
        per_col = int(h / line_h)
        if per_col < 4:
            return None
        cols, cur, used = [], [], 0
        for b in blocks:
            if used + len(b) > per_col and cur:   # never split a phase across columns
                cols.append(cur)
                cur, used = [], 0
            cur.append(b)
            used += len(b)
        if cur:
            cols.append(cur)
        if (w * fig_w_in) / len(cols) < min_col_in:
            return None
        return cols, line_h

    best = None
    pt = min_pt
    while pt <= max_pt:
        got = pack(pt)
        if got is None:
            break
        best, best_pt = got, pt
        pt += 0.25
    if best is None:
        return
    cols, line_h = best

    col_w = w / len(cols)
    for ci, col in enumerate(cols):
        cx = x0 + ci * col_w
        y = y0 + h
        for block in col:
            for kind, val in block:
                if kind == "gap":
                    y -= line_h * 0.6
                    continue
                if kind == "head":
                    fig.text(cx, y, val, fontproperties=F_BLACK, fontsize=best_pt * 1.05,
                             color=INK, ha="left", va="top")
                elif kind == "sub":
                    fig.text(cx, y, val, fontproperties=F_REG, fontsize=best_pt * 0.9,
                             color=MUTED, ha="left", va="top")
                else:
                    name, rng = val
                    fig.text(cx + col_w * 0.03, y, name, fontproperties=F_REG,
                             fontsize=best_pt, color="#2A3F47", ha="left", va="top")
                    fig.text(cx + col_w * 0.90, y, rng, fontproperties=F_REG,
                             fontsize=best_pt, color=MUTED, ha="right", va="top")
                y -= line_h


def render_sheet(s: Scene, preset: Preset, overlays: set[str], name: str,
                 *, watermark: bool = True) -> list[Path]:
    """Large-format sheet: title band, map band, reference index, footer."""
    fig = plt.figure(figsize=(preset.w, preset.h), dpi=preset.dpi, facecolor=SAND)
    W, H = preset.w, preset.h
    margin = max(0.75, min(W, H) * 0.035)
    safe = margin + preset.bleed          # keep type clear of the trim
    inx = lambda v: v / W
    iny = lambda v: v / H

    title_h = H * 0.075
    footer_h = H * 0.055
    map_w = W - 2 * safe
    map_h = min(map_w / 3.0, H - 2 * safe - title_h - footer_h - H * 0.30)
    map_rect = [inx(safe), iny(H - safe - title_h - map_h), inx(map_w), iny(map_h)]

    ax = fig.add_axes(map_rect)
    ax.set_facecolor(LAND)
    lw = max(1.0, W / 22)
    draw_base(ax, s, lw_scale=lw * 0.7)
    draw_phases(ax, s, None, lw_scale=lw * 0.6, show_lots="all")
    draw_roads(ax, s, lw_scale=lw * 0.7)
    draw_overlays(ax, s, overlays, lw_scale=lw)
    draw_phase_labels(ax, s, None, lw_scale=lw * 0.75, show_plat=True)
    set_view(ax, s.extent, 0.04, ax_aspect(fig, map_rect))
    if watermark:
        draw_watermark(ax, s, fontsize=max(7.5, W * 0.42))
    if preset.detail == "full":
        draw_street_labels(ax, s, fontsize=max(3.6, W * 0.13))
        draw_amenity_labels(ax, s, fontsize=max(4.5, W * 0.16))
    draw_landmarks(ax, s, lw_scale=lw * 0.8)
    scale_bar(ax, s, lw_scale=lw * 0.8)
    north_arrow(ax, s, lw_scale=lw * 0.8)

    fig.text(inx(safe), iny(H - safe * 0.75), "Latitude Margaritaville Watersound",
             fontproperties=F_BLACK, fontsize=W * 1.05, color=INK, ha="left", va="top")
    fig.text(inx(safe), iny(H - safe * 0.75 - title_h * 0.55),
             f"Area 1 \u00b7 {s.summary} \u00b7 {s.total_acres:,.0f} acres \u00b7 "
             f"every boundary from Bay County public record",
             fontproperties=F_REG, fontsize=W * 0.45, color=MUTED, ha="left", va="top")
    fig.text(inx(W - safe), iny(H - safe * 0.75), "  \u00b7  ".join(s.meta["agent_block"]),
             fontproperties=F_BOLD, fontsize=W * 0.40, color=DEEP, ha="right", va="top")

    ref_top = map_rect[1] - iny(H * 0.030)
    ref_bottom = iny(safe + footer_h)
    _flow_reference(fig, s, [inx(safe), ref_bottom, inx(map_w), ref_top - ref_bottom])

    fig.text(inx(safe), iny(safe * 0.75), credit_line(s), fontproperties=F_REG,
             fontsize=W * 0.28, color=MUTED, ha="left", va="bottom", linespacing=1.6)

    # The sheet labels every phase in place, so it needs no colour key -- but it
    # does print "?" on unconfirmed landmarks, and an unexplained "?" on a wall
    # map is worse than no mark at all. The poster says this in its legend.
    if s.needs_confirmation:
        fig.text(inx(W - safe), iny(safe * 0.75),
                 "Landmark \u201c?\u201d = position not yet confirmed",
                 fontproperties=F_REG, fontsize=W * 0.28, color=MUTED,
                 ha="right", va="bottom")

    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for fmt in preset.formats:
        path = OUT / f"{name}.{fmt}"
        fig.savefig(path, facecolor=SAND, format=fmt)
        written.append(path)
    plt.close(fig)
    return written


def render_poster(s: Scene, overlays: set[str], *, pdf: bool = False,
                  watermark: bool = True) -> Path:
    # 20 x 12 in at 400 dpi = 8000 x 4800.
    fig = plt.figure(figsize=(20, 12), dpi=400 if not pdf else 150, facecolor=SAND)
    ax = fig.add_axes(POSTER_RECT)
    ax.set_facecolor(LAND)

    draw_base(ax, s)
    draw_phases(ax, s, None, show_lots="all")
    draw_roads(ax, s)
    draw_overlays(ax, s, overlays)
    draw_phase_labels(ax, s, None)
    set_view(ax, s.extent, 0.05, ax_aspect(fig, POSTER_RECT))
    if watermark:
        draw_watermark(ax, s, fontsize=14.0)
    draw_landmarks(ax, s)
    scale_bar(ax, s)
    north_arrow(ax, s)
    legend(ax, s)

    fig.text(0.025, 0.955, "Latitude Margaritaville Watersound", fontproperties=F_BLACK,
             fontsize=36, color=INK, ha="left", va="center")
    fig.text(0.025, 0.921, "Area 1 \u2014 every recorded phase, drawn from Bay County public records",
             fontproperties=F_REG, fontsize=16, color=MUTED, ha="left", va="center")
    fig.text(0.975, 0.955, f"{s.summary}  \u00b7  {s.total_acres:,.0f} acres",
             fontproperties=F_BOLD, fontsize=15, color=DEEP, ha="right", va="center")
    fig.text(0.975, 0.921, "  \u00b7  ".join(s.meta["agent_block"]), fontproperties=F_REG,
             fontsize=12, color=MUTED, ha="right", va="center")
    fig.text(0.5, 0.032, credit_line(s), fontproperties=F_REG, fontsize=9.5,
             color=MUTED, ha="center", va="center", linespacing=1.55)

    OUT.mkdir(parents=True, exist_ok=True)
    if pdf:
        path = OUT / "latitude-phase-map.pdf"
        with PdfPages(path) as pp:
            pp.savefig(fig, facecolor=SAND)
    else:
        path = OUT / "latitude-phase-map.png"
        fig.savefig(path, facecolor=SAND)
    plt.close(fig)
    return path


def render_thumbnail(s: Scene, overlays: set[str]) -> Path:
    """Thumbnail base plate: Karen's phase highlighted, left third left clear
    for her cutout. See platforms/youtube/.../thumbnail-brief.md."""
    karen = next((p["label"] for p in s.phases if p.get("karen_lives_here")), None)
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=SAND)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(LAND)
    draw_base(ax, s, lw_scale=1.3)
    draw_phases(ax, s, karen, lw_scale=1.3, show_lots="all")
    draw_roads(ax, s, lw_scale=1.3, label_hwy=False)
    set_view(ax, s.extent, 0.02, 16 / 9)
    draw_landmarks(ax, s, only_anchors=True, lw_scale=1.4)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "latitude-phase-map-thumbnail.png"
    fig.savefig(path, facecolor=SAND)
    plt.close(fig)
    return path


def _panel_text(fig, s: Scene, p: dict) -> None:
    """Right-hand info panel for a phase frame.

    Everything here is permanent public record. Live inventory is deliberately
    absent -- it is spoken and dated at record time, never printed.
    """
    x = 0.735
    fig.patches.append(
        FancyBboxPatch((0.715, 0.03), 0.27, 0.94, boxstyle="round,pad=0.006",
                       transform=fig.transFigure, facecolor=NAVY, edgecolor=DEEP,
                       lw=2, zorder=20, mutation_aspect=0.6)
    )
    y = 0.90
    fig.text(x, y, p["label"].upper(), fontproperties=F_BLACK, fontsize=30,
             color="white", ha="left", va="center", zorder=21)
    y -= 0.055
    if p.get("karen_lives_here"):
        fig.text(x, y, "\u2665  Karen lives here", fontproperties=F_BOLD, fontsize=15,
                 color=PINK, ha="left", va="center", zorder=21)
        y -= 0.050
    if p.get("hwy79_audible"):
        fig.text(x, y, "You can hear Highway 79 here", fontproperties=F_BOLD,
                 fontsize=12, color=GOLD, ha="left", va="center", zorder=21)
        y -= 0.026
        fig.text(x, y, "Karen, first-hand", fontproperties=F_REG,
                 fontsize=9.5, color=TEAL, ha="left", va="center", zorder=21)
        y -= 0.032

    rows = [
        ("Recorded plat", p["plat"]),
        (p.get("homesite_label") or "Platted homesites", f"{p['lot_count']:,}"),
        ("Size", f"{p['acres']:,.0f} acres"),
    ]
    if p.get("lot_number_range"):
        lo, hi = p["lot_number_range"]
        rows.append(("Lot numbers", ident_range(lo, hi, dash=" \u2013 ")))
    # Distance to the Town Center is meaningless on the Town Center's own frame.
    if p["label"] != s.tc_label:
        for key, target in (("To Town Center", "Town Square Amenity"),):
            d = s.distance_mi(p, target)
            if d is not None:
                rows.append((key, f"{d:.1f} mi"))
    d79 = s.hwy79_distance_mi(p)
    if d79 is not None:
        rows.append(("To Hwy 79", f"{d79:.1f} mi"))

    for key, val in rows:
        fig.text(x, y, key.upper(), fontproperties=F_REG, fontsize=9.5, color=TEAL,
                 ha="left", va="center", zorder=21)
        fig.text(x + 0.245, y, val, fontproperties=F_BOLD, fontsize=13, color="white",
                 ha="right", va="center", zorder=21)
        y -= 0.043

    streets = [st["name"] for st in p.get("streets", [])]
    if streets:
        y -= 0.012
        fig.text(x, y, "STREETS", fontproperties=F_REG, fontsize=9.5, color=TEAL,
                 ha="left", va="center", zorder=21)
        y -= 0.030
        for name in streets[:9]:
            fig.text(x, y, name, fontproperties=F_REG, fontsize=11.5, color="#DCE8EA",
                     ha="left", va="center", zorder=21)
            y -= 0.028
        if len(streets) > 9:
            fig.text(x, y, f"+{len(streets) - 9} more", fontproperties=F_REG, fontsize=11,
                     color=MUTED, ha="left", va="center", zorder=21)
            y -= 0.028

    note = p.get("karen_says") or p.get("note") or ""
    if note:
        y = max(y - 0.015, 0.10)
        # Silently dropping the tail of a note is how a hedged statement turns
        # into an unhedged one, so an over-long note is flagged rather than cut.
        wrapped = _wrap(note, 34)
        limit = max(1, int((y - 0.055) / 0.026))
        if len(wrapped) > limit:
            print(f"  NOTE TOO LONG for the {p['label']} panel: "
                  f"{len(wrapped)} lines, room for {limit}. Shorten it in phase_meta.json.")
            wrapped = wrapped[:limit - 1] + ["..."]
        for ln in wrapped:
            fig.text(x, y, ln, fontproperties=F_REG, fontsize=11, color="#9FB6BC",
                     ha="left", va="center", zorder=21)
            y -= 0.026


def _wrap(text: str, width: int) -> list[str]:
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


def _locator_inset(fig, s: Scene, active: str) -> None:
    rect = [0.022, 0.695, 0.145, 0.235]
    fig.patches.append(
        Rectangle((rect[0] - 0.007, rect[1] - 0.012), rect[2] + 0.014, rect[3] + 0.024,
                  transform=fig.transFigure, facecolor="white", edgecolor=DIM_EDGE,
                  lw=1.2, zorder=14)
    )
    ax = fig.add_axes(rect, zorder=15)
    ax.set_facecolor("white")
    for p in s.phases:
        on = p["label"] == active
        for pts in s.phase_rings[p["label"]]:
            ax.add_patch(MPoly(pts, closed=True, facecolor=DEEP if on else "#D5CBB6",
                               edgecolor="white", lw=0.5, alpha=1.0 if on else 0.95, zorder=2))
    set_view(ax, s.extent, 0.06, ax_aspect(fig, rect))
    ax.text(0.5, 1.06, "WHERE THIS IS IN THE COMMUNITY", transform=ax.transAxes,
            fontproperties=F_BOLD, fontsize=8.5, color=MUTED, ha="center", va="bottom")


SEQ_RECT = [0.015, 0.055, 0.685, 0.855]


def render_sequence(s: Scene, overlays: set[str]) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    frames_dir = OUT / "frames"
    frames_dir.mkdir(exist_ok=True)
    # Frames are numbered by position, so renaming or reordering a phase leaves
    # the old file behind under its old number. An editor pulling frames by
    # filename would then cut a stale image into the video.
    for stale in frames_dir.glob("*.png"):
        stale.unlink()
    written: list[Path] = []

    def new_fig():
        # 3840 x 2160 -- 4K, so the editor has room to push in on a phase before
        # exporting at 1080p.
        fig = plt.figure(figsize=(19.2, 10.8), dpi=200, facecolor=SAND)
        ax = fig.add_axes(SEQ_RECT)
        ax.set_facecolor(LAND)
        return fig, ax

    def footer(fig):
        fig.text(0.015, 0.026, credit_line(s), fontproperties=F_REG, fontsize=8.0,
                 color=MUTED, ha="left", va="center", zorder=1, linespacing=1.5)

    # 00 - the whole community
    fig, ax = new_fig()
    aspect = ax_aspect(fig, SEQ_RECT)
    draw_base(ax, s)
    draw_phases(ax, s, None, show_lots="all")
    draw_roads(ax, s)
    draw_overlays(ax, s, overlays)
    draw_phase_labels(ax, s, None)
    set_view(ax, s.extent, 0.04, aspect)
    draw_landmarks(ax, s)
    scale_bar(ax, s)
    north_arrow(ax, s)
    legend(ax, s, loc="lower left")
    fig.text(0.722, 0.905, "ALL 16 PHASES", fontproperties=F_BLACK, fontsize=30,
             color=INK, ha="left", va="center")
    fig.text(0.722, 0.872, "Area 1 \u2014 Phases 1 to 10. Every one is a separate\n"
                           "recorded plat, with a book and page you can look up.",
             fontproperties=F_REG, fontsize=12.5, color=MUTED, ha="left", va="top")
    yy = 0.792
    for p in s.phases:
        fig.text(0.722, yy, p["short"], fontproperties=F_BOLD, fontsize=12.5, color=INK,
                 ha="left", va="center")
        fig.text(0.986, yy, f"{p['plat']}   {p['lot_count']:>4} lots", fontproperties=F_REG,
                 fontsize=12, color=MUTED, ha="right", va="center")
        yy -= 0.0405
    footer(fig)
    path = frames_dir / "00_all-phases.png"
    fig.savefig(path, facecolor=SAND)
    plt.close(fig)
    written.append(path)
    print(f"  {path.name}")

    # one frame per phase, zoomed, with the anchors kept on screen
    for i, p in enumerate(s.phases, 1):
        lab = p["label"]
        fig, ax = new_fig()
        draw_base(ax, s, lw_scale=1.4)
        draw_phases(ax, s, lab, lw_scale=1.4)
        draw_roads(ax, s, lw_scale=1.4, label_hwy=True)
        draw_overlays(ax, s, overlays, lw_scale=1.4)
        draw_phase_labels(ax, s, lab, lw_scale=1.4)

        box = phase_box(s, lab)
        # Keep the Sales Center and Town Center in shot so viewers stay oriented.
        # Not on the Town Center's own frame though: the Sales Center is 1.5 km
        # north-east, so anchoring to it zoomed this frame out until the tract
        # was a thumbnail and its buildings, cottages and pool were invisible --
        # on the one frame whose whole job is to show what is in there. The
        # locator inset already says where it sits in the community.
        anchors = [] if lab == s.tc_label else [
            s.landmark(n) for n in ("Sales Center", "Town Square Amenity")]
        xs = [box[0], box[2]] + [a[0] for a in anchors if a]
        ys = [box[1], box[3]] + [a[1] for a in anchors if a]
        set_view(ax, (min(xs), min(ys), max(xs), max(ys)), 0.12, aspect)
        draw_landmarks(ax, s, only_anchors=False, lw_scale=1.4)
        # On the Town Center frame the viewer is looking straight at the amenity
        # core and will ask what is in it, so name the amenities here. The
        # buildings themselves are drawn as measured massing by
        # draw_tc_buildings, but only one of them has a confirmed identity, so
        # the rest of the names are listed against the tract rather than
        # attached to a particular roof.
        if lab == "Town Center":
            draw_amenity_labels(ax, s, fontsize=11.0, corner="bottom-left")
        scale_bar(ax, s, lw_scale=1.2)
        north_arrow(ax, s, lw_scale=1.2)
        _panel_text(fig, s, p)
        _locator_inset(fig, s, lab)
        footer(fig)

        slug = lab.lower().replace("phase ", "phase-").replace(" & ", "-").replace(" ", "")
        path = frames_dir / f"{i:02d}_{slug}.png"
        fig.savefig(path, facecolor=SAND)
        plt.close(fig)
        written.append(path)
        print(f"  {path.name}")

    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+",
                    choices=["poster", "print", "thumbnail", "sequence"],
                    help="render a subset of the standard outputs")
    ap.add_argument("--preset", nargs="+", choices=sorted(PRESETS),
                    help="large-format sizes: " + ", ".join(
                        f"{k} ({v.describe()})" for k, v in PRESETS.items()))
    ap.add_argument("--size", nargs=2, type=float, metavar=("WIDTH_IN", "HEIGHT_IN"),
                    help="one-off sheet size in inches, instead of a preset")
    ap.add_argument("--dpi", type=int, default=300, help="dpi for --size (default 300)")
    ap.add_argument("--detail", choices=["clean", "full"], default="full",
                    help="'full' adds street names, address ranges and the "
                         "amenity list; only sensible at large sizes")
    ap.add_argument("--overlays", nargs="*", default=[],
                    choices=["hwy79", "towncenter", "bandshell"],
                    help="optional context layers; off by default to keep the map clean")
    ap.add_argument("--check-palette", action="store_true",
                    help="report perceptual separation between phase colours and exit")
    ap.add_argument("--no-watermark", action="store_true",
                    help="render without the tiled ownership watermark")
    args = ap.parse_args()

    s = Scene(load_features())
    if args.check_palette:
        # The cottages are not a phase and so are not in the phase palette, but
        # they are a fill on the same paper and have to clear it just the same.
        palette_report({**s.palette, s.cottages_label: COTTAGE_FILL})
        return
    overlays = set(args.overlays)
    wm = not args.no_watermark

    if args.size:
        w, h = args.size
        name = f"latitude-phase-map-{w:g}x{h:g}"
        p = Preset("sheet", w, h, args.dpi, ("png", "pdf"), args.detail, 0.25)
        print(f"{name}  {p.describe()}")
        for out in render_sheet(s, p, overlays, name, watermark=wm):
            print(f"  -> {out.name}")

    for key in args.preset or []:
        p = PRESETS[key]
        name = f"latitude-phase-map-{key}"
        print(f"{key}  {p.describe()}")
        for out in render_sheet(s, p, overlays, name, watermark=wm):
            print(f"  -> {out.name}  ({out.stat().st_size / 1e6:.1f} MB)")

    if args.preset or args.size:
        if not args.only:
            _report_needs(s)
            return

    jobs = args.only or ["poster", "print", "thumbnail", "sequence"]
    if "poster" in jobs:
        print("poster ->", render_poster(s, overlays, watermark=wm).name)
    if "print" in jobs:
        print("print  ->", render_poster(s, overlays, pdf=True, watermark=wm).name)
    if "thumbnail" in jobs:
        print("thumb  ->", render_thumbnail(s, overlays).name)
    if "sequence" in jobs:
        print("sequence:")
        got = render_sequence(s, overlays)
        print(f"  {len(got)} frames -> output/frames/")
    _report_needs(s)


def _report_needs(s: Scene) -> None:
    if s.needs_confirmation:
        print("\nNEEDS CONFIRMATION before publishing:")
    for l in s.needs_confirmation:
        print(f"  landmark '{l['name']}': {l.get('needs', 'unconfirmed')}")


if __name__ == "__main__":
    main()




