#!/usr/bin/env python3
"""Solana Wallet Tracker - Track top profitable Solana wallets and tokens."""

import requests
import json
from datetime import datetime
from collections import defaultdict

# DexScreener API endpoints
DEXSCREENER_TOKENS = "https://api.dexscreener.com/latest/dex/tokens/solana"
DEXSCREENER_TOKEN = "https://api.dexscreener.com/latest/dex/tokens/"
DEXSCREENER_PUMPFUN = "https://api.dexscreener.com/latest/dex/tokens?pairsOnly=true&limit=50"

# Solscan API for wallet details
SOLSCAN_API = "https://api.solscan.io"
SOLSCAN_HEADERS = {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzaG9ydFRva2VuIjoiODQyN2I0YjAtMjI3ZS00NjRlLWFjNWItNjdlNDQyMjEwZjQ1IiwidXNlciI6eyJpZCI6IjBiOTI0Y2VmLTViMGY0M2E3YTQ0YjFjMjE4YmU0ZjM4YiIsInVzZXJuYW1lIjoiaGVybWVzLWFpLWFjY291bnQiLCJlbWFpbCI6IiIsImF2YXRhciI6IiIsImNyZWF0ZWRBdCI6IjIwMjYtMDUtMTlUMDA6NDI6MzMuNTUyWiJ9LCJwZXJtaXNzaW9ucyI6WyJiYXNpYyIsImFkdmFuY2VkIiwiZGF0YV9leHBvcnQiXSwiZXhwIjoxNzgwMTM2ODIzfQ.9G8k7Y5Jz8K3L4M6N8O0P2Q4R6S8T0U2V4W6X8Y0Z2A",
}


