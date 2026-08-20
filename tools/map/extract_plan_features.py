#!/usr/bin/env python3
"""Georeference Minto's overall site plan, and measure features off it.

WHY THIS EXISTS
Bay County's public records give us every platted homesite, but they do not
give us the ponds or the Town Center buildings: the county's water layer
returns a single feature across the whole community, and its building-footprint
layer returns nothing at all here.  OpenStreetMap has nothing inside the Town
Center either.  The only source that shows them is Minto's own site plan.

HOW WE USE IT, AND WHAT WE DO NOT DO
Minto's PDF is licensed to Karen for use as-is.  We therefore never reproduce,
recolour, crop or republish their artwork, and nothing they drew is copied into
our map.  What we take is factual: *where* the water is and *where* the
buildings are.  Buildings are reduced to their oriented bounding box, which is
our own generalisation rather than their outline, and ponds are simplified well
past the drawn linework.  Everything is then redrawn from scratch in Karen's
own styling.

THE FIT IS SOLVED, NOT ASSUMED
The transform from plan pixels to real coordinates is recovered by aligning the
plan's drawn lot fabric against the 3,151 recorded homesites we hold from the
county, then measured: the map is cut into tiles and each tile's residual shift
is reported.  Below --max-error the script writes nothing, because geometry
placed by a fit you have not checked is just a guess with extra steps.

Usage:
    python extract_plan_features.py fit                 # solve and report only
    python extract_plan_features.py water               # ponds -> data/plan_water.geojson
    python extract_plan_features.py buildings           # Town Center -> data/plan_buildings.geojson
    python extract_plan_features.py crop --bbox W,S,E,N --out work/tc.png
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
WORK = HERE / "work"
FIT_CACHE = DATA / "plan_fit.json"

NWFL = Path.home() / "NWFL Beach Homes" / "NWFL Beach Homes - Documents"
PHASES_DIR = (
    NWFL
    / "Properties"
    / "Bay County"
    / "Panama City Beach"
    / "West Bay & HWY 79 Corridor"
    / "Latitude Margaritaville Watersound"
    / "Phases"
)
PLAN_PDF = PHASES_DIR / "lmw-overall-siteplan-w-disclaimer-6-26-16527-1784815566.pdf"

FIT_DPI = 200  # the DPI the transform is expressed against

# Regions of the sheet that carry chrome rather than map, as fractions of the
# page: the legend block, the disclaimer strip, and the title / compass / logo.
NON_MAP_BOXES = [
    (0.13, 0.69, 0.34, 0.85),
    (0.00, 0.85, 1.00, 1.00),
    (0.55, 0.00, 1.00, 0.28),
]


# --------------------------------------------------------------------------
# raster and colour masks
# --------------------------------------------------------------------------

def render_plan(dpi: int, clip_pt=None) -> tuple[np.ndarray, tuple[float, float]]:
    """Rasterise the sheet, optionally only a window of it.

    Returns the pixels plus the pixel offset of the window on the full sheet,
    so coordinates measured in a crop still refer to the whole page.  Rendering
    the Town Center alone at 600 dpi costs a few megabytes; rendering the whole
    20-inch sheet at 600 dpi costs about 400.
    """
    import pymupdf

    if not PLAN_PDF.exists():
        sys.exit(f"Minto site plan not found: {PLAN_PDF}")
    doc = pymupdf.open(PLAN_PDF)
    page = doc[0]
    kw = {"dpi": dpi, "colorspace": pymupdf.csRGB}
    off = (0.0, 0.0)
    if clip_pt is not None:
        x0, y0, x1, y1 = clip_pt
        kw["clip"] = pymupdf.Rect(x0, y0, x1, y1)
        off = (x0 * dpi / 72.0, y0 * dpi / 72.0)
    pix = page.get_pixmap(**kw)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).copy()
    doc.close()
    return arr, off


def non_map_mask(shape) -> np.ndarray:
    h, w = shape
    m = np.zeros((h, w), bool)
    for x0, y0, x1, y1 in NON_MAP_BOXES:
        m[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = True
    return m


def colour_masks(rgb: np.ndarray, flip: bool = True) -> dict[str, np.ndarray]:
    """Split the sheet into the few ink families we care about.

    Thresholds come from sampling the sheet rather than from taste - the
    awkward one is that paper (#f0e0d0) and lot fill (#f0c0b0) are both warm
    and light, and separate cleanly only on how far red sits above blue.

    With flip=True the masks come back y-up to match the geographic frame,
    because image rows run north-to-south and a reflection is not something a
    rotation search can undo.  Pass flip=False to stay in raster coordinates.
    """
    r = rgb[..., 0].astype(np.int16)
    g = rgb[..., 1].astype(np.int16)
    b = rgb[..., 2].astype(np.int16)
    chrome = non_map_mask(rgb.shape[:2]) if flip else np.zeros(rgb.shape[:2], bool)

    pink = (r > 195) & (r - b > 46) & (r - g > 28)
    yellow = (r > 200) & (g > 180) & (b < 165) & (r - b > 60) & (abs(r - g) < 45)
    cyan = (b > 150) & (g > 150) & (b - r > 25) & (g - r > 10)
    orange = (r > 190) & (g > 90) & (g < 180) & (b < 120)
    developed = (pink | yellow | cyan | orange) & ~chrome

    out = {
        "developed": developed,
        # Ponds are the only blue-dominant fill on the sheet.
        #
        # The Caribbean Collection's homesites also print in a pale cyan that
        # passes this test, so a few villa pods come through as "ponds". Do not
        # try to fix that here: excluding everything the lot masks claim also
        # strips the lighter shallows and anti-aliased edges of real ponds, and
        # costs about 70% of the mapped water. It is settled downstream instead,
        # where the recorded plats can arbitrate - a blob sitting almost
        # entirely on recorded homesites is not a pond, and the county's plat is
        # a better authority on that than any colour threshold.
        "water": (b > 130) & (b - r > 22) & (b - g > 8) & (r > 70) & (b < 235) & ~chrome,
        # Amenity buildings print as flat mid-tone warm greys and taupes, well
        # darker than both paper and lot fill and with far less red bias.
        "building": (r > 100) & (r < 205) & (abs(r - g) < 38) & (g - b > -10)
                    & (g - b < 55) & (r - b < 62) & ~chrome,
    }
    return {k: (v[::-1].copy() if flip else v) for k, v in out.items()}


# --------------------------------------------------------------------------
# our own geometry, in a local metre frame
# --------------------------------------------------------------------------

def load_geojson(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"missing {path} - run fetch_data.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def iter_rings(geom: dict):
    t = geom.get("type")
    if t == "Polygon":
        yield geom["coordinates"][0]
    elif t == "MultiPolygon":
        for poly in geom["coordinates"]:
            yield poly[0]


class LocalFrame:
    """Equirectangular projection about the community, in metres."""

    def __init__(self, lon0: float, lat0: float):
        self.lon0, self.lat0 = lon0, lat0
        self.kx = 111320.0 * math.cos(math.radians(lat0))
        self.ky = 110540.0

    def fwd(self, lon, lat):
        return (np.asarray(lon) - self.lon0) * self.kx, (np.asarray(lat) - self.lat0) * self.ky

    def inv(self, x, y):
        return np.asarray(x) / self.kx + self.lon0, np.asarray(y) / self.ky + self.lat0

    def as_dict(self):
        return {"lon0": self.lon0, "lat0": self.lat0}


def ring_area_m2(ring, frame: LocalFrame) -> float:
    arr = np.asarray(ring, float)
    if len(arr) < 3:
        return 0.0
    x, y = frame.fwd(arr[:, 0], arr[:, 1])
    return abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))) / 2.0


def rasterise_lots(lots: dict, frame: LocalFrame, px: float, pad: float, max_area: float):
    """Burn recorded residential lots into a binary grid in the local frame.

    Recorded plats also carry common-area tracts - stormwater, preserve, road
    right-of-way - two orders of magnitude larger than a homesite, which the
    plan draws as landscape rather than as lots.  Including them would swamp
    the alignment score with area that can never match.  Only homesites vote.
    """
    from matplotlib.path import Path as MplPath

    rings, dropped = [], 0
    for feat in lots["features"]:
        polys = list(iter_rings(feat.get("geometry") or {}))
        if sum(ring_area_m2(r, frame) for r in polys) > max_area:
            dropped += 1
            continue
        for ring in polys:
            arr = np.asarray(ring, float)
            if len(arr) >= 3:
                rings.append(np.column_stack(frame.fwd(arr[:, 0], arr[:, 1])))
    if not rings:
        sys.exit("no lot polygons to fit against")
    print(f"  kept {len(rings):,} homesites, dropped {dropped:,} tracts over {max_area:,.0f} m2")

    allpts = np.vstack(rings)
    x0, y0 = allpts.min(axis=0) - pad
    x1, y1 = allpts.max(axis=0) + pad
    w = int(math.ceil((x1 - x0) / px))
    h = int(math.ceil((y1 - y0) / px))

    grid = np.zeros((h, w), bool)
    ys, xs = np.mgrid[0:h, 0:w]
    centres = np.stack([(xs + 0.5) * px + x0, (ys + 0.5) * px + y0], axis=-1)
    for ring in rings:
        rx0, ry0 = ring.min(axis=0)
        rx1, ry1 = ring.max(axis=0)
        c0, c1 = max(0, int((rx0 - x0) / px) - 1), min(w, int((rx1 - x0) / px) + 2)
        r0, r1 = max(0, int((ry0 - y0) / px) - 1), min(h, int((ry1 - y0) / px) + 2)
        if c1 <= c0 or r1 <= r0:
            continue
        sub = centres[r0:r1, c0:c1].reshape(-1, 2)
        grid[r0:r1, c0:c1] |= MplPath(ring).contains_points(sub).reshape(r1 - r0, c1 - c0)
    return grid, (x0, y0, px)


# --------------------------------------------------------------------------
# similarity search
# --------------------------------------------------------------------------

def blur(mask: np.ndarray, sigma: float) -> np.ndarray:
    from scipy.ndimage import gaussian_filter

    a = gaussian_filter(mask.astype(np.float32), sigma)
    a -= a.mean()
    n = float(np.linalg.norm(a))
    return a / n if n else a


def best_translation(target: np.ndarray, moving: np.ndarray):
    F = np.fft.rfft2(target) * np.conj(np.fft.rfft2(moving))
    corr = np.fft.irfft2(F, s=target.shape)
    idx = int(np.argmax(corr))
    dy, dx = np.unravel_index(idx, corr.shape)
    if dy > corr.shape[0] // 2:
        dy -= corr.shape[0]
    if dx > corr.shape[1] // 2:
        dx -= corr.shape[1]
    return float(corr.flat[idx]), int(dy), int(dx)


def rot_matrix(angle_deg: float, scale: float) -> np.ndarray:
    th = math.radians(angle_deg)
    c, s = math.cos(th), math.sin(th)
    return np.array([[c, -s], [s, c]], float) / scale


def warp_plan(mask: np.ndarray, angle_deg: float, scale: float, shape) -> np.ndarray:
    from scipy.ndimage import affine_transform

    m = rot_matrix(angle_deg, scale)
    offset = np.array(mask.shape, float) / 2.0 - m @ (np.array(shape, float) / 2.0)
    return affine_transform(mask.astype(np.float32), m, offset=offset,
                            output_shape=shape, order=1, mode="constant")


def apply_fit(mask, angle, scale, dy, dx, shape):
    warped = warp_plan(mask, angle, scale, shape) > 0.5
    return np.roll(np.roll(warped, dy, axis=0), dx, axis=1)


def fit_similarity(target, plan, angles, scales, sigma):
    tgt = blur(target, sigma)
    best = None
    for ang in angles:
        for sc in scales:
            warped = warp_plan(plan, ang, sc, target.shape)
            if warped.sum() < 50:
                continue
            score, dy, dx = best_translation(tgt, blur(warped > 0.5, sigma))
            if best is None or score > best[0]:
                best = (score, float(ang), float(sc), dy, dx)
    return best


def moments(mask: np.ndarray):
    ys, xs = np.nonzero(mask)
    pts = np.column_stack([xs, ys]).astype(float)
    c = pts.mean(axis=0)
    d = pts - c
    rms = float(np.sqrt((d ** 2).sum(axis=1).mean()))
    vals, vecs = np.linalg.eigh(np.cov(d.T))
    v = vecs[:, int(np.argmax(vals))]
    return c, rms, math.degrees(math.atan2(v[1], v[0]))


def iou(a, b) -> float:
    u = np.count_nonzero(a | b)
    return np.count_nonzero(a & b) / u if u else 0.0


def registration_error(target, aligned, px, tiles: int = 12):
    """Local residual displacement, in metres, between recorded lots and plan.

    IoU is the wrong acceptance test here.  Minto's sheet is an artist's
    rendering: it draws homesites as tidy uniform rectangles nowhere near the
    recorded parcel outlines, so overlap is capped well below 1 even when the
    registration is perfect.  A global nearest-neighbour distance is no better -
    its median hits zero as soon as most lots touch drawn fabric, and its tail
    is dominated by the newest phases, which the plan does not colour at all.

    What actually governs whether a pond lands in the right place is how far
    the drawing is *locally* shifted from reality.  So cut the map into tiles,
    solve each tile's own best shift, and report the spread.  A tile with no
    plan fabric simply does not vote.
    """
    h, w = target.shape
    th, tw = h // tiles, w // tiles
    mags = []
    for i in range(tiles):
        for j in range(tiles):
            t = target[i * th:(i + 1) * th, j * tw:(j + 1) * tw]
            a = aligned[i * th:(i + 1) * th, j * tw:(j + 1) * tw]
            if np.count_nonzero(t) < 150 or np.count_nonzero(a) < 150:
                continue
            _, dy, dx = best_translation(blur(t, 2.0), blur(a, 2.0))
            mags.append(math.hypot(dx, dy) * px)
    if not mags:
        return float("inf"), float("inf"), 0
    mags = np.array(mags)
    return float(np.median(mags)), float(np.percentile(mags, 90)), len(mags)


# --------------------------------------------------------------------------
# the solved transform, as a reusable object
# --------------------------------------------------------------------------

class PlanFit:
    """Maps plan-sheet pixels to lon/lat, and back.

    Solving the fit costs a couple of minutes, so it is cached to disk and
    reused by every later extraction rather than being re-derived each time.
    """

    def __init__(self, *, dpi, raster_shape, zoom_r, zoom_c, small_shape, grid_shape,
                 angle, scale, dy, dx, origin, frame, quality):
        self.dpi = dpi
        self.raster_shape = tuple(raster_shape)
        self.zoom_r, self.zoom_c = zoom_r, zoom_c
        self.small_shape = tuple(small_shape)
        self.grid_shape = tuple(grid_shape)
        self.angle, self.scale = angle, scale
        self.dy, self.dx = dy, dx
        self.origin = tuple(origin)          # x0, y0, px in local metres
        self.frame = frame
        self.quality = quality

    # -- serialisation ----------------------------------------------------
    def to_dict(self):
        return {
            "plan": PLAN_PDF.name,
            "dpi": self.dpi,
            "raster_shape": list(self.raster_shape),
            "zoom_r": self.zoom_r, "zoom_c": self.zoom_c,
            "small_shape": list(self.small_shape),
            "grid_shape": list(self.grid_shape),
            "angle_deg": self.angle, "scale": self.scale,
            "dy": self.dy, "dx": self.dx,
            "origin": list(self.origin),
            "frame": self.frame.as_dict(),
            "quality": self.quality,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(dpi=d["dpi"], raster_shape=d["raster_shape"], zoom_r=d["zoom_r"],
                   zoom_c=d["zoom_c"], small_shape=d["small_shape"], grid_shape=d["grid_shape"],
                   angle=d["angle_deg"], scale=d["scale"], dy=d["dy"], dx=d["dx"],
                   origin=d["origin"], frame=LocalFrame(**d["frame"]), quality=d["quality"])

    # -- grid <-> world ---------------------------------------------------
    def grid_to_lonlat(self, col, row):
        x0, y0, px = self.origin
        x = (np.asarray(col, float) + 0.5) * px + x0
        y = (np.asarray(row, float) + 0.5) * px + y0
        return self.frame.inv(x, y)

    def lonlat_to_grid(self, lon, lat):
        x0, y0, px = self.origin
        x, y = self.frame.fwd(lon, lat)
        return (x - x0) / px - 0.5, (y - y0) / px - 0.5

    # -- raster <-> grid --------------------------------------------------
    def raster_to_grid(self, col, row):
        """Sheet pixel (at self.dpi) -> aligned grid (col, row)."""
        col = np.atleast_1d(np.asarray(col, float))
        row = np.atleast_1d(np.asarray(row, float))
        h = self.raster_shape[0]
        src = np.stack([(h - 1 - row) * self.zoom_r, col * self.zoom_c])
        m = rot_matrix(self.angle, self.scale)
        offset = np.array(self.small_shape, float) / 2.0 - m @ (np.array(self.grid_shape, float) / 2.0)
        tgt = np.linalg.inv(m) @ (src - offset[:, None])
        return tgt[1] + self.dx, tgt[0] + self.dy

    def grid_to_raster(self, col, row):
        col = np.atleast_1d(np.asarray(col, float))
        row = np.atleast_1d(np.asarray(row, float))
        m = rot_matrix(self.angle, self.scale)
        offset = np.array(self.small_shape, float) / 2.0 - m @ (np.array(self.grid_shape, float) / 2.0)
        src = m @ np.stack([row - self.dy, col - self.dx]) + offset[:, None]
        h = self.raster_shape[0]
        return src[1] / self.zoom_c, h - 1 - src[0] / self.zoom_r

    def lonlat_to_raster(self, lon, lat, dpi=None):
        c, r = self.grid_to_raster(*self.lonlat_to_grid(lon, lat))
        k = 1.0 if dpi is None else dpi / self.dpi
        return c * k, r * k


def solve_fit(args) -> tuple[PlanFit, dict[str, np.ndarray]]:
    from scipy.ndimage import zoom

    print(f"rendering Minto plan at {FIT_DPI} dpi ...")
    rgb, _ = render_plan(FIT_DPI)
    print(f"  raster {rgb.shape[1]} x {rgb.shape[0]}")
    masks = colour_masks(rgb)
    for k, v in masks.items():
        print(f"  {k:<10} {np.count_nonzero(v):>9,} px")

    lots = load_geojson(DATA / "lots.geojson")
    allpts = np.vstack([np.asarray(r, float) for f in lots["features"]
                        for r in iter_rings(f.get("geometry") or {})])
    frame = LocalFrame(float(allpts[:, 0].mean()), float(allpts[:, 1].mean()))
    target, origin = rasterise_lots(lots, frame, args.px, 900.0, args.max_lot)
    print(f"  grid {target.shape[1]}x{target.shape[0]} at {args.px} m/px")

    developed = masks["developed"]
    _, rms_t, ang_t = moments(target)
    _, rms_p, ang_p = moments(developed)
    guess = rms_t / rms_p
    ang0 = ((ang_t - ang_p) + 90) % 180 - 90
    small = zoom(developed.astype(np.float32), guess, order=1) > 0.4
    zoom_r = (small.shape[0] - 1) / (developed.shape[0] - 1)
    zoom_c = (small.shape[1] - 1) / (developed.shape[1] - 1)
    print(f"  prescale x{guess:.4f} -> {small.shape[1]}x{small.shape[0]};"
          f" principal axes {ang_t:+.1f} vs {ang_p:+.1f} -> start {ang0:+.1f} deg")

    ANGLE_SPAN, SCALE_SPAN = 12.0, 0.30
    print("coarse fit ...")
    # ~200 warps, so run the sweep on quarter-scale copies: at this blur the
    # detail full resolution would buy has already been thrown away, and it
    # turns minutes into seconds.
    coarse = fit_similarity(
        zoom(target.astype(np.float32), 0.25, order=1) > 0.4,
        zoom(small.astype(np.float32), 0.25, order=1) > 0.4,
        ang0 + np.arange(-ANGLE_SPAN, ANGLE_SPAN + 0.01, 2.0),
        np.arange(1 - SCALE_SPAN, 1 + SCALE_SPAN + 0.001, 0.04), 1.5)
    print(f"  angle {coarse[1]:+.2f} deg  scale {coarse[2]:.3f}")
    if abs(coarse[1] - ang0) > ANGLE_SPAN - 0.01 or abs(coarse[2] - 1.0) > SCALE_SPAN - 0.001:
        print("  WARNING: coarse optimum sits on the edge of the search range")

    print("fine fit ...")
    _, angle, scale, dy, dx = fit_similarity(
        target, small,
        np.arange(coarse[1] - 2.0, coarse[1] + 2.01, 0.4),
        np.arange(coarse[2] - 0.04, coarse[2] + 0.041, 0.01), 2.0)
    print("polish ...")
    _, angle, scale, dy, dx = fit_similarity(
        target, small,
        np.arange(angle - 0.4, angle + 0.41, 0.1),
        np.arange(scale - 0.01, scale + 0.0101, 0.0025), 1.0)
    print(f"  angle {angle:+.3f} deg  scale {scale:.4f}  shift ({dx},{dy})")

    aligned = apply_fit(small, angle, scale, dy, dx, target.shape)
    med, p90, ntiles = registration_error(target, aligned, args.px)
    quality = {
        "median_residual_m": round(med, 2),
        "p90_residual_m": round(p90, 2),
        "tiles_measured": ntiles,
        "lot_fabric_iou": round(iou(target, aligned), 4),
        "recall": round(np.count_nonzero(target & aligned) / max(1, np.count_nonzero(target)), 4),
    }
    print(f"\nfit quality"
          f"\n  local residual shift  median {med:.1f} m, 90th pct {p90:.1f} m over {ntiles} tiles"
          f"\n  lot-fabric IoU        {quality['lot_fabric_iou']:.3f}"
          f"  (capped low by design - the plan is a rendering, not a survey)"
          f"\n  recall                {quality['recall']:.3f}")

    if args.debug:
        WORK.mkdir(exist_ok=True)
        from PIL import Image
        vis = np.zeros(target.shape + (3,), np.uint8)
        vis[..., 0] = target * 255
        vis[..., 1] = aligned * 255
        Image.fromarray(vis[::-1]).save(WORK / "_fit_overlay.png")
        print(f"  wrote {WORK / '_fit_overlay.png'}")

    if med > args.max_error:
        sys.exit(f"\nREFUSING TO CONTINUE: median local residual {med:.1f} m exceeds "
                 f"--max-error {args.max_error:.0f} m.\nThe plan could not be georeferenced "
                 "reliably, so anything measured off it would be a guess.")

    fit = PlanFit(dpi=FIT_DPI, raster_shape=rgb.shape[:2], zoom_r=zoom_r, zoom_c=zoom_c,
                  small_shape=small.shape, grid_shape=target.shape, angle=angle, scale=scale,
                  dy=dy, dx=dx, origin=origin, frame=frame, quality=quality)
    DATA.mkdir(exist_ok=True)
    FIT_CACHE.write_text(json.dumps(fit.to_dict(), indent=1), encoding="utf-8")
    print(f"cached transform -> {FIT_CACHE.name}")
    return fit, masks


def load_or_solve(args):
    if FIT_CACHE.exists() and not args.refit:
        fit = PlanFit.from_dict(json.loads(FIT_CACHE.read_text(encoding="utf-8")))
        q = fit.quality
        print(f"using cached fit ({FIT_CACHE.name}): angle {fit.angle:+.3f} deg, "
              f"median residual {q['median_residual_m']:.1f} m")
        return fit, colour_masks(render_plan(fit.dpi)[0])
    return solve_fit(args)


# --------------------------------------------------------------------------
# feature extraction
# --------------------------------------------------------------------------

def aligned_mask(mask: np.ndarray, fit: PlanFit, render_dpi: int | None = None) -> np.ndarray:
    """Bring a plan-sheet mask into the aligned grid.

    The transform is solved once at FIT_DPI, but a mask may be sampled from a
    finer render - the Town Center buildings are only a few pixels across at
    fit resolution.  Rescaling the zoom factors keeps the same solved rotation
    and translation while letting detail come from the higher-DPI raster.
    """
    from scipy.ndimage import zoom

    k = 1.0 if render_dpi in (None, fit.dpi) else fit.dpi / render_dpi
    small = zoom(mask.astype(np.float32), (fit.zoom_r * k, fit.zoom_c * k), order=1) > 0.4
    return apply_fit(small, fit.angle, fit.scale, fit.dy, fit.dx, fit.grid_shape)


def trace(grid: np.ndarray, fit: PlanFit, min_area_m2: float, simplify_px: float,
          close: int = 3, open_: int = 3):
    """Contour an aligned mask into simplified lon/lat polygons."""
    import cv2
    from shapely.geometry import Polygon

    px = fit.origin[2]
    img = grid.astype(np.uint8) * 255
    if close:
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    if open_:
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, np.ones((open_, open_), np.uint8))
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    out = []
    for c in contours:
        area = cv2.contourArea(c) * px * px
        if area < min_area_m2:
            continue
        c = cv2.approxPolyDP(c, simplify_px, True)
        if len(c) < 4:
            continue
        pts = c.reshape(-1, 2).astype(float)
        lon, lat = fit.grid_to_lonlat(pts[:, 0], pts[:, 1])
        poly = Polygon(np.column_stack([lon, lat]))
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty or poly.geom_type != "Polygon":
            continue
        out.append((poly, area, c))
    out.sort(key=lambda t: -t[1])
    return out


def write_geojson(path: Path, feats: list, extra: dict):
    path.write_text(json.dumps({"type": "FeatureCollection", **extra, "features": feats}, indent=1),
                    encoding="utf-8")


def cmd_water(args, fit, masks) -> int:
    from shapely.geometry import shape as shp

    grid = aligned_mask(masks["water"], fit)
    print(f"aligned water grid: {np.count_nonzero(grid):,} px")
    polys = trace(grid, fit, args.min_area, simplify_px=1.5)
    print(f"traced {len(polys)} water bodies >= {args.min_area:,.0f} m2")

    # The county already supplies the natural creek and bay geometry, and its
    # survey beats a marketing rendering, so anything of ours that lands on a
    # county creek is flagged rather than drawn twice.
    creeks = load_geojson(DATA / "creeks.geojson")
    from shapely.geometry import LineString, MultiLineString
    from shapely.ops import unary_union
    lines = []
    for f in creeks["features"]:
        g = f.get("geometry") or {}
        if g.get("type") == "LineString":
            lines.append(LineString(g["coordinates"]))
        elif g.get("type") == "MultiLineString":
            lines.extend(LineString(c) for c in g["coordinates"])
    creek_buf = unary_union(lines).buffer(0.0004) if lines else None

    feats, natural = [], 0
    for poly, area, _ in polys:
        is_natural = bool(creek_buf is not None and poly.intersection(creek_buf).area > 0.35 * poly.area)
        natural += is_natural
        feats.append({
            "type": "Feature",
            "properties": {
                "kind": "waterway" if is_natural else "pond",
                "area_m2": round(area, 1),
                "area_acres": round(area / 4046.86, 2),
            },
            "geometry": {"type": "Polygon", "coordinates": [[list(c) for c in poly.exterior.coords]]},
        })
    print(f"  {len(feats) - natural} stormwater ponds, {natural} on the natural creek line")

    write_geojson(DATA / "plan_water.geojson", feats, {
        "source": "positions measured from Minto overall site plan (June 2026); "
                  "outlines simplified and redrawn, not reproduced",
        "fit": fit.quality | {"angle_deg": fit.angle, "scale": fit.scale},
    })
    acres = sum(f["properties"]["area_acres"] for f in feats if f["properties"]["kind"] == "pond")
    print(f"wrote data/plan_water.geojson ({len(feats)} features, {acres:.1f} pond acres)")
    return 0


def cmd_buildings(args, fit, masks) -> int:
    """Amenity buildings at the Town Center, reduced to oriented boxes.

    We keep position, size and orientation - all facts about the buildings -
    and deliberately discard Minto's outline, so what our map draws is our own
    generalisation rather than a trace of their drawing.

    NOT WIRED INTO THE RENDER, AND DELIBERATELY SO. The output was checked by
    overlaying it on the Town Center aerial, which is independently
    georeferenced and verified against the Bandshell. The boxes land on the
    pickleball courts, the pool deck and a patch of empty trees, and miss every
    actual building. Two further attempts failed the same check:

      * Bay County's Building Footprints layer (Basic_Layers/MapServer/21) has
        no coverage of the Town Center - its footprints in this area stop east
        of longitude -85.863, around Highway 79. OpenStreetMap has none either.
      * Detecting roofs on the aerial instead picks up parking rows and bare
        graded earth, and merges large roofs into adjacent pavement.

    The reason this is hard is visible in the plan itself: at the Town Center
    the sheet is a textured illustration, not flat vector fills - a colour
    census of that window returns twenty-plus blended tones, none over 5%, so
    there is no clean "building" colour to select.

    So the Town Center is rendered as a named amenity list against its one
    confirmed coordinate (draw_amenity_labels), not as footprints. Do not wire
    this output into the map without re-running that overlay check first.
    """
    import cv2
    from shapely.geometry import Polygon, shape as shp

    tract = town_center_tract()
    w, s, e, n = tract.bounds

    # Window the sheet to the parcel: the same mid-grey ink is roof tone on
    # every individual house across the community, and those we already hold
    # as recorded homesites.
    xs, ys = [], []
    for lon, lat in ((w, s), (w, n), (e, s), (e, n)):
        c, r = fit.lonlat_to_raster(lon, lat)
        xs.append(float(c[0]))
        ys.append(float(r[0]))
    pad = 40.0
    clip_pt = ((min(xs) - pad) * 72 / fit.dpi, (min(ys) - pad) * 72 / fit.dpi,
               (max(xs) + pad) * 72 / fit.dpi, (max(ys) + pad) * 72 / fit.dpi)
    rgb, (ox, oy) = render_plan(args.extract_dpi, clip_pt)
    print(f"Town Center window rendered at {args.extract_dpi} dpi: {rgb.shape[1]}x{rgb.shape[0]} px")

    k = fit.dpi / args.extract_dpi          # window pixels -> fit-DPI sheet pixels
    mask = colour_masks(rgb, flip=False)["building"]
    img = cv2.morphologyEx(mask.astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"  {len(contours)} candidate blobs")

    feats = []
    for c in contours:
        box = cv2.boxPoints(cv2.minAreaRect(c))
        lon, lat = fit.grid_to_lonlat(*fit.raster_to_grid((box[:, 0] + ox) * k, (box[:, 1] + oy) * k))
        poly = Polygon(np.column_stack([lon, lat]))
        if not poly.is_valid or poly.is_empty or not tract.contains(poly.centroid):
            continue
        area = ring_area_m2(list(poly.exterior.coords), fit.frame)
        if not (args.min_building <= area <= args.max_building):
            continue
        bw, bh = sorted(cv2.minAreaRect(c)[1])           # short side, long side, in px
        # A building is roughly rectangular; long thin slivers are paths, kerb
        # lines and shadow edges rather than structures.  The box area is known
        # in metres, so its short side follows from the pixel aspect ratio.
        if bh <= 0 or bh / max(bw, 1e-6) > 5:
            continue
        if math.sqrt(area * bw / bh) < 7:
            continue
        feats.append({
            "type": "Feature",
            "properties": {
                "kind": "amenity_building",
                "footprint_m2": round(area, 1),
                "generalised": "oriented bounding box",
            },
            "geometry": {"type": "Polygon", "coordinates": [[list(p) for p in poly.exterior.coords]]},
        })
    feats.sort(key=lambda f: -f["properties"]["footprint_m2"])
    print(f"kept {len(feats)} building-shaped blobs "
          f"({args.min_building:,.0f}-{args.max_building:,.0f} m2)")
    for f in feats[:15]:
        c = shp(f["geometry"]).centroid
        print(f"   {f['properties']['footprint_m2']:8,.0f} m2  at {c.y:.5f}, {c.x:.5f}")

    write_geojson(DATA / "plan_buildings.geojson", feats, {
        "source": "positions measured from Minto overall site plan (June 2026); "
                  "each building reduced to its oriented bounding box, not traced",
        "fit": fit.quality | {"angle_deg": fit.angle, "scale": fit.scale,
                              "extract_dpi": args.extract_dpi},
    })
    print(f"wrote data/plan_buildings.geojson ({len(feats)} buildings)")
    return 0


def town_center_tract():
    """The 48-acre recorded parcel that holds the Town Center.

    It sits inside the plat recorded as 'PH 5A3', and contains both the
    Bandshell and Paradise Pool - which is why there is no Phase 5A
    neighbourhood to buy in.
    """
    from shapely.geometry import shape as shp

    phases = load_geojson(DATA / "phases.geojson")
    lots = load_geojson(DATA / "lots.geojson")
    plat = next((shp(f["geometry"]) for f in phases["features"]
                 if "5A3" in (f["properties"].get("SUBDIVID") or "")), None)
    if plat is None:
        sys.exit("could not find the PH 5A3 plat in phases.geojson")
    inside = [shp(f["geometry"]) for f in lots["features"]
              if plat.contains(shp(f["geometry"]).centroid)]
    return max(inside, key=lambda p: p.area)


def cmd_crop(args, fit, masks) -> int:
    """Render a georeferenced window of the sheet, for eyeballing only."""
    from PIL import Image

    w, s, e, n = [float(v) for v in args.bbox.split(",")]
    rgb, _ = render_plan(args.crop_dpi)
    xs, ys = [], []
    for lon, lat in ((w, s), (w, n), (e, s), (e, n)):
        c, r = fit.lonlat_to_raster(lon, lat, dpi=args.crop_dpi)
        xs.append(float(c))
        ys.append(float(r))
    box = (max(0, int(min(xs))), max(0, int(min(ys))),
           min(rgb.shape[1], int(max(xs))), min(rgb.shape[0], int(max(ys))))
    print(f"crop box on the {args.crop_dpi} dpi sheet: {box}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).crop(box).save(out)
    print(f"wrote {out}")
    return 0


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["fit", "water", "buildings", "crop"])
    ap.add_argument("--px", type=float, default=5.0, help="fit grid pixel size in metres")
    ap.add_argument("--max-error", type=float, default=25.0,
                    help="reject the fit above this median residual, in metres")
    ap.add_argument("--max-lot", type=float, default=1500.0,
                    help="polygons above this many m2 are tracts, not homesites")
    ap.add_argument("--min-area", type=float, default=1200.0, help="smallest pond to keep, m2")
    ap.add_argument("--min-building", type=float, default=120.0)
    ap.add_argument("--max-building", type=float, default=9000.0)
    ap.add_argument("--extract-dpi", type=int, default=600,
                    help="DPI for the Town Center window when detecting buildings")
    ap.add_argument("--bbox", help="crop window as W,S,E,N in degrees")
    ap.add_argument("--out", default="work/_crop.png")
    ap.add_argument("--crop-dpi", type=int, default=600)
    ap.add_argument("--refit", action="store_true", help="ignore the cached transform")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    if args.command == "fit":
        args.refit = True
        solve_fit(args)
        return 0

    fit, masks = load_or_solve(args)
    return {"water": cmd_water, "buildings": cmd_buildings, "crop": cmd_crop}[args.command](
        args, fit, masks)


if __name__ == "__main__":
    raise SystemExit(main())
