from fastapi import FastAPI, Response, HTTPException
import requests

app = FastAPI()

# --- CONFIGURATION ---
# Recent Israel Proxy (Ensure periodic updates if it stops working)
PROXIES = {
    "http": "http://185.175.145.146:3128",
    "https": "http://185.175.145.146:3128"
}

MAKO_HLS_URL = "https://mako-vna-eu.akamaized.net/hls/live/2033787/mako12/index.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il"
}

@app.get("/")
def home():
    return {
        "status": "Koko Premium Proxy is Online",
        "service": "Mako 12 Live",
        "region": "Israel"
    }

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # Request stream via Israel Proxy with 15s timeout
        response = requests.get(MAKO_HLS_URL, headers=HEADERS, proxies=PROXIES, timeout=15)
        
        if response.status_code == 200:
            # Return M3U8 content directly to the player (VLC/Panel)
            return Response(content=response.text, media_type="application/vnd.apple.mpegurl")
        else:
            # Fallback: Attempt direct request if proxy fails
            response_direct = requests.get(MAKO_HLS_URL, headers=HEADERS, timeout=10)
            return Response(content=response_direct.text, media_type="application/vnd.apple.mpegurl")
            
    except Exception as e:
        # Return detailed error if both attempts fail
        raise HTTPException(status_code=500, detail=f"Streaming Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
