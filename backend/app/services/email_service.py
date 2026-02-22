"""
Email notification service for sending alerts and notifications
Supports incident alerts, vulnerability alerts, and digest emails
"""

import os
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from jinja2 import Template
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """Handle email notifications"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@cybersecurity-tracker.com")
        self.enabled = bool(self.smtp_user and self.smtp_password)
    
    async def send_incident_alert(
        self, 
        recipient_email: str, 
        incident_title: str, 
        severity: str,
        description: str,
        created_at: datetime,
        incident_id: str
    ) -> bool:
        """Send new incident alert email"""
        if not self.enabled:
            print(f"[EMAIL] Email disabled. Would send: {recipient_email} - {incident_title}")
            return False
        
        subject = f"🚨 New {severity} Incident: {incident_title}"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                    <h1 style="color: #d32f2f;">New Incident Alert</h1>
                    <p>A new <strong style="color: #{self._severity_color(severity)}">{severity}</strong> security incident has been reported.</p>
                    
                    <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #{self._severity_color(severity)}; margin: 20px 0;">
                        <h2 style="margin-top: 0;">{incident_title}</h2>
                        <p><strong>Severity:</strong> {severity}</p>
                        <p><strong>Created:</strong> {created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                        <p><strong>Description:</strong></p>
                        <p>{description}</p>
                    </div>
                    
                    <a href="https://cybersecurity-tracker.vercel.app/incidents?id={incident_id}" 
                       style="display: inline-block; background-color: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                        View Incident
                    </a>
                    
                    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 12px;">
                        This is an automated notification. You can change your notification preferences in settings.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return await self._send_email(recipient_email, subject, html_body)
    
    async def send_vulnerability_alert(
        self,
        recipient_email: str,
        cve_id: str,
        title: str,
        severity: str,
        cvss_score: float,
        affected_systems: List[str],
        vulnerability_id: str
    ) -> bool:
        """Send critical vulnerability alert email"""
        if not self.enabled:
            print(f"[EMAIL] Email disabled. Would send: {recipient_email} - {cve_id}")
            return False
        
        subject = f"⚠️ Critical Vulnerability Found: {cve_id}"
        
        systems_list = ", ".join(affected_systems) if affected_systems else "Not specified"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                    <h1 style="color: #ff6f00;">Vulnerability Alert</h1>
                    <p>A critical vulnerability has been discovered in your organization.</p>
                    
                    <div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff6f00; margin: 20px 0;">
                        <h2 style="margin-top: 0; color: #e65100;">{cve_id}</h2>
                        <p><strong>Title:</strong> {title}</p>
                        <p><strong>Severity:</strong> <span style="color: #ff6f00; font-weight: bold;">{severity}</span></p>
                        <p><strong>CVSS Score:</strong> {cvss_score}/10.0</p>
                        <p><strong>Affected Systems:</strong> {systems_list}</p>
                    </div>
                    
                    <a href="https://cybersecurity-tracker.vercel.app/vulnerabilities?id={vulnerability_id}" 
                       style="display: inline-block; background-color: #ff6f00; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                        View Vulnerability Details
                    </a>
                    
                    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 12px;">
                        This is an automated notification. You can change your notification preferences in settings.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return await self._send_email(recipient_email, subject, html_body)
    
    async def send_incident_update(
        self,
        recipient_email: str,
        incident_title: str,
        old_status: str,
        new_status: str,
        updated_by: str,
        incident_id: str
    ) -> bool:
        """Send incident status update notification"""
        if not self.enabled:
            print(f"[EMAIL] Email disabled. Would send: {recipient_email} - {incident_title}")
            return False
        
        subject = f"📝 Incident Updated: {incident_title}"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                    <h1 style="color: #1976d2;">Incident Update</h1>
                    <p>An incident you're assigned to has been updated.</p>
                    
                    <div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
                        <h2 style="margin-top: 0;">{incident_title}</h2>
                        <p><strong>Updated By:</strong> {updated_by}</p>
                        <p><strong>Status Change:</strong> <span style="color: #d32f2f;">{old_status}</span> → <span style="color: #388e3c;">{new_status}</span></p>
                    </div>
                    
                    <a href="https://cybersecurity-tracker.vercel.app/incidents?id={incident_id}" 
                       style="display: inline-block; background-color: #1976d2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                        View Incident
                    </a>
                    
                    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 12px;">
                        This is an automated notification. You can change your notification preferences in settings.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return await self._send_email(recipient_email, subject, html_body)
    
    async def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Internal method to send email via SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            # Attach HTML
            part = MIMEText(html_body, "html")
            msg.attach(part)
            
            # Send via SMTP
            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(msg)
            
            print(f"✅ Email sent to {to_email}: {subject}")
            return True
        
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def _severity_color(severity: str) -> str:
        """Get hex color for severity level"""
        colors = {
            "CRITICAL": "d32f2f",  # Red
            "HIGH": "ff6f00",       # Orange
            "MEDIUM": "fbc02d",     # Yellow
            "LOW": "388e3c"         # Green
        }
        return colors.get(severity, "666666")


# Global instance
email_service = EmailService()
