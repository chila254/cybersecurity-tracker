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

    def __init__(self, pihole_url: str, api_key: Optional[str] = None):
        self.pihole_url = pihole_url.rstrip('/')
        self.api_key = api_key
        self.session = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=10)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def test_connection(self) -> Dict:
        """
        Test connection to Pi-hole API
        """
        try:
            url = f"{self.pihole_url}/api.php"
            params = {}
            if self.api_key:
                params['auth'] = self.api_key

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                if 'domains_being_blocked' in data:
                    return {
                        'success': True,
                        'version': data.get('version', 'unknown'),
                        'domains_blocked': data.get('domains_being_blocked', 0),
                        'message': 'Successfully connected to Pi-hole'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Invalid Pi-hole API response'
                    }

        except Exception as e:
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
            url = f"{self.pihole_url}/api.php"
            params = {
                'recent': '',
                'limit': str(limit)
            }
            if self.api_key:
                params['auth'] = self.api_key

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
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
            url = f"{self.pihole_url}/api.php"
            params = {
                'getAllQueries': '',
                'limit': str(limit)
            }
            if self.api_key:
                params['auth'] = self.api_key
            if from_timestamp:
                params['from'] = str(from_timestamp)
            if until_timestamp:
                params['until'] = str(until_timestamp)

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
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
            url = f"{self.pihole_url}/api.php"
            params = {}
            if self.api_key:
                params['auth'] = self.api_key

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
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

