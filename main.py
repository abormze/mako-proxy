from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- YOUR STABLE HOME PROXY (82.81) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# The Direct Mako Ticket API (Fastest and most stable)
MAKO_API_TICKET = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def status():
    return {"status": "Koko Shield v7 Online", "proxy": "Home-82.81", "region": "Israel-Only"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # --- 1. GEO-FENCE: ISRAEL ONLY ---
    # Detect country from Koyeb/Cloudflare header
    visitor_country = request.headers.get("cf-ipcountry", "Unknown")
    
    if visitor_country != "IL" and visitor_country != "Unknown":
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Stream restricted to Israel residents only."
        )

    try:
        # --- 2. GET FRESH TOKEN VIA HOME PROXY ---
        # Calling Mako API directly to get the mediaUrl
        api_response = requests.get(MAKO_API_TICKET, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        data = api_response.json()
        fresh_url = data.get("mediaUrl")
        
        if fresh_url:
            # --- 3. PULL M3U8 PLAYLIST VIA PROXY ---
            r = requests.get(fresh_url, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
            
            if r.status_code == 200:
                # --- 4. PATH CORRECTION FOR VLC ---
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako API failed to provide a token")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
