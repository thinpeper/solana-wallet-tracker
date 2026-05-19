import requests
import json
from datetime import datetime

def get_trending_tokens():
    """Get trending tokens from DexScreener"""
    url = "https://api.dexscreener.com/latest/dex/tokens"
    tokens = [
        "So11111111111111111111111111111111111111112",  # SOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    ]
    params = {"tokens": tokens}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data.get("pairs", [])
    except:
        return []

def get_top_traders(token_address):
    """Get top traders for a specific token"""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return []
        # Get the pair with highest volume
        pairs.sort(key=lambda x: x.get("volume", {}).get("h24", 0), reverse=True)
        return pairs[0].get("topPools", [])
    except:
        return []

def analyze_insider_wallets(token_address):
    """Analyze wallets for insider behavior"""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return []
        pairs.sort(key=lambda x: x.get("volume", {}).get("h24", 0), reverse=True)
        pair = pairs[0]
        
        # Get top holders/traders
        top_holders = pair.get("topHolders", [])
        insiders = []
        
        for holder in top_holders:
            address = holder.get("address", "")
            balance = holder.get("balance", 0)
            price = pair.get("priceUsd", 0)
            value = balance * price if price else 0
            
            # Check for insider behavior
            # High balance relative to supply = potential insider
            supply = pair.get("supply", 1)
            holder_percentage = (balance / supply * 100) if supply else 0
            
            if holder_percentage > 5:  # Hold more than 5% of supply
                insiders.append({
                    "address": address,
                    "balance": balance,
                    "value_usd": value,
                    "percentage": holder_percentage
                })
        
        return insiders
    except:
        return []

def print_results():
    """Print trending tokens and insider analysis"""
    print("=" * 80)
    print("SOLANA INSIDER WALLET TRACKER")
    print("=" * 80)
    
    # Get trending tokens
    trending = get_trending_tokens()
    
    print(f"\n🔥 TRENDING TOKENS (24h)\n")
    print(f"{'Token':<30} {'Address':<44} {'Volume 24h':<15} {'MC':<15}")
    print("-" * 100)
    
    for i, pair in enumerate(trending[:15], 1):
        base_token = pair.get("baseToken", {})
        quote_token = pair.get("quoteToken", {})
        name = base_token.get("name", "Unknown")
        address = base_token.get("address", "")
        volume = pair.get("volume", {}).get("h24", 0)
        mc = pair.get("fdv", 0) or pair.get("marketCap", 0)
        
        print(f"{name:<30} {address:<44} ${volume:>12,.2f}  ${mc:>12,.2f}")
    
    # Analyze insiders for top tokens
    print(f"\n\n🎯 INSIDER WALLET ANALYSIS\n")
    
    for pair in trending[:5]:  # Analyze top 5 trending tokens
        base_token = pair.get("baseToken", {})
        token_address = base_token.get("address", "")
        token_name = base_token.get("name", "Unknown")
        
        print(f"\n{'='*80}")
        print(f"📊 Token: {token_name}")
        print(f"🔗 Address: {token_address}")
        print(f"{'='*80}")
        
        insiders = analyze_insider_wallets(token_address)
        
        if insiders:
            print(f"\n{'Address':<44} {'Balance':<15} {'Value (USD)':<15} {'% Supply':<10}")
            print("-" * 85)
            for insider in insiders:
                print(f"{insider['address']:<44} {insider['balance']:>15,.0f}  ${insider['value_usd']:>12,.2f}  {insider['percentage']:>7.2f}%")
        else:
            print("\nNo significant insider wallets found.")
        
        print()

if __name__ == "__main__":
    print_results()
