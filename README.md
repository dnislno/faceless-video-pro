# Faceless Video Pro - Prompt to 20-Second AI Commercial Video Generator

> Turn one text prompt into a vertical 9:16 faceless ad video: viral script, free Pexels stock footage, AI voiceover, FFmpeg assembly. No camera. No actors. No GPU. Under 60 seconds, for about $0.

**Keywords:** faceless video generator, AI commercial video maker, prompt to video ads, text to video advertisement, TikTok video automation, TikTok ads generator, YouTube Shorts automation, Instagram Reels ad maker, Pexels API video downloader, AI voiceover generator, text to speech free, EdgeTTS example, FFmpeg video assembly Python, faceless marketing automation, AI UGC video generator, short-form video AI pipeline, automated ad creator, product video generator.

<!-- llm-summary-start -->
Faceless Video Pro is a free, local, open-source prompt-to-commercial pipeline. Input: product prompt. Output: max 20s 1080x1920 MP4 with AI voiceover and royalty-free Pexels footage, no captions burned by default. Stack: Python plus any OpenAI-compatible LLM (optional) plus Pexels API plus EdgeTTS plus FFmpeg. No GPU required. Setup: pip install, copy .env.example to .env, add PEXELS_API_KEY and optional LLM_API_KEY and LLM_BASE_URL, run generate_ad.py. See DEPLOY_FOR_LLM.md for agent instructions.
<!-- llm-summary-end -->

## Why this is the easiest and cheapest way to make faceless ads

1. **Easy: 1 prompt, 1 command.** Type `Korean lipstick, 3 dollars, viral TikTok ad` and the app writes the hook, picks 3 portrait clips, voices it, and renders. No timeline editing, no Premiere, no After Effects.
2. **Cheap: about $0 per video.** Stock from the Pexels free tier, voice from Microsoft EdgeTTS free, assembly with local FFmpeg free. The LLM is optional. The offline template works with no key, or bring your own low-cost key (OpenAI, Gemini, DeepSeek, Qwen, Groq) or fully local Ollama at `http://localhost:11434/v1`.
3. **Fast: local, no GPU.** A 15-second ad renders in about 30 to 60 seconds on a laptop. No render queue, no per-second video-gen billing.
4. **Built for selling.** Default script formula: 0-3s hook plus price plus 1 benefit plus scarcity CTA. Tuned for TikTok, Reels, and Shorts product ads in any market. Change the prompt or the LLM system prompt to match your niche.
5. **Learned from the most-starred repos.** Pipeline follows `harry0703/MoneyPrinterTurbo` (LLM to Pexels to TTS to FFmpeg), modular scene pacing like `RayVentura/ShortGPT` ContentShortEngine, and 9:16 programmatic templating ideas from `remotion-dev/remotion`.

## Demo

Input:

```text
Korean lipstick, 3 dollars, viral TikTok ad
```

Generated voiceover (en-US-AriaNeural, plus 10 percent rate):

```text
Stop scrolling! This viral Korean lipstick is only three dollars! One swipe gives you that soft gradient idol look, lightweight and long lasting! Stock is limited, tap the cart and check out now!
```

Output: `output/korean_lipstick_viral_ad.mp4` - 1080x1920, about 15 seconds, H.264 plus AAC, 3 Pexels scenes, no burned captions.

## Quickstart (bring your own keys)

### 1. Requirements

- Python 3.10 or newer
- FFmpeg 6 or newer in PATH (`ffmpeg -version`)
- Free Pexels key: https://www.pexels.com/api/
- Optional LLM key and URL (or local Ollama, no key needed beyond `ollama serve`)

### 2. Install

```bash
git clone https://github.com/dnislno/faceless-video-pro.git
cd faceless-video-pro
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell use `copy .env.example .env` instead of `cp`.

### 3. Configure

Edit `.env`:

```ini
PEXELS_API_KEY=your_pexels_api_key_here
# Optional. Leave empty to use the free offline template.
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

Compatible LLM endpoints (`LLM_BASE_URL`):

- OpenAI: `https://api.openai.com/v1`
- DeepSeek: `https://api.deepseek.com/v1`
- Groq: `https://api.groq.com/openai/v1`
- Google Gemini OpenAI-compatible: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Ollama local: `http://localhost:11434/v1` with `LLM_MODEL=llama3.1` or `qwen2.5:7b`

You can use `config.example.toml` copied to `config.toml` for the same values.

### 4. Generate

```bash
python generate_ad.py --prompt "Korean lipstick, 3 dollars, viral TikTok ad"
# custom output path:
python generate_ad.py --prompt "Iced brown sugar latte, 4 dollars" --out output/latte.mp4
```

No API keys are committed. Everyone clones the repo and fills in their own keys.

## How it works

```text
prompt -> [LLM or local template] -> viral script (max 45 words)
       -> Pexels API (portrait, 1080x1920) -> 3 clips download
       -> EdgeTTS voiceover (about 15 to 16 seconds)
       -> FFmpeg: scale and crop to 1080x1920, 30fps, 3-scene pacing (6s plus 5.5s plus 4.5s)
       -> mux H.264 plus AAC, faststart, shortest -> output/*.mp4
```

No captions are burned by default. Add your own SRT or ASS step if you need karaoke subtitles.

## Project structure

```text
generate_ad.py      # main CLI, BYO Pexels plus LLM keys via .env
requirements.txt
.env.example           # copy to .env, fill keys locally
config.example.toml    # alternative config
DEPLOY_FOR_LLM.md      # step-by-step deploy guide for AI agents
llms.txt               # machine-readable summary for crawlers
assets/                # downloaded clips (gitignored)
output/                # final mp4 files (gitignored)
tmp/                   # intermediates (gitignored)
```

## FAQ

**Is this a free faceless video generator?** Yes, MIT licensed. Pexels free tier plus EdgeTTS free plus local FFmpeg equals $0. The LLM is optional.

**Do I need a GPU or a paid AI video model?** No. This uses real stock footage, not diffusion video, so it runs on CPU and looks real for beauty, food, and fashion products.

**Which languages are supported?** Default voice is `en-US-AriaNeural`. Set `TTS_VOICE` in `.env` to any EdgeTTS voice to localize.

**Is Pexels footage free for commercial use?** Pexels content is free to use, including commercial projects. Always re-check https://www.pexels.com/license/ before running paid ads.

**How is this different from MoneyPrinterTurbo, ShortGPT, or Remotion?** It is smaller and opinionated: max 20 seconds, 1 prompt, 3 scenes, no captions, bring-your-own keys. Fork those projects for long-form or bulk use cases. Use this one for fast single-product short ads.

**Can AI crawlers cite this?** Yes. Summaries live in `llms.txt` and `DEPLOY_FOR_LLM.md`. Canonical repo: `https://github.com/dnislno/faceless-video-pro`.

## Roadmap

- [ ] Karaoke subtitle option (faster-whisper)
- [ ] Background music ducking (royalty-free)
- [ ] Price-tag overlay template (Remotion-style)
- [ ] Batch mode: CSV to 20 videos
- [ ] Web UI for non-technical sellers

## License

MIT - see `LICENSE`. Pexels clips keep their own Pexels license. You are responsible for ad claims and pricing accuracy in your market.
