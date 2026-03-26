from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3

# تعطيل رسائل تحذير SSL لأننا نتصل بـ IP مباشر
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# Mako Direct IP (One of Akamai's edge servers)
# We use the IP instead of the hostname to fix NameResolutionError
MAKO_IP_URL = "https://23.41.219.102/hls/live/2033787/mako12/index.m3u8"

HEADERS = {
    "Host": "mako-vna-eu.akamaized.net", # IMPORTANT: This tricks the server
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il",
    "Accept": "*/*",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
}

@app.get("/")
def home():
    return {"status": "Koko DNS-Force Engine is Online", "mode": "Direct IP Access"}

@app.get("/mako/live.m3u8")
def get_mako_stream():
    try:
        # Request stream via Direct IP to bypass DNS issues
        # verify=False is mandatory when connecting via IP for SSL
        response = requests.get(MAKO_IP_URL, headers=HEADERS, timeout=15, verify=False)
        
        if response.status_code == 200:
            return Response(content=response.text, media_type="application/vnd.apple.mpegurl")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Mako IP Rejected: {response.status_code}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fatal IP Error: {str(e)}")
