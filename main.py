import requests
from fastapi import FastAPI, Response, HTTPException

app = FastAPI()

# --- BEZEQ RESIDENTIAL ISRAEL PROXY ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# The Direct Mako Link
MAKO_URL = "https://mako-vna-eu.akamaized.net/hls/live/2033787/mako12/index.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/",
}

@app.get("/")
def status():
    return {"status": "Koko Bezeq Proxy Active", "ip": "82.81.95.155"}

@app.get("/mako/live.m3u8")
def get_stream():
    try:
        # Requesting the M3U8 using Bezeq Proxy
        # We use verify=False to avoid SSL issues with some local proxies
        r = requests.get(MAKO_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        if r.status_code == 200:
            return Response(content=r.text, media_type="application/vnd.apple.mpegurl")
        else:
            # If proxy fails, try direct as backup
            r_direct = requests.get(MAKO_URL, headers=HEADERS, timeout=10)
            return Response(content=r_direct.text, media_type="application/vnd.apple.mpegurl")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming Error: {str(e)}")
