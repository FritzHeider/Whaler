import asyncio
from connection import get_web3, reconnect_websocket
from transaction_handler import fetch_pending_transactions, handle_event, print_small_transactions_summary

# Main asynchronous loop for logging transactions
async def log_loop_async():
    web3 = get_web3()

    while True:
        if not web3.is_connected():
            await reconnect_websocket()

        try:
            pending_transactions = await fetch_pending_transactions(web3)
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
            print(f"Error while fetching pending transactions: {e}")
            await asyncio.sleep(5)  # Wait before retrying

# Start the async loop
if __name__ == "__main__":
    asyncio.run(log_loop_async())