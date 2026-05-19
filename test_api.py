import requests

url = "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112"
r = requests.get(url)
print("Status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    pairs = data.get("pairs", [])
    print(f"Pairs: {len(pairs)}")
    if pairs:
        print("First pair:", pairs[0].get("baseToken", {}).get("name"))
        print("Volume:", pairs[0].get("volume", {}).get("h24"))
else:
    print("Error:", r.text)
