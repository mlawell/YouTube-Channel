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
import json
import math
import os
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Polygon as MPoly, Rectangle

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

STATUS = {
    "new-build": ("#1FB894", "New-build homesites available"),
    "resale-only": ("#F2856B", "Resale only \u2014 no new-build homesites"),
    "unconfirmed": ("#B9B2A4", "Status not yet confirmed"),
}

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
        self.provisional = [p["label"] for p in self.phases if not p.get("confirmed")]

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

    def status(self, p: dict) -> tuple[str, str]:
        return STATUS.get(p.get("availability", "unconfirmed"), STATUS["unconfirmed"])

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


def draw_phases(ax, s: Scene, active: str | None, *, lw_scale: float = 1.0,
                show_lots: str = "active") -> None:
    for p in s.phases:
        lab = p["label"]
        on = lab == active
        colour, _ = s.status(p)
        face = colour if (on or active is None) else DIM_FILL
        alpha = 0.62 if on else (0.55 if active is None else 0.42)
        edge = DEEP if on else ("#7E8F86" if active is None else "#A99C86")
        for pts in s.phase_rings[lab]:
            ax.add_patch(MPoly(pts, closed=True, facecolor=face, alpha=alpha,
                               edgecolor=edge, lw=(3.2 if on else 1.5) * lw_scale,
                               zorder=2 if not on else 2.5))

    # Inactive lots stay on screen, just quietly - the street pattern is what makes
    # the map readable, and dropping it leaves the rest of the community looking empty.
    if show_lots == "none":
        return
    for p in s.phases:
        lab = p["label"]
        on = lab == active
        if show_lots == "active" and active and not on:
            for pts in s.lot_rings.get(lab, []):
                ax.add_patch(MPoly(pts, closed=True, facecolor="#FFFFFF", alpha=0.5,
                                   edgecolor="#B8AC97", lw=0.28 * lw_scale, zorder=2.8))
            continue
        for pts in s.lot_rings.get(lab, []):
            ax.add_patch(MPoly(pts, closed=True,
                               facecolor=GOLD if on else "#FFFFFF",
                               alpha=0.95 if on else 0.85,
                               edgecolor="#9C6B00" if on else "#9A8E78",
                               lw=(0.5 if on else 0.35) * lw_scale, zorder=3))


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
    for key, landmark, miles, colour in (
        ("towncenter", "Town Square Amenity", 0.5, TEAL),
        ("bandshell", "Bandshell", 0.5, PINK),
    ):
        if key not in overlays:
            continue
        c = s.landmark(landmark)
        if not c:
            continue
        radius = miles / MI_PER_M / math.cos(lat)
        ax.add_patch(Circle(c, radius, facecolor=colour, alpha=0.10, edgecolor=colour,
                            lw=1.6 * lw_scale, ls=(0, (5, 4)), zorder=1.7))


def draw_landmarks(ax, s: Scene, *, only_anchors: bool = False, lw_scale: float = 1.0) -> None:
    """Draw landmark pins with labels. Call *after* set_view -- placement is
    collision-aware and needs the final axes limits."""
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

    gap = 0.036 * lw_scale
    placed: list[tuple[float, float]] = []
    for fy, fx, x, y, l in visible:
        ax.plot([x], [y], marker="o", ms=9 * lw_scale, mfc=CORAL, mec="white",
                mew=2.0 * lw_scale, zorder=7)
        # Near the right edge the label would run off the map (or under the
        # info panel), so hang it off the left of the pin instead.
        flip = fx > 0.70
        lx = fx - 0.012 if flip else fx + 0.012
        ly = fy + 0.016
        while any(abs(ly - py) < gap and abs(lx - px) < 0.24 for px, py in placed):
            ly -= gap
        placed.append((lx, ly))
        label = l["short"] + ("" if l.get("confirmed") else " ?")
        t = ax.text(
            x0 + lx * span_x, y0 + ly * span_y, label,
            fontproperties=F_BOLD, fontsize=11 * lw_scale, color=INK, zorder=7.5,
            ha="right" if flip else "left", va="center",
            path_effects=[pe.withStroke(linewidth=3.5 * lw_scale, foreground="white")],
        )
        t.set_clip_on(True)
        t.set_clip_box(ax.bbox)


