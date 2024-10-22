from web3 import Web3
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

INFURA_KEY = os.getenv('INFURA_KEY')
infura_ws_url = f'wss://mainnet.infura.io/ws/v3/{INFURA_KEY}'

# Using the Legacy WebSocket provider for compatibility
web3 = Web3(Web3.LegacyWebSocketProvider(infura_ws_url))

if web3.is_connected():
    print("Connected to Ethereum WebSocket")
else:
    print("WebSocket connection failed")

# Define a function to handle and filter whale transactions
def handle_event(tx_hash):
    tx = web3.eth.get_transaction(tx_hash)
    if tx and tx['value'] and web3.from_wei(tx['value'], 'ether') > 1000:  # Use web3.fromWei directly
        print(f"Whale transaction detected: {tx['hash']} - {web3.fromWei(tx['value'], 'ether')} ETH")

# Define a loop to continuously poll pending transactions
def log_loop():
    while True:
        try:
            pending_transactions = web3.eth.get_block('pending')['transactions']
            for tx_hash in pending_transactions:
                handle_event(tx_hash)
            time.sleep(10)  # Poll every 10 seconds
        except Exception as e:
            print(f"Error while fetching pending transactions: {e}")
            time.sleep(5)  # Wait before retrying

log_loop()