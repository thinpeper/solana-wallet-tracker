import requests

# Try the search API
url = "https://api.dexscreener.com/latest/dex/search"
params = {"q": "Fartcoin"}
resp = requests.get(url, params=params, timeout=10)
data = resp.json()

print("Search API Response:")
pairs = data.get("pairs", [])
if pairs:
    for pair in pairs[:3]:
        print(f"\nToken: {pair.get('baseToken', {}).get('name', 'Unknown')}")
        print(f"Address: {pair.get('baseToken', {}).get('address', 'Unknown')}")
        print(f"Keys: {list(pair.keys())}")
        
        # Check for holder data
        for key in pair.keys():
            if "holder" in key.lower() or "top" in key.lower():
                print(f"\n{key}:")
                print(pair[key])
