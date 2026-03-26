from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ISRAELI RESIDENTIAL PROXY ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# Official Mako Ticket API (Auto-Refresh Source)
MAKO_API_TICKET = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
# Base streaming path
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def status():
    return {"status": "Koko Shield Active", "region": "Israel Only"}

@app.get("/mako/live.m3u8")
def get_auto_stream(request: Request):
    # --- SECURITY GATE: ISRAEL ONLY ---
    # Detect country from Koyeb/Cloudflare header
    visitor_country = request.headers.get("cf-ipcountry", "Unknown")
    
    # Allow only IL (Israel) or Unknown (for local testing/no-header cases)
    if visitor_country != "IL" and visitor_country != "Unknown":
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Your location ({visitor_country}) is blocked. Israel only."
        )

    try:
        # Step 1: Request fresh Tokenized URL from Mako via Proxy
        api_response = requests.get(MAKO_API_TICKET, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        data = api_response.json()
        fresh_url = data.get("mediaUrl")
        
        if fresh_url:
            # Step 2: Fetch the actual M3U8 using the NEW token
            r = requests.get(fresh_url, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
            
            if r.status_code == 200:
                # Step 3: Path Correction for VLC/IPTV
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako API failed to return a link")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
