# HeyGen — API & MCP Server

HeyGen generates AI avatar / talking-photo videos with natural motion. In this repo
it's the paid, higher-quality alternative to the local SadTalker path for Karen
presenter clips (see [make_presenter_heygen.py](make_presenter_heygen.py) vs
[make_presenter.py](make_presenter.py)). There are two ways to drive it:

| | REST API | Remote MCP server |
| --- | --- | --- |
| Setup | API key in `X-Api-Key` header | Add connector URL, OAuth sign-in |
| Runs on | Your code | HeyGen's hosted infrastructure |
| Auth | API key | OAuth (no key) |
| Best for | Scripted/batch pipelines (our tools) | Conversational use from an AI agent |

Docs: https://developers.heygen.com/docs/quick-start · MCP: https://developers.heygen.com/mcp/overview

---

## 1. REST API

- **Base URL:** `https://api.heygen.com`
- **Auth header:** `X-Api-Key: <your-key>` (create/rotate in HeyGen → Settings → API)
- **Upload host:** `https://upload.heygen.com`

### Auth (do NOT commit the key)

```powershell
setx HEYGEN_API_KEY "your-key-here"   # persists; reopen the shell after
# or, current session only:
$env:HEYGEN_API_KEY = "your-key-here"
```

### Quick start — Video Agent (v3, flagship: prompt → finished MP4)

```python
import requests, time, os
KEY = os.environ["HEYGEN_API_KEY"]
H = {"X-Api-Key": KEY}

# 1. Create a session from a prompt
sid = requests.post("https://api.heygen.com/v3/video-agents", headers=H,
    json={"prompt": "A presenter explaining our product launch in 30 seconds"}
).json()["data"]["session_id"]

# 2. Wait for a video_id, then poll the video for its URL
vid = None
while not vid:
    vid = requests.get(f"https://api.heygen.com/v3/video-agents/{sid}", headers=H).json()["data"].get("video_id")
    if not vid: time.sleep(5)
while True:
    v = requests.get(f"https://api.heygen.com/v3/videos/{vid}", headers=H).json()["data"]
    if v["status"] in ("completed", "failed"): break
    time.sleep(10)
print(v.get("video_url"))
```

### Endpoints you'll use most

| Purpose | Endpoint |
| --- | --- |
| Video Agent (prompt → video) | `POST /v3/video-agents` → `GET /v3/video-agents/{session_id}` |
| Avatar video (you pick avatar+voice+script) | `POST /v3/videos` (engines: Avatar III/IV/V; IV default) |
| Video status | `GET /v3/videos/{video_id}` (`status`, `video_url`, `failure_code`) |
| Text-to-speech | `POST /v3/voices/speech` |
| Clone a voice | `POST` clone → poll `GET /v3/voices/{voice_clone_id}` |
| List voices (TTS-compatible) | `GET /v3/voices?engine=starfish` |
| Direct-to-S3 asset upload | `create_asset_upload` → PUT bytes → `POST /v3/assets/{id}/complete` |
| Webhooks (skip polling) | pass `callback_url`; see `/docs/webhooks` |

> **Versioning:** v3 is current. The repo's `make_presenter_heygen.py` still targets
> the **v2** avatar-video API (`/v2/video/generate`), which HeyGen supports **until
> Oct 31, 2026**. Migrate it to `POST /v3/videos` before then.

### Repo script: `make_presenter_heygen.py`

Drives HeyGen to render waist-up Karen presenter clips and writes them to
`<model_dir>/video/presenters/<ImageStem>.<ext>` so
[../video/build_tour.py](../video/build_tour.py) picks them up unchanged.

Environment variables it reads:

| Var | Purpose |
| --- | --- |
| `HEYGEN_API_KEY` | API key (required) |
| `HEYGEN_TALKING_PHOTO_ID` | Pre-uploaded Karen photo-avatar id (optional; else it uploads the photo) |
| `HEYGEN_AVATAR_ID` | Studio avatar id (optional alternative to talking photo) |
| `HEYGEN_VOICE_ID` | Karen voice-clone id (optional; else uses the local XTTS narration WAV) |
| `HEYGEN_BACKGROUND` | `transparent`, or a hex like `#00FF00` for green screen (default) that `rembg`/`build_tour` can key |

