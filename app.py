import streamlit as st
from src.wallet import Wallet
from src.database import WalletDatabase
from src.transaction import TransactionManager
from src.skip_api import SkipAPI
from src.notifications import NotificationService
import time

st.set_page_config(page_title="Mock Web3 Wallet", page_icon="₿", layout="wide")

wallet_manager = Wallet()
db = WalletDatabase()
skip_api = SkipAPI()
notifier = NotificationService()

# Initialisation of session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_address' not in st.session_state:
    st.session_state.user_address = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'tx_manager' not in st.session_state:
    st.session_state.tx_manager = TransactionManager()

tx_manager = st.session_state.tx_manager

def logout():
    st.session_state.authenticated = False
    st.session_state.user_address = None
    st.session_state.user_email = None

st.title("₿ Mock Web3 Wallet")
st.markdown("---")

sidebar_menu = st.sidebar.radio(
    "Menu",
    ["Home", "Blockchain Explorer"] if not st.session_state.authenticated 
    else ["My Wallet", "Send Funds", "My Transactions", "Blockchain Explorer", "Logout"]
)

if sidebar_menu == "Home" and not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.header("Login to Your Wallet")
        secret_phrase = st.text_area("Enter your 12-word secret phrase:", height=100, key="login_secret")
        
        if st.button("Login", type="primary"):
            if secret_phrase:
                user_data = db.authenticate_wallet(secret_phrase)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.user_address = user_data['address']
                    st.session_state.user_email = user_data['email']
                    st.success(f"Login successful! Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid secret phrase or wallet not found")
            else:
                st.warning("Please enter your secret phrase")
    
    with tab2:
        st.header("Create New Wallet")
        email = st.text_input("Email Address:", key="signup_email")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate New secret Phrase", type="primary"):
                new_mnemonic = wallet_manager.generate_mnemonic()
                st.session_state.generated_mnemonic = new_mnemonic
        
        if 'generated_mnemonic' in st.session_state:
            st.info("**Your secret Phrase (Save this securely!):**")
            st.code(st.session_state.generated_mnemonic, language=None)
            st.warning("Write this down! You'll need it to access your wallet.")
            
            if st.button("Create Wallet with This secret Phrase"):
                account = wallet_manager.get_account_from_mnemonic(st.session_state.generated_mnemonic)
                balance = db.create_wallet(account.address, st.session_state.generated_mnemonic, email)
                st.success(f"Wallet created successfully!")
                st.info(f"Address: `{account.address}`")
                st.info(f"Initial Balance: {balance:.4f} ETH")
                del st.session_state.generated_mnemonic

elif sidebar_menu == "My Wallet" and st.session_state.authenticated:
    st.header("My Wallet")
    
    wallet_data = db.get_wallet_by_address(st.session_state.user_address)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Wallet Address", st.session_state.user_address[:10] + "..." + st.session_state.user_address[-8:])
        st.metric("Balance", f"{wallet_data['balance']:.6f} ETH")
    
    with col2:
        if wallet_data['email']:
            st.metric("Email", wallet_data['email'])
        st.info(f"Full Address: `{st.session_state.user_address}`")

