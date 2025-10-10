"""
Email Notifier - Send email notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from config.settings import Settings

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications"""
    
    def __init__(self):
        """Initialize email notifier"""
        self.enabled = Settings.EMAIL_ENABLED
        self.smtp_server = Settings.SMTP_SERVER
        self.smtp_port = Settings.SMTP_PORT
        self.username = Settings.SMTP_USERNAME
        self.password = Settings.SMTP_PASSWORD
        self.from_email = Settings.EMAIL_FROM
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """Send email"""
        if not self.enabled:
            logger.warning("Email notifications disabled")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
