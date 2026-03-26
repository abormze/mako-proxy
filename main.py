from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import RedirectResponse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- YOUR STABLE HOME PROXY (Important for M3U8 fetching) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# The Link from your screenshot (720p Stable)
ROTANA_CINEMA_720P = "https://rotana.hibridcdn.net/rotananet/cinema_net-7Y83PP5adWixDF93/rotana/cinema_720p/chunks.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def home():
    return {"status": "Rotana Direct-Pass Active"}

@app.get("/rotana/cinema.m3u8")
def get_cinema_m3u8():
    try:
        # Step 1: Fetch the m3u8 using your Home Proxy
        r = requests.get(ROTANA_CINEMA_720P, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail="M3U8 Fetch Failed")

        # Step 2: Fix the paths so VLC can find the segments (.ts)
        base_url = ROTANA_CINEMA_720P.rsplit('/', 1)[0] + '/'
        original_content = r.text
        fixed_content = ""

        for line in original_content.splitlines():
            if line.endswith(".ts") and not line.startswith("http"):
                # Make the path full so VLC knows where to go
                fixed_content += base_url + line + "\n"
            else:
                fixed_content += line + "\n"
        
        return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")

    except Exception as e:
        return {"error": str(e)}

# Adding a simple Redirect for the segments if needed
@app.get("/rotana/segment")
def redirect_segment(url: str):
    return RedirectResponse(url=url)
