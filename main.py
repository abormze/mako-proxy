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

# Official Mako API for mobile apps (The most stable source)
MAKO_TICKET_API = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def home():
    # If this shows "Version 5.0", then the update is successful
    return {"status": "Koko Mako-API Online", "version": "5.0", "proxy": "Active"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # 1. Geo-Lock: Allow Israel (IL) or Unknown
    country = request.headers.get("cf-ipcountry", "Unknown")
    if country not in ["IL", "Unknown"]:
        raise HTTPException(status_code=403, detail=f"Access Denied: {country} is blocked.")

    try:
        # 2. Call Mako's official API via Proxy to get the secret Ticket
        api_response = requests.get(MAKO_TICKET_API, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        data = api_response.json()
        dynamic_url = data.get("mediaUrl")

        if dynamic_url:
            # 3. Fetch the actual playlist using the token
            r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
            
            if r.status_code == 200:
                # 4. Fix relative paths for VLC/IPTV
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako API Error: No mediaUrl found")

    except Exception as e:
        # Detailed error logging
        raise HTTPException(status_code=500, detail=f"API Connection Failure: {str(e)}")
