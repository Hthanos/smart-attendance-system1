"""
SMS Notifier - Send SMS via Africa's Talking
"""

import logging
from typing import Optional

from config.settings import Settings

logger = logging.getLogger(__name__)


class SMSNotifier:
    """Send SMS notifications using Africa's Talking"""
    
    def __init__(self):
        """Initialize SMS notifier"""
        self.enabled = Settings.SMS_ENABLED
        
        if self.enabled:
            try:
                import africastalking
                
                africastalking.initialize(
                    Settings.AFRICASTALKING_USERNAME,
                    Settings.AFRICASTALKING_API_KEY
                )
                
                self.sms = africastalking.SMS
                logger.info("Africa's Talking SMS initialized")
                
            except ImportError:
                logger.error("africastalking module not installed")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize SMS: {str(e)}")
                self.enabled = False
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS to phone number"""
        if not self.enabled:
            logger.warning("SMS notifications disabled")
            return False
        
        try:
            response = self.sms.send(
                message,
                [phone_number],
                Settings.SMS_SENDER_ID
            )
            
            logger.info(f"SMS sent to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
