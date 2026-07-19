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

## Security

- Never paste the API key into chat or commit it. Use the `HEYGEN_API_KEY` env var.
- Prefer the MCP server (OAuth) for interactive/agent use so no key is stored locally.
- Canonical contact and brand details for generated scripts: [../../brand/README.md](../../brand/README.md).
