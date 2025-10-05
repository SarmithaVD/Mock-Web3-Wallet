import sqlite3
import random
import bcrypt
import hashlib
from datetime import datetime
from typing import Optional, List, Dict
from src.wallet import Wallet

class WalletDatabase:
    def __init__(self, db_path = "wallet.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT PRIMARY KEY,
                hashed_secret_phrase TEXT NOT NULL,
                email TEXT,
                balance REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount REAL NOT NULL,
                amount_usd REAL,
                tx_hash TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_secret_phrase(self, secret_phrase):
        sha256_hash = hashlib.sha256(secret_phrase.encode('utf-8')).hexdigest()
        return bcrypt.hashpw(sha256_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_secret_phrase(self, secret_phrase, hashed):
        sha256_hash = hashlib.sha256(secret_phrase.encode('utf-8')).hexdigest()
        return bcrypt.checkpw(sha256_hash.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_wallet(self, address, secret_phrase, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        initial_balance = round(random.uniform(1.0, 10.0), 4)
        hashed_secret = self.hash_secret_phrase(secret_phrase)
        
        try:
            cursor.execute(
                "INSERT INTO wallets (address, hashed_secret_phrase, email, balance) VALUES (?, ?, ?, ?)",
                (address, hashed_secret, email, initial_balance)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            cursor.execute("SELECT balance FROM wallets WHERE address = ?", (address,))
            result = cursor.fetchone()
            initial_balance = result[0] if result else 0.0
        finally:
            conn.close()
        
        return initial_balance
    
    def get_wallet_by_address(self, address):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT address, hashed_secret_phrase, email, balance FROM wallets WHERE address = ?",
            (address,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'address': result[0],
                'hashed_secret_phrase': result[1],
                'email': result[2],
                'balance': result[3]
            }
        return None
    
    def authenticate_wallet(self, secret_phrase):
        wallet = Wallet()
        
        if not wallet.is_valid_mnemonic(secret_phrase):
            return None
        
        account = wallet.get_account_from_mnemonic(secret_phrase)
        address = account.address
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT address, hashed_secret_phrase, email, balance FROM wallets WHERE address = ?",
            (address,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and self.verify_secret_phrase(secret_phrase, result[1]):
            return {
                'address': result[0],
                'email': result[2],
                'balance': result[3]
            }
        return None
    
    def get_balance(self, address):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT balance FROM wallets WHERE address = ?", (address,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def update_balance(self, address, new_balance):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE wallets SET balance = ? WHERE address = ?",
            (new_balance, address)
        )
        
        conn.commit()
        conn.close()
    
    def wallet_exists(self, address):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM wallets WHERE address = ?", (address,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def transfer(self, from_address, to_address, amount, amount_usd: Optional[float] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT balance FROM wallets WHERE address = ?", (from_address,))
        sender_result = cursor.fetchone()
        
        if not sender_result:
            conn.close()
            return False, "Sender wallet not found"
        
        if sender_result[0] < amount:
            conn.close()
            return False, f"Insufficient balance. Available: {sender_result[0]:.6f} ETH"
        
        cursor.execute("SELECT balance FROM wallets WHERE address = ?", (to_address,))
        recipient_result = cursor.fetchone()
        
        if not recipient_result:
            conn.close()
            return False, "Receiver wallet does not exist in our database"
        
        recipient_balance = recipient_result[0]
        new_sender_balance = sender_result[0] - amount
        new_recipient_balance = recipient_balance + amount
        
        if new_sender_balance < 0:
            conn.close()
            return False, "Transaction would result in negative balance"
        
        cursor.execute("UPDATE wallets SET balance = ? WHERE address = ?", (new_sender_balance, from_address))
        cursor.execute("UPDATE wallets SET balance = ? WHERE address = ?", (new_recipient_balance, to_address))
        
        cursor.execute(
            """INSERT INTO transactions (from_address, to_address, amount, amount_usd) 
               VALUES (?, ?, ?, ?)""",
            (from_address, to_address, amount, amount_usd)
        )
        
        conn.commit()
        conn.close()
        
        return True, "Transaction successful"
    
    def get_transaction_history(self, address = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if address:
            cursor.execute(
                """SELECT id, from_address, to_address, amount, amount_usd, timestamp, status
                   FROM transactions 
                   WHERE from_address = ? OR to_address = ?
                   ORDER BY timestamp DESC""",
                (address, address)
            )
        else:
            cursor.execute(
                """SELECT id, from_address, to_address, amount, amount_usd, timestamp, status
                   FROM transactions 
                   ORDER BY timestamp DESC"""
            )
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'id': row[0],
                'from': row[1],
                'to': row[2],
                'amount': row[3],
                'amount_usd': row[4],
                'timestamp': row[5],
                'status': row[6]
            })
        
        conn.close()
        return transactions
    
    def get_all_wallets(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT address, balance, created_at FROM wallets ORDER BY created_at DESC"
        )
        
        wallets = []
        for row in cursor.fetchall():
            wallets.append({
                'address': row[0],
                'balance': row[1],
                'created_at': row[2]
            })
        
        conn.close()
        return wallets
    
    def get_wallet_email(self, address: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT email FROM wallets WHERE address = ?", (address,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] else None
