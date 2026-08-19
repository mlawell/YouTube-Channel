# Latitude Margaritaville Watersound — Every Phase Explained

**Channel:** Living in Latitude Margaritaville Watersound (`@LivingMargaritavillewithKaren`)
**Target runtime:** 14–16 minutes
**Status:** script ready — **blocked on Karen's confirmations** (see below)

The flagship phase video. Built around one thing no competitor can say:
**Karen lives in Phase 8.**

## Files

| File | What it is |
| --- | --- |
| [`script.md`](script.md) | Full shot-by-shot script with timecodes and on-screen frame cues |
| [`metadata.md`](metadata.md) | Titles, description, tags, chapters, end screen, pinned comment |
| [`thumbnail-brief.md`](thumbnail-brief.md) | Thumbnail composition and the A/B variant |

## Visuals

Every map frame comes from [`tools/map`](../../../../tools/map). Regenerate with:

```powershell
cd tools\map
python render_map.py --only sequence
```

Frames land in `tools/map/output/frames/`. The script calls them by filename.
`00_all-phases.png` is the establishing shot; `01`–`16` are one per phase,
each zoomed with that phase highlighted and the Sales Center + Town Center
kept on screen so viewers stay oriented.

## Why this video wins

The video it replaces (@TheLatitudeGuy, 6:55) is a screen recording of a site
plan with a mouse scribble per phase. See
[`knowledge/competitors/thelatitudeguy.md`](../../../../knowledge/competitors/thelatitudeguy.md).

Five gaps we exploit:

1. **He never says most phases are resale-only.** That is the single most
   important fact for a buyer and it is the spine of our video.
2. **He gets Phase 3 wrong** — treats it as one blob. Public record shows three
   separate recorded plats: 3A, 3B & 3C, 3D.
3. **He gets 5A wrong** — "they changed it and kind of skipped it." PH 5A3 is a
   recorded plat, book 32 page 81.
4. **6:55 cannot hit 7 minutes of absolute watch time.** Ours is built to.
5. **He sells there. Karen lives there.**

## Blocked on Karen

The script has `[KAREN]` markers everywhere a claim needs her. Do not record
until these are settled:

- [ ] New-build vs resale-only for all 16 phases (all currently provisional)
- [ ] The noise / Highway 79 / Town Center / Bandshell call per phase
- [ ] Is there a second Town Square planned for Area 2? (a commenter asked;
      we have no public confirmation)
- [ ] Which phase releases next, and when would a home there finish?
- [ ] Can the grocery tenant be named on screen?
- [ ] Exact Town Center and Bandshell points for the map
