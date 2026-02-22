"""
Services package for business logic
Email, webhooks, integrations, notifications
"""

from app.services.email_service import email_service, EmailService
from app.services.webhook_service import WebhookService, SlackIntegration, TeamsIntegration

__all__ = [
    "email_service",
    "EmailService",
    "WebhookService",
    "SlackIntegration",
    "TeamsIntegration"
]
