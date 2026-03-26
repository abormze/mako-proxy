from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3

# إخفاء تحذيرات الـ SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- NEW ISRAELI PROXY (Updated as per your request) ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# --- THE WORKING TOKEN URL ---
# Note: Use the manual link you captured from HTTP Toolkit here
MAKO_TOKEN_URL = (
    "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/index.m3u8"
    "?b-in-range=0-1800&hdnea=st%3D1774497892%7Eexp%3D1774498792%7Eacl%3D%2F*%7E"
    "hmac%3Da592eee68f26e9bbd5d798d84cd4f648c9d23885d18ad2d7aecb0a6bbbd98fc0"
)

# Base path for internal segments (Prevents 404)
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def home():
    return {
        "status": "Koko Manual Relay Online", 
        "proxy": "45.150.108.239", 
        "mode": "Direct-Token"
    }

@app.get("/mako/live.m3u8")
def get_stream():
    try:
        # Request the .m3u8 file through the Israeli proxy
        r = requests.get(MAKO_TOKEN_URL, headers=HEADERS, proxies=PROXIES, timeout=20, verify=False)
        
        if r.status_code == 200:
            # Fix internal profile links for VLC
            fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
            return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        else:
            # If Proxy fails, it will show the status code here
            raise HTTPException(status_code=r.status_code, detail=f"Mako server returned status: {r.status_code}")
            
    except Exception as e:
        # Catching proxy connection timeout or failure
        raise HTTPException(status_code=500, detail=f"Proxy Connection Error: {str(e)}")
