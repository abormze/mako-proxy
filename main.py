from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ISRAELI RESIDENTIAL PROXY ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# The Main Mako Live Page
MAKO_WEB_URL = "https://www.mako.co.il/mako-vod-live/VOD-65d214a14a38241006.htm"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def status():
    return {"status": "Koko Shield Active", "mode": "Smart-Scraper", "region": "Israel-Only"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # --- 1. GEO-FENCE: ISRAEL ONLY ---
    # Using Koyeb/Cloudflare Country Header
    visitor_country = request.headers.get("cf-ipcountry", "Unknown")
    
    # Block anyone NOT in Israel
    if visitor_country != "IL" and visitor_country != "Unknown":
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Stream restricted to Israel. Detected: {visitor_country}"
        )

    # --- 2. AUTOMATIC LINK EXTRACTION ---
    try:
        session = requests.Session()
        # Fetch the webpage via Proxy
        response = session.get(MAKO_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # Regex to find the tokenized .m3u8 link (handles escaped slashes)
        match = re.search(r'https?[:\\/]+[^"\s]+index\.m3u8\?hdnea=[^"\s]+', response.text)
        
        if match:
            # Clean the URL (remove backslashes if any)
            dynamic_url = match.group(0).replace('\\', '')
            
            # Request the actual playlist
            r = session.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
            
            if r.status_code == 200:
                # Path Fix for VLC compatibility
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Scraper failed to extract token from page.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
