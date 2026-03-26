from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3
import re

# Disable SSL warnings for proxy handling
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- NEW ISRAELI PROXY UPDATED ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# Target Source URLs
MAKO_WEB_URL = "https://www.mako.co.il/mako-vod-live/VOD-65d214a14a38241006.htm"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il"
}

def get_dynamic_token_url():
    """
    Scrapes the fresh .m3u8 link with the session token 
    using the new updated proxy.
    """
    try:
        session = requests.Session()
        # Requesting through the NEW proxy: 45.150.108.239
        response = session.get(MAKO_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # Regex search for the index.m3u8 URL containing 'hdnea'
        match = re.search(r'https://[^\s"]+index\.m3u8\?hdnea=[^\s"]+', response.text)
        
        if match:
            clean_url = match.group(0).replace('\\', '')
            return clean_url
        return None
    except Exception as e:
        print(f"Scraping Error: {str(e)}")
        return None

@app.get("/")
def home():
    return {
        "status": "Koko Engine Online",
        "current_proxy": "45.150.108.239",
        "region": "Israel"
    }

@app.get("/mako/live.m3u8")
def get_stream():
    # 1. Fetch fresh tokenized URL
    dynamic_url = get_dynamic_token_url()
    
    if not dynamic_url:
        raise HTTPException(status_code=500, detail="Could not retrieve a fresh Israel Token")

    try:
        # 2. Pull the playlist content via the NEW proxy
        r = requests.get(dynamic_url, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        if r.status_code == 200:
            #
