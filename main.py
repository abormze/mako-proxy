from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ISRAELI RESIDENTIAL PROXY ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# Mobile API Endpoint
MAKO_API_TICKET = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

# Realistic Mobile Headers to bypass "Line 1 Column 1" error
HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; SM-G998B Build/TP1A.220624.014)",
    "Host": "mass.mako.co.il",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip"
}

@app.get("/")
def status():
    return {"status": "Shield Active", "mode": "Auto-API", "region": "Israel-Only"}

@app.get("/mako/live.m3u8")
def get_auto_stream(request: Request):
    # 1. Geo-Gate: Check if requester is from Israel
    visitor_country = request.headers.get("cf-ipcountry", "Unknown")
    
    # Strictly allow Israel (IL) or Unknown (for local testing)
    if visitor_country != "IL" and visitor_country != "Unknown":
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Region {visitor_country} is not allowed."
        )

    try:
        # 2. Get fresh Ticket via Proxy with Mobile Headers
        session = requests.Session()
        api_response = session.get(MAKO_API_TICKET, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # Check if response is empty or invalid
        if not api_response.text or api_response.status_code != 200:
            raise HTTPException(status_code=502, detail="Proxy failed to reach Mako API")

        data = api_response.json()
        fresh_url = data.get("mediaUrl")
        
        if fresh_url:
            # 3. Pull M3U8 using the fresh token
            r = session.get(fresh_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
            
            if r.status_code == 200:
                # 4. Path Fix for VLC
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako API returned invalid mediaUrl")

    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Mako API returned non-JSON response. Check Proxy.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
