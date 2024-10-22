from web3 import Web3
from dotenv import load_dotenv
import os
from colorama import Fore, Style, init
import asyncio

# Initialize colorama for cross-platform color support
init()

# Load environment variables
load_dotenv()

INFURA_KEY = os.getenv('INFURA_KEY')
infura_ws_url = f'wss://mainnet.infura.io/ws/v3/{INFURA_KEY}'

# Initialize the web3 object
web3 = Web3(Web3.LegacyWebSocketProvider(infura_ws_url))

async def reconnect_websocket():
    """Reconnection logic for WebSocket"""
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

def get_web3():
    """Returns the web3 connection"""
    return web3