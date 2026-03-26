from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3

# تعطيل تحذيرات SSL للتعامل مع البروكسي المنزلي
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- إعدادات البروكسي المنزلي الإسرائيلي (بيزك) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# الرابط الأساسي (لإصلاح الروابط النسبية)
MAKO_BASE_URL = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

# الرابط الطويل مع التوكن (الذي استخرجته من HTTP Toolkit)
TOKEN_URL = (
    "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/index.m3u8"
    "?b-in-range=0-1800&hdnea=st%3D1774497892%7Eexp%3D1774498792%7Eacl%3D%2F*%7E"
    "hmac%3Da592eee68f26e9bbd5d798d84cd4f648c9d23885d18ad2d7aecb0a6bbbd98fc0"
    "&dxseg=mWPE8VTE%2CMLT0tmGC%2CmqZmzXw7%2CzDDDMl3T&dxu=32eb34b1-4ead-459a-8d09-4825af57d50b"
    "&user_id=89ccd74b70b765653456b1f1d56b6d85"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il"
}

@app.get("/")
def home():
    return {"status": "Koko Premium Proxy is Online", "proxy": "Bezeq Residential"}

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # طلب الملف من مـاكو عبر البروكسي الإسرائيلي
        response = requests.get(TOKEN_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        if response.status_code == 200:
            # السحر هنا: تحويل الروابط الناقصة لروابط كاملة تبدأ بسيرفر مـاكو مباشرة
            # هذا يمنع خطأ الـ 404 في VLC
            modified_playlist = response.text.replace('profile', MAKO_BASE_URL + 'profile')
            return Response(content=modified_playlist, media_type="application/vnd.apple.mpegurl")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Mako Error: {response.status_code}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy Connection Failed: {str(e)}")