def draw_phase_labels(ax, s: Scene, active: str | None, *, lw_scale: float = 1.0) -> None:
    for p in s.phases:
        lab = p["label"]
        on = lab == active
        if active is not None and not on:
            continue
        x, y = s.centroids[lab]
        text = p["short"] if active is None else p["label"]
        if p.get("karen_lives_here"):
            text += "  \u2014 Karen lives here" if on else " \u2665"
        ax.text(
            x, y, text, fontproperties=F_BLACK if on else F_BOLD,
            fontsize=(15 if on else 9.5) * lw_scale, color="white" if on else INK,
            ha="center", va="center", zorder=8,
            bbox=dict(boxstyle="round,pad=0.42",
                      fc=PINK if (on and p.get("karen_lives_here")) else (DEEP if on else "white"),
                      ec="white" if on else DIM_EDGE, lw=1.8 if on else 0.9,
                      alpha=0.96),
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


def provisional_stamp(fig, s: Scene, y: float = 0.052) -> None:
    """Loud, unmissable banner while any phase availability is still unconfirmed."""
    if not s.provisional:
        return
    fig.patches.append(
        FancyBboxPatch((0.315, y), 0.37, 0.030, boxstyle="round,pad=0.004",
                       transform=fig.transFigure, facecolor="#FFE9A8",
                       edgecolor="#C99A00", lw=1.6, zorder=40, mutation_aspect=0.4)
    )
    fig.text(0.5, y + 0.015,
             f"PROVISIONAL \u2014 availability unconfirmed for "
             f"{len(s.provisional)} of {len(s.phases)} phases",
             fontproperties=F_BOLD, fontsize=12, color="#7A5C00",
             ha="center", va="center", zorder=41)


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
    handles = [
        MPoly([(0, 0)], facecolor=c, edgecolor=DEEP, lw=1.0, alpha=0.6, label=t)
        for c, t in STATUS.values()
    ]
    handles += [
        MPoly([(0, 0)], facecolor=GOLD, edgecolor="#9C6B00", lw=0.6,
              label="Platted homesites in the phase being shown"),
        Line2D([0], [0], marker="o", ms=8, mfc=CORAL, mec="white", mew=1.6, ls="none",
               label="Landmark  (\u201c?\u201d = awaiting confirmation)"),
    ]
    leg = ax.legend(handles=handles, loc=loc, frameon=True, fontsize=9.5 * lw_scale,
                    prop=FontProperties(fname=F_REG.get_file(), size=9.5 * lw_scale),
                    borderpad=0.9, labelspacing=0.7, handlelength=1.6)
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_edgecolor(DIM_EDGE)
    leg.get_frame().set_alpha(0.95)
    leg.set_zorder(10)


def credit_line(s: Scene) -> str:
    return (
        f"{s.meta['data_credit']}  \u00b7  retrieved {date.today().isoformat()}"
        f"   |   {s.meta['disclaimer']}"
    )


# ---------------------------------------------------------------- exports
POSTER_RECT = [0.025, 0.075, 0.95, 0.845]


def render_poster(s: Scene, overlays: set[str], *, pdf: bool = False) -> Path:
    fig = plt.figure(figsize=(20, 12), dpi=200 if not pdf else 150, facecolor=SAND)
    ax = fig.add_axes(POSTER_RECT)
    ax.set_facecolor(LAND)

    draw_base(ax, s)
    draw_phases(ax, s, None, show_lots="all")
    draw_roads(ax, s)
    draw_overlays(ax, s, overlays)
    draw_phase_labels(ax, s, None)
    set_view(ax, s.extent, 0.05, ax_aspect(fig, POSTER_RECT))
    draw_landmarks(ax, s)
    scale_bar(ax, s)
    north_arrow(ax, s)
    legend(ax, s)

    fig.text(0.025, 0.955, "Latitude Margaritaville Watersound", fontproperties=F_BLACK,
             fontsize=36, color=INK, ha="left", va="center")
    fig.text(0.025, 0.921, "Every recorded phase, drawn from Bay County public records",
             fontproperties=F_REG, fontsize=16, color=MUTED, ha="left", va="center")
    fig.text(0.975, 0.955, f"{len(s.phases)} recorded phases  \u00b7  {s.total_lots:,} platted homesites"
                           f"  \u00b7  {s.total_acres:,.0f} acres",
             fontproperties=F_BOLD, fontsize=15, color=DEEP, ha="right", va="center")
    fig.text(0.975, 0.921, "  \u00b7  ".join(s.meta["agent_block"]), fontproperties=F_REG,
             fontsize=12, color=MUTED, ha="right", va="center")
    fig.text(0.5, 0.030, credit_line(s), fontproperties=F_REG, fontsize=10.5,
             color=MUTED, ha="center", va="center")
    provisional_stamp(fig, s)

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
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=SAND)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(LAND)
    draw_base(ax, s, lw_scale=1.3)
    draw_phases(ax, s, None, lw_scale=1.3, show_lots="all")
    draw_roads(ax, s, lw_scale=1.3, label_hwy=False)
    set_view(ax, s.extent, 0.02, 16 / 9)
    draw_landmarks(ax, s, only_anchors=True, lw_scale=1.4)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "latitude-phase-map-thumbnail.png"
    fig.savefig(path, facecolor=SAND)
    plt.close(fig)
    return path


