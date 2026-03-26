from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ORIGINAL HOME PROXY (STABLE) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# Official Mako Ticket API
MAKO_API_TICKET = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
# Base streaming path for VLC compatibility
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def status():
    return {
        "engine": "Koko Home Shield Active",
        "proxy": "Home-82.81",
        "region": "Israel-Only"
    }

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # 1. GEO-FENCE: ISRAEL ONLY (Koyeb/Cloudflare Header)
    # This ensures only users in Israel can open the link
    visitor_country = request.headers.get("cf-ipcountry", "Unknown")
    
    if visitor_country != "IL" and visitor_country != "Unknown":
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Region {visitor_country} is blocked. Israel only."
        )

    try:
        session = requests.Session()
        
        # 2. Get fresh Token URL using Home Proxy
        api_response = session.get(MAKO_API_TICKET, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        data = api_response.json()
        fresh_url = data.get("mediaUrl")
        
        if not fresh_url:
            raise HTTPException(status_code=500, detail="Mako API failed to return mediaUrl")

        # 3. Pull the actual M3U8 playlist using Home Proxy
        r = session.get(fresh_url, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        
        if r.status_code == 200:
