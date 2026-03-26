from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- YOUR STABLE HOME PROXY (To fetch fresh Token) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# Rotana Cinema Web Page (The source of tokens)
ROTANA_WEB_URL = "https://rotana.net/en/live/channels#/live/rotana-cinema"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def home():
    return {"status": "Koko Token-Hunter Active", "proxy": "Home-82.81"}

@app.get("/rotana/cinema.m3u8")
def get_cinema_auto():
    try:
        # Step 1: Visit the website via Proxy to find the NEW Token
        # We look for the pattern in the page source
        web_res = requests.get(ROTANA_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # Regex to find the dynamic part (the token)
        # It looks for something like cinemamasr_net-TOKEN or cinema_net-TOKEN
        token_match = re.search(r'cinema_net-([a-zA-Z0-9]+)', web_res.text)
        
        if not token_match:
            # Fallback to another common pattern if the first fails
            token_match = re.search(r'cinemamasr_net-([a-zA-Z0-9]+)', web_res.text)

        if token_match:
            new_token = token_match.group(1)
            # Step 2: Construct the dynamic URL with the fresh token
            dynamic_url = f"https://rotana.hibridcdn.net/rotananet/cinema_net-{new_token}/rotana/cinema_720p/chunks.m3u8"
            
            # Step 3: Fetch the M3U8 content
            r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
            
            if r.status_code == 200:
                # Step 4: Fix paths for VLC
                base_url = dynamic_url.rsplit('/', 1)[0] + '/'
                fixed_content = r.text.replace('chunks', base_url + 'chunks')
                return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")

        raise HTTPException(status_code=500, detail="Could not find a fresh Token on Rotana page.")

    except Exception as e:
        return {"error": str(e)}
