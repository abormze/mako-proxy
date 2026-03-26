from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3
import re

# Disable SSL warnings for proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- YOUR UPDATED ISRAELI PROXY ---
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
    return {"status": "Koko Israel Shield Online", "version": "Automated v3"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # --- ENHANCED GEO-LOCK CHECK ---
    # Try multiple ways to get the visitor's country
    country = request.headers.get("cf-ipcountry") or request.headers.get("x-vercel-ip-country") or "Unknown"
    visitor_ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0]
    
    print(f"[*] Access attempt: IP={visitor_ip} | Country={country}")

    # السماح بـ IL (إسرائيل) أو Unknown (عشان ما يقفلش في وشك لو الهيدر ناقص)
    # الحظر فقط لو الدولة معروفة إنها مش إسرائيل (مثل US, GB, DE)
    if country != "Unknown" and country != "IL":
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Your Country is {country}. Israel residents only."
        )

    # --- AUTO-SCRAPER LOGIC ---
    try:
        session = requests.Session()
        res = session.get(MAKO_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # Search for fresh .m3u8 with token
        match = re.search(r'https://[^\s"]+index\.m3u8\?hdnea=[^\s"]+', res.text)
        
        if match:
            dynamic_url = match.group(0).replace('\\', '')
            r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
            
            if r.status_code == 200:
                # Fix relative paths for VLC
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Scraper Error: Could not find token")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
