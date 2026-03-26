from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- NEW ISRAELI PROXY UPDATED ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# The Main VOD/Live Page
MAKO_WEB_URL = "https://www.mako.co.il/mako-vod-live/VOD-65d214a14a38241006.htm"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.mako.co.il/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

@app.get("/")
def home():
    return {"status": "Koko Scraper v4 Online", "secure": "True"}

@app.get("/mako/live.m3u8")
def get_stream(request: Request):
    # 1. Quick Geo-Check
    country = request.headers.get("cf-ipcountry", "Unknown")
    if country not in ["IL", "Unknown"]:
        raise HTTPException(status_code=403, detail=f"Access Denied for {country}")

    # 2. Advanced Scraping Logic
    try:
        session = requests.Session()
        # نطلب الصفحة بالبروكسي لضمان الحصول على توكن إسرائيلي
        response = session.get(MAKO_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # البحث عن الرابط بأكثر من نمط (Regex)
        # النمط الأول: الرابط المباشر
        match = re.search(r'https://[^\s"]+index\.m3u8\?hdnea=[^\s"]+', response.text)
        
        # النمط الثاني: لو الرابط "مخفي" بتنسيق يونيكود
        if not match:
            match = re.search(r'https:[\\/]+[^\s"]+index\.m3u8\?hdnea=[^\s"]+', response.text)

        if match:
            dynamic_url = match.group(0).replace('\\', '')
            print(f"[*] Found Token URL: {dynamic_url[:60]}...")
            
            # طلب ملف الـ M3U8 الفعلي
            r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
            
            if r.status_code == 200:
                # تصحيح المسارات لـ VLC
                fixed_content = r.text.replace('profile', BASE_PATH + 'profile')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
            else:
                raise HTTPException(status_code=r.status_code, detail=f"Mako rejected Proxy Request: {r.status_code}")
        
        # لو فشل الـ Scraper تماماً، اطبع جزء من الصفحة في الـ Logs عشان نعرف السبب
        print(f"[-] Scraper Failed. Page Content Length: {len(response.text)}")
        raise HTTPException(status_code=500, detail="Mako Scraper could not find the stream link")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
