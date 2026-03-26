from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ISRAELI PROXY (STABLE VERSION) ---
PROXIES = {
    "http": "http://45.150.108.239:39811",
    "https": "http://45.150.108.239:39811"
}

# The latest working URL with the Session Token from your capture
MAKO_TOKEN_URL = (
    "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/index.m3u8"
    "?b-in-range=0-1800&hdnea=st%3D1774497892%7Eexp%3D1774498792%7Eacl%3D%2F*%7E"
    "hmac%3Da592eee68f26e9bbd5d798d84cd4f648c9d23885d18ad2d7aecb0a6bbbd98fc0"
)

# Base path for quality profiles (Prevents 404 in VLC)
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/"
}

@app.get("/")
def home():
    return {"status": "Koko Manual Mode Online", "proxy": "45.150.108.239"}

@app.get("/mako/live.m3u8")
def get_stream():
    try:
        # Request the playlist directly through the proxy
        r = requests.get(MAKO_TOKEN_URL, headers=HEADERS, proxies=PROXIES, timeout=20, verify=False)
        
        if r.status_code == 200:
            # Fix internal profile links for VLC
            fixed_content = r.text.replace('profile', BASE_PATH + 'profile
