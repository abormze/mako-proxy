from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3

# Disable SSL warnings for smoother proxy performance
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ISRAELI RESIDENTIAL PROXY CONFIGURATION ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# Official Mako Ticket API (Used by mobile apps)
MAKO_API_TICKET = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
# Base streaming path to resolve relative segments
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def status():
    return {
        "engine": "Koko Auto-Refresh Active",
        "proxy": "45.150.108.239",
        "status": "online"
    }

@app.get("/mako/live.m3u8")
def get_auto_stream(request: Request):
    try:
        # Step 1: Request a fresh Tokenized URL from Mako API via Proxy
        api_response = requests.get(MAKO_API_TICKET, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        data = api_response.json()
        
        # Extract the dynamic media URL containing the fresh 'hdnea' token
        fresh_url = data.get("mediaUrl")
        
        if fresh_url:
            # Step 2: Fetch the actual M3U8 playlist using the new token
            r = requests.get(fresh_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
            
            if r.status_code == 200:
                # Step 3: Path Correction (Ensures internal segments load in VLC)
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako API failed to provide a valid link")

    except Exception as e:
        # Log error details if the proxy or API fails
        raise HTTPException(status_code=500, detail=f"Auto-Fetch System Error: {str(e)}")
