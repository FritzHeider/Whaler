from web3 import Web3
from dotenv import load_dotenv
import os
import time
from colorama import Fore, Style, init
from web3.middleware import geth_poa_middleware
import asyncio

# Initialize colorama for cross-platform color support
init()

# Load environment variables
load_dotenv()

INFURA_KEY = os.getenv('INFURA_KEY')
infura_ws_url = f'wss://mainnet.infura.io/ws/v3/{INFURA_KEY}'

# Using the Legacy WebSocket provider for compatibility
web3 = Web3(Web3.LegacyWebSocketProvider(infura_ws_url))

# Add middleware for POA networks like Rinkeby or other testnets
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Initialize counters for small transactions
small_transactions_count = 0
small_transactions_total_value = 0

# Function to reconnect WebSocket
async def reconnect_websocket():
    global web3
    while not web3.is_connected():
        try:
            print(Fore.YELLOW + "Attempting to reconnect..." + Style.RESET_ALL)
            web3 = Web3(Web3.LegacyWebSocketProvider(infura_ws_url))
            if web3.is_connected():
                print(Fore.GREEN + "Reconnected to Ethereum WebSocket" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Reconnection failed: {e}" + Style.RESET_ALL)
        await asyncio.sleep(5)  # Retry every 5 seconds if disconnected

# Function to handle and filter whale transactions
def handle_event(tx):
    global small_transactions_count, small_transactions_total_value
    try:
        value_in_eth = tx['value'] / 10**18  # Convert value from Wei to Ether
        if value_in_eth > 1000:  # Whale transaction threshold
            print(Fore.RED + f"Whale transaction detected: {tx['hash']} - {value_in_eth} ETH" + Style.RESET_ALL)
        elif value_in_eth > 10:  # Significant transaction threshold
            print(Fore.YELLOW + f"Significant transaction: {tx['hash']} - {value_in_eth} ETH" + Style.RESET_ALL)
        elif value_in_eth > 0:  # Small transaction, group these
            small_transactions_count += 1
            small_transactions_total_value += value_in_eth
    except Exception as e:
        print(Fore.RED + f"Error processing transaction {tx['hash']}: {e}" + Style.RESET_ALL)

# Function to print summary of small transactions
def print_small_transactions_summary():
    global small_transactions_count, small_transactions_total_value
    if small_transactions_count > 0:
        print(Fore.CYAN + f"{small_transactions_count} small transactions under 10 ETH, total: {small_transactions_total_value:.4f} ETH" + Style.RESET_ALL)
        # Reset counters
        small_transactions_count = 0
        small_transactions_total_value = 0

# Asynchronous log loop to fetch and process pending transactions
async def log_loop_async():
    while True:
        if not web3.is_connected():
            await reconnect_websocket()

        try:
            print("Fetching pending transactions...")
            pending_block = web3.eth.get_block('pending')
            pending_transactions = pending_block['transactions']
            print(f"Found {len(pending_transactions)} pending transactions")

            for tx_hash in pending_transactions:
                tx = web3.eth.get_transaction(tx_hash)
                if tx:
                    print(f"From: {tx['from']}, To: {tx['to']}, Gas Price: {tx['gasPrice']} Wei")
                    handle_event(tx)

            # Print summary of small transactions after processing the block
            print_small_transactions_summary()

            await asyncio.sleep(10)  # Poll every 10 seconds
        except Exception as e:
            print(Fore.RED + f"Error while fetching pending transactions: {e}" + Style.RESET_ALL)
            await asyncio.sleep(5)  # Wait before retrying

# Function to cease trading based on whale activity
def cease_automatic_trading(value_in_eth):
    if value_in_eth > 1000:
        print(Fore.MAGENTA + "Ceasing trading due to whale activity!" + Style.RESET_ALL)
        # Call your trading bot's stop function or modify trade parameters
        trading_bot.stop_trading()
    elif value_in_eth > 10:
        print(Fore.MAGENTA + "Adjusting trading strategy based on significant transactions." + Style.RESET_ALL)
        # Adjust the trading algorithm dynamically
        trading_bot.modify_strategy()

# Run the async log loop
asyncio.run(log_loop_async())