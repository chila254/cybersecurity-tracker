"""
DNS Log Service
Parses DNS logs and categorizes websites
"""

from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import DNSLog, SiteCategory
import logging

logger = logging.getLogger(__name__)

# Domain category database (in production, use a real category service)
DOMAIN_CATEGORIES = {
    # Social Media
    "facebook.com": "social",
    "twitter.com": "social",
    "instagram.com": "social",
    "linkedin.com": "social",
    "tiktok.com": "social",
    "snapchat.com": "social",
    "reddit.com": "social",
    "pinterest.com": "social",
    
    # Video Streaming
    "youtube.com": "streaming",
    "netflix.com": "streaming",
    "twitch.tv": "streaming",
    "hulu.com": "streaming",
    "disney.com": "streaming",
    "primevideo.com": "streaming",
    
    # Work/Productivity
    "github.com": "work",
    "gitlab.com": "work",
    "slack.com": "work",
    "microsoft.com": "work",
    "google.com": "work",
    "notion.so": "work",
    "atlassian.net": "work",
    "jira.com": "work",
    "confluence.com": "work",
    "zoom.us": "work",
    
    # News
    "bbc.com": "news",
    "cnn.com": "news",
    "reuters.com": "news",
    "apnews.com": "news",
    "nytimes.com": "news",
    "theguardian.com": "news",
    
    # Shopping
    "amazon.com": "shopping",
    "ebay.com": "shopping",
    "etsy.com": "shopping",
    "walmart.com": "shopping",
    "target.com": "shopping",
    
    # Known Malware/Phishing
    "malicious-domain.com": "malware",
    "phishing-site.com": "malware",
    
    # Adult Content
    "adult-site.com": "adult",
    
    # Gambling
    "bet365.com": "gambling",
    "pokerstars.com": "gambling",
    "casino.com": "gambling",
}

RISK_LEVELS = {
    "social": "low",
    "streaming": "medium",
    "work": "low",
    "news": "low",
    "shopping": "low",
    "malware": "high",
    "adult": "medium",
    "gambling": "high",
}


