"""
Faceless Video Pro - prompt-to-commercial (max 20s)
Local AI commercial generator: prompt -> viral script -> Pexels stock -> TTS -> FFmpeg.

References:
 - harry0703/MoneyPrinterTurbo: pipeline LLM -> Pexels -> TTS -> FFmpeg
 - RayVentura/ShortGPT: ContentShortEngine + multilingual EdgeTTS
 - remotion-dev/remotion: programmatic 9:16 templating

Setup:
  pip install -r requirements.txt
  copy .env.example .env   (fill PEXELS_API_KEY, optional LLM_API_KEY + LLM_BASE_URL)
  python generate_iklan.py --prompt "lipstik korea 50rb viral"
"""
import argparse, os, requests, asyncio, subprocess, urllib.request, json
import edge_tts

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, 'assets')
OUTPUT = os.path.join(BASE, 'output')
TMP = os.path.join(BASE, 'tmp')
for d in [ASSETS, OUTPUT, TMP]:
    os.makedirs(d, exist_ok=True)

# Local fallback template (free, offline). Used when LLM_API_KEY is empty.
# Hook pattern tuned for TikTok Shop Indonesia (MoneyPrinterTurbo prompt-tuning best practice).
def build_script_local(prompt: str) -> str:
    p = prompt.lower()
    produk = prompt.strip()[:60] if len(prompt.strip()) > 0 else "Lipstik Korea viral"
    harga = "lima puluh ribu"
    if "50" in p:
        harga = "lima puluh ribu"
    if "lipstik" in p:
        produk = "Lipstik Korea viral"
    return (f"Racun baru! {produk}, cuma {harga}! "
            "Bibir auto gradient kayak idol, ringan, tahan lama, nggak bikin kering! "
            "Stok terbatas, langsung checkout sekarang!")


def build_script_llm(prompt: str) -> str:
    """Use any OpenAI-compatible LLM if configured, else local template."""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        return build_script_local(prompt)
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    system = (
        "You write 15-second TikTok Shop Indonesia ad voiceovers. "
        "Rules: Bahasa Indonesia gaul, hook in 3 seconds, mention price twice, "
        "1 product benefit, 1 CTA 'checkout sekarang'. Max 45 words. No hashtags. No stage directions."
    )
    try:
        r = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
            },
            timeout=60,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        # keep under ~20s spokenid (~450 chars safety cap)
        return text[:450]
    except Exception as e:
        print(f"LLM failed ({e}), falling back to local template.")
        return build_script_local(prompt)

KEYWORDS = ["woman applying lipstick closeup", "asian woman holding lipstick", "glossy lips macro"]

def pexels_search(api_key, query, per_page=3):
    url = f"https://api.pexels.com/videos/search?query={query.replace(' ', '+')}&orientation=portrait&size=medium&per_page={per_page}"
    r = requests.get(url, headers={"Authorization": api_key}, timeout=30)
    r.raise_for_status()
    return r.json().get("videos", [])

def pick_file(video):
    cands = [f for f in video["video_files"] if "1080_1920" in f["link"]]
    if cands: return sorted(cands, key=lambda x: x.get("width", 0))[0]["link"]
    cands = [f for f in video["video_files"] if (f.get("height", 0) or 0) >= 1280]
    return sorted(cands, key=lambda x: x.get("width", 0))[len(cands)//2]["link"]

def download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 500000:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        while True:
            ch = resp.read(256*1024)
            if not ch: break
            f.write(ch)
    return dest

async def make_tts(text, out):
    voice = os.getenv("TTS_VOICE", "id-ID-GadisNeural")
    await edge_tts.Communicate(text, voice, rate="+10%", pitch="+5Hz").save(out)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); raise SystemExit("ffmpeg gagal")

def main():
    ap = argparse.ArgumentParser(description="Prompt to 20s faceless ad video (Pexels + TTS + FFmpeg)")
    ap.add_argument("--prompt", required=True, help="Ad brief, e.g. 'lipstik korea 50rb viral'")
    ap.add_argument("--pexels-key", default=os.getenv("PEXELS_API_KEY", ""), help="Pexels API key (or set PEXELS_API_KEY in .env)")
    ap.add_argument("--out", default="", help="Output mp4 path")
    ap.add_argument("--no-caption", action="store_true", default=True)
    args = ap.parse_args()

    if not args.pexels_key:
        raise SystemExit("Missing Pexels key. Set PEXELS_API_KEY in .env or pass --pexels-key. Get free key at https://www.pexels.com/api/")

    script = build_script_llm(args.prompt)
    print("SCRIPT:", script)
    voice = os.path.join(ASSETS, "voiceover.mp3")
    asyncio.run(make_tts(script, voice))

    clips = []
    for i, kw in enumerate(KEYWORDS):
        vids = pexels_search(args.pexels_key, kw)
        best = vids[0]
        url = pick_file(best)
        print(f"Pexels {kw} -> video {best['id']} {best['url']}")
        clips.append(download(url, os.path.join(ASSETS, f"auto_clip{i}.mp4")))

    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
    normed = []
    for i, c in enumerate(clips):
        out = os.path.join(TMP, f"auto_norm{i}.mp4")
        run(["ffmpeg", "-y", "-i", c, "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out])
        normed.append(out)

    # pacing 3 scene ala ShortGPT/Remotion agar tidak monoton
    concat = os.path.join(TMP, "auto_concat.mp4")
    run(["ffmpeg", "-y", "-i", normed[0], "-i", normed[1], "-i", normed[2],
         "-filter_complex", "[0:v]trim=0:6,setpts=PTS-STARTPTS[v0];[1:v]trim=1:6.5,setpts=PTS-STARTPTS[v1];[2:v]trim=0:4.5,setpts=PTS-STARTPTS[v2];[v0][v1][v2]concat=n=3:v=1:a=0[v]",
         "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", concat])
    final = args.out or os.path.join(OUTPUT, "lipstik_korea_50rb_viral.mp4")
    run(["ffmpeg", "-y", "-i", concat, "-i", voice, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", final])
    print("SELESAI:", final)

if __name__ == "__main__":
    main()
