from fastapi import FastAPI, Response, HTTPException
import requests

app = FastAPI()

# --- BEZEQ RESIDENTIAL ISRAEL PROXY (100% WORKING) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

MAKO_HLS_URL = "https://mako-vna-eu.akamaized.net/hls/live/2033787/mako12/index.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
}

@app.get("/")
def home():
    return {
        "status": "Koko Bezeq Proxy is Online",
        "region": "Israel (Bezeq)",
        "proxy": "82.81.95.155"
    }

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # Request stream via Bezeq Residential Proxy
        response = requests.get(MAKO_HLS_URL, headers=HEADERS, proxies=PROXIES, timeout=15)
        
        if response.status_code == 200:
            # Passing the high-quality playlist to VLC/Panel
            return Response(content=response.text, media_type="application/vnd.apple.mpegurl")
        else:
            # Fallback to direct request if proxy fluctuates
            r_direct = requests.get(MAKO_HLS_URL, headers=HEADERS, timeout=10)
            return Response(content=r_direct.text, media_type="application/vnd.apple.mpegurl")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bezeq Proxy Error: {str(e)}")
