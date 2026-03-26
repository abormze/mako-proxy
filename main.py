from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = FastAPI()

# --- البيانات من الـ Logs اللي بعتها ---
PROXIES = {"http": "http://82.81.95.155:39811", "https": "http://82.81.95.155:39811"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def home():
    return {"status": "Koko Ultra-Relay Active"}

@app.get("/rotana/cinema.m3u8")
def get_playlist():
    try:
        # 1. نجيب التوكن الحي من الموقع
        web = requests.get("https://rotana.net/en/live/channels#/live/rotana-cinema", headers=HEADERS, proxies=PROXIES, timeout=10)
        token_match = re.search(r'cinema_net-([a-zA-Z0-9]+)', web.text)
        token = token_match.group(1) if token_match else "7Y83PP5adWixDF93"

        # 2. نجيب ملف الـ M3U8
        stream_url = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
        r = requests.get(stream_url, headers=HEADERS, proxies=PROXIES, timeout=10)
        
        base_path = stream_url.rsplit('/', 1)[0] + '/'
        lines = r.text.splitlines()
        fixed_lines = []
        
        for line in lines:
            if line.endswith(".ts") and not line.startswith("http"):
                # السر هنا: بنجبر VLC يطلب قطعة الفيديو من سيرفرنا إحنا
                full_ts = base_path + line
                fixed_lines.append(f"https://repulsive-novelia-kokoa1-781312d9.koyeb.app/stream_ts?url={full_ts}")
            else:
                fixed_lines.append(line)
        
        return Response(content="\n".join(fixed_lines), media_type="application/vnd.apple.mpegurl")
    except Exception as e:
        return {"error": str(e)}

@app.get("/stream_ts")
def stream_ts(url: str):
    # السيرفر بيسحب قطعة الفيديو بالبروكسي والـ Headers ويبعتها لـ VLC
    def relay_video():
        try:
            with requests.get(url, headers=HEADERS, proxies=PROXIES, stream=True, timeout=15, verify=False) as r:
                for chunk in r.iter_content(chunk_size=1024*512):
                    yield chunk
        except:
            pass
    return StreamingResponse(relay_video(), media_type="video/MP2T")
