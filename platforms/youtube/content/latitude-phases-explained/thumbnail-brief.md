# Thumbnail brief — Latitude Margaritaville Watersound: Every Phase Explained

**Canvas:** 1280 × 720, under 2 MB, PNG or JPG
**Base plate:** `tools/map/output/latitude-phase-map-thumbnail.png`
(regenerate with `python render_map.py --only thumbnail`)

The plate is the map rendered clean at 16:9 with no title block, sized so the
right two-thirds carries the map and the left third is free for Karen. Drop
Karen and the text on top of it.

## Composition

```
┌──────────────────────────────────────────────────────────┐
│                                            [teal chip]   │
│   ALL 16                                   I LIVE HERE ♥ │
│   PHASES                                                 │
│   ┌──────┐                    ~~~~ the map ~~~~          │
│   │      │        Phase 8 highlighted in gold            │
│   │KAREN │        everything else soft                   │
│   │ face │                                               │
│   │      │   ┌────────────────────────┐                  │
│   └──────┘   │  MOST ARE SOLD OUT     │  ← coral banner  │
└──────────────────────────────────────────────────────────┘
```

## Elements

**1. Karen — bottom left, cut out, ~55% of frame height.**
Head and shoulders, looking at camera, warm and slightly incredulous — the
"nobody tells you this" face, not a listing headshot. Feather the cutout edge;
hard mask edges read as cheap at thumbnail size.

**2. "ALL 16 PHASES" — top left, over Karen's shoulder.**
Arial Black or the channel display face. Deep navy `#12333F` with a 6 px sand
`#FAF3E4` outline so it survives on any background. Two lines, tight leading.

**3. "MOST ARE SOLD OUT" — coral `#FF6B5B` banner, bottom centre-left.**
This is the hook. White Arial Black, slight rotation (−3°). It must be legible
at 210 px wide — check it at that size before shipping.

**4. "I LIVE HERE ♥" — teal `#20D0C4` chip, top right.**
Small. It is the credibility mark, not the headline. Pink `#FF4FA3` heart to
match the Phase 8 treatment on the map.

**5. The map.** Phase 8 stays gold and highlighted; drop the rest to about 60%
opacity so the eye lands on the one phase. Kill the legend and the footer
credit — no small type survives on a phone.

## Rules

- **Four elements maximum.** Face, big text, banner, chip. Nothing else.
- **No more than six words of text total.**
- **Test at 210 px wide.** That is the mobile feed size. If "MOST ARE SOLD OUT"
  is not readable there, it is not done.
- **No Minto logo, no Margaritaville wordmark, no brokerage logo.** Trademarks
  in a thumbnail invite trouble and add nothing to CTR.
- **Karen's face must not be cropped by the timestamp.** YouTube stamps the
  bottom-right corner — keep her clear of it.

## A/B variant

Same plate, same face, different headline. Test question versus statement:

| | A (ship first) | B |
| --- | --- | --- |
| Big text | `ALL 16 PHASES` | `WHICH PHASE?` |
| Banner | `MOST ARE SOLD OUT` | `I LIVE IN PHASE 8` |

A leads with completeness, B leads with the personal angle. Run A for 48 hours,
then swap if CTR is under 4%.

## Source assets

- Karen's portrait: the M365 library — see [`brand/README.md`](../../../../brand/README.md).
  Use the same headshot as the channel profile picture for recognition.
- Brand colours: `tools/banner/make_margaritaville_banner.py` is the reference
  (teal `#20D0C4`), and the map renderer carries the full palette in
  `tools/map/render_map.py`.
