import requests
import time
from datetime import datetime

# Insert API Key from Helius between quotes
API_KEY = ''
# Insert Your wallet between quotes
ADDRESS = ''
# API URL to Helius to pull information from address
BASE_URL = f"https://api.helius.xyz/v0/addresses/{ADDRESS}/transactions"

has_more = True
before_signature = None

# List of rewards wallet addresses sending you SOL
source_list = ['ChGA1Wbh9WN8MDiQ4ggA5PzBspS2Z6QheyaxdVo3XdW6', 'imgXJgVM2oFdVyLXuZSwdsPEB5e9PBZcst51tF3T7nR', 'imgTMPcxbJf4iNbKR3E5DmhQP1SUk6HarhNnBpSYTci']
wallet = ADDRESS
total_received = 0

# Path to Transaction File
file_path = "img_transactions.txt"
# Path to Total File
file_path_2 = "img_total.txt"

# Clear then Open Transaction File in write mode
img_file = open(file_path, "w")
img_file.write("timestamp\tfrom\tto\tamount in SOL\n")

params = {
  "api-key": API_KEY,
  "limit": 100,
  "before": None
}
while has_more:
    response = requests.get(BASE_URL, params=params)
    txs = response.json()

    if not txs:
        has_more = False
        print("No more transactions to fetch.")
        break

    for tx in txs:
      for transfer in tx.get("nativeTransfers", []):
        temp_source = transfer.get("fromUserAccount")
        temp_destination = transfer.get("toUserAccount")
        if (temp_source in source_list and temp_destination == wallet):
          time_stamp = datetime.utcfromtimestamp(tx['timestamp'])
          amount = transfer.get("amount") / 1e9  # convert lamports to SOL
          total_received += amount
          img_file.write(f"{time_stamp}\t{temp_source}\t{wallet}\t{amount}\n")
    try:
        before_signature = txs[-1].get("signature")
        if before_signature is None:
            raise KeyError("Signature not found in transaction.")
    except Exception as e:
        print("Error accessing signature:", e)
        print("Last tx content:", txs[-1])
        break

    if before_signature:
        params["before"] = before_signature

    # Throttle to respect rate limits
    time.sleep(1.25)

# Close Transaction File
img_file.close()

# Create Total File and write total received
with open(file_path_2, "w") as file:
  file.write(f"Total received: {total_received}\n")
  file.close()
