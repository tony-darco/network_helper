import os
import requests
from dotenv import load_dotenv

import json

from langchain_core.tools import tool
from typing import Optional, List
from pydantic import BaseModel, Field, conint

load_dotenv()

# Retrieve environment variables
MERAKI_API_KEY = os.environ.get("MERAKI_API_KEY")
NETWORK_ID = os.environ.get("NETWORK_ID")

class RadiusServerModel(BaseModel):
    host: str = Field(description="The IP address of your RADIUS server")
    port: int = Field(
        description="The UDP port your RADIUS servers listens on for Access-requests",
        default=1812
    )

class BandwidthLimitsModel(BaseModel):
    perClientBandwidthLimitDown: Optional[int] = Field(
        default=0,
        description="The download bandwidth limit in Kbps. (0 represents no limit.)"
    )
    perClientBandwidthLimitUp: Optional[int] = Field(
        default=0,
        description="The upload bandwidth limit in Kbps. (0 represents no limit.)"
    )
    perSsidBandwidthLimitDown: Optional[int] = Field(
        default=0,
        description="The total download bandwidth limit in Kbps. (0 represents no limit.)"
    )
    perSsidBandwidthLimitUp: Optional[int] = Field(
        default=0,
        description="The total upload bandwidth limit in Kbps. (0 represents no limit.)"
    )

class RadiusConfigModel(BaseModel):
    radiusServerTimeout: Optional[conint(ge=1, le=10)] = Field(
        default=5,
        description="The amount of time for which a RADIUS client waits for a reply (1-10 seconds)"
    )
    radiusServerAttemptsLimit: Optional[conint(ge=1, le=5)] = Field(
        default=3,
        description="Maximum number of transmit attempts before failover (1-5)"
    )
    radiusAccountingInterimInterval: Optional[int] = Field(
        description="Interval (seconds) for updating RADIUS accounting information"
    )
    radiusAccountingEnabled: Optional[bool] = Field(default=False)
    radiusGuestVlanEnabled: Optional[bool] = Field(default=False)
    radiusGuestVlanId: Optional[int] = Field(
        description="VLAN ID of the RADIUS Guest VLAN"
    )

class SSIDConfigModel(BaseModel):
    name: str = Field(description="The name of the SSID")
    enabled: bool = Field(default=True, description="Whether or not the SSID is enabled")
    authMode: str = Field(
        description="The association control method for the SSID",
        examples=["open", "psk", "8021x-meraki"]
    )
    encryptionMode: Optional[str] = Field(
        default=None,
        description="The psk encryption mode for the SSID",
        examples=["wep", "wpa"]
    )
    wpaEncryptionMode: Optional[str] = Field(
        default=None,
        description="WPA encryption mode for the SSID",
        examples=["WPA2 only", "WPA1 and WPA2", "WPA3 Transition Mode"]
    )
    psk: Optional[str] = Field(
        default=None,
        description="The passkey for the SSID (only valid if authMode is 'psk')"
    )
    bandSelection: Optional[str] = Field(
        default="Dual band operation",
        description="The client-serving radio frequencies of this SSID"
    )
    visible: bool = Field(
        default=True,
        description="Boolean indicating whether APs should advertise this SSID"
    )
    defaultVlanId: Optional[int] = Field(
        default=None,
        description="The default VLAN ID used for 'all other APs'"
    )
    vlanId: Optional[int] = Field(
        default=None,
        description="The VLAN ID used for VLAN tagging"
    )
    ipAssignmentMode: Optional[str] = Field(
        default="Bridge mode",
        description="The client IP assignment mode"
    )
    minBitrate: Optional[float] = Field(
        default=11.0,
        description="The minimum bitrate in Mbps of this SSID"
    )
    mandatoryDhcpEnabled: Optional[bool] = Field(
        default=False,
        description="Enforce DHCP-assigned IP addresses"
    )
    lanIsolationEnabled: Optional[bool] = Field(
        default=False,
        description="Enable Layer 2 LAN isolation"
    )
    bandwidth_limits: Optional[BandwidthLimitsModel] = Field(
        default_factory=BandwidthLimitsModel
    )
    radius_config: Optional[RadiusConfigModel] = Field(
        default_factory=RadiusConfigModel
    )
    radiusServers: Optional[List[RadiusServerModel]] = Field(
        default=None,
        description="The RADIUS 802.1X servers for authentication"
    )

class PayloadModel(BaseModel):
    ssid_number:int = Field(
        description="The ssid number to update"
    )
    payload: SSIDConfigModel = Field(
        description="The Payload for the meraki api"
    )

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

@tool("post_ssid_names", args_schema=PayloadModel, return_direct=True)
def post_ssid_names(ssid_number:int, payload:dict):
    """create and update ssids on Meraki Networks"""

    # Convert Pydantic model to dict, then clean it
    payload_dict = json.loads(payload.model_dump_json())
    cleaned_payload = clean_payload(payload_dict)
    print(cleaned_payload)
    url = f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/wireless/ssids/{ssid_number}"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-Key": MERAKI_API_KEY
    }

    # Make the API request
    response = requests.put(url, headers=headers, json=payload)

    # Check the response
    if response.status_code == 200:
        print("SSID created/updated successfully.")
        print(response.json())
    else:
        print(f"Failed to create/update SSID. Status code: {response.status_code}")
        print(response.text)