class DNSService:
    """Service for handling DNS logs and categorization"""
    
    @staticmethod
    def categorize_domain(domain: str) -> str:
        """Categorize a domain based on known categories"""
        domain_lower = domain.lower().strip()
        
        # Direct match
        if domain_lower in DOMAIN_CATEGORIES:
            return DOMAIN_CATEGORIES[domain_lower]
        
        # Check if domain is a subdomain of known domain
        for known_domain, category in DOMAIN_CATEGORIES.items():
            if domain_lower.endswith("." + known_domain) or domain_lower == known_domain:
                return category
        
        # Default category
        return "unknown"
    
    @staticmethod
    def get_risk_level(category: str) -> str:
        """Get risk level for a category"""
        return RISK_LEVELS.get(category, "low")
    
    @staticmethod
    async def add_dns_log(
        db: Session,
        org_id: UUID,
        mac_address: str,
        domain: str,
        device_id: Optional[UUID] = None,
        query_type: str = "A",
        response_code: str = "NOERROR",
        is_blocked: bool = False
    ) -> DNSLog:
        """Add a DNS log entry"""
        try:
            category = DNSService.categorize_domain(domain)
            
            dns_log = DNSLog(
                org_id=org_id,
                device_id=device_id,
                mac_address=mac_address,
                domain=domain,
                domain_category=category,
                query_type=query_type,
                response_code=response_code,
                is_blocked=is_blocked,
                timestamp=datetime.utcnow()
            )
            
            db.add(dns_log)
            db.commit()
            db.refresh(dns_log)
            
            return dns_log
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding DNS log: {str(e)}")
            raise
    
    @staticmethod
    def import_dns_logs(
        db: Session,
        org_id: UUID,
        logs: List[Dict]
    ) -> int:
        """Import multiple DNS logs from a list"""
        count = 0
        
        try:
            for log_entry in logs:
                category = DNSService.categorize_domain(log_entry.get("domain", ""))
                
                # Check if log already exists
                existing = db.query(DNSLog).filter(
                    and_(
                        DNSLog.org_id == org_id,
                        DNSLog.mac_address == log_entry.get("mac_address"),
                        DNSLog.domain == log_entry.get("domain"),
                        DNSLog.timestamp == log_entry.get("timestamp")
                    )
                ).first()
                
                if not existing:
                    dns_log = DNSLog(
                        org_id=org_id,
                        device_id=log_entry.get("device_id"),
                        mac_address=log_entry.get("mac_address"),
                        domain=log_entry.get("domain"),
                        domain_category=category,
                        query_type=log_entry.get("query_type", "A"),
                        response_code=log_entry.get("response_code", "NOERROR"),
                        is_blocked=log_entry.get("is_blocked", False),
                        timestamp=log_entry.get("timestamp", datetime.utcnow())
                    )
                    db.add(dns_log)
                    count += 1
            
            db.commit()
            logger.info(f"Imported {count} DNS logs for org {org_id}")
            return count
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error importing DNS logs: {str(e)}")
            return 0
    
    @staticmethod
    def get_user_dns_history(
        db: Session,
        org_id: UUID,
        mac_address: str,
        limit: int = 100
    ) -> List[DNSLog]:
        """Get DNS history for a specific user/device"""
        return db.query(DNSLog).filter(
            and_(
                DNSLog.org_id == org_id,
                DNSLog.mac_address == mac_address
            )
        ).order_by(DNSLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_blocked_queries(
        db: Session,
        org_id: UUID,
        limit: int = 100
    ) -> List[DNSLog]:
        """Get blocked DNS queries"""
        return db.query(DNSLog).filter(
            and_(
                DNSLog.org_id == org_id,
                DNSLog.is_blocked == True
            )
        ).order_by(DNSLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_top_domains(
        db: Session,
        org_id: UUID,
        limit: int = 10
    ) -> List[Dict]:
        """Get top domains accessed"""
        from sqlalchemy import func
        
        results = db.query(
            DNSLog.domain,
            func.count(DNSLog.id).label("count"),
            DNSLog.domain_category
        ).filter(
            DNSLog.org_id == org_id
        ).group_by(
            DNSLog.domain,
            DNSLog.domain_category
        ).order_by(
            func.count(DNSLog.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "domain": r[0],
                "count": r[1],
                "category": r[2]
            }
            for r in results
        ]
    
    @staticmethod
    def get_category_distribution(
        db: Session,
        org_id: UUID
    ) -> List[Dict]:
        """Get distribution of domains by category"""
        from sqlalchemy import func
        
        results = db.query(
            DNSLog.domain_category,
            func.count(DNSLog.id).label("count")
        ).filter(
            DNSLog.org_id == org_id
        ).group_by(
            DNSLog.domain_category
        ).order_by(
            func.count(DNSLog.id).desc()
        ).all()
        
        return [
            {
                "category": r[0],
                "count": r[1]
            }
            for r in results
        ]
    
    @staticmethod
    def get_high_risk_domains(
        db: Session,
        org_id: UUID,
        limit: int = 50
    ) -> List[DNSLog]:
        """Get high-risk domain queries"""
        high_risk_categories = ["malware", "adult", "gambling"]
        
        return db.query(DNSLog).filter(
            and_(
                DNSLog.org_id == org_id,
                DNSLog.domain_category.in_(high_risk_categories)
            )
        ).order_by(DNSLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def sync_categories(db: Session, org_id: UUID):
        """Sync domain categories to database"""
        try:
            for domain, category in DOMAIN_CATEGORIES.items():
                existing = db.query(SiteCategory).filter(
                    SiteCategory.domain == domain
                ).first()
                
                if not existing:
                    risk_level = RISK_LEVELS.get(category, "low")
                    site_category = SiteCategory(
                        domain=domain,
                        category=category,
                        risk_level=risk_level,
                        is_blocked=False
                    )
                    db.add(site_category)
            
            db.commit()
            logger.info(f"Synced {len(DOMAIN_CATEGORIES)} domain categories")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error syncing categories: {str(e)}")
