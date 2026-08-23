# YouTube

**Status: Active.** The primary long-form channel platform. Strategy is fully
documented in the Channel Junkies knowledge volume; this folder holds the applied,
per-channel operational setup and content.

## Our channels

Managed under the Gmail account `kalawell@gmail.com` (channel switcher):

1. **Living in Panama City Beach FL — The Lawell Team** — `@LivinginPanamaCityBeachFLtheLT` (`UCKTGNXomdGLpNjxkrVWlkpw`)
2. **Living in Latitude Margaritaville Watersound** — `@LivingMargaritavillewithKaren` (`UCN3mqc01vMeNemUJ2ae60YA`)
3. **Karen Lawell, Realtor with Counts Real Estate** — `@KarenLawellRealtor`

## Key references

- **Channel setup (reusable template + our applied configs):**
  [`../../knowledge/channel-junkies/playbook/channel-setup-config.md`](../../knowledge/channel-junkies/playbook/channel-setup-config.md)
- **Full YouTube strategy playbook:**
  [`../../knowledge/channel-junkies/playbook/realtor-playbook.md`](../../knowledge/channel-junkies/playbook/realtor-playbook.md)
- **Banner design brief:**
  [`../../knowledge/channel-junkies/playbook/margaritaville-banner-brief.md`](../../knowledge/channel-junkies/playbook/margaritaville-banner-brief.md)
- **Brand identity + canonical contact:** [`../../brand/README.md`](../../brand/README.md)

## Content & assets

- `content/` — video titles, descriptions, upload-default copy, scripts, end-screen plans.
- `assets/` — banners, thumbnails, watermarks (produced with
  [`../../tools/banner`](../../tools/banner) and [`../../tools/video`](../../tools/video)).

### Video packages

Full index: [`content/README.md`](content/README.md).

| Package | Channel | Status |
| --- | --- | --- |
| [Karen's voice and humor](content/karen-voice-and-humor.md) | Both | **Read first.** Voice, banned phrases, the em-dash rule, signature details and the line bank. These videos are avatar-narrated, so humor has to be written in advance or it does not exist |
| [Karen's presenter treatment](content/karen-presenter-treatment.md) | Both | **Read second.** How she appears: the treatment hierarchy, the face-time budget, the cutaway rule, and the verified asset inventory. There is no real footage of Karen, so every appearance is composited |
| [Five Kinds of Life in Panama City Beach](content/pcb-five-neighborhoods/README.md) | Living in Panama City Beach FL | ~30 min vlog tour of five neighborhoods. Ready to record — **[3 blocking `[KAREN]` items](content/pcb-five-neighborhoods/README.md#before-you-record)** |
| [Latitude Margaritaville Watersound — Every Phase Explained](content/latitude-phases-explained/README.md) | Living in Latitude Margaritaville Watersound | Script ready, awaiting Karen's confirmations |
| [Phase Deep Dives — one video per phase](content/phase-deep-dives/README.md) | Living in Latitude Margaritaville Watersound | Ten drafts + metadata + thumbnails generated. Cart times are estimated, so the remaining gap is **[resident quotes](content/phase-deep-dives/drive-sheet.md)** — the nine phases Karen doesn't live in need someone asked |

The two Latitude packages are a hub and its spokes: the flagship answers "how do
the phases work", each deep dive answers "should I buy in *this* one". The deep
dives are generated from the same public record the map is, by
[`tools/scripts/build_phase_scripts.py`](../../tools/scripts/build_phase_scripts.py),
so they cannot drift from the map.

The PCB package is the driver-city **vlog tour** — one of the four permanent
assets every relocation channel needs, and the format Channel Junkies rates
highest for activating browse and suggested. That channel has one published
video, so it is effectively a launch.
