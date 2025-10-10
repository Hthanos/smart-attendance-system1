"""
Validation utilities
"""

import re
from typing import Optional


class Validators:
    """Input validation functions"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (Kenya format)"""
        if not phone:
            return False
        
        # Remove spaces and special characters
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check Kenyan phone formats: +254..., 0..., 254...
        patterns = [
            r'^\+254\d{9}$',  # +254712345678
            r'^0\d{9}$',      # 0712345678
            r'^254\d{9}$'     # 254712345678
        ]
        
        return any(re.match(pattern, cleaned) for pattern in patterns)
    
    @staticmethod
    def validate_registration_number(reg_number: str) -> bool:
        """Validate registration number format"""
        if not reg_number:
            return False
        
        # Example: E028-01-1532/2022
        pattern = r'^[A-Z]\d{3}-\d{2}-\d{4}/\d{4}$'
        return re.match(pattern, reg_number) is not None
    
    @staticmethod
    def validate_course_code(course_code: str) -> bool:
        """Validate course code format"""
        if not course_code:
            return False
        
        # Example: EEE101, CSC201
        pattern = r'^[A-Z]{3}\d{3}$'
        return re.match(pattern, course_code) is not None
    
    @staticmethod
    def validate_not_empty(value: str, field_name: str = "Field") -> tuple[bool, Optional[str]]:
        """Validate that a field is not empty"""
        if not value or not value.strip():
            return False, f"{field_name} cannot be empty"
        return True, None
    
    @staticmethod
    def validate_positive_integer(value: int, field_name: str = "Value") -> tuple[bool, Optional[str]]:
        """Validate that a value is a positive integer"""
        try:
            val = int(value)
            if val <= 0:
                return False, f"{field_name} must be positive"
            return True, None
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid number"
