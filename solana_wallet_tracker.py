import requests
import json
import time
import sys

def fetch_with_retry(url, params=None, headers=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
    return None

def get_trending_tokens():
    """Get trending Solana tokens from DexScreener using known token addresses"""
    # Query multiple known tokens to get their pairs
    tokens = [
        "So11111111111111111111111111111111111111112",  # Wrapped SOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",  # JUP
        "7vfCXTUXx5WJV5JALh7Ha7vQE5y5JAHSGtqcR3dJW8Mq",  # BONK
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK (another)
        "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",  # WIF
        "6p6xgHyF7AeE6TZkSmFsko444wqoP15icng6G7ScfnB1",  # ORCA
        "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",  # RAY
        "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",  # mSOL
    ]
    
    all_pairs = []
    seen_addresses = set()
    
    for token in tokens:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token}"
        data = fetch_with_retry(url)
        if data and data.get("pairs"):
            for pair in data["pairs"]:
                addr = pair.get("baseToken", {}).get("address", "")
                if addr and addr not in seen_addresses:
                    seen_addresses.add(addr)
                    all_pairs.append(pair)
    
    # Filter out Wrapped SOL and stablecoins
    meme_coins = [p for p in all_pairs 
                  if "wrapped" not in p.get("baseToken", {}).get("name", "").lower()
                  and "solana" not in p.get("baseToken", {}).get("name", "").lower()
                  and float(p.get("priceUsd", 0) or 0) > 0.001
                  and float(p.get("volume", {}).get("h24", 0) or 0) > 1000]
    
    meme_coins.sort(key=lambda x: x.get("volume", {}).get("h24", 0) or 0, reverse=True)
    return meme_coins[:20]

def get_top_traders(token_address):
    """Get top traders from Birdeye API"""
    url = "https://api.birdeye.so/v1/defi/token_top_traders"
    headers = {"X-Token": "demo"}
    params = {"address": token_address}
    data = fetch_with_retry(url, params=params, headers=headers)
    if data and data.get("data", {}).get("items"):
        return data["data"]["items"]
    return []

def analyze_insiders(traders, token_address):
    """Filter for insider wallets (small entries, huge PNL)"""
    insiders = []
    for trader in traders:
        pnl = trader.get("pnl", 0) or 0
        entry_size = trader.get("entry_size", 0) or 0
        if pnl > 1000 and entry_size < 10000:
            insiders.append({
                "address": trader.get("address", ""),
                "pnl": pnl,
                "entry_size": entry_size,
                "total_trades": trader.get("total_trades", 0) or 0
            })
    return sorted(insiders, key=lambda x: x["pnl"], reverse=True)

def print_results():
    print("=" * 100)
    print("SOLANA INSIDER WALLET TRACKER - DexScreener Trending Meme Coins (24h)")
    print("=" * 100)

    trending = get_trending_tokens()

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
    print("INSIDER WALLET ANALYSIS (Top Traders with Small Entries, Huge PNL)")
    print(f"{'='*100}\n")

    for pair in trending[:5]:
        base = pair.get("baseToken", {})
        token_address = base.get("address", "")
        token_name = base.get("name", "Unknown")

        print(f"Token: {token_name}")
        print(f"Address: {token_address}")
        print()

        traders = get_top_traders(token_address)
        insiders = analyze_insiders(traders, token_address)

        if insiders:
            print(f"{'Address':<44} {'PNL':<15} {'Entry Size':<15} {'Trades':<10}")
            print("-" * 85)
            for insider in insiders:
                print(f"{insider['address']:<44} ${insider['pnl']:>12,.2f}  ${insider['entry_size']:>12,.2f}  {insider['total_trades']:>10}")
        else:
            print("No significant insider wallets found.\n")

        print()

if __name__ == "__main__":
    print_results()
