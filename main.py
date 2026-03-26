import requests
import re
from fastapi import FastAPI, Response, HTTPException

app = FastAPI()

# البروكسي بتاعك (هنستخدمه بس عشان نجيب التوكن الجديد)
PROXIES = {"http": "http://82.81.95.155:39811", "https": "http://82.81.95.155:39811"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/rotana/cinema.m3u8")
def get_cinema():
    try:
        # 1. بنروح لصفحة روتانا نجيب التوكن "الحي" حالياً
        web_res = requests.get("https://rotana.net/en/live/channels#/live/rotana-cinema", headers=HEADERS, proxies=PROXIES, timeout=10)
        
        # 2. بنطلع التوكن من جافا سكريبت الصفحة (مثلاً: 7Y83PP5adWixDF93)
        token_match = re.search(r'cinema_net-([a-zA-Z0-9]+)', web_res.text)
        token = token_match.group(1) if token_match else "7Y83PP5adWixDF93"

        # 3. ده الرابط الخام اللي المتصفح بيفتحه عندك
        final_link = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
        
        # 4. بنجيب محتوى الملف ونعدل الروابط جواه عشان تبقى كاملة
        r = requests.get(final_link, headers=HEADERS, proxies=PROXIES, timeout=10)
        base_url = final_link.rsplit('/', 1)[0] + '/'
        
        # بنضيف الـ Full Path لكل قطعة فيديو
        fixed_content = r.text.replace('l_154', base_url + 'l_154')
        
        return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
