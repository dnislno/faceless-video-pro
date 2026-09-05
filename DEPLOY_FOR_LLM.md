# DEPLOY_FOR_LLM - Faceless Video Pro v1.0.0

> Machine-readable deploy guide. Goal: from a fresh clone to a finished local MP4 file, then report its absolute path to the user.

## 1. Goal and success criteria

- Read a product brief from the user (example: `Korean lipstick, 3 dollars, viral TikTok ad`).
- Produce exactly one file: a vertical MP4 ad, max 20 seconds, 1080x1920, with voiceover audio.
- Final answer to the user MUST contain the absolute local path of the MP4, for example:
  `C:\projects\faceless-video-pro\output\korean_lipstick_viral_ad.mp4`
- Verify before answering: duration <= 20s, resolution 1080x1920, both video and audio streams present.

## 2. Prerequisites (check first, install what is missing)

1. Python 3.10 or newer: `python --version`
2. FFmpeg 6 or newer in PATH: `ffmpeg -version` and `ffprobe -version`
3. A free Pexels API key from https://www.pexels.com/api/
4. Optional: an LLM key plus base URL (OpenAI, Gemini, DeepSeek, Qwen, Groq) or local Ollama. Skip if none. The offline template works without it.

## 3. Install (exact steps)

```bash
git clone https://github.com/dnislno/faceless-video-pro.git
cd faceless-video-pro
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell replace `cp` with:

```powershell
copy .env.example .env
```

## 4. Configure (user supplies keys, never invent them)

1. Ask the user for `PEXELS_API_KEY`. Put it in `.env` as `PEXELS_API_KEY=...`
2. Ask for `LLM_API_KEY` and `LLM_BASE_URL` only if the user wants AI-written scripts. If they decline, leave `LLM_API_KEY` empty. The app falls back to the built-in English template.
3. Optional: set `TTS_VOICE` (default `en-US-AriaNeural`) and `TARGET_SECONDS` (default `16`).
4. Never print keys back, never commit `.env`.

Endpoint reference:

| Provider | LLM_BASE_URL | LLM_MODEL example |
|---|---|---|
| OpenAI | https://api.openai.com/v1 | gpt-4o-mini |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |
| Groq | https://api.groq.com/openai/v1 | llama-3.1-8b-instant |
| Gemini | https://generativelanguage.googleapis.com/v1beta/openai/ | gemini-2.0-flash |
| Ollama local | http://localhost:11434/v1 | llama3.1 |

## 5. Generate (exact command)

```bash
python generate_ad.py --prompt "Korean lipstick, 3 dollars, viral TikTok ad"
```

Custom output path:

```bash
python generate_ad.py --prompt "Iced brown sugar latte, 4 dollars" --out output/latte.mp4
```

What the script does, in order:

1. Writes a viral script of max 45 words (LLM if configured, else local template).
2. Searches Pexels for 3 portrait queries and downloads 1080x1920-capable clips to `assets/`.
3. Synthesizes the voiceover with EdgeTTS to `assets/voiceover.mp3`.
4. Normalizes each clip to 1080x1920 30fps in `tmp/`, cuts a 3-scene pacing (6s plus 5.5s plus 4.5s).
5. Muxes H.264 plus AAC with faststart to `output/*.mp4`.

## 6. Verify (do this before reporting, fix on failure)

```bash
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,codec_name,codec_type -of default=noprint_wrappers=1 output/korean_lipstick_viral_ad.mp4
```

Checklist:

| Check | Expected | Fix if wrong |
|---|---|---|
| Duration | <= 20.0 seconds | Shorten prompt script or lower TARGET_SECONDS |
| Resolution | 1080 x 1920 | Re-run, the scale-crop filter enforces it |
| Streams | 1 video (h264) plus 1 audio (aac) | Check voiceover.mp3 exists, re-run mux step |
| Captions | None burned in | Default has no subtitles, do not add any |
| File size | Roughly 5 to 12 MB | Normal for 15s 1080x1920 |

Optional visual check, extract 3 frames:

```bash
ffmpeg -y -ss 3 -i output/korean_lipstick_viral_ad.mp4 -vframes 1 tmp/check1.jpg
ffmpeg -y -ss 8 -i output/korean_lipstick_viral_ad.mp4 -vframes 1 tmp/check2.jpg
ffmpeg -y -ss 13 -i output/korean_lipstick_viral_ad.mp4 -vframes 1 tmp/check3.jpg
```

Each frame should show product-relevant footage with no text overlay.

## 7. Report (exact final format)

Reply in English with:

1. The absolute local MP4 path as a code string.
2. Duration, resolution, and voice used.
3. The voiceover script text.
4. The 3 Pexels video page URLs used.

Example:

```text
Done. Your ad is ready:
C:\projects\faceless-video-pro\output\korean_lipstick_viral_ad.mp4
Duration 15.6s, 1080x1920, voice en-US-AriaNeural.
Script: "Stop scrolling! ..."
Footage: <url1>, <url2>, <url3>
```

## 8. Troubleshooting

- `Missing Pexels key`: `.env` was not filled or not loaded. Check `PEXELS_API_KEY`.
- `moov atom not found` on a normalized clip: partial download. Delete that `tmp/auto_norm*.mp4` and re-run.
- Audio cut off at the end: concat shorter than voiceover. The default 3-scene cut totals about 16s, longer than the voiceover. Re-run the concat step.
- `ffmpeg: not recognized`: FFmpeg missing from PATH. Install it and reopen the terminal.
- LLM 401 errors: wrong key or base URL. The script auto-falls back to the local template, so the run still completes.

Keywords: faceless video generator deploy, prompt to video ads setup, Pexels API key setup, EdgeTTS install, FFmpeg install guide, TikTok ad automation tutorial, AI commercial pipeline self-hosted.
