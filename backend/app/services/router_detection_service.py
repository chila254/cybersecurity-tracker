"""
Router Auto-Detection Service
Automatically detect router type and configuration
"""

import httpx
import asyncio
import socket
import ipaddress
import subprocess
import platform
from typing import Optional, Dict, List
import logging
import re

logger = logging.getLogger(__name__)

# Common router URLs to try
ROUTER_URLS = [
    "http://192.168.1.1",
    "http://192.168.0.1",
    "http://192.168.100.1",
    "http://10.0.0.1",
    "http://tendawifi.com",
    "http://router.local",
    "https://192.168.1.1:8443",  # UniFi
    "https://192.168.1.1",
    "https://192.168.0.1:8443",
]

# Router detection signatures
ROUTER_SIGNATURES = {
    "unifi": [
        "UniFi",
        "ubiquiti",
        "network.name = 'UniFi OS'",
        "UBIQUITI",
    ],
    "tenda": [
        "Tenda",
        "tendawifi",
        "Tenda Router",
        "F3",
    ],
    "tp_link": [
        "TP-Link",
        "tplink",
        "tp-link",
        "TP Link",
    ],
    "meraki": [
        "Meraki",
        "cisco",
        "Cisco Meraki",
    ],
    "mikrotik": [
        "Mikrotik",
        "RouterOS",
        "mikrotik",
    ],
    "netgear": [
        "NETGEAR",
        "netgear",
    ],
}


