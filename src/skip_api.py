import requests
from typing import Optional, Tuple

class SkipAPI:
    def __init__(self):
        self.base_url = "https://api.skip.build/v2/fungible/msgs_direct"
        self.usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        self.eth_native = "ethereum-native"
        self.chain_id = "1"
        self.default_address = "0x742d35Cc6634C0532925a3b8D4C9db96c728b0B4"
    
    def usd_to_wei(self, usd_amount):
        return int(usd_amount * 1_000_000)
    
    def wei_to_eth(self, wei_amount):
        return wei_amount / 1_000_000_000_000_000_000
    
    def eth_to_wei(self, eth_amount):
        return int(eth_amount * 1_000_000_000_000_000_000)
    
    def get_eth_quote_for_usd(self, usd_amount):
        try:
            amount_in_usdc_wei = self.usd_to_wei(usd_amount)
            
            payload = {
                "source_asset_denom": self.usdc_address,
                "source_asset_chain_id": self.chain_id,
                "dest_asset_denom": self.eth_native,
                "dest_asset_chain_id": self.chain_id,
                "amount_in": str(amount_in_usdc_wei),
                "chain_ids_to_addresses": {
                    self.chain_id: self.default_address
                },
                "slippage_tolerance_percent": "1",
                "smart_swap_options": {
                    "evm_swaps": True
                },
                "allow_unsafe": False
            }
            
            response = requests.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'route' in data and 'amount_out' in data['route']:
                amount_out = data['route']['amount_out']
                eth_amount = self.wei_to_eth(int(amount_out))
                return eth_amount, data
            
            print(f"Unexpected API response structure: {list(data.keys())}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"Error fetching quote from Skip API: {e}")
            return None
    
    def check_price_tolerance(self, original_eth, current_eth, tolerance_percent = 1.0):
        price_diff_percent = abs((current_eth - original_eth) / original_eth) * 100
        return price_diff_percent <= tolerance_percent
