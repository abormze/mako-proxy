from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- NEW ISRAELI PROXY ---
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

@app.get("/")
def home():
    return {"status": "Koko Israel-Only Shield Active"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # --- SMART GEO-LOCK (FASTEST METHOD) ---
    # Koyeb passes the visitor's country in 'cf-ipcountry' header
    visitor_country = request.headers.get("cf-ipcountry", "Unknown")
    
    # Get Real IP for logging
    visitor_ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0]
    
    print(f"[*] Access attempt from: {visitor_ip} | Country: {visitor_country}")

    # السماح فقط بـ IL (إسرائيل) أو Unknown (احتياطاً لبعض الحالات)
    if visitor_country not in ["IL", "Unknown"]:
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Your Country is {visitor_country}. This stream is for Israel residents only."
        )

    # --- AUTO-SCRAPER LOGIC ---
    try:
        session = requests.Session()
        res = session.get(MAKO_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # البحث عن الرابط الجديد بالتوكن
        match = re.search(r'https://[^\s"]+index\.m3u8\?hdnea=[^\s"]+', res.text)
        
        if match:
            dynamic_url = match.group(0).replace('\\', '')
            
            # سحب الملف عبر البروكسي
            r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
            
            if r.status_code == 200:
                # تصحيح المسارات لـ VLC
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako Scraper Failed")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
