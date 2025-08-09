
"""
Email notification service for ESG alerts and updates.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

try:
    from config import settings
except ImportError:
    from app.core.config import settings

class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.username = os.getenv('SMTP_USERNAME')
        self.password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.username)
        self.enabled = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.username and self.password and self.enabled)
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: str = None):
        """Send an email asynchronously."""
        if not self.is_configured():
            print("Email service not configured, skipping email send")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_esg_score_notification(self, user_email: str, user_name: str, score_data: Dict[str, Any]):
        """Send ESG score improvement notification."""
        subject = f"Your ESG Score Update - {score_data.get('overall_score', 0)}/100"
        
        body = f"""
Hello {user_name},

Your ESG assessment has been completed! Here are your results:

Overall Score: {score_data.get('overall_score', 0)}/100
Badge: {score_data.get('badge', 'N/A')}

Category Breakdown:
- Environmental: {score_data.get('category_scores', {}).get('environmental', 'N/A')}
- Social: {score_data.get('category_scores', {}).get('social', 'N/A')}
- Governance: {score_data.get('category_scores', {}).get('governance', 'N/A')}

Improvement Suggestions:
"""
        
        suggestions = score_data.get('improvement_suggestions', [])
        for i, suggestion in enumerate(suggestions, 1):
            body += f"{i}. {suggestion}\n"
        
        body += f"""

Keep up the great work on your sustainability journey!

Best regards,
ESG Compliance Tracker Team
"""
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #059669;">ESG Score Update</h2>
    
    <p>Hello {user_name},</p>
    
    <p>Your ESG assessment has been completed! Here are your results:</p>
    
    <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="margin: 0; color: #0369a1;">Overall Score: {score_data.get('overall_score', 0)}/100</h3>
        <p style="margin: 10px 0; font-size: 18px;"><strong>Badge: {score_data.get('badge', 'N/A')}</strong></p>
    </div>
    
    <h3>Category Breakdown:</h3>
    <ul>
        <li><strong>Environmental:</strong> {score_data.get('category_scores', {}).get('environmental', 'N/A')}</li>
        <li><strong>Social:</strong> {score_data.get('category_scores', {}).get('social', 'N/A')}</li>
        <li><strong>Governance:</strong> {score_data.get('category_scores', {}).get('governance', 'N/A')}</li>
    </ul>
    
    <h3>Improvement Suggestions:</h3>
    <ol>
"""
        
        for suggestion in suggestions:
            html_body += f"<li>{suggestion}</li>"
        
        html_body += """
    </ol>
    
    <p>Keep up the great work on your sustainability journey!</p>
    
    <p style="color: #6b7280;">
        Best regards,<br>
        ESG Compliance Tracker Team
    </p>
</body>
</html>
"""
        
        await self.send_email(user_email, subject, body, html_body)
    
    async def send_compliance_alert(self, user_email: str, user_name: str, alert_data: Dict[str, Any]):
        """Send compliance deadline alert."""
        subject = f"ESG Compliance Alert: {alert_data.get('title', 'Important Update')}"
        
        body = f"""
Hello {user_name},

You have a new ESG compliance alert:

Title: {alert_data.get('title', '')}
Category: {alert_data.get('category', '')}
Severity: {alert_data.get('severity', '')}

Description:
{alert_data.get('description', '')}

Please log into your ESG dashboard to review this alert and take necessary action.

Best regards,
ESG Compliance Tracker Team
"""
        
        # Determine severity color
        severity_colors = {
            'low': '#10b981',
            'medium': '#f59e0b', 
            'high': '#ef4444',
            'critical': '#dc2626'
        }
        severity_color = severity_colors.get(alert_data.get('severity', '').lower(), '#6b7280')
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #dc2626;">ESG Compliance Alert</h2>
    
    <p>Hello {user_name},</p>
    
    <div style="background-color: #fef2f2; border-left: 4px solid {severity_color}; padding: 20px; margin: 20px 0;">
        <h3 style="margin: 0; color: {severity_color};">{alert_data.get('title', '')}</h3>
        <p style="margin: 10px 0;"><strong>Category:</strong> {alert_data.get('category', '')}</p>
        <p style="margin: 10px 0;"><strong>Severity:</strong> 
            <span style="color: {severity_color}; font-weight: bold;">{alert_data.get('severity', '').upper()}</span>
        </p>
    </div>
    
    <h3>Description:</h3>
    <p>{alert_data.get('description', '')}</p>
    
    <p>Please log into your ESG dashboard to review this alert and take necessary action.</p>
    
    <p style="color: #6b7280;">
        Best regards,<br>
        ESG Compliance Tracker Team
    </p>
</body>
</html>
"""
        
        await self.send_email(user_email, subject, body, html_body)

# Global email service instance
email_service = EmailService()
