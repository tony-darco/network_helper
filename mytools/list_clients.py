import os
import requests
from dotenv import load_dotenv

from langchain_core.tools import tool

load_dotenv()

# Environment variables for Meraki API
MERAKI_API_KEY = os.environ.get("MERAKI_API_KEY")
NETWORK_ID = os.environ.get("NETWORK_ID")

# Base URL for Meraki API
BASE_URL = "https://api.meraki.com/api/v1"
@tool("get_network_clients", return_direct=True)
def get_network_clients():
    """Returns all clients on a network"""
    url = f"{BASE_URL}/networks/{NETWORK_ID}/clients"

    # Headers for the API request
    headers = {
        "X-Cisco-Meraki-API-Key": MERAKI_API_KEY,
        "Content-Type": "application/json"
    }

    # Make the API request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        clients = response.json()
        # Print the names of the SSIDs
        return(clients)
    else:
        return(f"Failed to retrieve SSIDs. Status code: {response.status_code}, Response: {response.text}")
