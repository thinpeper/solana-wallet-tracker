import requests

# Test DexScreener API
print("Testing DexScreener API...")
r = requests.get("https://api.dexscreener.com/latest/dex/tokens/solana", timeout=15)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:500]}")
