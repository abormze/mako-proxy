from fastapi import FastAPI, Response
import requests
import re

app = FastAPI()

# البروكسي (لجلب التوكن فقط)
PROXIES = {"http": "http://82.81.95.155:39811", "https": "http://82.81.95.155:39811"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://rotana.net/"
}

@app.get("/rotana/cinema.m3u8")
def get_final():
    try:
        # 1. جلب التوكن الحي
        web = requests.get("https://rotana.net/en/live/channels#/live/rotana-cinema", headers=HEADERS, proxies=PROXIES, timeout=7)
        token = re.search(r'cinema_net-([a-zA-Z0-9]+)', web.text).group(1)
        
        # 2. رابط الـ 720p اللي شغال عندك في الكروم
        stream_url = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
        
        # 3. بناء ملف M3U8 ذكي بيجبر المشغل يبعت الـ Referer
        # الطريقة دي بتخلي VLC يشتغل كأنه متصفح
        m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=1280000,RESOLUTION=1280x720
#EXTVLCOPT:http-user-agent={HEADERS['User-Agent']}
#EXTVLCOPT:http-referrer={HEADERS['Referer']}
{stream_url}|User-Agent={HEADERS['User-Agent']}&Referer={HEADERS['Referer']}"""

        return Response(content=m3u8_content, media_type="application/vnd.apple.mpegurl")
    except:
        return {"error": "Try again in a moment"}