class RouterDetectionService:
    """Service for auto-detecting router configuration"""

    @staticmethod
    async def detect_router() -> Optional[Dict]:
        """
        Auto-detect router type and URL using multiple methods
        Returns: {"router_type": "unifi", "router_url": "http://...", "detected": True}
        """

        # Method 1: Try network scanning for common router IPs
        logger.info("Scanning network for routers...")
        network_routers = await RouterDetectionService._scan_network_for_routers()
        if network_routers:
            for router_info in network_routers:
                logger.info(f"Found potential router: {router_info}")
                # Test if it's actually a router
                router_type = await RouterDetectionService._identify_router(router_info['url'])
                if router_type:
                    return {
                        "router_type": router_type,
                        "router_url": router_info['url'],
                        "detected": True,
                        "method": "network_scan",
                        "message": f"Found {router_type.upper()} router at {router_info['url']} via network scan"
                    }

        # Method 2: Try ARP table analysis
        logger.info("Checking ARP table for router...")
        arp_routers = await RouterDetectionService._check_arp_table()
        if arp_routers:
            for router_info in arp_routers:
                router_type = await RouterDetectionService._identify_router(router_info['url'])
                if router_type:
                    return {
                        "router_type": router_type,
                        "router_url": router_info['url'],
                        "detected": True,
                        "method": "arp_table",
                        "message": f"Found {router_type.upper()} router at {router_info['url']} via ARP table"
                    }

        # Method 3: Try common URLs (fallback)
        logger.info("Trying common router URLs...")
        for url in ROUTER_URLS:
            try:
                router_type = await RouterDetectionService._identify_router(url)

                if router_type:
                    logger.info(f"Detected {router_type} router at {url}")
                    return {
                        "router_type": router_type,
                        "router_url": url,
                        "detected": True,
                        "method": "common_urls",
                        "message": f"Found {router_type.upper()} router at {url}"
                    }

            except Exception as e:
                logger.debug(f"Router not found at {url}: {str(e)}")
                continue

        return {
            "detected": False,
            "message": "Could not auto-detect router. Please enter details manually.",
            "suggestions": [
                "Try logging in to http://tendawifi.com",
                "Or try http://192.168.1.1 or http://192.168.0.1",
                "Check your router documentation for the IP address",
                "Run 'arp -a' in terminal to find your router IP"
            ]
        }

    @staticmethod
    async def _scan_network_for_routers() -> List[Dict]:
        """
        Scan local network for potential routers
        """
        try:
            routers = []

            # Get local IP and subnet
            local_ip = RouterDetectionService._get_local_ip()
            if not local_ip:
                return routers

            # Calculate subnet (assume /24 for common home networks)
            ip_parts = local_ip.split('.')
            subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"

            # Common router IPs to check in subnet
            potential_router_ips = [
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1",  # .1
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.254",  # .254
                f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.100",  # Some ISP routers
            ]

            # Test each potential IP
            for ip in potential_router_ips:
                try:
                    # Quick TCP connect test on common router ports
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((ip, 80))
                    sock.close()

                    if result == 0:  # Port 80 open
                        routers.append({
                            'ip': ip,
                            'url': f"http://{ip}",
                            'method': 'port_scan'
                        })

                    # Also test HTTPS
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((ip, 443))
                    sock.close()

                    if result == 0:  # Port 443 open
                        routers.append({
                            'ip': ip,
                            'url': f"https://{ip}",
                            'method': 'port_scan'
                        })

                except Exception as e:
                    logger.debug(f"Failed to test {ip}: {str(e)}")
                    continue

            return routers

        except Exception as e:
            logger.error(f"Network scanning failed: {str(e)}")
            return []

    @staticmethod
    async def _check_arp_table() -> List[Dict]:
        """
        Check ARP table for potential router IPs
        """
        try:
            routers = []

            # Get ARP table
            if platform.system() == "Windows":
                arp_output = subprocess.check_output(["arp", "-a"], universal_newlines=True)
            else:  # Linux/Mac
                arp_output = subprocess.check_output(["arp", "-n"], universal_newlines=True)

            # Parse ARP entries
            lines = arp_output.strip().split('\n')
            for line in lines:
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 3:
                    ip = parts[1] if platform.system() == "Windows" else parts[0]
                    mac = parts[2] if platform.system() == "Windows" else parts[2]

                    # Check if this looks like a router IP (common patterns)
                    if RouterDetectionService._is_likely_router_ip(ip):
                        routers.append({
                            'ip': ip,
                            'mac': mac,
                            'url': f"http://{ip}",
                            'method': 'arp_table'
                        })

            return routers

        except Exception as e:
            logger.error(f"ARP table check failed: {str(e)}")
            return []

    @staticmethod
    def _get_local_ip() -> Optional[str]:
        """
        Get local IP address
        """
        try:
            # Create a socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to Google DNS
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            logger.debug(f"Could not determine local IP: {str(e)}")
            return None

    @staticmethod
    def _is_likely_router_ip(ip: str) -> bool:
        """
        Check if IP looks like a router IP
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                # Common router IPs
                octets = ip.split('.')
                last_octet = int(octets[3])
                return last_octet in [1, 254, 100, 10, 2]  # Common router IPs
            return False
        except:
            return False

    @staticmethod
    async def _identify_router(url: str) -> Optional[str]:
        """
        Identify router type by checking response content
        """
        try:
            async with httpx.AsyncClient(verify=False, timeout=5) as client:
                # Try to get the page
                response = await client.get(url, follow_redirects=True)
                content = response.text.lower()
                headers = str(response.headers).lower()
                
                # Check signatures
                for router_type, signatures in ROUTER_SIGNATURES.items():
                    for signature in signatures:
                        if signature.lower() in content or signature.lower() in headers:
                            return router_type
                
                # If we got a response but no match, might still be a router
                if response.status_code == 200 and ("login" in content or "password" in content):
                    # Likely a router, guess based on URL
                    if "tendawifi" in url:
                        return "tenda"
                    elif "unifi" in url:
                        return "unifi"
                    else:
                        return "tp_link"  # Default to TP-Link as most common
        
        except (httpx.ConnectError, httpx.TimeoutException, asyncio.TimeoutError):
            return None
        except Exception as e:
            logger.debug(f"Error identifying router at {url}: {str(e)}")
            return None

    @staticmethod
    async def test_connection(router_url: str, password: str, router_type: str = "tenda") -> Dict:
        """
        Test if router credentials work
        """
        try:
            if router_type == "tenda":
                return await RouterDetectionService._test_tenda(router_url, password)
            elif router_type == "tp_link":
                return await RouterDetectionService._test_tp_link(router_url, password)
            elif router_type == "unifi":
                return await RouterDetectionService._test_unifi(router_url, password)
            else:
                return {"success": False, "error": f"Unsupported router type: {router_type}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    async def _test_tenda(router_url: str, password: str) -> Dict:
        """Test Tenda router connection"""
        try:
            async with httpx.AsyncClient(verify=False, timeout=5) as client:
                # Try to access Tenda API
                response = await client.get(f"{router_url}/webroot/", auth=("admin", password))
                
                if response.status_code in [200, 401]:
                    return {
                        "success": True,
                        "message": "Successfully connected to Tenda router",
                        "router_type": "tenda"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Connection failed with status {response.status_code}",
                        "message": "Check your password"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Could not connect to Tenda router. Check password and router is accessible."
            }

    @staticmethod
    async def _test_tp_link(router_url: str, password: str) -> Dict:
        """Test TP-Link router connection"""
        try:
            async with httpx.AsyncClient(verify=False, timeout=5) as client:
                # Try to access TP-Link API
                response = await client.post(
                    f"{router_url}/cgi-bin/luci/api/auth",
                    data={"username": "admin", "password": password}
                )
                
                if response.status_code in [200, 401]:
                    return {
                        "success": True,
                        "message": "Successfully connected to TP-Link router",
                        "router_type": "tp_link"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Connection failed",
                        "message": "Check your password"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Could not connect to TP-Link router"
            }

    @staticmethod
    async def _test_unifi(router_url: str, password: str) -> Dict:
        """Test UniFi router connection"""
        try:
            async with httpx.AsyncClient(verify=False, timeout=5) as client:
                # Try UniFi API
                response = await client.post(
                    f"{router_url}/api/auth/login",
                    json={"username": "admin", "password": password}
                )
                
                if response.status_code in [200, 401]:
                    return {
                        "success": True,
                        "message": "Successfully connected to UniFi router",
                        "router_type": "unifi"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Connection failed",
                        "message": "Check your password"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Could not connect to UniFi router"
            }
