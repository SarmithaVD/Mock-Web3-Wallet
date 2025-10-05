from mnemonic import Mnemonic
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import json
import os

class Wallet:
    def __init__(self, storage_path = "wallet_config.json"):
        self.storage_path = storage_path
        self.mnemo = Mnemonic("english")
        Account.enable_unaudited_hdwallet_features()
    
    def generate_mnemonic(self):
        return self.mnemo.generate(strength=128)
    
    def is_valid_mnemonic(self, mnemonic):
        return self.mnemo.check(mnemonic)
    
    def get_account_from_mnemonic(self, mnemonic, index = 0):
        if not self.is_valid_mnemonic(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        
        account = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{index}")
        return account
    
    def save_wallet(self, mnemonic, address):
        wallet_data = {
            'mnemonic': mnemonic,
            'address': address
        }
        with open(self.storage_path, 'w') as f:
            json.dump(wallet_data, f)
    
    def load_wallet(self):
        if not os.path.exists(self.storage_path):
            return None
        
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def sign_message(self, message, private_key):
        message_hash = encode_defunct(text=message)
        signed_message = Account.sign_message(message_hash, private_key=private_key)
        return signed_message.signature.hex()
    
    def verify_signature(self, message, signature, expected_address):
        try:
            message_hash = encode_defunct(text=message)
            recovered_address = Account.recover_message(message_hash, signature=signature)
            return recovered_address.lower() == expected_address.lower()
        except Exception:
            return False
    
    def wallet_exists(self):
        return os.path.exists(self.storage_path)
