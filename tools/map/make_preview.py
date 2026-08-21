"""Populate `preview/` -- the committed artifacts.

`output/` is git-ignored because it regenerates and the large masters are tens
of megabytes. But two things should be obtainable without running the pipeline:
the map needs to be *visible* in the repo and in pull requests, and Karen needs
the print master she hands to a print shop without going through Python.

So this copies the 36 x 24 vector PDF across as-is (1.1 MB) and downscales the
rasters into `preview/`, which is tracked.

    python make_preview.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
OUT = HERE / "output"
PREVIEW = HERE / "preview"

# Copied verbatim -- small enough to commit, and the actual deliverable.
VERBATIM = [OUT / "latitude-phase-map-print-36x24.pdf"]


def stale_inputs(pdf: Path) -> list[Path]:
    """Inputs that changed after the print master was rendered.

    `output/` is git-ignored, so nothing stops a stale PDF sitting there --
    a render that failed, or one a PDF viewer had open and locked. Copying it
    across is silent and looks fine: it prints "(verbatim)" and a plausible
    size, and the repo ends up showing a map that is not the map the code and
    data produce. This is the check that catches that, and it caught it once.
    """
    if not pdf.exists():
        return []
    cutoff = pdf.stat().st_mtime + 1  # a second of slack for filesystem rounding
    watched = [HERE / "render_map.py", HERE / "build_features.py"]
    watched += sorted(HERE.glob("*.json"))
    watched += sorted((HERE / "data").glob("*.json"))
    return [p for p in watched if p.exists() and p.stat().st_mtime > cutoff]


def frame(suffix: str) -> Path:
    """Find a reveal frame by name rather than by its sequence number.

    Frames are numbered by position, so adding or reordering one silently
    renumbers the rest. Matching on the phase name keeps the preview pointing
    at the right image instead of quietly skipping it.
    """
    hits = sorted((OUT / "frames").glob(f"*_{suffix}.png"))
    return hits[0] if hits else OUT / "frames" / f"{suffix}.png"


# (source, destination, target width)
ITEMS = [
    (OUT / "latitude-phase-map.png", "latitude-phase-map-preview.png", 1600),
    (OUT / "latitude-phase-map-print-36x24.png", "print-sheet-preview.png", 1600),
    (frame("all-phases"), "frame-00-all-phases.png", 1280),
    (frame("phase-8"), "frame-phase-8-karen.png", 1280),
    (frame("towncenter"), "frame-town-center.png", 1280),
    (OUT / "latitude-phase-map-thumbnail.png", "thumbnail-plate.png", 960),
]


def rasterise_sheet() -> None:
    """The print sheet is vector-only, so make a raster of it to preview."""
    src = OUT / "latitude-phase-map-print-36x24.pdf"
    if not src.exists():
        return
    try:
        import pymupdf
    except ImportError:
        return
    doc = pymupdf.open(src)
    doc[0].get_pixmap(dpi=60).save(OUT / "latitude-phase-map-print-36x24.png")


def main() -> None:
    stale = stale_inputs(OUT / "latitude-phase-map-print-36x24.pdf")
    if stale:
        print("REFUSING: output/ is older than its inputs, so the preview would")
        print("ship a map that is not the one this repo produces. Changed since:")
        for p in stale:
            print(f"  {p.relative_to(HERE)}")
        print("\nRe-run:  python render_map.py")
        print("(if the render failed with PermissionError, a PDF viewer has the")
        print(" print master open -- close it and render again)")
        raise SystemExit(1)

    PREVIEW.mkdir(parents=True, exist_ok=True)
    rasterise_sheet()
    total = 0
    for src in VERBATIM:
        if not src.exists():
            print(f"  skip {src.name} (not rendered yet)")
            continue
        dst = PREVIEW / src.name
        try:
            shutil.copy2(src, dst)
        except PermissionError:
            # Usually a PDF viewer holding the file open. Not worth aborting the
            # rest of the run over.
            print(f"  SKIP {src.name} -- destination is locked (close it and re-run)")
            continue
        kb = dst.stat().st_size / 1024
        total += kb
        print(f"  {src.name}  (verbatim)  {kb:,.0f} KB")
    for src, name, width in ITEMS:
        if not src.exists():
            print(f"  skip {src.name} (not rendered yet)")
            continue
        im = Image.open(src).convert("RGB")
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
        dst = PREVIEW / name
        im.save(dst, optimize=True)
        kb = dst.stat().st_size / 1024
        total += kb
        print(f"  {name}  {width}x{h}  {kb:,.0f} KB")
    print(f"preview/ -> {total / 1024:.2f} MB total")


if __name__ == "__main__":
    main()
