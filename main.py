from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3
import re

# تعطيل تحذيرات SSL لضمان استقرار الاتصال عبر البروكسي
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ORIGINAL HOME PROXY (Essential for Rotana) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# Rotana URLs
ROTANA_WEB_PAGE = "https://rotana.net/en/live/channels#/live/rotana-cinema"
# المجلد الرئيسي للبث
ROTANA_BASE_STREAM = "https://rotana.hibridcdn.net/rotananet/"

# Headers matching your yt-dlp and Chrome 146 logs
LATEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def status():
    return {"status": "Koko Hybrid Engine Active", "modes": ["API", "HTML_Scraper"]}

@app.get("/rotana/cinema.m3u8")
def get_cinema_stream():
    token = None
    
    # --- STEP 1: HTML SCRAPER SYSTEM ---
    try:
        # محاولة استخراج التوكن من كود الصفحة (HTML)
        response = requests.get(ROTANA_WEB_PAGE, headers=LATEST_HEADERS, proxies=PROXIES, timeout=10)
        # البحث عن نمط التوكن (مثلاً: cinema_net-7Y83PP5adWixDF93)
        match = re.search(r'cinema_net-([a-zA-Z0-9]+)', response.text)
        if match:
            token = match.group(1)
            print(f"Token found via HTML: {token}")
    except Exception as e:
        print(f"HTML Scraper failed: {e}")

    # --- STEP 2: FALLBACK TO API OR LAST KNOWN (If HTML fails) ---
    if not token:
        # توكن احتياطي (التوكن الذي يعمل حالياً عندك)
        token = "7Y83PP5adWixDF93" 
        print(f"Using Fallback Token: {token}")

    # --- STEP 3: CONSTRUCT FINAL URL & FIX PATHS ---
    # بناء رابط الـ 720p الذي جربته أنت ونجح
    target_url = f"{ROTANA_BASE_STREAM}cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
    
    try:
        # جلب ملف الـ M3U8 النهائي
        r = requests.get(target_url, headers=LATEST_HEADERS, proxies=PROXIES, timeout=12, verify=False)
        
        if r.status_code == 200:
            # إصلاح المسارات الداخلية لملفات الـ .ts لتعمل في VLC مباشرة
            base_path = target_url.rsplit('/', 1)[0] + '/'
            lines = r.text.splitlines()
            fixed_lines = []
            
            for line in lines:
                if line.endswith(".ts") and not line.startswith("http"):
                    fixed_lines.append(base_path + line)
                else:
                    fixed_lines.append(line)
            
            return Response(content="\n".join(fixed_lines), media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=r.status_code, detail="Stream rejected by Rotana server")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
