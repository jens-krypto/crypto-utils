"""
Hark! The KMOON Ecosystem Analytics Calculator

A most noble instrument for calculating both Market Cap and TVL (Liquidity),
across the vast KMOON ecosystem spanning multiple blockchain realms.

Verily, we shall employ:
- For Solana: Jupiter's wisdom for price, DexScreener's sight for liquidity
- For Ethereum: Uniswap's pools and Chainlink's oracle
- For TRON: The sacred scrolls of TRONSCAN

Author: A humble servant of the KMOON ecosystem
Date: As the moon waxeth full in the year of our Lord 2024
License: MIT, as decreed by the ancient scrolls
"""

import json
from decimal import Decimal
import requests
from web3 import Web3
import logging
from pathlib import Path
from typing import Dict

# Lo! Configure the logging scrolls
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KMOON-Analytics")

class KMOONEcosystemAnalytics:
    """O! This most excellent machinery doth calculate treasures across the realms"""
    
    def __init__(self):
        # Prithee, establish connections to the various realms
        self.solana_rpc = "https://api.mainnet-beta.solana.com"
        self.dexscreener_api = "https://api.dexscreener.com/latest/dex/tokens/"
        self.eth_w3 = Web3(Web3.HTTPProvider('https://cloudflare-eth.com'))
        self.tron_api = "https://apilist.tronscan.org/api"
        
        # The sacred addresses of our digital treasures
        self.tokens = {
            "solana": [
                "5tzkqRo8XjHefzuJumij7suA6N7nTZA1FSLtzM8Bpump",  # IYKYK
                "HQ2KXz4rJf1b18sHiGgvsCUe8hgEH21jqf2gys5jpump"   # KMOON
            ],
            "ethereum": [
                "0x5c050f01db04c98206eb55a6ca4dc3287c69abff",  # AA
                "0x9756f5cd1cb7c0dbb6893973c2f0cec59c671c05"   # RB
            ],
            "tron": [
                "TLxGAoiRk3oCr4yFPKHPrVAd7ZknhFcMWo"  # IYKYK
            ]
        }
        
        # The ancient scrolls of contract interpretation
        self.erc20_abi = [
            {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
            {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
        ]

    def get_solana_metrics(self, token_address: str) -> Dict:
        """Harken ye to the metrics from the Solana realm!
        
        By Jupiter's grace we divine the price,
        Through DexScreener's eye we glimpse the liquidity,
        And from Solana's own RPC we learn of supply.
        """
        try:
            logger.info(f"Seeking wisdom about the token at {token_address}")
            
            # First, let us consult the Solana RPC about supply
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenSupply",
                "params": [token_address]
            }
            supply_response = requests.post(self.solana_rpc, json=payload)
            supply_data = supply_response.json()
            
            if not supply_data.get('result', {}).get('value'):
                return {"error": "The supply remains shrouded in mystery"}
            
            # Calculate the grand sum, as the prophecy foretold
            amount = int(supply_data['result']['value']['amount'])
            decimals = supply_data['result']['value']['decimals']
            supply = Decimal(amount) / Decimal(10 ** decimals)
            
            # Seek counsel from Jupiter about the price
            price_response = requests.get(f"https://price.jup.ag/v4/price?ids={token_address}")
            price_data = price_response.json()
            
            if 'data' not in price_data or token_address not in price_data['data']:
                return {"error": "Jupiter's oracle remains silent"}
            
            price = Decimal(str(price_data['data'][token_address]['price']))
            ticker = price_data['data'][token_address].get('mintSymbol', '')
            
            # Now, let us gaze into DexScreener's pool of knowledge
            dex_response = requests.get(f"{self.dexscreener_api}{token_address}")
            dex_data = dex_response.json()
            
            total_liquidity = Decimal('0')
            if dex_data.get('pairs'):
                total_liquidity = sum(
                    Decimal(str(pair.get('liquidity', {}).get('usd', 0))) 
                    for pair in dex_data['pairs']
                )
            
            return {
                "ticker": ticker,
                "price": float(price),
                "supply": float(supply),
                "tvl": float(total_liquidity)
            }
            
        except Exception as e:
            logger.error(f"Alas! Our Solana quest has failed: {str(e)}")
            return {"error": str(e)}

    def get_ethereum_metrics(self, token_address: str) -> Dict:
        """Journey forth into the Ethereum realm to seek out treasures
        
        Through Uniswap's pools we divine both price and liquidity,
        While Chainlink's oracle doth tell us ETH's true worth.
        """
        try:
            logger.info(f"Venturing into Ethereum for token {token_address}")
            
            # First, commune with the token contract
            contract = self.eth_w3.eth.contract(
                address=Web3.to_checksum_address(token_address), 
                abi=self.erc20_abi
            )
            
            decimals = contract.functions.decimals().call()
            ticker = contract.functions.symbol().call()
            raw_supply = contract.functions.totalSupply().call()
            supply = Decimal(raw_supply) / Decimal(10 ** decimals)
            
            # Seek the Uniswap pools
            factory_abi = [{"constant":True,"inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"}],"name":"getPair","outputs":[{"name":"pair","type":"address"}],"type":"function"}]
            factory = self.eth_w3.eth.contract(
                address=Web3.to_checksum_address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"),
                abi=factory_abi
            )
            
            weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            pair_address = factory.functions.getPair(Web3.to_checksum_address(token_address), weth).call()
            
            price = Decimal('0')
            tvl = Decimal('0')
            
            if pair_address != "0x0000000000000000000000000000000000000000":
                pair_abi = [{"constant":True,"inputs":[],"name":"getReserves","outputs":[{"name":"","type":"uint112"},{"name":"","type":"uint112"},{"name":"","type":"uint32"}],"type":"function"}]
                pair = self.eth_w3.eth.contract(address=pair_address, abi=pair_abi)
                reserves = pair.functions.getReserves().call()
                
                # Consult Chainlink's oracle for ETH's value
                chainlink = self.eth_w3.eth.contract(
                    address="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
                    abi=[{"inputs":[],"name":"latestAnswer","outputs":[{"name":"","type":"int256"}],"type":"function"}]
                )
                eth_price = Decimal(chainlink.functions.latestAnswer().call()) / Decimal(10**8)
                
                # Calculate the divine numbers
                eth_reserves = Decimal(reserves[1]) / Decimal(10**18)
                token_reserves = Decimal(reserves[0]) / Decimal(10**decimals)
                price = (eth_reserves / token_reserves) * eth_price
                tvl = eth_reserves * eth_price * 2
            
            return {
                "ticker": ticker,
                "price": float(price),
                "supply": float(supply),
                "tvl": float(tvl)
            }
            
        except Exception as e:
            logger.error(f"Our Ethereum quest has met with misfortune: {str(e)}")
            return {"error": str(e)}

    def get_tron_metrics(self, token_address: str) -> Dict:
        """Venture into TRON's domain to gather intelligence
        
        From TRONSCAN's sacred scrolls we shall learn
        Of price, supply, and liquidity alike.
        """
        try:
            logger.info(f"Consulting the TRON oracles about {token_address}")
            
            response = requests.get(f"{self.tron_api}/token_trc20?contract={token_address}")
            data = response.json()
            
            if not data.get('trc20_tokens'):
                return {"error": "The token remains unknown to TRON's seers"}
            
            token_info = data['trc20_tokens'][0]
            
            if 'market_info' not in token_info:
                return {"error": "The market's wisdom eludes us"}
                
            market_info = token_info['market_info']
            ticker = token_info.get('symbol', '')
            decimals = int(token_info.get('decimals', 6))
            total_supply = Decimal(token_info.get('total_supply_with_decimals', '0'))
            supply = total_supply / Decimal(10 ** decimals)
            price = Decimal(str(market_info.get('priceInUsd', '0')))
            liquidity = Decimal(str(market_info.get('liquidity', '0')))
            
            return {
                "ticker": ticker,
                "price": float(price),
                "supply": float(supply),
                "tvl": float(liquidity)
            }
            
        except Exception as e:
            logger.error(f"Our TRON expedition has faltered: {str(e)}")
            return {"error": str(e)}

    def calculate_ecosystem_metrics(self) -> Dict:
        """The grand calculation of our entire realm's worth!
        
        Gather ye all metrics from each chain,
        Sum up the bounties and treasures therein,
        And present a unified view of our kingdom's wealth.
        """
        results = {
            "tokens": {},
            "totals": {
                "total_market_cap": 0,
                "total_tvl": 0
            }
        }
        
        logger.info("Beginning the grand calculation of our ecosystem's worth...")
        
        for chain, addresses in self.tokens.items():
            for address in addresses:
                if chain == "solana":
                    metrics = self.get_solana_metrics(address)
                elif chain == "ethereum":
                    metrics = self.get_ethereum_metrics(address)
                else:  # tron
                    metrics = self.get_tron_metrics(address)
                
                if "error" not in metrics:
                    market_cap = metrics['price'] * metrics['supply']
                    
                    results["tokens"][address] = {
                        "ticker": metrics['ticker'],
                        "market_cap": market_cap,
                        "tvl": metrics['tvl']
                    }
                    
                    results["totals"]["total_market_cap"] += market_cap
                    results["totals"]["total_tvl"] += metrics['tvl']
        
        return results

def get_kmoon_ecosystem_metrics() -> Dict:
    """A most convenient function to divine our ecosystem's metrics"""
    calculator = KMOONEcosystemAnalytics()
    return calculator.calculate_ecosystem_metrics()

def main():
    """The grand orchestration of our analytics quest"""
    # Gather the metrics from across the realms
    results = get_kmoon_ecosystem_metrics()
    
    # Present our findings to the world
    print("\nKMOON Ecosystem Analytics Summary:")
    print(json.dumps(results, indent=2))
    
    # Archive our discoveries for posterity
    output_path = Path('kmoon_ecosystem_metrics.json')
    with output_path.open('w') as f:
        json.dump(results, indent=2, fp=f)
    logger.info(f"Our findings have been inscribed in {output_path}")

if __name__ == "__main__":
    main()