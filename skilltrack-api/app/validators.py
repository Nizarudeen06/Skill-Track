"""Input validation utilities for SkillTrack."""
import re
from typing import Any


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_password(password: str) -> str:
    """
    Validate password strength.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        The password if valid

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")

    if len(password) > 128:
        raise ValidationError("Password must not exceed 128 characters")

    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")

    # Check for common patterns
    common_patterns = [
        r'password', r'12345', r'qwerty', r'admin', r'letmein',
        r'welcome', r'monkey', r'dragon', r'master', r'sunshine'
    ]
    password_lower = password.lower()
    for pattern in common_patterns:
        if pattern in password_lower:
            raise ValidationError(f"Password contains common pattern '{pattern}' and is not secure")

    return password


def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email to validate

    Returns:
        Normalized email (lowercase)

    Raises:
        ValidationError: If email is invalid
    """
    if not email or len(email) < 3:
        raise ValidationError("Email is too short")

    if len(email) > 200:
        raise ValidationError("Email is too long")

    # Basic email regex (not perfect, but catches most issues)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email format")

    return email.lower()


def validate_reg_no(reg_no: str | None) -> str | None:
    """
    Validate registration number format.

    Args:
        reg_no: Registration number to validate

    Returns:
        Cleaned registration number

    Raises:
        ValidationError: If format is invalid
    """
    if reg_no is None or reg_no.strip() == "":
        return None

    reg_no = reg_no.strip().upper()

    if len(reg_no) < 3:
        raise ValidationError("Registration number too short")

    if len(reg_no) > 30:
        raise ValidationError("Registration number too long")

    # Alphanumeric and hyphens only
    if not re.match(r'^[A-Z0-9-]+$', reg_no):
        raise ValidationError("Registration number can only contain letters, numbers, and hyphens")

    return reg_no


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing dangerous characters and trimming.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValidationError: If string is too long after sanitization
    """
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")

    # Remove null bytes and control characters
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')

    # Trim whitespace
    value = value.strip()

    # Check length
    if len(value) > max_length:
        raise ValidationError(f"Value too long (max {max_length} characters)")

    return value


def validate_positive_int(value: Any, field_name: str = "Value", min_value: int = 1) -> int:
    """
    Validate that a value is a positive integer.

    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        min_value: Minimum allowed value

    Returns:
        Integer value

    Raises:
        ValidationError: If value is not a valid positive integer
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a number")

    if int_value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")

    return int_value
