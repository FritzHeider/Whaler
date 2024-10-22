from colorama import Fore, Style
import asyncio

# Initialize counters for small transactions
small_transactions_count = 0
small_transactions_total_value = 0

async def fetch_pending_transactions(web3):
    """Fetch pending transactions from the blockchain"""
    print("Fetching pending transactions...")
    pending_block = web3.eth.get_block('pending')
    return pending_block['transactions']

def handle_event(tx):
    """Process each transaction and classify as whale or small"""
    global small_transactions_count, small_transactions_total_value
    try:
        value_in_eth = tx['value'] / 10**18  # Convert value from Wei to Ether
        if value_in_eth > 1000:  # Whale transaction threshold
            print(Fore.RED + f"Whale transaction detected: {tx['hash']} - {value_in_eth} ETH" + Style.RESET_ALL)
        elif value_in_eth > 10:  # Significant transaction threshold
            print(Fore.YELLOW + f"Significant transaction: {tx['hash']} - {value_in_eth} ETH" + Style.RESET_ALL)
        else:  # Small transaction
            small_transactions_count += 1
            small_transactions_total_value += value_in_eth
    except Exception as e:
        print(Fore.RED + f"Error processing transaction {tx['hash']}: {e}" + Style.RESET_ALL)

def print_small_transactions_summary():
    """Print the summary of small transactions"""
    global small_transactions_count, small_transactions_total_value
    if small_transactions_count > 0:
        print(Fore.CYAN + f"{small_transactions_count} small transactions under 10 ETH, total: {small_transactions_total_value:.4f} ETH" + Style.RESET_ALL)
        # Reset counters
        small_transactions_count = 0
        small_transactions_total_value = 0