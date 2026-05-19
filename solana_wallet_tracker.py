import requests
import json
import time
import sys

def fetch_with_retry(url, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2)
    return None

def get_trending_meme_coins():
    """Get trending meme coins from DexScreener"""
    tokens = [
        "So11111111111111111111111111111111111111112",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    ]
    all_pairs = []
    for token in tokens:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token}"
        data = fetch_with_retry(url)
        if data:
            pairs = data.get("pairs", [])
            all_pairs.extend(pairs)
    
    meme_coins = [p for p in all_pairs if "wrapped" not in p.get("baseToken", {}).get("name", "").lower()]
    meme_coins.sort(key=lambda x: x.get("volume", {}).get("h24", 0) or 0, reverse=True)
    return meme_coins

def get_token_holders(token_address):
    """Get top holders from DexScreener search"""
    url = "https://api.dexscreener.com/token-approval-book/latest/dex/tokens"
    params = {"tokens": [token_address]}
    data = fetch_with_retry(url, params=params)
    if data:
        return data.get("pairs", [])
    return []

def analyze_insiders(pair):
    """Analyze top holders for insider behavior"""
    top_holders = pair.get("topHolders", [])
    insiders = []
    
    supply = pair.get("supply", 1) or 1
    price_usd = pair.get("priceUsd", 0) or 0
    
    for holder in top_holders[:20]:
        address = holder.get("address", "")
        balance = holder.get("balance", 0) or 0
        pct = (balance / supply * 100) if supply else 0
        value = balance * price_usd if price_usd else 0
        
        if pct > 5:
            insiders.append({
                "address": address,
                "balance": balance,
                "value_usd": value,
                "percentage": pct
            })
    
    return sorted(insiders, key=lambda x: x["percentage"], reverse=True)

def print_results():
    print("=" * 100)
    print("SOLANA INSIDER WALLET TRACKER - DexScreener Trending Meme Coins (24h)")
    print("=" * 100)
    
    trending = get_trending_meme_coins()
    
    if not trending:
        print("No trending meme coins found. Check your internet connection.")
        return
    
    print(f"\n{'#':<3} {'Token':<25} {'Address':<44} {'Vol 24h':<15} {'MC':<15}")
    print("-" * 100)
    
    for i, pair in enumerate(trending[:15], 1):
        base = pair.get("baseToken", {})
        name = base.get("name", "Unknown")
        address = base.get("address", "")
        vol = pair.get("volume", {}).get("h24", 0) or 0
        mc = pair.get("marketCap", 0) or pair.get("fdv", 0) or 0
        print(f"{i:<3} {name:<25} {address:<44} ${vol:>12,.2f}  ${mc:>12,.2f}")
    
    print(f"\n{'='*100}")
    print("INSIDER WALLET ANALYSIS (Top Holders >5% Supply)")
    print(f"{'='*100}\n")
    
    for pair in trending[:5]:
        base = pair.get("baseToken", {})
        token_address = base.get("address", "")
        token_name = base.get("name", "Unknown")
        
        holders = get_token_holders(token_address)
        if holders:
            details = holders[0]
        else:
            details = pair
        
        print(f"Token: {token_name}")
        print(f"Address: {token_address}")
        print()
        
        insiders = analyze_insiders(details)
        
        if insiders:
            print(f"{'Address':<44} {'Balance':<15} {'Value USD':<15} {'% Supply':<10}")
            print("-" * 85)
            for insider in insiders:
                print(f"{insider['address']:<44} {insider['balance']:>15,.0f}  ${insider['value_usd']:>12,.2f}  {insider['percentage']:>7.2f}%")
        else:
            print("No significant insider wallets found.\n")
        
        print()

if __name__ == "__main__":
    print_results()
