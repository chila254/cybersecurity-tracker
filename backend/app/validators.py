"""
Input validation utilities and custom validators
"""

from typing import Optional, List
import re


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_no_sql_injection(value: str) -> bool:
    """Basic SQL injection detection"""
    dangerous_patterns = [
        r"('\s*(OR|AND)\s*')",  # ' OR ' / ' AND '
        r"(--\s*$)",  # SQL comments
        r"(;\s*(DROP|DELETE|INSERT|UPDATE|SELECT))",  # Command chaining
        r"(\*|;|\||&|\$|\?)",  # Special shell chars
    ]
    
    value_lower = value.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_lower):
            return False
    return True


def validate_string_field(value: str, min_length: int = 1, max_length: int = 500) -> bool:
    """Validate string field length and content"""
    if not value or len(value) < min_length or len(value) > max_length:
        return False
    return validate_no_sql_injection(value)


def validate_cvss_score(score: float) -> bool:
    """Validate CVSS score (0-10)"""
    return 0 <= score <= 10


def validate_severity(severity: str) -> bool:
    """Validate severity level"""
    valid = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    return severity in valid


def validate_status(status: str) -> bool:
    """Validate incident/vulnerability status"""
    incident_statuses = ["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"]
    vuln_statuses = ["UNPATCHED", "PATCHED", "MITIGATED", "MONITORING"]
    return status in incident_statuses or status in vuln_statuses
