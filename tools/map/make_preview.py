"""Make the small, committed preview images.

`output/` is git-ignored because it regenerates, but the map should still be
visible in the repo and in pull requests without cloning and running the whole
pipeline. This downscales the poster and three frames into `preview/`, which
is committed.

    python make_preview.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
OUT = HERE / "output"
PREVIEW = HERE / "preview"

# (source, destination, target width)
ITEMS = [
    (OUT / "latitude-phase-map.png", "latitude-phase-map-preview.png", 1600),
    (OUT / "frames" / "00_all-phases.png", "frame-00-all-phases.png", 1280),
    (OUT / "frames" / "14_phase-8.png", "frame-14-phase-8.png", 1280),
    (OUT / "latitude-phase-map-thumbnail.png", "thumbnail-plate.png", 960),
]


def main() -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    total = 0
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