Run: `tools/avatar/.venv/Scripts/python.exe tools/avatar/make_presenter_heygen.py`
(any Python 3.9+ with `requests`; no GPU needed).

### Troubleshooting

- **401 Unauthorized** — `X-Api-Key` missing or key inactive.
- **429 Too Many Requests** — rate/concurrency limit; honor `Retry-After` and back off.
- **400 download_failed** — a URL you passed isn't publicly reachable / not a direct file link.
- **status = failed** — read `failure_code` / `failure_message` on `GET /v3/videos/{id}`.

---

## 2. Remote MCP server

Lets an MCP-capable agent (VS Code Copilot, Claude, Cursor, Gemini CLI, etc.) call
HeyGen conversationally — **no API key, nothing to install**. Billing draws on your
existing HeyGen plan credits.

- **Endpoint:** `https://mcp.heygen.com/mcp/v1/`
- **Auth:** one-time OAuth sign-in (domain-whitelisted; request access via HeyGen's
  Integration Intake form if your agent's domain isn't already allowed)

### Add it

1. In your agent's **MCP servers / Connectors** settings, choose **Add custom connector**.
2. Name it `HeyGen`, URL `https://mcp.heygen.com/mcp/v1/`.
3. Click **Connect** and approve via OAuth.
4. Ask, e.g., *"Make a 30-second Latitude Margaritaville explainer with HeyGen."*

For VS Code, add to your MCP config (`mcp.json`) alongside the existing Playwright entry:

```jsonc
{
  "servers": {
    "heygen": { "url": "https://mcp.heygen.com/mcp/v1/" }
  }
}
```

### Tool groups exposed over MCP

Video Agent (`create_video_agent`, `get_video_agent_session`, …), Videos
(`create_video`, `get_video`, `list_videos`, `delete_video`), Templates
(`generate_from_template`, …), Voices (`clone_voice`, `create_speech`,
`design_voice`, `list_voices`), Audio (`search_audio_sounds`), Video Translate,
AI Clipping, Lipsync, Avatars (`create_avatar`, `create_avatar_consent`, looks),
Assets, Batches (video / translation / lipsync / asset), Brand kits, and
`get_current_user` (credits/balance).

---

## 3. Full developer-site reference