elif sidebar_menu == "Send Funds" and st.session_state.authenticated:
    st.header("Send Funds")
    
    # Initialisation of transaction state
    if 'pending_tx' not in st.session_state:
        st.session_state.pending_tx = None
    
    balance = db.get_balance(st.session_state.user_address)
    st.info(f"Available Balance: **{balance:.6f} ETH**")
    
    if not st.session_state.pending_tx:
        recipient = st.text_input("Recipient Wallet Address:")
        
        col1, col2 = st.columns(2)
        with col1:
            currency = st.selectbox("Currency:", ["ETH", "USD"])
        with col2:
            amount = st.number_input(f"Amount ({currency}):", min_value=0.0, step=0.01)
        
        if st.button("Send Transaction", type="primary"):
            if not recipient:
                st.error("Please enter recipient address")
            elif not db.wallet_exists(recipient):
                st.error("Receiver wallet does not exist in our database. They must create a wallet first!")
            elif amount <= 0:
                st.error("Please enter a valid amount")
            else:
                amount_eth = amount
                amount_usd = None
                
                if currency == "USD":
                    with st.spinner("Converting USD to ETH via Skip API..."):
                        result = skip_api.get_eth_quote_for_usd(amount)
                        
                        if not result:
                            st.error("Failed to get price quote from Skip API!")
                            st.stop()
                        
                        amount_eth, quote_data = result
                        amount_usd = amount
                        st.success(f"Quote: {amount_eth:.6f} ETH for ${amount_usd:.2f} USD")
                
                if amount_eth > balance:
                    st.error(f"Insufficient balance! You have {balance:.6f} ETH but trying to send {amount_eth:.6f} ETH")
                else:
                    message, nonce = tx_manager.create_approval_message(
                        st.session_state.user_address, 
                        recipient, 
                        amount_eth, 
                        amount_usd,
                        expiry_seconds=300
                    )
                    
                    # Store transaction in session state
                    st.session_state.pending_tx = {
                        'recipient': recipient,
                        'amount_eth': amount_eth,
                        'amount_usd': amount_usd,
                        'currency': currency,
                        'message': message,
                        'nonce': nonce
                    }
                    st.rerun()
    
    else:
        tx = st.session_state.pending_tx
        
        st.warning("**Transaction Approval Required**")
        st.info(f"**To:** `{tx['recipient']}`")
        if tx['amount_usd']:
            st.info(f"**Amount:** {tx['amount_eth']:.6f} ETH (${tx['amount_usd']:.2f} USD)")
        else:
            st.info(f"**Amount:** {tx['amount_eth']:.6f} ETH")
        
        st.code(tx['message'].split('|')[0])
        
        secret_for_signing = st.text_input("Enter your secret phrase to sign:", type="password", key="secret_sign")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve and Sign Transaction", type="primary"):
                if not secret_for_signing:
                    st.error("Please enter your secret phrase to sign the transaction")
                else:
                    wallet_data = db.authenticate_wallet(secret_for_signing)
                    if not wallet_data or wallet_data['address'] != st.session_state.user_address:
                        st.error("Invalid secret phrase!")
                    else:
                        with st.spinner("Signing transaction..."):
                            account = wallet_manager.get_account_from_mnemonic(secret_for_signing)
                            signature = wallet_manager.sign_message(tx['message'], account.key.hex())
                            
                            if wallet_manager.verify_signature(tx['message'], signature, st.session_state.user_address):
                                tx_data = tx_manager.verify_and_get_transaction(tx['nonce'])
                                
                                if not tx_data:
                                    st.error("Transaction expired!")
                                    st.session_state.pending_tx = None
                                    st.stop()
                                
                                if tx['currency'] == "USD" and tx['amount_usd']:
                                    with st.spinner("Re-checking price tolerance..."):
                                        result = skip_api.get_eth_quote_for_usd(tx['amount_usd'])
                                        if result:
                                            current_eth, _ = result
                                            if not skip_api.check_price_tolerance(tx['amount_eth'], current_eth):
                                                st.error(f"Price changed too much! Transaction rejected.")
                                                tx_manager.complete_transaction(tx['nonce'])
                                                st.session_state.pending_tx = None
                                                st.stop()
                                
                                success, message_result = db.transfer(
                                    st.session_state.user_address,
                                    tx['recipient'],
                                    tx['amount_eth'],
                                    tx['amount_usd']
                                )
                                
                                if success:
                                    tx_manager.complete_transaction(tx['nonce'])
                                    
                                    sender_balance = db.get_balance(st.session_state.user_address)
                                    receiver_balance = db.get_balance(tx['recipient'])
                                    
                                    sender_email = db.get_wallet_email(st.session_state.user_address)
                                    receiver_email = db.get_wallet_email(tx['recipient'])
                                    
                                    notifier.notify_transaction(
                                        sender_email,
                                        receiver_email,
                                        st.session_state.user_address,
                                        tx['recipient'],
                                        tx['amount_eth'],
                                        sender_balance,
                                        receiver_balance,
                                        tx['amount_usd']
                                    )
                                    
                                    st.success("Transaction successful!")
                                    st.info(f"New Balance: {sender_balance:.6f} ETH")
                                    st.session_state.pending_tx = None
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(f"{message_result}")
                                    st.session_state.pending_tx = None
                            else:
                                st.error("Signature verification failed!")
        
        with col2:
            if st.button("Cancel Transaction"):
                st.session_state.pending_tx = None
                st.rerun()

elif sidebar_menu == "My Transactions" and st.session_state.authenticated:
    st.header("My Transaction History")
    
    transactions = db.get_transaction_history(st.session_state.user_address)
    
    if not transactions:
        st.info("No transactions found")
    else:
        for tx in transactions:
            direction = "SENT" if tx['from'].lower() == st.session_state.user_address.lower() else "RECEIVED"
            
            with st.expander(f"{direction} - {tx['timestamp']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**From:** `{tx['from']}`")
                    st.write(f"**To:** `{tx['to']}`")
                with col2:
                    if tx['amount_usd']:
                        st.write(f"**Amount:** {tx['amount']:.6f} ETH (${tx['amount_usd']:.2f} USD)")
                    else:
                        st.write(f"**Amount:** {tx['amount']:.6f} ETH")
                    st.write(f"**Status:** {tx['status']}")

elif sidebar_menu == "Blockchain Explorer":
    st.header("Public Blockchain Explorer")
    st.info("All wallet balances and transactions are publicly visible on this distributed ledger simulation")
    
    tab1, tab2 = st.tabs(["All Wallets", "All Transactions"])
    
    with tab1:
        st.subheader("All Wallets")
        wallets = db.get_all_wallets()
        
        if wallets:
            for wallet in wallets:
                with st.expander(f"📍 {wallet['address'][:16]}...{wallet['address'][-12:]} - {wallet['balance']:.6f} ETH"):
                    st.write(f"**Full Address:** `{wallet['address']}`")
                    st.write(f"**Balance:** {wallet['balance']:.6f} ETH")
                    st.write(f"**Created:** {wallet['created_at']}")
        else:
            st.info("No wallets found")
    
    with tab2:
        st.subheader("All Transactions")
        all_transactions = db.get_transaction_history()
        
        if all_transactions:
            for tx in all_transactions:
                with st.expander(f"TX #{tx['id']} - {tx['timestamp']}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**From:** `{tx['from']}`")
                        st.write(f"**To:** `{tx['to']}`")
                    with col2:
                        if tx['amount_usd']:
                            st.write(f"**Amount:** {tx['amount']:.6f} ETH (${tx['amount_usd']:.2f} USD)")
                        else:
                            st.write(f"**Amount:** {tx['amount']:.6f} ETH")
                        st.write(f"**Status:** {tx['status']}")
        else:
            st.info("No transactions found")

elif sidebar_menu == "Logout":
    logout()
    st.success("Logged out successfully!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Mock Web3 Wallet\n\nA Web3 wallet simulator")
