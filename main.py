from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3

# Disable SSL warnings for using residential proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- ISRAELI RESIDENTIAL PROXY CONFIGURATION ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# The latest working URL with the Session Token you captured
MAKO_TOKEN_URL = (
    "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/index.m3u8"
    "?b-in-range=0-1800&hdnea=st%3D1774497892%7Eexp%3D1774498792%7Eacl%3D%2F*%7E"
    "hmac%3Da592eee68f26e9bbd5d798d84cd4f648c9d23885d18ad2d7aecb0a6bbbd98fc0"
)

# Base path for quality profiles to prevent 404 errors
BASE_PATH = "https://mako-streaming.akamaized.net/stream/hls/live/2033791/k12makowad/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.mako.co.il/",
    "Origin": "https://www.mako.co.il"
}

@app.get("/")
def home():
    return {
        "status": "Koko Resident Engine Online",
        "proxy_mode": "Active",
        "region": "Israel"
    }

@app.get("/mako/live.m3u8")
def get_stream():
    try:
        # Requesting through proxy to bypass Koyeb's IP block
        response = requests.get(
            MAKO_TOKEN_URL, 
            headers=HEADERS, 
            proxies=PROXIES, 
            timeout=20, 
            verify=False
        )
        
        if response.status_code == 200:
            # Fixing
