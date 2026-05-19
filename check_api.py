import requests
import json

url = "https://api.dexscreener.com/latest/dex/tokens/9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump"
resp = requests.get(url, timeout=10)
data = resp.json()

pairs = data.get("pairs", [])
if pairs:
    p = pairs[0]
    print("Available keys:", list(p.keys()))
    
    # Check for holder data
    for key in p.keys():
        val = p[key]
        if isinstance(val, (list, dict)) and len(str(val)) > 100:
            print(f"\n{key} (type: {type(val).__name__}):")
            print(str(val)[:500])
