from fastapi import FastAPI, Response, HTTPException
import requests

app = FastAPI()

# Mako 12 Direct Stream URL
MAKO_HLS_URL = "https://mako-vna-eu.akamaized.net/hls/live/2033787/mako12/index.m3u8"

# High-Level Headers to simulate a real Israeli browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il",
    "Accept": "*/*",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive"
}

@app.get("/")
def home():
    return {
        "status": "Koko Stream Engine is Online",
        "mode": "Direct Bypass",
        "region": "Israel Optimized"
    }

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # Request stream directly with advanced headers to bypass Geo-block
        response = requests.get(MAKO_HLS_URL, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            # Success! Stream playlist returned to VLC/Panel
            return Response(content=response.text, media_type="application/vnd.apple.mpegurl")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Mako Rejected: {response.status_code}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine Error: {str(e)}")
