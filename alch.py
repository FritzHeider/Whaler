from web3 import Web3

# Connect to the Ethereum network
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/vrRb6GHy-EKITm2Pw7Q_QS2t9MRTQJSX'))

# Get block by number
block_number = 20953503  # Replace with the desired block number or use 'latest'
block = w3.eth.get_block(block_number)

print(block)