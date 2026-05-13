"""
Pi-hole Integration Service
Integrate with Pi-hole for real-time DNS monitoring and website tracking
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
    """Service for integrating with Pi-hole DNS server"""

    def __init__(self, pihole_url: str, password: Optional[str] = None):
        self.pihole_url = pihole_url.rstrip('/')
        self.password = password
        self.session = None
        self.sid = None
        self.csrf = None
        self.session_expires = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=10)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def authenticate(self) -> bool:
        """
        Authenticate with Pi-hole and get session ID
        """
        if not self.password:
            # If no password set, Pi-hole might not require authentication
            return True

        try:
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                url = f"{self.pihole_url}/api/auth"
                payload = {"password": self.password}

                response = await client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()
                if 'session' in data and data['session'].get('valid'):
                    self.sid = data['session']['sid']
                    self.csrf = data['session'].get('csrf')
                    self.session_expires = data['session']['validity']
                    logger.info("Successfully authenticated with Pi-hole")
                    return True
                else:
                    logger.error(f"Authentication failed: {data}")
                    return False

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def _ensure_authenticated(self) -> bool:
        """
        Ensure we have a valid session
        """
        if not self.sid and self.password:
            return await self.authenticate()
        return True

    async def _make_authenticated_request(self, method: str, endpoint: str,
                                        params: Dict = None, json_data: Dict = None) -> Dict:
        """
        Make an authenticated request to Pi-hole API
        """
        await self._ensure_authenticated()

        url = f"{self.pihole_url}{endpoint}"

        headers = {}
        if self.sid:
            headers['X-FTL-SID'] = self.sid
            if self.csrf:
                headers['X-FTL-CSRF'] = self.csrf

        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            if method.upper() == 'GET':
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = await client.post(url, headers=headers, json=json_data, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

    async def test_connection(self) -> Dict:
        """
        Test connection to Pi-hole API
        """
        try:
            # Try to get basic info without authentication first
            data = await self._make_authenticated_request('GET', '/api/info/version')

            return {
                'success': True,
                'version': data.get('version', 'unknown'),
                'message': 'Successfully connected to Pi-hole'
            }

        except Exception as e:
            # Try without authentication for basic endpoints
            try:
                async with httpx.AsyncClient(verify=False, timeout=10) as client:
                    response = await client.get(f"{self.pihole_url}/api.php")
                    response.raise_for_status()

                    data = response.json()
                    if 'domains_being_blocked' in data:
                        return {
                            'success': True,
                            'version': data.get('version', 'unknown'),
                            'domains_blocked': data.get('domains_being_blocked', 0),
                            'message': 'Successfully connected to Pi-hole (no auth required)'
                        }
            except Exception as inner_e:
                pass

            return {
                'success': False,
                'error': str(e),
                'message': 'Could not connect to Pi-hole API'
            }

    async def get_recent_queries(self, limit: int = 100) -> List[Dict]:
        """
        Get recent DNS queries from Pi-hole
        """
        try:
            params = {'recent': '', 'limit': str(limit)}
            data = await self._make_authenticated_request('GET', '/api.php', params=params)

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

            data = await self._make_authenticated_request('GET', '/api.php', params=params)

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

    async def get_stats(self) -> Dict:
        """
        Get Pi-hole statistics
        """
        try:
            data = await self._make_authenticated_request('GET', '/api.php')

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

    async def add_custom_blocklist(self, domains: List[str]) -> Dict:
        """
        Add domains to Pi-hole blocklist
        """
        try:
            # This would require Pi-hole's gravity update or API
            # For now, return not implemented
            result = {
                'success': False,
                'error': 'Custom blocklist management not yet implemented',
                'message': 'Use Pi-hole admin interface to manage blocklists'
            }
            return result
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e)
            }
            return error_result

