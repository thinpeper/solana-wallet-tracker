#!/usr/bin/env python3
"""
Solana Wallet Tracker - Tracks most profitable Phantom wallets
Monitors pump.fun token launches and ranks wallets by buy activity.
Uses DexScreener API for real-time data.
"""

import requests
import json
from datetime import datetime
from collections import defaultdict

class SolanaWalletTracker:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    def get_top_tokens(self, limit=20):
        """Get top Solana tokens by 24h volume via search"""
        try:
            r = requests.get("https://api.dexscreener.com/latest/dex/search",
                           params={"q": "solana", "limit": limit},
                           headers=self.headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                pairs = data.get("pairs", [])
                # Filter for Solana chains and sort by volume
                sol_pairs = [p for p in pairs if p.get("chainId") == "solana"]
                return sorted(sol_pairs, 
                            key=lambda x: x.get("volume", {}).get("h24", 0), 
                            reverse=True)[:limit]
        except Exception as e:
            print(f"Error getting top tokens: {e}")
        return []
    
    def get_pumpfun_tokens(self, limit=30):
        """Get pump.fun tokens"""
        try:
            r = requests.get("https://api.dexscreener.com/latest/dex/search",
                           params={"q": "pump", "limit": limit},
                           headers=self.headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                pairs = data.get("pairs", [])
                return [p for p in pairs if p.get("chainId") == "solana"]
        except Exception as e:
            print(f"Error getting pump.fun: {e}")
        return []
    
    def get_top_pumpers(self, limit=10):
        """Get top pump.fun creators by aggregating across tokens"""
        try:
            r = requests.get("https://api.dexscreener.com/latest/dex/search",
                           params={"q": "pump", "limit": 100},
                           headers=self.headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                pairs = data.get("pairs", [])
                # Group by creator wallet
                wallet_activity = defaultdict(lambda: {
                    "tokens": 0,
                    "volume": 0,
                    "tokens_list": []
                })
                for pair in pairs:
                    creator = pair.get("creator", "")
                    if creator and pair.get("chainId") == "solana":
                        wallet_activity[creator]["tokens"] += 1
                        wallet_activity[creator]["volume"] += pair.get("volume", {}).get("h24", 0)
                        wallet_activity[creator]["tokens_list"].append(pair.get("baseMint", ""))
                sorted_wallets = sorted(wallet_activity.items(),
                                      key=lambda x: x[1]["volume"],
                                      reverse=True)
                return sorted_wallets[:limit]
        except Exception as e:
            print(f"Error getting top pumpers: {e}")
        return []
    
    def get_new_pairs(self, limit=20):
        """Get newest Solana pairs"""
        try:
            r = requests.get("https://api.dexscreener.com/latest/dex/search",
                           params={"q": "new", "limit": limit},
                           headers=self.headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                pairs = data.get("pairs", [])
                sol_pairs = [p for p in pairs if p.get("chainId") == "solana"]
                return sorted(sol_pairs,
                            key=lambda x: x.get("pairCreatedAt", 0),
                            reverse=True)[:limit]
        except Exception as e:
            print(f"Error getting new pairs: {e}")
        return []
    
    def format_report(self):
        """Format a comprehensive report"""
        report = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report.append("=" * 70)
        report.append("  SOLANA WALLET TRACKER - TRENDING & PUMP.FUN")
        report.append(f"  Generated: {now}")
        report.append("=" * 70)
        
        # Top tokens by volume
        top_tokens = self.get_top_tokens(15)
        if top_tokens:
            report.append("\n[1] TOP 15 SOLANA TOKENS BY 24H VOLUME")
            report.append("-" * 55)
            for i, pair in enumerate(top_tokens[:15], 1):
                symbol = pair.get("baseToken", {}).get("symbol", "???")
                address = pair.get("baseToken", {}).get("address", "")[:10] + "..."
                vol = float(pair.get("volume", {}).get("h24", 0))
                price = float(pair.get("priceUsd", 0))
                mc = float(pair.get("fdv", 0))
                txns = pair.get("txns", {}).get("h24", {}).get("buys", 0) + pair.get("txns", {}).get("h24", {}).get("sells", 0)
                change = float(pair.get("priceChange", {}).get("h24", 0))
                change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
                buys = pair.get("txns", {}).get("h24", {}).get("buys", 0)
                sells = pair.get("txns", {}).get("h24", {}).get("sells", 0)
                report.append(f"  {i:>2}. {symbol:<15} ({address})")
                report.append(f"     Vol: ${vol:>12,.2f}  Price: ${price:>12.8f}  MC: ${mc:>12,.0f}")
                report.append(f"     24h TXNs: {txns:>6,}  Buys: {buys:>6,}  Sells: {sells:>6,}  Chg: {change_str:>7}")
                report.append("")
        
        # Pump.fun tokens
        pump_tokens = self.get_pumpfun_tokens(30)
        if pump_tokens:
            pump_pairs = sorted(pump_tokens,
                              key=lambda x: x.get("volume", {}).get("h24", 0),
                              reverse=True)[:20]
            report.append("\n[2] TOP PUMP.FUN TOKENS BY VOLUME")
            report.append("-" * 55)
            for i, pair in enumerate(pump_pairs[:20], 1):
                symbol = pair.get("baseToken", {}).get("symbol", "???")
                address = pair.get("baseToken", {}).get("address", "")[:10] + "..."
                vol = float(pair.get("volume", {}).get("h24", 0))
                price = float(pair.get("priceUsd", 0))
                mc = float(pair.get("fdv", 0))
                txns = pair.get("txns", {}).get("h24", {}).get("buys", 0) + pair.get("txns", {}).get("h24", {}).get("sells", 0)
                change = float(pair.get("priceChange", {}).get("h24", 0))
                change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
                buys = pair.get("txns", {}).get("h24", {}).get("buys", 0)
                sells = pair.get("txns", {}).get("h24", {}).get("sells", 0)
                report.append(f"  {i:>2}. {symbol:<15} ({address})")
                report.append(f"     Vol: ${vol:>12,.2f}  Price: ${price:>12.8f}  MC: ${mc:>12,.0f}")
                report.append(f"     24h TXNs: {txns:>6,}  Buys: {buys:>6,}  Sells: {sells:>6,}  Chg: {change_str:>7}")
                report.append("")
        
        # Top pumpers (creators)
        top_pumpers = self.get_top_pumpers()
        if top_pumpers:
            report.append("\n[3] TOP PUMP.FUN CREATORS (by volume)")
            report.append("-" * 55)
            for i, (wallet, activity) in enumerate(top_pumpers[:10], 1):
                report.append(f"  {i:>2}. {wallet}")
                report.append(f"     Tokens: {activity['tokens']}  Volume: ${activity['volume']:>12,.2f}")
                tokens_preview = ", ".join([t[:8] + "..." for t in activity["tokens_list"][:5]])
                report.append(f"     Tokens: {tokens_preview}")
                report.append("")
        
        # New pairs
        new_pairs = self.get_new_pairs(15)
        if new_pairs:
            report.append("\n[4] TRENDING NEW PAIRS")
            report.append("-" * 55)
            for i, pair in enumerate(new_pairs[:15], 1):
                symbol = pair.get("baseToken", {}).get("symbol", "???")
                address = pair.get("baseToken", {}).get("address", "")[:10] + "..."
                vol = float(pair.get("volume", {}).get("h24", 0))
                price = float(pair.get("priceUsd", 0))
                mc = float(pair.get("fdv", 0))
                txns = pair.get("txns", {}).get("h24", {}).get("buys", 0) + pair.get("txns", {}).get("h24", {}).get("sells", 0)
                change = float(pair.get("priceChange", {}).get("h24", 0))
                change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
                buys = pair.get("txns", {}).get("h24", {}).get("buys", 0)
                sells = pair.get("txns", {}).get("h24", {}).get("sells", 0)
                report.append(f"  {i:>2}. {symbol:<15} ({address})")
                report.append(f"     Vol: ${vol:>12,.2f}  Price: ${price:>12.8f}  MC: ${mc:>12,.0f}")
                report.append(f"     24h TXNs: {txns:>6,}  Buys: {buys:>6,}  Sells: {sells:>6,}  Chg: {change_str:>7}")
                report.append("")
        
        report.append("=" * 70)
        return "\n".join(report)
    
    def run(self):
        """Run tracker and print report"""
        report = self.format_report()
        print(report)
        return report


if __name__ == "__main__":
    tracker = SolanaWalletTracker()
    tracker.run()
