"""
Pi-hole Integration Service
Integrate with Pi-hole for real-time DNS monitoring and website tracking

Based on official Pi-hole API implementation:
https://github.com/pi-hole/pi-hole/blob/master/advanced/Scripts/api.sh

API Documentation: http://pi.hole/api/docs (served locally by Pi-hole)
"""

import asyncio
import httpx
import json
from typing import List, Dict, Optional
from datetime import datetime
from app.models import DNSLog
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class PiHoleService:
    """Service for integrating with Pi-hole DNS server using official API"""

    def __init__(self, pihole_url: str, password: Optional[str] = None):
        self.pihole_url = pihole_url.rstrip('/')
        self.password = password
        self.sid = None
        self.csrf = None
        self.needs_auth = None  # Will be determined during connection test

    async def test_connection(self) -> Dict:
        """
        Test connection to Pi-hole API and determine auth requirements
        Based on TestAPIAvailability() from official api.sh
        """
        try:
            # First test basic connectivity
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                # Test the auth endpoint to see if API is available
                response = await client.get(f"{self.pihole_url}/api/auth")

                if response.status_code == 200:
                    # API available without authentication
                    self.needs_auth = False
                    data = response.json()
                    return {
                        'success': True,
                        'needs_auth': False,
                        'version': data.get('version', 'unknown'),
                        'message': 'Pi-hole API accessible without authentication'
                    }

                elif response.status_code == 401:
                    # API requires authentication
                    self.needs_auth = True
                    data = response.json()
                    needs_totp = data.get('session', {}).get('totp', False)
                    return {
                        'success': True,
                        'needs_auth': True,
                        'needs_totp': needs_totp,
                        'message': 'Pi-hole API requires authentication'
                    }

                else:
                    return {
                        'success': False,
                        'error': f'Unexpected response: {response.status_code}',
                        'message': 'Pi-hole API not responding correctly'
                    }

        except httpx.ConnectError:
            return {
                'success': False,
                'error': 'Connection failed',
                'message': 'Cannot connect to Pi-hole. Check URL and network connectivity.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to test Pi-hole connection'
            }

    async def authenticate(self) -> bool:
        """
        Authenticate with Pi-hole using session-based auth
        Based on LoginAPI() and Authentication() from official api.sh
        """
        if not self.needs_auth or not self.password:
            return True

        try:
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                # POST to /api/auth with password
                payload = {"password": self.password}
                response = await client.post(
                    f"{self.pihole_url}/api/auth",
                    json=payload,
                    headers={"User-Agent": "Cybersecurity Tracker"}
                )

                if response.status_code != 200:
                    logger.error(f"Auth failed with status {response.status_code}")
                    return False

                data = response.json()
                session = data.get('session', {})

                if session.get('valid'):
                    self.sid = session.get('sid')
                    self.csrf = session.get('csrf')
                    logger.info("Successfully authenticated with Pi-hole")
                    return True
                else:
                    error_msg = data.get('error', {}).get('message', 'Unknown error')
                    logger.error(f"Authentication failed: {error_msg}")
                    return False

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def logout(self) -> bool:
        """
        Logout from Pi-hole session
        Based on LogoutAPI() from official api.sh
        """
        if not self.sid:
            return True

        try:
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                response = await client.delete(
                    f"{self.pihole_url}/api/auth",
                    headers={
                        "X-FTL-SID": self.sid,
                        "Accept": "application/json"
                    }
                )

                if response.status_code == 204:
                    logger.info("Successfully logged out from Pi-hole")
                    self.sid = None
                    self.csrf = None
                    return True
                else:
                    logger.warning(f"Logout returned status {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False

    async def _make_api_request(self, method: str, endpoint: str,
                               params: Optional[Dict] = None,
                               json_data: Optional[Dict] = None) -> Dict:
        """
        Make authenticated API request to Pi-hole
        Based on GetFTLData() and PostFTLData() from official api.sh
        """
        # Ensure we're authenticated if needed
        if self.needs_auth and not self.sid:
            if not await self.authenticate():
                raise Exception("Failed to authenticate with Pi-hole")

        url = f"{self.pihole_url}/api{endpoint}"
        headers = {"Accept": "application/json"}

        if self.sid:
            headers["X-FTL-SID"] = self.sid
            if self.csrf:
                headers["X-FTL-CSRF"] = self.csrf

        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            if method.upper() == 'GET':
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = await client.post(url, headers=headers, json=json_data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

    async def get_stats(self) -> Dict:
        """
        Get Pi-hole statistics
        """
        try:
            data = await self._make_api_request('GET', '')
            return {
                'domains_being_blocked': data.get('domains_being_blocked', 0),
                'dns_queries_today': data.get('dns_queries_today', 0),
                'ads_blocked_today': data.get('ads_blocked_today', 0),
                'ads_percentage_today': data.get('ads_percentage_today', 0),
                'unique_domains': data.get('unique_domains', 0),
                'queries_forwarded': data.get('queries_forwarded', 0),
                'queries_cached': data.get('queries_cached', 0),
                'clients_ever_seen': data.get('clients_ever_seen', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Pi-hole stats: {str(e)}")
            return {}

    async def get_recent_queries(self, limit: int = 100) -> List[Dict]:
        """
        Get recent DNS queries from Pi-hole
        """
        try:
            params = {'recent': '', 'limit': str(limit)}
            data = await self._make_api_request('GET', '', params=params)

            queries = []
            if 'data' in data:
                for query in data['data']:
                    queries.append({
                        'timestamp': query.get('timestamp', datetime.utcnow()),
                        'domain': query.get('domain', ''),
                        'client': query.get('client', ''),
                        'query_type': query.get('type', 'A'),
                        'status': query.get('status', 'unknown'),
                        'reply_type': query.get('reply_type', ''),
                        'dnssec': query.get('dnssec', '')
                    })

            return queries

        except Exception as e:
            logger.error(f"Failed to get Pi-hole queries: {str(e)}")
            return []

    async def get_query_logs(self, from_timestamp: Optional[int] = None,
                           until_timestamp: Optional[int] = None,
                           limit: int = 1000) -> List[Dict]:
        """
        Get DNS query logs from Pi-hole with time range
        """
        try:
            params = {'getAllQueries': '', 'limit': str(limit)}
            if from_timestamp:
                params['from'] = str(from_timestamp)
            if until_timestamp:
                params['until'] = str(until_timestamp)

            data = await self._make_api_request('GET', '', params=params)

            queries = []
            if 'data' in data:
                for query in data['data']:
                    queries.append({
                        'timestamp': query[0],
                        'query_type': query[1],
                        'domain': query[2],
                        'client': query[3],
                        'status': query[4]
                    })

            return queries

        except Exception as e:
            logger.error(f"Failed to get Pi-hole logs: {str(e)}")
            return []

    async def sync_dns_logs_to_db(self, db: Session, org_id: int,
                                 since_timestamp: Optional[int] = None) -> int:
        """
        Sync DNS logs from Pi-hole to database
        Returns number of logs imported
        """
        try:
            # Get queries from Pi-hole
            queries = await self.get_query_logs(from_timestamp=since_timestamp, limit=5000)

            imported_count = 0
            for query in queries:
                try:
                    # Check if log already exists
                    existing = db.query(DNSLog).filter(
                        DNSLog.org_id == org_id,
                        DNSLog.domain == query['domain'],
                        DNSLog.timestamp == datetime.fromtimestamp(query['timestamp'])
                    ).first()

                    if not existing:
                        # Categorize domain
                        from app.services.dns_service import DNSService
                        category = DNSService.categorize_domain(query['domain'])

                        # Determine if blocked
                        is_blocked = query['status'] in ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

                        dns_log = DNSLog(
                            org_id=org_id,
                            device_id=None,  # Will be determined by MAC later
                            mac_address=query['client'],  # Pi-hole uses IP, we'll resolve to MAC
                            domain=query['domain'],
                            domain_category=category,
                            query_type=query['query_type'],
                            response_code=query['status'],
                            is_blocked=is_blocked,
                            timestamp=datetime.fromtimestamp(query['timestamp'])
                        )

                        db.add(dns_log)
                        imported_count += 1

                except Exception as e:
                    logger.error(f"Error processing DNS log: {str(e)}")
                    continue

            db.commit()
            logger.info(f"Imported {imported_count} DNS logs from Pi-hole for org {org_id}")
            return imported_count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to sync DNS logs: {str(e)}")
            return 0

    async def get_api_docs_url(self) -> str:
        """
        Get the URL for Pi-hole's local API documentation
        """
        return f"{self.pihole_url}/api/docs"

    # Context manager support for automatic logout
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()