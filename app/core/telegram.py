import re
from typing import Optional

def validate_telegram_id(telegram_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate a Telegram ID or username.
    
    Args:
        telegram_id: The Telegram ID or username to validate
        
    Returns:
        tuple: (is_valid, error_message)
        - is_valid: bool indicating if the ID is valid
        - error_message: str with error description if invalid, None if valid
    """
    # Check if it's a username (starts with @)
    if telegram_id.startswith('@'):
        # Username must be 5-32 characters long and contain only letters, numbers, and underscores
        if not re.match(r'^@[a-zA-Z0-9_]{5,32}$', telegram_id):
            return False, "Invalid Telegram username format. Must be 5-32 characters long and contain only letters, numbers, and underscores."
        return True, None
    
    # Check if it's a numeric ID
    try:
        user_id = int(telegram_id)
        if user_id <= 0:
            return False, "Telegram ID must be a positive number."
        return True, None
    except ValueError:
        return False, "Telegram ID must be either a username starting with @ or a numeric ID." 