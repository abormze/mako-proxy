from fastapi import FastAPI, Response, HTTPException, Request
import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- PROXY FOR FETCHING M3U8 ONLY ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# Rotana Configuration
ROTANA_WEB_PAGE = "https://rotana.net/en/live/channels#/live/rotana-cinema"
ROTANA_BASE = "https://rotana.hibridcdn.net/rotananet/"

# Professional Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def status():
    return {"status": "Koko Ultra-Fast Active", "mode": "Direct-Redirect"}

@app.get("/rotana/cinema.m3u8")
def get_cinema_fast():
    token = "7Y83PP5adWixDF93" # Default Fallback
    
    # --- 1. SMART HTML SCRAPER (TO GET FRESH TOKEN) ---
    try:
        # We fetch the page to keep the token alive
        res = requests.get(ROTANA_WEB_PAGE, headers=HEADERS, proxies=PROXIES, timeout=8)
        match = re.search(r'cinema_net-([a-zA-Z0-9]+)', res.text)
        if match:
            token = match.group(1)
    except:
        pass

    # --- 2. FETCH M3U8 & REWRITE ---
    target_url = f"{ROTANA_BASE}cinema_net-{token}/rotana/cinema_720p/chunks.m3u8"
    
    try:
        # Use proxy to get the playlist
        r = requests.get(target_url, headers=HEADERS, proxies=PROXIES, timeout=10, verify=False)
        
        if r.status_code == 200:
            base_path = target_url.rsplit('/', 1)[0] + '/'
            lines = r.text.splitlines()
            fixed_lines = []
            
            for line in lines:
                # If it's a video segment, provide the FULL DIRECT URL
                if line.endswith(".ts") and not line.startswith("http"):
                    # This allows VLC to pull directly from Rotana's CDN if possible
                    # or at least gives it the clean absolute path
                    fixed_lines.append(base_path + line)
                else:
                    fixed_lines.append(line)
            
            # Use a longer Cache-Control to prevent constant refreshing
            return Response(
                content="\n".join(fixed_lines), 
                media_type="application/vnd.apple.mpegurl",
                headers={"Cache
