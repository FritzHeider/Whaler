from flask import Flask, render_template, jsonify
from transaction_handler import fetch_pending_transactions, handle_event, print_small_transactions_summary
from connection import get_web3, reconnect_websocket
import requests  # Import requests for API calls
import asyncio
import threading
from scipy.stats import pearsonr

app = Flask(__name__)

# Store whale transactions and counts
whale_transactions = []
eth_price_data = []  # Store ETH price data
transaction_counts = {
    "whale": 0,
    "significant": 0,
    "small": 0
}

# CoinGecko API URL
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
CURRENCY = "usd"
DAYS = 1  # Fetch data for the past day (or adjust as needed)

def fetch_eth_price():
    """Fetch ETH price data from CoinGecko."""
    try:
        params = {
            "vs_currency": CURRENCY,
            "days": DAYS,
            "interval": "minute"  # Fetch price data at 1-minute intervals
        }
        response = requests.get(COINGECKO_API_URL, params=params)
        data = response.json()

        prices = data.get("prices", [])
        eth_price_data.clear()  # Clear old data
        for p in prices:
            eth_price_data.append({
                "timestamp": p[0],  # Timestamp
                "price": p[1]  # Price in USD
            })
    except Exception as e:
        print(f"Error fetching ETH price data: {e}")

def calculate_correlation():
    """Calculate the Pearson correlation coefficient between whale transactions and ETH price."""
    tx_values = [tx['value'] for tx in whale_transactions]
    price_values = [price['price'] for price in eth_price_data]

    # Ensure that both lists have the same length
    if len(tx_values) == len(price_values) and len(tx_values) > 1:
        correlation, _ = pearsonr(tx_values, price_values)
        return correlation
    return 0  # Return 0 if there's insufficient data

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/api/whale_transactions')
def get_whale_transactions():
    """API endpoint to fetch whale transactions and ETH prices."""
    return jsonify({
        "whales": whale_transactions,
        "prices": eth_price_data,
        "transaction_counts": transaction_counts
    })

@app.route('/api/correlation')
def get_correlation():
    """API to return correlation between whale transactions and ETH prices."""
    correlation = calculate_correlation()
    return jsonify({"correlation": correlation})

# Background task to fetch ETH price data periodically
def fetch_price_data_periodically():
    while True:
        fetch_eth_price()  # Fetch ETH prices from CoinGecko
        asyncio.sleep(60)  # Fetch every 60 seconds

# Main asynchronous loop for logging whale transactions
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

                    # Classify transaction
                    value_in_eth = tx['value'] / 10**18  # Convert to ETH
                    whale_transactions.append({"hash": tx['hash'].hex(), "value": value_in_eth})
                    if value_in_eth > 1000:
                        transaction_counts['whale'] += 1
                    elif value_in_eth > 10:
                        transaction_counts['significant'] += 1
                    else:
                        transaction_counts['small'] += 1

            # Print summary of small transactions after processing the block
            print_small_transactions_summary()

            await asyncio.sleep(10)  # Poll every 10 seconds
        except Exception as e:
            print(f"Error while fetching pending transactions: {e}")
            await asyncio.sleep(5)  # Wait before retrying

# Run the log loop in a separate thread so it doesn't block Flask
def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(log_loop_async())

thread = threading.Thread(target=start_async_loop)
thread.start()

# Run the price fetching loop in a separate thread
price_thread = threading.Thread(target=fetch_price_data_periodically)
price_thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)