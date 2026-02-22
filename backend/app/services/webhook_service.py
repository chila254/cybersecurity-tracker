"""
Webhook and integration service for sending events to external systems
Supports Slack, Teams, and generic webhooks
"""

import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from app.models import Webhook


class WebhookService:
    """Handle webhook notifications to external services"""
    
    TIMEOUT = 5.0  # 5 second timeout
    
    @staticmethod
    async def trigger_incident_webhook(
        org_id: str,
        incident_id: str,
        incident_title: str,
        severity: str,
        description: str,
        status: str,
        db: Session
    ):
        """Trigger webhooks for incident creation/update"""
        webhooks = db.query(Webhook).filter(
            Webhook.org_id == org_id,
            Webhook.is_active == True
        ).all()
        
        for webhook in webhooks:
            if "incident" in webhook.events or "all" in webhook.events:
                payload = {
                    "event": "incident.created",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "incident_id": str(incident_id),
                        "title": incident_title,
                        "severity": severity,
                        "description": description,
                        "status": status,
                        "dashboard_url": f"https://cybersecurity-tracker.vercel.app/incidents?id={incident_id}"
                    }
                }
                
                # Send to appropriate handler based on URL
                asyncio.create_task(
                    WebhookService._send_webhook(webhook.url, payload)
                )
    
    @staticmethod
    async def trigger_vulnerability_webhook(
        org_id: str,
        vulnerability_id: str,
        cve_id: str,
        title: str,
        severity: str,
        cvss_score: float,
        affected_systems: List[str],
        db: Session
    ):
        """Trigger webhooks for vulnerability discovery"""
        webhooks = db.query(Webhook).filter(
            Webhook.org_id == org_id,
            Webhook.is_active == True
        ).all()
        
        for webhook in webhooks:
            if "vulnerability" in webhook.events or "all" in webhook.events:
                payload = {
                    "event": "vulnerability.discovered",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "vulnerability_id": str(vulnerability_id),
                        "cve_id": cve_id,
                        "title": title,
                        "severity": severity,
                        "cvss_score": float(cvss_score),
                        "affected_systems": affected_systems,
                        "dashboard_url": f"https://cybersecurity-tracker.vercel.app/vulnerabilities?id={vulnerability_id}"
                    }
                }
                
                asyncio.create_task(
                    WebhookService._send_webhook(webhook.url, payload)
                )
    
    @staticmethod
    async def _send_webhook(url: str, payload: Dict) -> bool:
        """Send webhook payload to URL"""
        try:
            async with httpx.AsyncClient(timeout=WebhookService.TIMEOUT) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    print(f"✅ Webhook sent to {url}")
                    return True
                else:
                    print(f"⚠️ Webhook failed for {url}: {response.status_code}")
                    return False
        
        except asyncio.TimeoutError:
            print(f"⏱️ Webhook timeout for {url}")
            return False
        except Exception as e:
            print(f"❌ Webhook error for {url}: {str(e)}")
            return False


class SlackIntegration:
    """Integration for Slack notifications"""
    
    @staticmethod
    def get_incident_message(
        incident_title: str,
        severity: str,
        description: str,
        incident_id: str
    ) -> Dict:
        """Format incident as Slack message"""
        severity_color = {
            "CRITICAL": "#d32f2f",
            "HIGH": "#ff6f00",
            "MEDIUM": "#fbc02d",
            "LOW": "#388e3c"
        }.get(severity, "#666666")
        
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🚨 *New Security Incident* ({severity})"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Title:*\n{incident_title}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{severity}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{description[:200]}..."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View in Dashboard"
                            },
                            "url": f"https://cybersecurity-tracker.vercel.app/incidents?id={incident_id}",
                            "style": "danger"
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_vulnerability_message(
        cve_id: str,
        title: str,
        severity: str,
        cvss_score: float,
        affected_systems: List[str],
        vulnerability_id: str
    ) -> Dict:
        """Format vulnerability as Slack message"""
        systems = ", ".join(affected_systems[:3])
        if len(affected_systems) > 3:
            systems += f" +{len(affected_systems) - 3} more"
        
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ *New Vulnerability Alert* ({severity})"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*CVE ID:*\n{cve_id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*CVSS Score:*\n{cvss_score}/10.0"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Title:*\n{title}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Affected Systems:*\n{systems}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Details"
                            },
                            "url": f"https://cybersecurity-tracker.vercel.app/vulnerabilities?id={vulnerability_id}",
                            "style": "danger"
                        }
                    ]
                }
            ]
        }


class TeamsIntegration:
    """Integration for Microsoft Teams notifications"""
    
    @staticmethod
    def get_incident_message(
        incident_title: str,
        severity: str,
        description: str,
        incident_id: str
    ) -> Dict:
        """Format incident as Teams message"""
        severity_color = {
            "CRITICAL": "FF0000",
            "HIGH": "FF6F00",
            "MEDIUM": "FBC02D",
            "LOW": "388E3C"
        }.get(severity, "666666")
        
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"New {severity} Incident: {incident_title}",
            "themeColor": severity_color,
            "sections": [
                {
                    "activityTitle": f"🚨 New Security Incident ({severity})",
                    "activitySubtitle": incident_title,
                    "facts": [
                        {
                            "name": "Severity:",
                            "value": severity
                        },
                        {
                            "name": "Description:",
                            "value": description[:200]
                        }
                    ],
                    "potentialAction": [
                        {
                            "name": "View Incident",
                            "targets": [
                                {
                                    "os": "default",
                                    "uri": f"https://cybersecurity-tracker.vercel.app/incidents?id={incident_id}"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_vulnerability_message(
        cve_id: str,
        title: str,
        severity: str,
        cvss_score: float,
        affected_systems: List[str],
        vulnerability_id: str
    ) -> Dict:
        """Format vulnerability as Teams message"""
        systems = ", ".join(affected_systems[:3])
        if len(affected_systems) > 3:
            systems += f" +{len(affected_systems) - 3} more"
        
        severity_color = {
            "CRITICAL": "FF0000",
            "HIGH": "FF6F00",
            "MEDIUM": "FBC02D",
            "LOW": "388E3C"
        }.get(severity, "666666")
        
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Vulnerability Alert: {cve_id}",
            "themeColor": severity_color,
            "sections": [
                {
                    "activityTitle": f"⚠️ New Vulnerability Alert ({severity})",
                    "activitySubtitle": cve_id,
                    "facts": [
                        {
                            "name": "Title:",
                            "value": title
                        },
                        {
                            "name": "CVSS Score:",
                            "value": f"{cvss_score}/10.0"
                        },
                        {
                            "name": "Affected Systems:",
                            "value": systems
                        }
                    ],
                    "potentialAction": [
                        {
                            "name": "View Vulnerability",
                            "targets": [
                                {
                                    "os": "default",
                                    "uri": f"https://cybersecurity-tracker.vercel.app/vulnerabilities?id={vulnerability_id}"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