def _panel_text(fig, s: Scene, p: dict) -> None:
    """Right-hand info panel for a phase frame."""
    colour, status_text = s.status(p)
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
        y -= 0.045

    fig.patches.append(
        FancyBboxPatch((x - 0.006, y - 0.032), 0.235, 0.046, boxstyle="round,pad=0.004",
                       transform=fig.transFigure, facecolor=colour, edgecolor="none",
                       zorder=21, mutation_aspect=0.5)
    )
    fig.text(x + 0.004, y - 0.009, status_text.upper(), fontproperties=F_BOLD, fontsize=11,
             color=NAVY if p.get("availability") != "resale-only" else "#3A1108",
             ha="left", va="center", zorder=22)
    y -= 0.075
    if not p.get("confirmed"):
        fig.text(x, y + 0.020, "provisional \u2014 confirm current inventory",
                 fontproperties=F_REG, fontsize=9.5, color=GOLD,
                 ha="left", va="center", zorder=21)
        y -= 0.012

    rows = [
        ("Recorded plat", p["plat"]),
        ("Platted homesites", f"{p['lot_count']:,}"),
        ("Size", f"{p['acres']:,.0f} acres"),
    ]
    if p.get("lot_number_range"):
        lo, hi = p["lot_number_range"]
        rows.append(("Lot numbers", f"{lo:,} \u2013 {hi:,}"))
    for key, target in (("To Town Center", "Town Square Amenity"), ("To Bandshell", "Bandshell")):
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
        wrapped = _wrap(note, 34)[:4]
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
    written: list[Path] = []

    def new_fig():
        fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=SAND)
        ax = fig.add_axes(SEQ_RECT)
        ax.set_facecolor(LAND)
        return fig, ax

    def footer(fig):
        fig.text(0.015, 0.022, credit_line(s), fontproperties=F_REG, fontsize=8.5,
                 color=MUTED, ha="left", va="center", zorder=1)

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
    fig.text(0.722, 0.872, "Every one is a separate recorded plat \u2014 with a\n"
                           "plat book and page anyone can look up.",
             fontproperties=F_REG, fontsize=12.5, color=MUTED, ha="left", va="top")
    yy = 0.792
    for p in s.phases:
        fig.text(0.722, yy, p["short"], fontproperties=F_BOLD, fontsize=12.5, color=INK,
                 ha="left", va="center")
        fig.text(0.986, yy, f"{p['plat']}   {p['lot_count']:>4} lots", fontproperties=F_REG,
                 fontsize=12, color=MUTED, ha="right", va="center")
        yy -= 0.0405
    footer(fig)
    provisional_stamp(fig, s)
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
        anchors = [s.landmark(n) for n in ("Sales Center", "Town Square Amenity")]
        xs = [box[0], box[2]] + [a[0] for a in anchors if a]
        ys = [box[1], box[3]] + [a[1] for a in anchors if a]
        set_view(ax, (min(xs), min(ys), max(xs), max(ys)), 0.12, aspect)
        draw_landmarks(ax, s, only_anchors=False, lw_scale=1.4)
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", nargs="+",
                    choices=["poster", "print", "thumbnail", "sequence"],
                    help="render a subset")
    ap.add_argument("--overlays", nargs="*", default=[],
                    choices=["hwy79", "towncenter", "bandshell"],
                    help="optional context layers; off by default to keep the map clean")
    args = ap.parse_args()

    s = Scene(load_features())
    overlays = set(args.overlays)
    jobs = args.only or ["poster", "print", "thumbnail", "sequence"]

    if "poster" in jobs:
        print("poster ->", render_poster(s, overlays).name)
    if "print" in jobs:
        print("print  ->", render_poster(s, overlays, pdf=True).name)
    if "thumbnail" in jobs:
        print("thumb  ->", render_thumbnail(s, overlays).name)
    if "sequence" in jobs:
        print("sequence:")
        got = render_sequence(s, overlays)
        print(f"  {len(got)} frames -> output/frames/")

    unconfirmed = [p["label"] for p in s.phases if not p.get("confirmed")]
    if unconfirmed:
        print("\nNEEDS CONFIRMATION before publishing:")
        print(f"  availability unconfirmed for {len(unconfirmed)} phases: "
              + ", ".join(p.replace("Phase ", "") for p in unconfirmed))
    for l in s.needs_confirmation:
        print(f"  landmark '{l['name']}': {l.get('needs', 'unconfirmed')}")


if __name__ == "__main__":
    main()
