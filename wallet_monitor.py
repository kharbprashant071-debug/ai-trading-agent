import time
import requests
from config import WALLET_ADDRESS

RPC_URL = "https://api.mainnet-beta.solana.com"


def get_recent_transactions(limit=10):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            WALLET_ADDRESS,
            {"limit": limit}
        ]
    }

    response = requests.post(RPC_URL, json=payload, timeout=20)
    response.raise_for_status()

    return response.json().get("result", [])


def monitor_wallet():
    print("===================================")
    print(" AI TRADING AGENT - WALLET MONITOR")
    print("===================================")
    print(f"Wallet: {WALLET_ADDRESS}")
    print("Mode: PAPER TRADING ONLY")
    print("-----------------------------------")

    last_signature = None

    while True:
        try:
            transactions = get_recent_transactions(10)

            if transactions:
                newest_signature = transactions[0]["signature"]

                if newest_signature != last_signature:
                    last_signature = newest_signature

                    print("\n[NEW WALLET ACTIVITY]")
                    print(f"Signature: {newest_signature}")
                    print(f"Status: {transactions[0].get('confirmationStatus')}")

            time.sleep(5)

        except Exception as error:
            print(f"[ERROR] {error}")
            time.sleep(10)


if __name__ == "__main__":
    monitor_wallet()
