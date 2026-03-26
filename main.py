from fastapi import FastAPI, Response, HTTPException, Request
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

CHANNELS = {
    "cinema": "https://rotana.hibridcdn.net/rotananet/cinemamasr_net-7Y83PP5adWixDF93/playlist.m3u8",
    "aflam": "https://d35j504z0x2vu2.cloudfront.net/v1/master/0bc8e8376bd8417a1b6761138aa41c26c7309312/rotana-aflam-plus/master.m3u8",
    "drama": "https://rotana.hibridcdn.net/rotananet/drama_net-7Y83PP5adWixDF93/playlist.m3u8"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://rotana.net/",
    "Origin": "https://rotana.net"
}

@app.get("/")
def home():
    return {"status": "Koko Stream Relay Active"}

@app.get("/rotana/{channel_name}.m3u8")
def proxy_stream(channel_name: str):
    if channel_name not in CHANNELS:
        raise HTTPException(status_code=404)
    
    target_url = CHANNELS[channel_name]
    
    try:
        # Step 1: Fetch the M3U8 content
        r = requests.get(target_url, headers=HEADERS, proxies=PROXIES, timeout=10, verify=False)
        
        # Step 2: Fix the content to make all segments go through our server
        # This is the "Magic" part that fixes the black screen
        original_text = r.text
        base_url = target_url.rsplit('/', 1)[0] + '/'
        
        fixed_content = ""
        for line in original_text.splitlines():
            if line.endswith(".ts") or line.endswith(".m3u8"):
                if not line.startswith("http"):
                    line = base_url + line
                # Redirect segment request through our proxy endpoint
                fixed_content += f"/proxy_segment?url={line}\n"
            else:
                fixed_content += line + "\n"
        
        return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
    except Exception as e:
        return {"error": str(e)}

@app.get("/proxy_segment")
def proxy_segment(url: str):
    # This function fetches the actual video data and streams it to the user
    def stream_video():
        with requests.get(url, headers=HEADERS, proxies=PROXIES, stream=True, timeout=15, verify=False) as r:
            for chunk in r.iter_content(chunk_size=1024*1024):
                yield chunk

    return StreamingResponse(stream_video(), media_type="video/MP2T")
