import os
import requests
import json
from dotenv import load_dotenv


from langchain_core.tools import tool
from typing import Optional, List
from pydantic import BaseModel, Field

load_dotenv()

# Retrieve environment variables
MERAKI_API_KEY = os.environ.get("MERAKI_API_KEY")
ORGANIZATION_ID = os.environ.get("ORGANIZATION_ID")

class NetworkCreateModel(BaseModel):
    name: str = Field(
        description="The name of the new network"
    )
    productTypes: List[str] = Field(
        description="The product type(s) of the new network. For combined networks, include multiple types",
        examples=[["wireless"], ["appliance", "camera", "wireless"]]
    )
    copyFromNetworkId: Optional[str] = Field(
        description="The ID of the network to copy configuration from. Must match network type"
    )
    notes: Optional[str] = Field(
        description="Additional notes or information about this network"
    )
    timeZone: Optional[str] = Field(
        description="The timezone of the network. Reference 'TZ' column in timezone article"
    )
    tags: Optional[List[str]] = Field(
        description="A list of tags to be applied to the network",
        examples=[["tag1", "tag2"]]
    )

class PayloadModel(BaseModel):
    payload: NetworkCreateModel = Field(
        description="The Payload for the meraki api"
    )


# Define the payload for creating a new network
def_payload:NetworkCreateModel = {
        "name": "Streamlit Test Network",
        "type": "wireless",  # You can specify the type of network, e.g., "wireless", "appliance", etc.
        "tags": "streamlit, test",  # Optional tags
        "timeZone": "America/Los_Angeles"  # Specify the time zone for the network
    }


def clean_payload(payload: json) -> json:
    """
    Removes any keys with null or None values from the payload

    Args:
        payload (json): The input JSON payload

    Returns:
        json: Cleaned payload with null/None values removed
    """
    if isinstance(payload, dict):
        return {
            key: clean_payload(value)
            for key, value in payload.items()
            if value is not None
        }
    elif isinstance(payload, list):
        return [clean_payload(item) for item in payload if item is not None]
    return payload


@tool("NetworkCreate-tool", args_schema=PayloadModel, return_direct=True)
def post_network(payload):
    """Creates Merkai Networks"""
    # Convert Pydantic model to dict, then clean it
    payload_dict = json.loads(payload.model_dump_json())
    cleaned_payload = clean_payload(payload_dict)
    print(cleaned_payload)
    
    url = f"https://api.meraki.com/api/v1/organizations/{ORGANIZATION_ID}/networks"

    headers = {
        "X-Cisco-Meraki-API-Key": MERAKI_API_KEY,
        "Content-Type": "application/json"
    }

    # Make the API request with cleaned payload
    response = requests.post(url, headers=headers, json=cleaned_payload)

    # Check the response
    print(response.text)
    if response.status_code == 201:
        return response.json()
    else:
        return{
            "response": str(response.status_code) + "\n" + response.text
        }
        print("Failed to create network.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

