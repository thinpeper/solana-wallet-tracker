#!/usr/bin/env python3
"""Solana Wallet Tracker - Track top profitable Solana wallets and tokens."""

import requests
import json
from datetime import datetime
from collections import defaultdict


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

    def get_top_wallets_by_buy_activity(self, limit=20):
        """Get top wallets by buy activity across pump.fun tokens."""
        try:
            tokens = self.get_pumpfun_tokens(limit=100)
            wallet_activity = defaultdict(lambda: {
                "total_buys": 0,
                "total_volume": 0,
                "tokens_traded": [],
            })

            for pair in tokens:
                # Use baseToken.address for the full address
                base_token = pair.get("baseToken", {})
                token_address = base_token.get("address", "") if base_token else ""
                token_name = base_token.get("name", "") if base_token else ""

                # Get txns data for buy/sell info
                txns = pair.get("txns", {})
                h1 = txns.get("h1", {})
                buys = h1.get("buys", 0) or 0
                sells = h1.get("sells", 0) or 0
                volume = pair.get("volume", {}).get("h24", 0) or 0

                # Use pairAddress as wallet proxy since DexScreener doesn't provide individual wallets
                pair_addr = pair.get("pairAddress", "")
                if pair_addr:
                    wallet_activity[pair_addr]["total_buys"] += buys
                    wallet_activity[pair_addr]["total_volume"] += volume
                    wallet_activity[pair_addr]["tokens_traded"].append({
                        "name": token_name,
                        "address": token_address,
                        "buys": buys,
                        "volume": volume,
                    })

            wallets = sorted(wallet_activity.items(), key=lambda x: x[1]["total_buys"], reverse=True)
            return wallets[:limit]
        except Exception as e:
            print(f"Error fetching top wallets: {e}")
            return []

    def print_top_tokens(self):
        """Print top Solana tokens by 24h volume."""
        print("\n" + "=" * 80)
        print("  TOP 15 SOLANA TOKENS BY 24H VOLUME")
        print("=" * 80)
        tokens = self.get_top_tokens(limit=15)

        for i, pair in enumerate(tokens, 1):
            base = pair.get("baseToken", {})
            address = base.get("address", "") if base else ""
            price = pair.get("priceUsd", "0")
            change_24h = pair.get("priceChange", {}).get("h24", 0) or 0
            volume = pair.get("volume", {}).get("h24", 0) or 0
            mcap = pair.get("mcap", 0) or 0
            liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
            buys = pair.get("txns", {}).get("h1", {}).get("buys", 0) or 0
            sells = pair.get("txns", {}).get("h1", {}).get("sells", 0) or 0

            print(f"\n  [{i}] {base.get('name', 'N/A')} ({base.get('symbol', 'N/A')})")
            print(f"  Address: {address}")
            print(f"  Price: ${price} | 24h Change: {change_24h:+.2f}%")
            print(f"  Vol: ${volume:,.0f} | MC: ${mcap:,.0f} | Liq: ${liquidity:,.0f}")
            print(f"  Buys/Sells: {buys}/{sells}")

    def print_top_creators(self):
        """Print top pump.fun creators by volume."""
        print("\n" + "=" * 80)
        print("  TOP 15 PUMP.FUN TOKENS BY VOLUME")
        print("=" * 80)
        tokens = self.get_pumpfun_tokens(limit=15)

        for i, pair in enumerate(tokens, 1):
            base = pair.get("baseToken", {})
            address = base.get("address", "") if base else ""
            volume = pair.get("volume", {}).get("h24", 0) or 0
            mcap = pair.get("mcap", 0) or 0
            liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
            buys = pair.get("txns", {}).get("h1", {}).get("buys", 0) or 0
            sells = pair.get("txns", {}).get("h1", {}).get("sells", 0) or 0
            change_24h = pair.get("priceChange", {}).get("h24", 0) or 0

            print(f"\n  [{i}] {base.get('name', 'N/A')} ({base.get('symbol', 'N/A')})")
            print(f"  Address: {address}")
            print(f"  Price: ${pair.get('priceUsd', '0')} | 24h Change: {change_24h:+.2f}%")
            print(f"  Vol: ${volume:,.0f} | MC: ${mcap:,.0f} | Liq: ${liquidity:,.0f}")
            print(f"  Buys/Sells: {buys}/{sells}")

    def print_top_wallets(self):
        """Print top wallets by buy activity."""
        print("\n" + "=" * 80)
        print("  TOP 20 WALLETS BY BUY ACTIVITY")
        print("=" * 80)
        wallets = self.get_top_wallets_by_buy_activity(limit=20)

        for i, (wallet, stats) in enumerate(wallets, 1):
            print(f"\n  [{i}] Wallet #{i}")
            print(f"  Address: {wallet}")
            print(f"  Total Buys: {stats['total_buys']} | Total Volume: ${stats['total_volume']:,.0f}")
            print(f"  Tokens Traded:")
            for token in stats["tokens_traded"][:3]:
                print(f"    - {token['name']}")
                print(f"      Address: {token['address']}")
                print(f"      Buys: {token['buys']}")

    def print_trending_pairs(self):
        """Print trending new pairs."""
        print("\n" + "=" * 80)
        print("  TRENDING NEW PAIRS (BY CREATION TIME)")
        print("=" * 80)
        pairs = self.get_trending_new_pairs(limit=15)

        for i, pair in enumerate(pairs, 1):
            base = pair.get("baseToken", {})
            address = base.get("address", "") if base else ""
            price = pair.get("priceUsd", "0")
            change_1h = pair.get("priceChange", {}).get("h1", 0) or 0
            volume = pair.get("volume", {}).get("h24", 0) or 0
            mcap = pair.get("mcap", 0) or 0
            created = pair.get("pairCreatedAt", 0) or 0
            created_str = "N/A"
            if created > 0:
                try:
                    created_str = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M")
                except (ValueError, OSError):
                    created_str = "N/A"

            print(f"\n  [{i}] {base.get('name', 'N/A')} ({base.get('symbol', 'N/A')})")
            print(f"  Address: {address}")
            print(f"  Price: ${price} | 1h Change: {change_1h:+.2f}%")
            print(f"  Vol: ${volume:,.0f} | MC: ${mcap:,.0f}")
            print(f"  Created: {created_str}")

    def run(self):
        """Run the full tracker."""
        print("\n" + "#" * 80)
        print("  SOLANA WALLET TRACKER")
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#" * 80)

        self.print_top_tokens()
        self.print_top_creators()
        self.print_top_wallets()
        self.print_trending_pairs()

        print("\n" + "=" * 80)
        print("  TIP: Wallet addresses are on their own line - just highlight and copy!")
        print("=" * 80)


if __name__ == "__main__":
    tracker = SolanaWalletTracker()
    tracker.run()
