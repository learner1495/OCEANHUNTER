import requests

# URL from the video screenshot
url = "https://api.nobitex.ir/market/global-stats"

# payload={}  <-- Commented out in video
# headers = {} <-- Commented out in video

print(f"Connecting to {url} ...")

try:
    # EXACTLY line 8 from screenshot
    response = requests.request("POST", url)

    # EXACTLY line 10 from screenshot
    print(response.text)
    
except Exception as e:
    print(f"❌ Error: {e}")
