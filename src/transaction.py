import time
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta

class TransactionManager:
    def __init__(self):
        self.pending_transactions = {}
    
    def create_approval_message(self, from_address, to_address, amount_eth, amount_usd: Optional[float] = None, expiry_seconds = 30) -> Tuple[str, str]:
        timestamp = int(time.time())
        nonce = hashlib.sha256(f"{from_address}{to_address}{timestamp}".encode()).hexdigest()[:16]
        
        if amount_usd:
            message = f"Transfer {amount_eth:.6f} ETH (${amount_usd:.2f} USD) to {to_address} from {from_address}"
        else:
            message = f"Transfer {amount_eth:.6f} ETH to {to_address} from {from_address}"
        
        message_with_nonce = f"{message}|nonce:{nonce}|expires:{timestamp + expiry_seconds}"
        
        self.pending_transactions[nonce] = {
            'from': from_address,
            'to': to_address,
            'amount_eth': amount_eth,
            'amount_usd': amount_usd,
            'message': message_with_nonce,
            'expires_at': timestamp + expiry_seconds,
            'created_at': timestamp
        }
        
        return message_with_nonce, nonce
    
    def verify_and_get_transaction(self, nonce):
        if nonce not in self.pending_transactions:
            return None
        
        tx = self.pending_transactions[nonce]
        current_time = int(time.time())
        
        if current_time > tx['expires_at']:
            del self.pending_transactions[nonce]
            return None
        
        return tx
    
    def complete_transaction(self, nonce):
        if nonce in self.pending_transactions:
            del self.pending_transactions[nonce]
    
    def cleanup_expired(self):
        current_time = int(time.time())
        expired_nonces = [
            nonce for nonce, tx in self.pending_transactions.items()
            if current_time > tx['expires_at']
        ]
        for nonce in expired_nonces:
            del self.pending_transactions[nonce]
