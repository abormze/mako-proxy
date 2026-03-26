from fastapi import FastAPI, Response, HTTPException
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# Rotana Channels Database (Direct Links)
CHANNELS = {
    "cinema": "https://rotana.hibridcdn.net/rotananet/cinemamasr_net-7Y83PP5adWixDF93/playlist.m3u8",
    "aflam": "https://d35j504z0x2vu2.cloudfront.net/v1/master/0bc8e8376bd8417a1b6761138aa41c26c7309312/rotana-aflam-plus/master.m3u8",
    "khalijia": "https://rotana.hibridcdn.net/rotananet/khalejia_net-7Y83PP5adWixDF93/playlist.m3u8",
    "drama": "https://rotana.hibridcdn.net/rotananet/drama_net-7Y83PP5adWixDF93/playlist.m3u8",
    "kids": "https://rotana.hibridcdn.net/rotananet/kids_net-7Y83PP5adWixDF93/playlist.m3u8",
    "clip": "https://rotana.hibridcdn.net/rotananet/clip_net-7Y83PP5adWixDF93/playlist.m3u8"
}

# Essential headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def home():
    return {
        "status": "Rotana Engine Online",
        "proxy_status": "Disabled (Direct Mode)",
        "available_channels": list(CHANNELS.keys())
    }

@app.get("/rotana/{channel_name}.m3u8")
def get_rotana_channel(channel_name: str):
    if channel_name not in CHANNELS:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    target_url = CHANNELS[channel_name]
    
    try:
        # Fetching directly from Koyeb server without proxy
        r = requests.get(target_url, headers=HEADERS, timeout=15, verify=False)
        
        if r.status_code == 200:
            return Response(content=r.text, media_type="application/vnd.apple.mpegurl")
        else:
            raise HTTPException(
                status_code=r.status_code, 
                detail=f"Rotana denied direct access (Status: {r.status_code})"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Connection Error: {str(e)}")
