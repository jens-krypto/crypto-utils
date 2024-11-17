"""
Hark! The KMOON Ecosystem TVL Calculator

A most noble instrument for calculating Treasury Values Lock'd (TVL),
across the vast KMOON ecosystem spanning multiple blockchain realms.

Author: A humble servant of the KMOON ecosystem
Date: As the moon waxeth full in the year of our Lord 2024
License: MIT, as decreed by the ancient scrolls
"""

import json
from decimal import Decimal
import requests
from web3 import Web3
from typing import Dict, Optional
import time
import logging
from pathlib import Path

# Verily, we shall configure our logging scrolls
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("KMOON-TVL")

class KMOONEcosystemTVL:
    """O! This most excellent machinery doth calculate the treasures of KMOON's realm"""
    
    def __init__(self):
        # Prithee, establish connections to the various realms
        self.solana_rpc = "https://api.mainnet-beta.solana.com"
        self.jupiter_api = "https://price.jup.ag/v4/price"
        
        # Lo! The Ethereum realm beckons
        self.eth_w3 = Web3(Web3.HTTPProvider('https://cloudflare-eth.com'))
        self.factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
        self.weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        
        # Hark! The Tron network calls
        self.tron_api = "https://apilist.tronscan.org/api"
        
        # The sacred scrolls of contract interpretation
        self._init_contract_abis()
        
    def _init_contract_abis(self) -> None:
        """Behold! The ancient texts that guide our communion with the chains"""
        self.factory_abi = [{"constant":True,"inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"}],"name":"getPair","outputs":[{"name":"pair","type":"address"}],"type":"function"}]
        self.pair_abi = [{"constant":True,"inputs":[],"name":"getReserves","outputs":[{"name":"reserve0","type":"uint112"},{"name":"reserve1","type":"uint112"},{"name":"blockTimestampLast","type":"uint32"}],"type":"function"},{"constant":True,"inputs":[],"name":"token0","outputs":[{"name":"","type":"address"}],"type":"function"}]

    def get_solana_tvl(self, token_address: str) -> Dict:
        """Pray tell, what treasures lie within the Solana realm?"""
        try:
            logger.info(f"Querying the Solana oracles for {token_address}")
            
            # Summon forth the token's bounty
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenSupply",
                "params": [token_address]
            }
            response = requests.post(self.solana_rpc, json=payload)
            supply_data = response.json()
            
            if not supply_data.get('result', {}).get('value'):
                logger.error(f"Alas! Could not divine the supply of {token_address}")
                return {"error": "Supply remains shrouded in mystery"}
            
            # Calculate the grand sum, as the prophecy foretold
            amount = int(supply_data['result']['value']['amount'])
            decimals = supply_data['result']['value']['decimals']
            supply = Decimal(amount) / Decimal(10 ** decimals)
            
            logger.info(f"Supply divined: {supply}")
            
            # Seek the price from Jupiter's oracle
            price_response = requests.get(f"{self.jupiter_api}?ids={token_address}")
            price_data = price_response.json()
            
            if 'data' in price_data and token_address in price_data['data']:
                price = Decimal(str(price_data['data'][token_address]['price']))
                tvl = supply * price
                logger.info(f"TVL calculated: ${tvl:,.2f}")
                return {"tvl": float(tvl)}
            
            logger.error(f"Price discovery failed for {token_address}")
            return {"error": "Forsooth! The price eludes our grasp"}
        except Exception as e:
            logger.error(f"O woeful day! Solana calculation failed: {str(e)}")
            return {"error": str(e)}

    def get_ethereum_tvl(self, token_address: str) -> Dict:
        """Query the Ethereum realm for its locked treasures"""
        try:
            logger.info(f"Consulting the Ethereum oracles for {token_address}")
            
            # ERC20 ABI for supply divination
            erc20_abi = [{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]
            
            # Summon the contract's essence
            contract = self.eth_w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
            decimals = contract.functions.decimals().call()
            raw_supply = contract.functions.totalSupply().call()
            supply = Decimal(raw_supply) / Decimal(10 ** decimals)
            
            logger.info(f"Supply divined: {supply}")
            
            # Seek the price through Uniswap's pools
            factory = self.eth_w3.eth.contract(
                address=Web3.to_checksum_address(self.factory_address), 
                abi=self.factory_abi
            )
            pair_address = factory.functions.getPair(
                Web3.to_checksum_address(token_address), 
                self.weth_address
            ).call()
            
            if pair_address != "0x0000000000000000000000000000000000000000":
                pair = self.eth_w3.eth.contract(address=pair_address, abi=self.pair_abi)
                reserves = pair.functions.getReserves().call()
                token0 = pair.functions.token0().call()
                
                if token0.lower() == token_address.lower():
                    token_reserves = reserves[0]
                    eth_reserves = reserves[1]
                else:
                    token_reserves = reserves[1]
                    eth_reserves = reserves[0]
                
                # Divine ETH's value through Chainlink's oracle
                chainlink = self.eth_w3.eth.contract(
                    address="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
                    abi=[{"inputs":[],"name":"latestAnswer","outputs":[{"name":"","type":"int256"}],"type":"function"}]
                )
                eth_price = Decimal(chainlink.functions.latestAnswer().call()) / Decimal(10**8)
                
                if token_reserves > 0:
                    price_in_eth = Decimal(eth_reserves) / Decimal(token_reserves)
                    price_in_usd = price_in_eth * eth_price
                    tvl = supply * price_in_usd
                    logger.info(f"TVL calculated: ${tvl:,.2f}")
                    return {"tvl": float(tvl)}
            
            logger.error(f"No price pool found for {token_address}")
            return {"tvl": 0}
        except Exception as e:
            logger.error(f"Ethereum calculation failed: {str(e)}")
            return {"error": str(e)}

    def get_tron_tvl(self, token_address: str) -> Dict:
        """Investigate the treasures within TRON's dominion"""
        try:
            logger.info(f"Consulting the TRON oracles for {token_address}")
            
            response = requests.get(f"{self.tron_api}/token_trc20?contract={token_address}")
            data = response.json()
            
            if not data.get('trc20_tokens'):
                logger.error(f"Token information not found for {token_address}")
                return {"error": "Token remains unknown to the oracles"}
            
            token_info = data['trc20_tokens'][0]
            decimals = int(token_info.get('decimals', 6))
            total_supply = token_info.get('total_supply_with_decimals')
            
            if total_supply:
                supply = Decimal(total_supply) / Decimal(10 ** decimals)
                logger.info(f"Supply divined: {supply}")
            else:
                logger.error("Supply information missing")
                return {"error": "Supply remains a mystery"}
            
            if 'market_info' in token_info and 'priceInUsd' in token_info['market_info']:
                price = Decimal(str(token_info['market_info']['priceInUsd']))
                tvl = supply * price
                logger.info(f"TVL calculated: ${tvl:,.2f}")
                return {"tvl": float(tvl)}
            
            logger.error("Price information missing")
            return {"tvl": 0}
        except Exception as e:
            logger.error(f"TRON calculation failed: {str(e)}")
            return {"error": str(e)}

def main():
    """The grand orchestration of our KMOON ecosystem TVL quest"""
    calculator = KMOONEcosystemTVL()
    
    # The sacred addresses of our digital treasures
    tokens = {
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
    
    results = {"tokens": {}, "total_tvl": 0}
    
    # Begin our grand calculation
    logger.info("Let the KMOON ecosystem TVL calculation commence!")
    
    for chain, addresses in tokens.items():
        for address in addresses:
            logger.info(f"Examining the treasures of {chain} at {address}")
            
            if chain == "solana":
                tvl_data = calculator.get_solana_tvl(address)
            elif chain == "ethereum":
                tvl_data = calculator.get_ethereum_tvl(address)
            else:  # tron
                tvl_data = calculator.get_tron_tvl(address)
            
            if "tvl" in tvl_data:
                results["tokens"][address] = tvl_data["tvl"]
                results["total_tvl"] += tvl_data["tvl"]
    
    # Present our findings to the world
    print("\nKMOON Ecosystem TVL Summary:")
    print(json.dumps(results, indent=2))
    
    # Archive our discoveries
    output_path = Path('kmoon_ecosystem_tvl.json')
    with output_path.open('w') as f:
        json.dump(results, indent=2, fp=f)
    logger.info(f"Our findings have been recorded in {output_path}")

if __name__ == "__main__":
    main()