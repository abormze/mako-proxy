import requests
import urllib3
import re
from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.responses import StreamingResponse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = FastAPI()

# --- البيانات الحقيقية من الـ Log الخاص بك ---
PROXIES = {"http": "http://82.81.95.155:39811", "https": "http://82.81.95.155:39811"}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
REFERER = "https://rotana.net/"

@app.get("/")
def home():
    return {"status": "Koko Full-Tunnel Relay Active"}

@app.get("/rotana/cinema.m3u8")
def get_m3u8():
    # 1. التوكن الحالي (يمكننا جعلها أوتوماتيكية لاحقاً)
    token = "7Y83PP5adWixDF93"
    target_url = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
    
    try:
        # 2. سحب ملف الـ Playlist بالبروكسي والـ Headers
        headers = {"User-Agent": USER_AGENT, "Referer": REFERER}
        r = requests.get(target_url, headers=headers, proxies=PROXIES, timeout=10, verify=False)
        
        if r.status_code == 200:
            base_url = target_url.rsplit('/', 1)[0] + '/'
            lines = r.text.splitlines()
            fixed_lines = []
            
            for line in lines:
                if line.endswith(".ts") and not line.startswith("http"):
                    # إجبار المشغل على طلب الفيديو من سيرفرك أنت (Relay)
                    full_ts_url = base_url + line
                    fixed_lines.append(f"/ts?url={full_ts_url}")
                else:
                    fixed_lines.append(line)
            
            return Response(content="\n".join(fixed_lines), media_type="application/vnd.apple.mpegurl")
        return {"error": "Rotana Source Down"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/ts")
def stream_ts(url: str):
    # 3. سحب قطعة الفيديو الفعلية بالبروكسي والـ Headers وتمريرها للمشاهد
    def generate():
        headers = {"User-Agent": USER_AGENT, "Referer": REFERER}
        with requests.get(url, headers=headers, proxies=PROXIES, stream=True, timeout=15, verify=False) as r:
            for chunk in r.iter_content(chunk_size=1024*256):
                yield chunk

    return StreamingResponse(generate(), media_type="video/MP2T")