class SolanaWalletTracker:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def get_top_tokens(self, limit=20):
        """Get top Solana tokens by 24h volume."""
        try:
            response = requests.get(
                "https://api.dexscreener.com/latest/dex/search?q=solana",
                headers=self.headers, timeout=15
            )
            data = response.json()
            pairs = data.get("pairs", [])
            # Filter for Solana pairs
            solana_pairs = [p for p in pairs if p.get("chainId") == "solana"]
            solana_pairs.sort(key=lambda x: x.get("volume", {}).get("h24", 0) or 0, reverse=True)
            return solana_pairs[:limit]
        except Exception as e:
            print(f"Error fetching top tokens: {e}")
            return []

    def get_pumpfun_tokens(self, limit=20):
        """Get top pump.fun tokens by volume."""
        try:
            response = requests.get(
                "https://api.dexscreener.com/latest/dex/search?q=pump",
                headers=self.headers, timeout=15
            )
            data = response.json()
            pairs = data.get("pairs", [])
            pumpfun_pairs = [p for p in pairs if "pump" in p.get("dexId", "").lower()]
            pumpfun_pairs.sort(key=lambda x: x.get("volume", {}).get("h24", 0) or 0, reverse=True)
            return pumpfun_pairs[:limit]
        except Exception as e:
            print(f"Error fetching pump.fun tokens: {e}")
            return []

    def get_token_pairs(self, token_address):
        """Get all pairs for a specific token."""
        try:
            response = requests.get(DEXSCREENER_TOKEN + token_address, headers=self.headers, timeout=15)
            data = response.json()
            return data.get("pairs", [])
        except Exception as e:
            print(f"Error fetching token pairs: {e}")
            return []

    def get_wallet_info(self, wallet_address):
        """Get wallet information from Solscan API."""
        try:
            response = requests.get(
                f"{SOLSCAN_API}/v1/account/overview/{wallet_address}",
                headers=SOLSCAN_HEADERS,
                timeout=15
            )
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error fetching wallet info: {e}")
            return None

    def get_top_pumpfun_creators(self, limit=20):
        """Get top pump.fun creators aggregated by volume."""
        try:
            tokens = self.get_pumpfun_tokens(limit=100)
            wallet_stats = defaultdict(lambda: {
                "total_volume": 0,
                "token_count": 0,
                "tokens": [],
                "total_mcap": 0,
                "total_liquidity": 0,
            })

            for pair in tokens:
                base_mint = pair.get("baseMint", "")
                creators = pair.get("info", {}).get("creator", "")
                if not creators:
                    continue

                volume = pair.get("volume", {}).get("h24", 0) or 0
                mcap = pair.get("mcap", 0) or 0
                liquidity = pair.get("liquidity", {}).get("usd", 0) or 0

                wallet_stats[creators]["total_volume"] += volume
                wallet_stats[creators]["token_count"] += 1
                wallet_stats[creators]["tokens"].append({
                    "name": pair.get("baseToken", {}).get("name", ""),
                    "address": base_mint,
                    "mcap": mcap,
                    "volume": volume,
                })
                wallet_stats[creators]["total_mcap"] += mcap
                wallet_stats[creators]["total_liquidity"] += liquidity

            creators = sorted(wallet_stats.items(), key=lambda x: x[1]["total_volume"], reverse=True)
            return creators[:limit]
        except Exception as e:
            print(f"Error fetching top creators: {e}")
            return []

    def get_top_wallets_by_buy_activity(self, limit=20):
        """Get top wallets by buy activity across pump.fun tokens."""
        try:
            tokens = self.get_pumpfun_tokens(limit=100)
            wallet_activity = defaultdict(lambda: {
                "total_buys": 0,
                "total_volume": 0,
                "tokens_traded": [],
                "last_activity": "",
            })

            for pair in tokens:
                base_mint = pair.get("baseMint", "")
                quotes = pair.get("quotes", [])

                for quote in quotes[:5]:  # Top 5 wallets per token
                    wallet = quote.get("wallet", "")
                    if not wallet:
                        continue

                    activity = quote.get("activity", {})
                    buys = activity.get("buys", 0) or 0
                    volume = activity.get("volume", 0) or 0

                    wallet_activity[wallet]["total_buys"] += buys
                    wallet_activity[wallet]["total_volume"] += volume
                    wallet_activity[wallet]["tokens_traded"].append({
                        "name": pair.get("baseToken", {}).get("name", ""),
                        "address": base_mint,
                        "buys": buys,
                        "volume": volume,
                    })

            wallets = sorted(wallet_activity.items(), key=lambda x: x[1]["total_buys"], reverse=True)
            return wallets[:limit]
        except Exception as e:
            print(f"Error fetching top wallets: {e}")
            return []

    def get_trending_new_pairs(self, limit=15):
        """Get trending new pairs sorted by creation time."""
        try:
            tokens = self.get_pumpfun_tokens(limit=100)
            pairs = []
            for pair in tokens:
                created = pair.get("pairCreatedAt", 0) or 0
                if created > 0:
                    pairs.append(pair)

            pairs.sort(key=lambda x: x.get("pairCreatedAt", 0) or 0, reverse=True)
            return pairs[:limit]
        except Exception as e:
            print(f"Error fetching trending pairs: {e}")
            return []

    def copy_wallet_address(self, wallet_address):
        """Copy wallet address to clipboard (works on Windows)."""
        try:
            import subprocess
            subprocess.run(["clip", "-input", wallet_address], shell=True, check=True)
            return True
        except Exception:
            return False

    def format_wallet_address(self, address):
        """Format wallet address for easy copying with copy button."""
        if not address or len(address) < 32:
            return address
        return f"[COPY] {address[:4]}...{address[-4:]}"

    def print_top_tokens(self):
        """Print top Solana tokens by 24h volume."""
        print("\n" + "=" * 80)
        print("🔥 TOP 15 SOLANA TOKENS BY 24H VOLUME")
        print("=" * 80)
        tokens = self.get_top_tokens(limit=15)

        for i, pair in enumerate(tokens, 1):
            base = pair.get("baseToken", {})
            quote = pair.get("quoteToken", {})
            price = pair.get("price", {}).get("usd", "0")
            change_24h = pair.get("priceChange", {}).get("h24", 0) or 0
            volume = pair.get("volume", {}).get("h24", 0) or 0
            mcap = pair.get("mcap", 0) or 0
            liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
            buys = pair.get("priceProgress", {}).get("24h", {}).get("buys", 0) or 0
            sells = pair.get("priceProgress", {}).get("24h", {}).get("sells", 0) or 0

            print(f"\n{i}. {base.get('name', 'N/A')} ({base.get('symbol', 'N/A')})")
            print(f"   Address: {self.format_wallet_address(pair.get('baseMint', ''))}")
            print(f"   Price: ${price} | 24h Change: {change_24h:+.2f}%")
            print(f"   Vol: ${volume:,.0f} | MC: ${mcap:,.0f} | Liq: ${liquidity:,.0f}")
            print(f"   Buys/Sells: {buys}/{sells}")

    def print_top_creators(self):
        """Print top pump.fun creators by volume."""
        print("\n" + "=" * 80)
        print("👑 TOP 15 PUMP.FUN CREATORS BY VOLUME")
        print("=" * 80)
        creators = self.get_top_pumpfun_creators(limit=15)

        for i, (wallet, stats) in enumerate(creators, 1):
            print(f"\n{i}. {self.format_wallet_address(wallet)}")
            print(f"   Tokens: {stats['token_count']} | Total Vol: ${stats['total_volume']:,.0f}")
            print(f"   Total MC: ${stats['total_mcap']:,.0f} | Total Liq: ${stats['total_liquidity']:,.0f}")
            print(f"   Top Tokens:")
            for token in stats["tokens"][:3]:
                print(f"     - {token['name']} ({token['address'][:8]}...{token['address'][-6:]}) - MC: ${token['mcap']:,.0f}")

    def print_top_wallets(self):
        """Print top wallets by buy activity."""
        print("\n" + "=" * 80)
        print("🎯 TOP 20 WALLETS BY BUY ACTIVITY")
        print("=" * 80)
        wallets = self.get_top_wallets_by_buy_activity(limit=20)

        for i, (wallet, stats) in enumerate(wallets, 1):
            print(f"\n{i}. {self.format_wallet_address(wallet)}")
            print(f"   Total Buys: {stats['total_buys']} | Total Volume: ${stats['total_volume']:,.0f}")
            print(f"   Tokens Traded:")
            for token in stats["tokens_traded"][:3]:
                print(f"     - {token['name']} ({token['address'][:8]}...{token['address'][-6:]}) - Buys: {token['buys']}")

    def print_trending_pairs(self):
        """Print trending new pairs."""
        print("\n" + "=" * 80)
        print("🚀 TRENDING NEW PAIRS (BY CREATION TIME)")
        print("=" * 80)
        pairs = self.get_trending_new_pairs(limit=15)

        for i, pair in enumerate(pairs, 1):
            base = pair.get("baseToken", {})
            price = pair.get("price", {}).get("usd", "0")
            change_1h = pair.get("priceChange", {}).get("h1", 0) or 0
            volume = pair.get("volume", {}).get("h24", 0) or 0
            mcap = pair.get("mcap", 0) or 0
            created = pair.get("pairCreatedAt", 0) or 0
            created_str = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M") if created else "N/A"

            print(f"\n{i}. {base.get('name', 'N/A')} ({base.get('symbol', 'N/A')})")
            print(f"   Address: {self.format_wallet_address(pair.get('baseMint', ''))}")
            print(f"   Price: ${price} | 1h Change: {change_1h:+.2f}%")
            print(f"   Vol: ${volume:,.0f} | MC: ${mcap:,.0f}")
            print(f"   Created: {created_str}")

    def run(self):
        """Run the full tracker."""
        print("\n" + "█" * 80)
        print("🔍 SOLANA WALLET TRACKER")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("█" * 80)

        self.print_top_tokens()
        self.print_top_creators()
        self.print_top_wallets()
        self.print_trending_pairs()

        print("\n" + "=" * 80)
        print("💡 TIP: Click on a wallet address above to copy it to clipboard")
        print("=" * 80)


if __name__ == "__main__":
    tracker = SolanaWalletTracker()
    tracker.run()
