from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# --- YOUR STABLE HOME PROXY ---
PROXIES = {
    "http": "http://82.81.95.155:39811",
    "https": "http://82.81.95.155:39811"
}

# The Direct 720p Chunk URL you provided
ROTANA_720P_URL = "https://rotana.hibridcdn.net/rotananet/cinema_net-7Y83PP5adWixDF93/rotana/cinema_720p/chunks.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def home():
    return {"status": "Koko Cinema Relay Active", "mode": "Full-Proxy-720p"}

@app.get("/rotana/cinema.m3u8")
def proxy_m3u8():
    try:
        # Step 1: Fetch the chunks.m3u8 via Proxy
        r = requests.get(ROTANA_720P_URL, headers=HEADERS, proxies=PROXIES, timeout=12, verify=False)
        lines = r.text.splitlines()
        
        # Step 2: Re-write the file to force every .ts segment through our server
        base_url = ROTANA_720P_URL.rsplit('/', 1)[0] + '/'
        new_m3u8 = []
        
        for line in lines:
            if line.endswith(".ts"):
                full_ts_url = base_url + line if not line.startswith("http") else line
                # Redirect segment to our internal proxy endpoint
                new_m3u8.append(f"/ts_relay?url={full_ts_url}")
            else:
                new_m3u8.append(line)
        
        return Response(content="\n".join(new_m3u8), media_type="application/vnd.apple.mpegurl")
    except Exception as e:
        return {"error": str(e)}

@app.get("/ts_relay")
def ts_relay(url: str):
    # Step 3: Fetch the actual video segment via Proxy and stream it back
    def stream_data():
        with requests.get(url, headers=HEADERS, proxies=PROXIES, stream=True, timeout=15, verify=False) as r:
            for chunk in r.iter_content(chunk_size=1024*512):
                yield chunk

    return StreamingResponse(stream_data(), media_type="video/MP2T")
