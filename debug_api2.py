import requests

# Test DexScreener search API
print("Testing DexScreener search API...")
r = requests.get("https://api.dexscreener.com/latest/dex/search?q=solana", timeout=15)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:500]}")

# Test with a specific token
print("\nTesting with specific token...")
r2 = requests.get("https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112", timeout=15)
print(f"Status: {r2.status_code}")
print(f"Body: {r2.text[:500]}")
