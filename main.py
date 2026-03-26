from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- PROXY FOR BYPASSING GEO-BLOCK ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# The Page to scrape for fresh tokens
ROTANA_PAGE = "https://rotana.net/en/live/channels#/live/rotana-cinema"

# Precise Headers from your log
LATEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8,he;q=0.7",
    "Origin": "https://rotana.net",
    "Referer": "https://rotana.net/"
}

@app.get("/")
def status():
    return {"status": "Koko Pro-Relay Active", "engine": "Chrome-146-Emulation"}

@app.get("/rotana/cinema.m3u8")
def get_cinema_live():
    try:
        session = requests.Session()
        # Step 1: Get the fresh token from the website using Proxy
        web_res = session.get(ROTANA_PAGE, headers=LATEST_HEADERS, proxies=PROXIES, timeout=10)
        
        # Look for the dynamic token (e.g., 7Y83PP5adWixDF93)
        token_match = re.search(r'cinema_net-([a-zA-Z0-9]+)', web_res.text)
        token = token_match.group(1) if token_match else "7Y83PP5adWixDF93" # Fallback to your working token

        # Step 2: Construct the exact Request URL from your logs
        target_url = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
        
        # Step 3: Fetch the M3U8 with the exact Headers
        # Note: We update the referer to match the Request URL as seen in your logs
        stream_headers = LATEST_HEADERS.copy()
        stream_headers["Referer"] = target_url
        
        r = session.get(target_url, headers=stream_headers, proxies=PROXIES, timeout=10, verify=False)
        
        if r.status_code == 200:
            # Step 4: Fix internal paths so VLC knows where to find .ts files
            base_url = target_url.rsplit('/', 1)[0] + '/'
            fixed_content = r.text.replace('l_154', base_url + 'l_154')
            return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
        raise HTTPException(status_code=r.status_code, detail="Stream Source Error")

    except Exception as e:
        return {"error": str(e)}
