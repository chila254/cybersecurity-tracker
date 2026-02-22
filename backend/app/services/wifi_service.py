"""
WiFi Device Tracking Service
Supports multiple router types: Unifi, Meraki, TP-Link, Mikrotik
"""

import asyncio
import httpx
import json
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import ConnectedDevice, WiFiConfig
import logging

logger = logging.getLogger(__name__)

class WiFiService:
    """Base service for WiFi device tracking"""
    
    def __init__(self, config: WiFiConfig):
        self.config = config
        self.router_type = config.router_type.lower()
        self.router_url = config.router_url
        self.username = config.router_username
        self.password = config.router_password
    
    async def get_connected_devices(self) -> List[Dict]:
        """Get list of connected devices from router"""
        if self.router_type == "unifi":
            return await self._get_unifi_devices()
        elif self.router_type == "meraki":
            return await self._get_meraki_devices()
        elif self.router_type == "tp_link":
            return await self._get_tp_link_devices()
        elif self.router_type == "mikrotik":
            return await self._get_mikrotik_devices()
        else:
            raise ValueError(f"Unsupported router type: {self.router_type}")
    
    async def _get_unifi_devices(self) -> List[Dict]:
        """Get devices from Ubiquiti UniFi controller"""
        try:
            async with httpx.AsyncClient(verify=False) as client:
                # Login to UniFi controller
                login_url = f"{self.router_url}/api/auth/login"
                login_data = {
                    "username": self.username,
                    "password": self.password
                }
                
                response = await client.post(login_url, json=login_data)
                response.raise_for_status()
                
                # Get connected clients
                devices_url = f"{self.router_url}/api/v2/sites/default/clients"
                devices_response = await client.get(devices_url)
                devices_response.raise_for_status()
                
                devices_data = devices_response.json()
                devices = []
                
                for client in devices_data.get("data", []):
                    device = {
                        "mac_address": client.get("mac"),
                        "ip_address": client.get("ip"),
                        "device_name": client.get("name", client.get("hostname")),
                        "device_type": self._detect_device_type(client.get("os_type", "")),
                        "user_name": client.get("name"),
                        "manufacturer": client.get("oui"),
                        "connected_at": datetime.fromtimestamp(client.get("assoc_time", 0) / 1000),
                        "data_sent_bytes": str(client.get("tx_bytes", 0)),
                        "data_received_bytes": str(client.get("rx_bytes", 0)),
                        "signal_strength": client.get("signal"),
                        "is_online": client.get("is_wired", False) or client.get("last_seen", 0) > (datetime.utcnow().timestamp() - 300),
                        "router_model": "UniFi"
                    }
                    devices.append(device)
                
                return devices
        
        except Exception as e:
            logger.error(f"Error fetching UniFi devices: {str(e)}")
            return []
    
    async def _get_meraki_devices(self) -> List[Dict]:
        """Get devices from Cisco Meraki (requires API key)"""
        try:
            headers = {
                "X-Cisco-Meraki-API-Key": self.password,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Get network devices
                devices_url = f"{self.router_url}/api/v1/networks/devices"
                response = await client.get(devices_url, headers=headers)
                response.raise_for_status()
                
                devices_data = response.json()
                devices = []
                
                for device in devices_data:
                    if device.get("status") == "online":
                        dev = {
                            "mac_address": device.get("mac"),
                            "ip_address": device.get("ip"),
                            "device_name": device.get("name"),
                            "device_type": device.get("productType", "unknown"),
                            "user_name": device.get("user"),
                            "manufacturer": device.get("model"),
                            "connected_at": datetime.fromisoformat(device.get("lastReportedAt", datetime.utcnow().isoformat())),
                            "data_sent_bytes": str(device.get("txPower", 0)),
                            "data_received_bytes": "0",
                            "signal_strength": device.get("signalQuality"),
                            "is_online": True,
                            "router_model": "Meraki"
                        }
                        devices.append(dev)
                
                return devices
        
        except Exception as e:
            logger.error(f"Error fetching Meraki devices: {str(e)}")
            return []
    
    async def _get_tp_link_devices(self) -> List[Dict]:
        """Get devices from TP-Link router"""
        try:
            async with httpx.AsyncClient() as client:
                # Login and get DHCP clients
                login_url = f"{self.router_url}/cgi-bin/luci/api/auth"
                login_data = {
                    "username": self.username,
                    "password": self.password
                }
                
                response = await client.post(login_url, data=login_data)
                response.raise_for_status()
                
                # Get connected devices
                devices_url = f"{self.router_url}/cgi-bin/luci/api/system/dhcp_clients"
                devices_response = await client.get(devices_url)
                devices_response.raise_for_status()
                
                devices_data = devices_response.json()
                devices = []
                
                for client_info in devices_data.get("data", []):
                    device = {
                        "mac_address": client_info.get("mac"),
                        "ip_address": client_info.get("ip"),
                        "device_name": client_info.get("hostname", client_info.get("name")),
                        "device_type": "unknown",
                        "user_name": None,
                        "manufacturer": self._get_manufacturer_from_mac(client_info.get("mac")),
                        "connected_at": datetime.utcnow(),
                        "data_sent_bytes": str(client_info.get("tx_bytes", 0)),
                        "data_received_bytes": str(client_info.get("rx_bytes", 0)),
                        "signal_strength": None,
                        "is_online": True,
                        "router_model": "TP-Link"
                    }
                    devices.append(device)
                
                return devices
        
        except Exception as e:
            logger.error(f"Error fetching TP-Link devices: {str(e)}")
            return []
    
    async def _get_mikrotik_devices(self) -> List[Dict]:
        """Get devices from Mikrotik RouterOS"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.password}"
                }
                
                # Get ARP entries
                arp_url = f"{self.router_url}/api/ip/arp"
                response = await client.get(arp_url, headers=headers)
                response.raise_for_status()
                
                arp_data = response.json()
                devices = []
                
                for entry in arp_data.get("data", []):
                    if entry.get("disabled") == "false":
                        device = {
                            "mac_address": entry.get("mac-address"),
                            "ip_address": entry.get("address"),
                            "device_name": entry.get("comment"),
                            "device_type": "unknown",
                            "user_name": None,
                            "manufacturer": self._get_manufacturer_from_mac(entry.get("mac-address")),
                            "connected_at": datetime.utcnow(),
                            "data_sent_bytes": "0",
                            "data_received_bytes": "0",
                            "signal_strength": None,
                            "is_online": True,
                            "router_model": "Mikrotik"
                        }
                        devices.append(device)
                
                return devices
        
        except Exception as e:
            logger.error(f"Error fetching Mikrotik devices: {str(e)}")
            return []
    
    @staticmethod
    def _detect_device_type(os_type: str) -> str:
        """Detect device type from OS"""
        os_lower = os_type.lower()
        if "windows" in os_lower:
            return "laptop"
        elif "macos" in os_lower or "darwin" in os_lower:
            return "laptop"
        elif "linux" in os_lower:
            return "laptop"
        elif "ios" in os_lower or "iphone" in os_lower:
            return "phone"
        elif "android" in os_lower:
            return "phone"
        elif "ipad" in os_lower:
            return "tablet"
        else:
            return "unknown"
    
    @staticmethod
    def _get_manufacturer_from_mac(mac: str) -> str:
        """Get manufacturer from MAC address (first 3 octets)"""
        # This is a simplified version - in production, use a MAC lookup API
        mac_prefix = mac.split(":")[0:3]
        return ":".join(mac_prefix).upper()
    
    async def save_devices_to_db(self, db: Session, org_id: UUID, devices: List[Dict]):
        """Save discovered devices to database"""
        try:
            for device_data in devices:
                # Check if device already exists
                existing = db.query(ConnectedDevice).filter(
                    ConnectedDevice.org_id == org_id,
                    ConnectedDevice.mac_address == device_data["mac_address"]
                ).first()
                
                if existing:
                    # Update existing device
                    existing.ip_address = device_data.get("ip_address")
                    existing.device_name = device_data.get("device_name")
                    existing.device_type = device_data.get("device_type")
                    existing.user_name = device_data.get("user_name")
                    existing.manufacturer = device_data.get("manufacturer")
                    existing.data_sent_bytes = device_data.get("data_sent_bytes")
                    existing.data_received_bytes = device_data.get("data_received_bytes")
                    existing.signal_strength = device_data.get("signal_strength")
                    existing.is_online = device_data.get("is_online", True)
                    existing.router_model = device_data.get("router_model")
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new device
                    new_device = ConnectedDevice(
                        org_id=org_id,
                        mac_address=device_data["mac_address"],
                        ip_address=device_data.get("ip_address"),
                        device_name=device_data.get("device_name"),
                        device_type=device_data.get("device_type"),
                        user_name=device_data.get("user_name"),
                        manufacturer=device_data.get("manufacturer"),
                        connected_at=device_data.get("connected_at", datetime.utcnow()),
                        data_sent_bytes=device_data.get("data_sent_bytes"),
                        data_received_bytes=device_data.get("data_received_bytes"),
                        signal_strength=device_data.get("signal_strength"),
                        is_online=device_data.get("is_online", True),
                        router_model=device_data.get("router_model")
                    )
                    db.add(new_device)
            
            db.commit()
            logger.info(f"Saved {len(devices)} devices for org {org_id}")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving devices to database: {str(e)}")
