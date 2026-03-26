from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- YOUR UPDATED ISRAELI PROXY ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# The Direct Mako Ticket API (Fastest and most stable)
MAKO_TICKET_API = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def home():
    return {"status": "Koko Mako-API v5 Online", "proxy": "45.150.108.239", "region": "Israel"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # 1. Geo-Check (Koyeb Region Check)
    country = request.headers.get("cf-ipcountry", "Unknown")
    if country != "Unknown" and country != "IL":
        # Block access if visitor is definitely not from Israel
        raise HTTPException(status_code=403, detail="Access Denied: Israel residents only.")

    try:
        # 2. Get the Tokenized URL from Mako's Ticket API using your proxy
        api_response = requests.get(MAKO_TICKET_API, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        
        # Parse JSON response
        data = api_response.json()
        dynamic_url = data.get("mediaUrl")

        if dynamic_url:
            # 3. Pull the .m3u8 playlist using the new token
            r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
            
            if r.status_code == 200:
                # 4. Correct internal profile paths for VLC/IPTV
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako API failed to return a valid stream link")

    except Exception as e:
        # Catching proxy or connection issues
        raise HTTPException(status_code=500, detail=f"API Connection Error: {str(e)}")
