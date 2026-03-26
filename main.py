from fastapi import FastAPI, Response, HTTPException
import requests

app = FastAPI()

# بيانات البروكسي الإسرائيلي الخاص بك
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

MAKO_HLS_URL = "https://mako-vna-eu.akamaized.net/hls/live/2033787/mako12/index.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def home():
    return {"status": "Koko Israel Proxy is Online", "proxy_active": "True"}

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # إرسال الطلب عبر البروكسي الإسرائيلي
        response = requests.get(MAKO_HLS_URL, headers=HEADERS, proxies=PROXIES, timeout=15)
        
        if response.status_code == 200:
            return Response(content=response.text, media_type="application/vnd.apple.mpegurl")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Proxy Error: {response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection Failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
