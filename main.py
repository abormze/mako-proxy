from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- YOUR UPDATED ISRAELI PROXY ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# Mako Ticket API (The secret source)
MAKO_TICKET_API = "https://mass.mako.co.il/ClicksStatistics/bentayemStreaming.dot?channelId=mako12&videoType=live"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def home():
    return {"status": "Koko Mako-API Online", "proxy": "45.150.108.239"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # 1. Geo-Check (Optional, lets you in by default)
    country = request.headers.get("cf-ipcountry", "Unknown")
    if country != "Unknown" and country != "IL":
        raise HTTPException(status_code=403, detail="Israel Residents Only")

    # 2. Call Mako API to get the fresh Token URL
    try:
        # بنكلم الـ API بالبروكسي عشان ناخد Ticket إسرائيلي
        response = requests.get(MAKO_TICKET_API, headers=HEADERS, proxies=PROXIES, timeout=10, verify=False)
        data = response.json()
        
        # استخراج الرابط من الـ JSON
        dynamic_url = data.get("mediaUrl")
        
        if dynamic_url:
            print(f"[*] API Success! Token Received.")
            # طلب ملف الـ M3U8 الفعلي بالبروكسي
            r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=10, verify=False)
            
            if r.status_code == 200:
                # تصحيح المسارات لـ VLC
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=500, detail="Mako API failed to return mediaUrl")

    except Exception as e:
        # لو فشل الـ API، بنجرب رابط احتياطي
        print(f"[-] API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
