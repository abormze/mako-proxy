import requests
import urllib3
import re
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = FastAPI()

# --- PROXY IS NOW MANDATORY FOR EVERYTHING ---
PROXIES = {"http": "http://82.81.95.155:39811", "https": "http://82.81.95.155:39811"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://rotana.net/"
}

@app.get("/")
def home():
    return {"status": "Koko Proxy-Tunnel Active"}

@app.get("/rotana/cinema.m3u8")
def get_m3u8():
    try:
        # 1. نجيب التوكن بالبروكسي
        web = requests.get("https://rotana.net/en/live/channels#/live/rotana-cinema", headers=HEADERS, proxies=PROXIES, timeout=10)
        token = re.search(r'cinema_net-([a-zA-Z0-9]+)', web.text).group(1)
        
        # 2. نجيب ملف الـ m3u8 بالبروكسي
        stream_url = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
        r = requests.get(stream_url, headers=HEADERS, proxies=PROXIES, timeout=10)
        
        # 3. تعديل الروابط عشان كل "قطعة فيديو" تمر من خلال البروكسي
        base_url = stream_url.rsplit('/', 1)[0] + '/'
        lines = r.text.splitlines()
        fixed_lines = []
        for line in lines:
            if line.endswith(".ts"):
                # بنجبر المشغل يطلب القطعة من السيرفر بتاعنا في Koyeb
                full_ts = base_url + line
                fixed_lines.append(f"/relay_ts?url={full_ts}")
            else:
                fixed_lines.append(line)
        
        return Response(content="\n".join(fixed_lines), media_type="application/vnd.apple.mpegurl")
    except:
        raise HTTPException(status_code=500, detail="Check your Home Proxy IP")

@app.get("/relay_ts")
def relay_ts(url: str):
    # السيرفر بيسحب الفيديو من البروكسي ويبعته للمشغل مباشرة
    def stream():
        with requests.get(url, headers=HEADERS, proxies=PROXIES, stream=True, timeout=20) as r:
            for chunk in r.iter_content(chunk_size=1024*256):
                yield chunk
    return StreamingResponse(stream(), media_type="video/MP2T")
