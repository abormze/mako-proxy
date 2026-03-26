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

MAKO_WEB_URL = "https://www.mako.co.il/mako-vod-live/VOD-65d214a14a38241006.htm"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

def is_visitor_from_israel(ip_address):
    """
    Checks if the person trying to watch is from Israel.
    """
    try:
        # Using a free GeoIP API to check the visitor's country
        check_url = f"https://ipapi.co/{ip_address}/country/"
        response = requests.get(check_url, timeout=5)
        return response.text.strip() == "IL"
    except:
        # In case of API failure, we allow (or block) as a safety measure
        return True 

def get_dynamic_token_url():
    try:
        session = requests.Session()
        response = session.get(MAKO_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        match = re.search(r'https://[^\s"]+index\.m3u8\?hdnea=[^\s"]+', response.text)
        if match:
            return match.group(0).replace('\\', '')
        return None
    except:
        return None

@app.get("/")
def home():
    return {"status": "Security Engine Active", "access": "Israel Only"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # --- SECURITY CHECK: ISRAEL ONLY ---
    visitor_ip = request.client.host
    # If Koyeb is behind a proxy, we use the real IP from headers
    real_ip = request.headers.get("x-forwarded-for", visitor_ip).split(",")[0]
    
    if not is_visitor_from_israel(real_ip):
        print(f"[!] Blocked access from foreign IP: {real_ip}")
        raise HTTPException(status_code=403, detail="Access Denied: This stream is for Israel residents only.")

    # --- PROCEED IF IN ISRAEL ---
    dynamic_url = get_dynamic_token_url()
    if not dynamic_url:
        raise HTTPException(status_code=500, detail="Token retrieval failed")

    try:
        r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        if r.status_code == 200:
            fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
            return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        else:
            raise HTTPException(status_code=r.status_code, detail="Mako connection error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
