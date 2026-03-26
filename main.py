from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3
import re

# Disable SSL warnings for the residential proxy connection
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ISRAELI RESIDENTIAL PROXY (Bezeq) ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# Source URLs
MAKO_WEB_URL = "https://www.mako.co.il/mako-vod-live/VOD-65d214a14a38241006.htm"
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

def get_dynamic_token_url():
    """
    Automated Token Scraper: 
    Accesses the Mako website to find the latest .m3u8 link containing the 'hdnea' token.
    """
    try:
        session = requests.Session()
        # Accessing the web page through the proxy to bypass Geo-blocking
        response = session.get(MAKO_WEB_URL, headers=HEADERS, proxies=PROXIES, timeout=15, verify=False)
        
        # Regex to find the .m3u8 URL with the 'hdnea' token in the page source
        # It looks for a pattern starting with https and containing 'index.m3u8?hdnea='
        match = re.search(r'https://[^\s"]+index\.m3u8\?hdnea=[^\s"]+', response.text)
        
        if match:
            # Clean the URL (remove escape backslashes if any)
            clean_url = match.group(0).replace('\\', '')
            print(f"[+] Successfully scraped new token URL: {clean_url[:50]}...")
            return clean_url
        
        return None
    except Exception as e:
        print(f"[-] Scraping Error: {str(e)}")
        return None

@app.get("/")
def health_check():
    return {"status": "Automated Mako Engine Online", "region": "Israel Proxy Active"}

@app.get("/mako/live.m3u8")
def get_stream():
    # Step 1: Automatically fetch a fresh Token URL
    dynamic_url = get_dynamic_token_url()
    
    # Fallback to a static URL if scraping fails (replace with your known working token if needed)
    if not dynamic_url:
        # Use your last known working link as a backup
        dynamic_url = "
