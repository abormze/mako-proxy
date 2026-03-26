from fastapi import FastAPI, Response
import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = FastAPI()

# البروكسي (فقط لجلب التوكن الحي)
PROXIES = {"http": "http://82.81.95.155:39811", "https": "http://82.81.95.155:39811"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://rotana.net/"
}

@app.get("/rotana/cinema.m3u8")
def get_rotana_final():
    try:
        # 1. جلب التوكن "الحي" من صفحة روتانا عبر البروكسي
        web = requests.get("https://rotana.net/en/live/channels#/live/rotana-cinema", headers=HEADERS, proxies=PROXIES, timeout=10)
        token_match = re.search(r'cinema_net-([a-zA-Z0-9]+)', web.text)
        token = token_match.group(1) if token_match else "7Y83PP5adWixDF93"

        # 2. بناء رابط الـ Master
        stream_url = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
        
        # 3. جلب محتوى الـ M3U8 وتعديله
        r = requests.get(stream_url, headers=HEADERS, proxies=PROXIES, timeout=10)
        base_url = stream_url.rsplit('/', 1)[0] + '/'
        
        lines = r.text.splitlines()
        fixed_lines = ["#EXTM3U"]
        
        # السر هنا: إجبار VLC على إرسال الـ Headers مع كل قطعة فيديو (TS)
        # نستخدم خاصية التمرير المباشر من روتانا
        for line in lines:
            if line.endswith(".ts") and not line.startswith("http"):
                # نقوم بحقن الـ Referer والـ User-Agent داخل الرابط ليفهمه VLC
                full_url = base_url + line
                # صياغة خاصة لبرامج IPTV و VLC لإرسال الـ Headers
                fixed_lines.append(f"#EXTVLCOPT:http-user-agent={HEADERS['User-Agent']}")
                fixed_lines.append(f"#EXTVLCOPT:http-referrer={HEADERS['Referer']}")
                fixed_lines.append(full_url)
            elif not line.startswith("#EXTM3U"):
                fixed_lines.append(line)
        
        return Response(content="\n".join(fixed_lines), media_type="application/vnd.apple.mpegurl")

    except Exception as e:
        return {"error": str(e)}
