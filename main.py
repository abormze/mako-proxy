from fastapi import FastAPI, Response, HTTPException
import requests

app = FastAPI()

# --- LIVE ISRAEL PROXY CONFIGURATION ---
# Using your provided proxy: 45.150.108.239:39811
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

MAKO_HLS_URL = "https://mako-vna-eu.akamaized.net/hls/live/2033787/mako12/index.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il"
}

@app.get("/")
def home():
    return {
        "status": "Koko Proxy is Online",
        "proxy_active": "45.150.108.239",
        "target": "Mako 12"
    }

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # Step 1: Attempt to get stream via your Israel Proxy
        response = requests.get(MAKO_HLS_URL, headers=HEADERS, proxies=PROXIES, timeout=12)
        
        if response.status_code == 200:
            return Response(content=response.text, media_type="application/vnd.apple.mpegurl")
        else:
            # Step 2: Fallback to direct request if proxy fails or returns non-200
            r_direct = requests.get(MAKO_HLS_URL, headers=HEADERS, timeout=8)
            return Response(content=r_direct.text, media_type="application/vnd.apple.mpegurl")
            
    except Exception as e:
        # Final error if both attempts fail
        raise HTTPException(status_code=500, detail=f"Streaming Error: {str(e)}")
