"""
Enhanced Domain Categorization Service
Uses external APIs and databases for comprehensive domain categorization
"""

import asyncio
import httpx
import json
import re
from typing import Optional, Dict, List
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class DomainCategorizer:
    """Enhanced domain categorization using multiple sources"""

    # Extended domain categories database
    ENHANCED_CATEGORIES = {
        # Social Media & Communication
        "facebook.com": "social",
        "twitter.com": "social",
        "instagram.com": "social",
        "linkedin.com": "social",
        "tiktok.com": "social",
        "snapchat.com": "social",
        "reddit.com": "social",
        "discord.com": "social",
        "telegram.org": "social",
        "whatsapp.com": "social",

        # Video Streaming
        "youtube.com": "streaming",
        "netflix.com": "streaming",
        "twitch.tv": "streaming",
        "hulu.com": "streaming",
        "disney.com": "streaming",
        "primevideo.com": "streaming",
        "hbomax.com": "streaming",
        "crunchyroll.com": "streaming",
        "tubitv.com": "streaming",

        # Work & Productivity
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
        "teams.microsoft.com": "work",
        "dropbox.com": "work",

        # News & Media
        "bbc.com": "news",
        "cnn.com": "news",
        "reuters.com": "news",
        "apnews.com": "news",
        "nytimes.com": "news",
        "theguardian.com": "news",
        "foxnews.com": "news",
        "washingtonpost.com": "news",
        "bloomberg.com": "news",

        # Shopping & Commerce
        "amazon.com": "shopping",
        "ebay.com": "shopping",
        "etsy.com": "shopping",
        "walmart.com": "shopping",
        "target.com": "shopping",
        "bestbuy.com": "shopping",
        "costco.com": "shopping",
        "aliexpress.com": "shopping",

        # Search Engines
        "google.com": "search",
        "bing.com": "search",
        "duckduckgo.com": "search",
        "yahoo.com": "search",

        # Gaming
        "steam.com": "gaming",
        "epicgames.com": "gaming",
        "riotgames.com": "gaming",
        "ea.com": "gaming",
        "ubisoft.com": "gaming",
        "minecraft.net": "gaming",

        # Adult Content
        "pornhub.com": "adult",
        "xvideos.com": "adult",
        "xhamster.com": "adult",
        "onlyfans.com": "adult",

        # Gambling
        "bet365.com": "gambling",
        "pokerstars.com": "gambling",
        "casino.com": "gambling",
        "draftkings.com": "gambling",
        "fanduel.com": "gambling",

        # Cloud Services
        "aws.amazon.com": "cloud",
        "cloud.google.com": "cloud",
        "azure.microsoft.com": "cloud",
        "cloudflare.com": "cloud",

        # Educational
        "coursera.org": "education",
        "udemy.com": "education",
        "khanacademy.org": "education",
        "edmodo.com": "education",

        # Health & Medical
        "webmd.com": "health",
        "mayoclinic.org": "health",
        "nih.gov": "health",
        "cdc.gov": "health",

        # Financial
        "paypal.com": "finance",
        "stripe.com": "finance",
        "bankofamerica.com": "finance",
        "chase.com": "finance",
        "robinhood.com": "finance",

        # Government
        "gov.uk": "government",
        "gov.us": "government",
        "europa.eu": "government",

        # File Sharing
        "mega.nz": "file_sharing",
        "mediafire.com": "file_sharing",
        "4shared.com": "file_sharing",

        # Torrent
        "thepiratebay.org": "torrent",
        "1337x.to": "torrent",
        "rarbg.to": "torrent",
    }

    RISK_LEVELS = {
        "social": "low",
        "streaming": "medium",
        "work": "low",
        "news": "low",
        "shopping": "low",
        "search": "low",
        "gaming": "medium",
        "cloud": "low",
        "education": "low",
        "health": "low",
        "finance": "low",
        "government": "low",
        "file_sharing": "medium",
        "adult": "high",
        "gambling": "high",
        "torrent": "high",
        "malware": "high",
        "phishing": "high",
        "unknown": "medium"
    }

    @staticmethod
    def categorize_domain(domain: str) -> str:
        """
        Categorize a domain using enhanced database and pattern matching
        """
        if not domain:
            return "unknown"

        domain = domain.lower().strip()
        domain = domain.replace("www.", "")  # Remove www prefix

        # Direct match
        if domain in DomainCategorizer.ENHANCED_CATEGORIES:
            return DomainCategorizer.ENHANCED_CATEGORIES[domain]

        # Subdomain match (check if it's a subdomain of known domain)
        for known_domain, category in DomainCategorizer.ENHANCED_CATEGORIES.items():
            if domain.endswith("." + known_domain) or domain == known_domain:
                return category

        # Pattern-based categorization
        return DomainCategorizer._categorize_by_pattern(domain)

    @staticmethod
    def _categorize_by_pattern(domain: str) -> str:
        """
        Categorize domain based on patterns and keywords
        """
        # Social media patterns
        if any(keyword in domain for keyword in ['social', 'chat', 'message', 'connect']):
            return "social"

        # Streaming patterns
        if any(keyword in domain for keyword in ['stream', 'video', 'watch', 'play']):
            return "streaming"

        # Adult content patterns (be careful with false positives)
        adult_keywords = ['porn', 'sex', 'adult', 'xxx', 'nsfw']
        if any(keyword in domain for keyword in adult_keywords):
            return "adult"

        # Gambling patterns
        gambling_keywords = ['bet', 'casino', 'poker', 'lottery', 'gambling']
        if any(keyword in domain for keyword in gambling_keywords):
            return "gambling"

        # Work/productivity patterns
        work_keywords = ['office', 'docs', 'drive', 'workspace', 'project']
        if any(keyword in domain for keyword in work_keywords):
            return "work"

        # Shopping patterns
        shop_keywords = ['shop', 'store', 'buy', 'cart', 'checkout', 'market']
        if any(keyword in domain for keyword in shop_keywords):
            return "shopping"

        # News patterns
        news_keywords = ['news', 'times', 'post', 'journal', 'herald']
        if any(keyword in domain for keyword in news_keywords):
            return "news"

        # Government patterns
        if '.gov' in domain or 'government' in domain:
            return "government"

        # Educational patterns
        edu_keywords = ['edu', 'university', 'college', 'school', 'learn']
        if any(keyword in domain for keyword in edu_keywords):
            return "education"

        # Health patterns
        health_keywords = ['health', 'medical', 'clinic', 'hospital', 'doctor']
        if any(keyword in domain for keyword in health_keywords):
            return "health"

        # Financial patterns
        finance_keywords = ['bank', 'finance', 'credit', 'loan', 'invest']
        if any(keyword in domain for keyword in finance_keywords):
            return "finance"

        return "unknown"

    @staticmethod
    def get_risk_level(category: str) -> str:
        """Get risk level for a category"""
        return DomainCategorizer.RISK_LEVELS.get(category, "medium")

    @staticmethod
    async def categorize_domains_batch(domains: List[str]) -> Dict[str, str]:
        """
        Categorize multiple domains efficiently
        """
        results = {}
        for domain in domains:
            results[domain] = DomainCategorizer.categorize_domain(domain)
        return results

    @staticmethod
    async def get_domain_info(domain: str) -> Dict:
        """
        Get comprehensive information about a domain
        """
        try:
            category = DomainCategorizer.categorize_domain(domain)
            risk_level = DomainCategorizer.get_risk_level(category)

            # Try to get additional info from APIs (if available)
            # This is a placeholder for future API integrations
            additional_info = await DomainCategorizer._get_additional_domain_info(domain)

            return {
                "domain": domain,
                "category": category,
                "risk_level": risk_level,
                "additional_info": additional_info
            }

        except Exception as e:
            logger.error(f"Error getting domain info for {domain}: {str(e)}")
            return {
                "domain": domain,
                "category": "unknown",
                "risk_level": "medium",
                "error": str(e)
            }

    @staticmethod
    async def _get_additional_domain_info(domain: str) -> Dict:
        """
        Get additional information about domain from external sources
        This is a placeholder for future API integrations
        """
        # Placeholder for future implementations:
        # - WHOIS lookup
        # - Domain reputation APIs
        # - Certificate transparency logs
        # - Passive DNS data

        return {
            "reputation_score": None,
            "first_seen": None,
            "last_seen": None,
            "malicious_reports": 0
        }

    @staticmethod
    def is_suspicious_domain(domain: str) -> bool:
        """
        Check if domain exhibits suspicious characteristics
        """
        if not domain:
            return False

        domain = domain.lower()

        # Check for suspicious patterns
        suspicious_patterns = [
            r'\d{8,}',  # Long numbers (common in DGA)
            r'[a-zA-Z0-9]{20,}',  # Very long domains
            r'[-_]{3,}',  # Multiple hyphens/underscores
            r'\.tk$',  # Free TLD often used for malware
            r'\.ml$',
            r'\.ga$',
            r'\.cf$',
            r'hash\.',  # Hash-like domains
            r'md5\.',
            r'sha1\.',
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, domain):
                return True

        return False

    @staticmethod
    def extract_root_domain(domain: str) -> str:
        """
        Extract the root domain from a full domain
        """
        try:
            parsed = urlparse(f"http://{domain}")
            domain_parts = parsed.netloc.split('.')

            # Handle different TLD lengths
            if len(domain_parts) >= 2:
                if domain_parts[-1] in ['com', 'org', 'net', 'edu', 'gov', 'mil', 'info']:
                    return '.'.join(domain_parts[-2:])
                else:
                    return '.'.join(domain_parts[-2:])

            return domain

        except Exception:
            return domain