Complete map of https://developers.heygen.com (summarized; follow links for detail).
Machine-readable index: `https://heygen-1fa696a7.mintlify.site/llms.txt`.
OpenAPI specs: [external-api.json](https://developers.heygen.com/openapi/external-api.json) · [openapi.yaml](https://developers.heygen.com/openapi.yaml).

### Getting started
| Page | What it covers |
| --- | --- |
| [For AI Agents](https://developers.heygen.com/docs/for-ai-agents) | Agent-first onboarding + the auth-detection ladder **MCP → CLI → raw API**. Read this first if an agent is acting for you. |
| [Quick Start](https://developers.heygen.com/docs/quick-start) | Zero → generated video: auth, create, poll. |
| [Choosing the Right Video API](https://developers.heygen.com/docs/choosing-the-right-video-api) | Video Agent vs direct video creation. |
| [Slack](https://developers.heygen.com/docs/slack) / [Discord](https://developers.heygen.com/docs/discord) | Generate from Slack; dev community. |
| [Changelog](https://developers.heygen.com/changelog) | Platform updates. |
| Official agent skills | [`heygen-com/skills`](https://github.com/heygen-com/skills) |

### Authentication, account & billing
| Page | What it covers |
| --- | --- |
| [API Key](https://developers.heygen.com/docs/api-key) | Generate, rotate, secure the key (`X-Api-Key`). |
| [Get Current User](https://developers.heygen.com/user-profile) | Profile, credit balance, plan tier (`GET /v3/user`). |
| [Self-Serve](https://developers.heygen.com/docs/pricing) / [Enterprise](https://developers.heygen.com/docs/enterprise-pricing) / [Dollar-based](https://developers.heygen.com/docs/enterprise-pricing-dollar-base) pricing | Per-operation and contract pricing. |
| [Usage Limits](https://developers.heygen.com/docs/usage-limits) | Rate limits, concurrency, quotas. |

### Errors & versioning
- [Error Codes](https://developers.heygen.com/docs/error-codes) — codes, HTTP statuses, troubleshooting.
- [Endpoint Version Comparison](https://developers.heygen.com/endpoint-version-comparison) — v1/v2 vs v3 coverage + migration. **v1/v2 supported until Oct 31, 2026.**

### Video Agent (prompt → finished video, flagship)
[Overview](https://developers.heygen.com/docs/overview) · [Prompt to Video](https://developers.heygen.com/docs/video-agent) · [Styles & References](https://developers.heygen.com/docs/styles-and-references) · [Upload Assets](https://developers.heygen.com/docs/upload-assets) · [Interactive Sessions](https://developers.heygen.com/docs/interactive-sessions) · [Writing Effective Video Prompts](https://developers.heygen.com/writing-effective-video-prompts). Modes: `generate` (fire-and-forget) and `chat` (multi-turn revisions).

### Direct video generation
Recommended defaults for `POST /v3/videos`: `aspect_ratio: "auto"`, `resolution: "1080p"` (avatar & image types). Cinematic Avatar supports 16:9/9:16/1:1 at 720p/1080p only.

| Topic | Notes |
| --- | --- |
| [Models](https://developers.heygen.com/models) | Avatar types (digital twin, photo, studio, image, prompt) × engines (Avatar III/IV/V). |
| [Avatar V](https://developers.heygen.com/avatar-v) | Highest-fidelity engine; cross-reference animation; opt-in per look. |
| [Avatar IV](https://developers.heygen.com/avatar-iv) | **Default** v3 engine; arbitrary image animation, `motion_prompt`, expressiveness. |
| [Avatar III](https://developers.heygen.com/avatar-iii) | Photo-to-video pipeline for photo/video avatars. |
| [Avatar Realtime](https://developers.heygen.com/avatar-realtime) / [Live Avatar](https://developers.heygen.com/live-avatar) | Real-time HLS streaming / conversational avatars (720p, billed per second). |
| [Digital Twin](https://developers.heygen.com/generate-avatar-video) | Avatar trained from real footage. |
| [Photo Avatar](https://developers.heygen.com/photo-avatar) / [Image to Video](https://developers.heygen.com/image-to-video) | Talking head from one still / animate any image (no avatar step). |
| [Assets](https://developers.heygen.com/assets) | Upload files for use across the API. |
| Batches | [Videos](https://developers.heygen.com/batch-videos) · [Translations](https://developers.heygen.com/batch-video-translations) · [Lipsyncs](https://developers.heygen.com/batch-lipsyncs) · [Assets](https://developers.heygen.com/batch-assets) — up to 100 per call. |

### Avatars · Voices · Audio
- **Avatars:** [Create](https://developers.heygen.com/docs/create-avatar) · [Consent](https://developers.heygen.com/docs/avatar-consent) · [Groups](https://developers.heygen.com/docs/avatars) · [Looks](https://developers.heygen.com/docs/avatar-looks) (a look id = the `avatar_id` you pass when creating video).
- **Voices:** [Overview](https://developers.heygen.com/docs/voices/overview) · [Browse](https://developers.heygen.com/docs/voices/search-voices) · [Design](https://developers.heygen.com/docs/voices/design-voices) · [Text to Speech (Starfish)](https://developers.heygen.com/docs/voices/speech).
- **Audio:** [Background music](https://developers.heygen.com/background-music) · [Sound effects](https://developers.heygen.com/sound-effects) — semantic search (`GET /v3/audio/sounds`).

### Lipsync & translation
- Lipsync: [Speed](https://developers.heygen.com/lipsync-speed) / [Precision](https://developers.heygen.com/lipsync-precision) — swap audio + re-animate lips.
- Video Translation: [Speed](https://developers.heygen.com/docs/video-translate) / [Precision](https://developers.heygen.com/docs/video-translation-precision) — 30+ languages, voice clone, lip-sync; Precision adds editable proofread sessions.

---

## ⭐ Expression, laughter and non-speech audio

**Checked against the developer docs on 2026-08-23**, because the YouTube scripts
plan to drop a **real recorded laugh** into Karen's narration and something has to
animate her face over it. Short version: **HeyGen cannot render a laugh, and there
is no API parameter that makes an avatar smile on cue.**

### What the API actually exposes

| Control | Where | What it really does |
| --- | --- | --- |
| `expressiveness` | **Avatar IV only**, and only for **photo avatars / images** | `high` · `medium` · `low` (default `low`). An **energy and range-of-movement dial**, not an emotion selector. Nothing documents `high` as "smiling" |
| `motion_prompt` | Avatar IV and Avatar V | Free-text **body motion and hand gestures**. No documented effect on the face |
| emotion / mood presets | — | **Do not exist** in the v3 API. No `emotion`, no `voice_emotion`, no expression preset. Third-party wrappers that advertise one are not quoting HeyGen |
| Video Agent `POST /v3/video-agents` | — | Takes `prompt`, `mode`, `avatar_id`, `voice_id`, `style_id`, `brand_kit_id`, `orientation`, `files`, callbacks. **No expression parameter** |

⚠️ `expressiveness` is **Avatar IV only and will fail validation on Avatar V**
([Digital Twin guide](https://developers.heygen.com/generate-avatar-video)). It is
also unavailable on Avatar III. See the
[models comparison](https://developers.heygen.com/models).

### Audio-driven video is supported

Handing HeyGen a finished audio track is **documented and supported**:
[Audio to Video](https://developers.heygen.com/audio-to-video), *"you supply the
audio, pick who says it, and HeyGen handles the lip-sync and render."* On v3 pass
`audio_url` **or** `audio_asset_id` to `POST /v3/videos`; the two are mutually
exclusive with `script`. Works for digital twins, studio avatars, photo avatars,
and even a bare image. This repo's `make_presenter_heygen.py` already does the v2
form of it, `{"type": "audio", "audio_asset_id": …}` in the `voice` block.

### But non-speech inside that audio is undocumented

**There is no documentation of what the avatar does during laughter, a sigh, a
breath, silence or music in a supplied track.** No idle behaviour, no blink cycle,
no expression mapping. The engine is a **speech-to-mouth** system: it re-animates
the **mouth region** against the waveform. Everything above the mouth — cheeks,
eyes, brow — stays in the avatar's default neutral.

So a laugh in the audio gets you *some* mouth movement and a **neutral face**,
which reads worse than no laugh at all.

### ⛔ The production rule this forces

> **Cut away from the avatar over any recorded reaction.** Put the laugh, the
> sigh or the breath over **B-roll, a map frame or a street-sign photo**, and
> return to the avatar on the next spoken sentence.

This is a scripting constraint, not an editing preference, and it is written into
[`karen-voice-and-humor.md`](../../platforms/youtube/content/karen-voice-and-humor.md)
so the cutaway gets planned rather than discovered in the edit.

### Pauses are supported, properly

`<break time="1s"/>` is documented for HeyGen TTS pacing
([usage limits](https://developers.heygen.com/docs/usage-limits)) and ElevenLabs
supports the same `<break time="x.xs" />` syntax. Use it for a scripted pause
instead of hoping punctuation lands.

### If a clip is already rendered

`POST /v3/lipsyncs` takes an **existing video plus new audio** and redraws the
mouth to match, in `speed` or `precision` mode. So narration can be re-mixed after
the fact and re-synced. It **does not add expression** — it is mouth-region
re-animation only, so it does not solve the laugh problem either.

### Webhooks
[Webhooks](https://developers.heygen.com/docs/webhooks) · [Webhook Events](https://developers.heygen.com/docs/webhook-events). Register an HTTPS URL, get a signing secret (shown once), subscribe to event types to skip polling.

### CLI (`heygen`)
[Overview](https://developers.heygen.com/cli) · [Commands](https://developers.heygen.com/commands) · [Output Modes](https://developers.heygen.com/output-modes) · [Features](https://developers.heygen.com/features) · [Examples](https://developers.heygen.com/examples). Scriptable (`heygen video create`, `heygen video download`); agent-friendly output modes.

### MCP (per-host setup)
[Top-level](https://developers.heygen.com/mcp) · [Overview](https://developers.heygen.com/mcp/overview) · [Claude Code](https://developers.heygen.com/mcp/claude-code) · [Claude Web](https://developers.heygen.com/mcp/claude-web) · [Gemini CLI](https://developers.heygen.com/mcp/gemini-cli) · [Manus](https://developers.heygen.com/mcp/manus) · [OpenAI](https://developers.heygen.com/mcp/open-ai) · [Superhuman](https://developers.heygen.com/mcp/superhuman). (Tool list + endpoint in §2 above.)

### Cookbook (use-case workflows)
[Overview](https://developers.heygen.com/overview) · [Showcase](https://developers.heygen.com/showcase). Recipes: [Social Media Pipeline](https://developers.heygen.com/social-media-content-pipeline) · [Sales Outreach](https://developers.heygen.com/personalized-sales-outreach) · [Training & Onboarding](https://developers.heygen.com/training-and-onboarding-videos) · [Product Demos](https://developers.heygen.com/product-demo-videos) · [Multilingual](https://developers.heygen.com/multilingual-content) · [Content Repurposing](https://developers.heygen.com/content-repurposing) · **[Real Estate Listing Videos](https://developers.heygen.com/real-estate-listing-videos)** (photos + listing data → narrated tours — directly relevant here) · [E-commerce](https://developers.heygen.com/e-commerce-product-videos) · [Automated Broadcast](https://developers.heygen.com/automated-broadcast) · [Docs to Video](https://developers.heygen.com/docs-to-video) · [Greetings & Recognition](https://developers.heygen.com/personalized-greetings-and-recognition).

### Hyperframes (HTML → video)
[Introduction](https://developers.heygen.com/hyperframes-overview) · [Cloud Rendering](https://developers.heygen.com/hyperframes) (`POST /v3/hyperframes/renders`) · [Use Cases](https://developers.heygen.com/hyperframes-heygen) · [Studio Templates](https://developers.heygen.com/templates) · [Motion Graphics from a Prompt](https://developers.heygen.com/motion-graphics) · [Data Visualization](https://developers.heygen.com/data-to-video) · [Automated Pipeline](https://developers.heygen.com/automated-pipeline).

### Legacy APIs (until Oct 31, 2026)
[Studio API](https://developers.heygen.com/studio-api) · [Template API](https://developers.heygen.com/template-api) · [More Legacy (v1/v2)](https://developers.heygen.com/more-legacy-api). The repo's `make_presenter_heygen.py` uses this generation.

### REST API reference (v3 resource families)
| Family | Endpoints |
| --- | --- |
| Videos | `POST /v3/videos` · `GET /v3/videos/{id}` · `GET /v3/videos` · `DELETE /v3/videos/{id}` |
| Video Agent | `POST /v3/video-agents` · `GET /v3/video-agents/{session_id}` · list sessions · list session videos · list styles · get session resource · send message/revision · stop session |
| Avatars | `POST /v3/avatars` (create) · `POST /v3/avatars/{group_id}/consent` · get/list groups · get/list/update looks |
| Voices | `GET /v3/voices` · `GET /v3/voices/{id}` · clone · design · `POST /v3/voices/speech` |
| Lipsync | `POST /v3/lipsyncs` · get/list/update/delete |
| Video Translation | `POST /v3/video-translations` · get/list/update/delete · list languages |
| Proofread | create/get session · download/upload SRT · generate video from proofread |
| Webhooks | create/list/update/delete endpoint · rotate signing secret · list event types · list events |
| Assets | `POST /v3/assets` (upload, ≤32 MB: png/jpeg/mp4/webm/mp3/wav/pdf) · direct-to-S3 upload flow |
| Audio | `GET /v3/audio/sounds` (music / sound_effects) |
| Hyperframes | `POST /v3/hyperframes/renders` |
| Account | `GET /v3/user` |

Per-endpoint reference pages live under `https://developers.heygen.com/reference/…`.

---

## Security

- Never paste the API key into chat or commit it. Use the `HEYGEN_API_KEY` env var.
- Prefer the MCP server (OAuth) for interactive/agent use so no key is stored locally.
- Webhook signing secrets are shown only at creation/rotation — store securely.
- Canonical contact and brand details for generated scripts: [../../brand/README.md](../../brand/README.md).
