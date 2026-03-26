from fastapi import FastAPI, Response, HTTPException
import requests

app = FastAPI()

# Mako 12 Direct IP-based URL (Bypassing DNS Issues)
MAKO_URL = "https://2.16.147.112/hls/live/2033787/mako12/index.m3u8"

HEADERS = {
    "Host": "mako-vna-eu.akamaized.net", # Essential to bypass Akamai check
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
}

@app.get("/")
def home():
    return {"status": "Koko DNS Bypass Engine Online", "target": "Mako 12"}

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # Request stream using Direct IP + Host Header
        # verify=False is used because SSL is issued to Domain, not IP
        response = requests.get(MAKO_URL, headers=HEADERS, timeout=15, verify=False)
        
        if response.status_code == 200:
            return Response(content=response.text, media_type="application/vnd.apple.mpegurl")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Mako Error: {response.status_code}")
            
    except Exception as e:
        # If IP fails, we try the domain as a last resort
        try:
            r_domain = requests.get("https://mako-vna-eu.akamaized.net/hls/live/2033787/mako12/index.m3u8", headers=HEADERS, timeout=10)
            return Response(content=r_domain.text, media_type="application/vnd.apple.mpegurl")
        except:
            raise HTTPException(status_code=500, detail=f"Total Failure: {str(e)}")
