"""
Router Auto-Detection Service
Automatically detect router type and configuration
"""

import httpx
import asyncio
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Common router URLs to try
ROUTER_URLS = [
    "http://192.168.1.1",
    "http://192.168.0.1",
    "http://192.168.100.1",
    "http://tendawifi.com",
    "http://router.local",
    "https://192.168.1.1:8443",  # UniFi
    "https://192.168.1.1",
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
        Auto-detect router type and URL
        Returns: {"router_type": "unifi", "router_url": "http://...", "detected": True}
        """
        
        for url in ROUTER_URLS:
            try:
                # Try to detect router type
                router_type = await RouterDetectionService._identify_router(url)
                
                if router_type:
                    logger.info(f"Detected {router_type} router at {url}")
                    return {
                        "router_type": router_type,
                        "router_url": url,
                        "detected": True,
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
                "Check your router documentation for the IP address"
            ]
        }

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
