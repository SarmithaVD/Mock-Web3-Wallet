# 🪙 Mock Web3 Wallet

https://mockweb3wallet.streamlit.app/

A *Blockchain Wallet Simulator* that demonstrates how cryptocurrency wallets work — all without real blockchain interaction.  
Create wallets, manage balances, send simulated ETH transfers, and explore transactions in a mock blockchain environment.

---

## 🚀 Overview

*Mock Web3 Wallet* is built in Python using *Streamlit*.  
It simulates key features of a real Ethereum wallet, such as:

- Wallet creation using mnemonic secret phrases  
- Address and balance management  
- ETH/USD transfer simulation  
- Transaction signing & verification  
- Email notifications on transactions  
- Blockchain explorer for transparency  
- Persistent database to store balances and history  

---

## ✨ Features

✅ **Wallet Creation** – Create your own simulated Ethereum wallet with a secret phrase  
✅ **Seed Phrase Login** – Log back in using your unique 12-word secret phrase  
✅ **Balance Management** – Each wallet starts with a random 1–10 ETH  
✅ **Send ETH or USD** – Transfer simulated ETH or USD (auto-converts at live rates)  
✅ **Transaction Signing** – Confirm every transaction by re-entering your seed phrase  
✅ **Blockchain Explorer** – View all wallets and transactions transparently  
✅ **Persistent Storage** – Balances and transactions stored in a local SQLite database  
✅ **Email Notifications** – Admin alert system for new transactions  
✅ **Streamlit Web UI** – Clean, interactive web interface  

---

## 🧩 Prerequisites

Before starting, ensure you have:

- **Python 3.8 or higher**  
- **pip** (Python package manager)

---

## ⚙ Installation

1. Clone or download this repository:

```bash
git clone https://github.com/your-username/mock-web3-wallet.git
cd mock-web3-wallet
```

### Install dependencies

```bash
pip install -r requirements.txt
```

**The dependencies include:**

- `streamlit` – Web interface  
- `eth-account` – Ethereum account generation & signing  
- `bcrypt` – Secure password hashing  
- `requests` – Real-time API communication (for ETH/USD rate)  
- `sqlite3` – Local database (built into Python)  

---

## 💻 Running the Application

Launch the Streamlit web app:

```bash
streamlit run app.py
```

Then open your browser and visit:  
👉 http://localhost:5000

---

## 🪪 How to Use the App

### 1️⃣ Create a Wallet

- Click **“Sign Up”**  
- Enter:
  - **Email:** (optional, for notifications)  
  - **Generate Seed Phrase:** creates your 12-word recovery phrase  
- **IMPORTANT:** Save your 12-word phrase securely! It’s the only way to access your wallet.  
- Click **“I’ve Saved My Seed Phrase”**  
- Your wallet is created with a random balance (1–10 ETH)

### 2️⃣ Log In to Your Wallet

- Click **“Login”**  
- Enter your **12-word seed phrase**  
- Click **“Login”** — you’ll be redirected to your wallet dashboard

### 3️⃣ Send Funds

- Navigate to **“Send Funds”**  
- Fill in:
  - **Recipient Address** (starts with `0x`)  
  - **Amount**  
  - **Currency:** **ETH** or **USD**  
- Click **Create Transaction**  
- Confirm the transaction by re-entering your seed phrase  
- Click **Approve and Sign**  
- ✅ Transaction will be completed and recorded instantly

### 4️⃣ View Transactions

- Go to **“My Transactions”** to see:
  - All sent and received transactions  
  - ETH & USD values  
  - Timestamps and sender/receiver info

### 5️⃣ Explore the Blockchain

- Click **“Blockchain Explorer”** to view:
  - All wallets created in the system  
  - Their current balances  
  - Every transaction between them

> 🧭 This simulates a public blockchain — anyone can view balances and transactions, but only the owner can spend.

---

## 🧱 Project Structure

```
├── app.py                     # Streamlit web application (main file)
├── requirements.txt           # Dependencies list
├── src/
│   ├── wallet.py              # Wallet creation and management
│   ├── database.py            # SQLite database operations
│   ├── transaction.py         # Transaction signing & verification
│   ├── skip_api.py            # ETH/USD conversion API utility
│   └── notifications.py       # Optional email notifications
├── wallet.db                  # SQLite database (auto-generated)
└── README.md                  # Documentation
```

---

## 🧠 Technologies Used

| Component        | Technology Used | Purpose                                      |
|------------------|-----------------|----------------------------------------------|
| Frontend         | Streamlit       | Web-based UI                                 |
| Backend          | Python 3        | Core logic                                   |
| Database         | SQLite          | Persistent local storage                     |
| Crypto Logic     | eth-account     | Ethereum-like wallet creation & signing      |
| Security         | bcrypt          | Hashing & seed protection                    |
| API              | requests        | Real-time ETH/USD conversion                 |
| Notifications    | smtplib         | Email alert system (optional)                |

---

## 📧 Email Notifications

To enable email alerts for transactions, configure environment variables:

```bash
export ADMIN_EMAIL="your-email@gmail.com"
export ADMIN_PASSWORD="your-app-specific-password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```

### 🔐 Gmail Setup

1. Enable **2-Step Verification** on your Gmail account  
2. Create an **App Password** for “Mail”  
3. Use that app password in the `ADMIN_PASSWORD` environment variable

If not configured, notifications will simply print to the console.

---
