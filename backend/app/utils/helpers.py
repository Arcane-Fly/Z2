"""
Helper utility functions for the Z2 backend.
"""

import os
import re
from datetime import datetime
from typing import Any, Optional


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length, adding suffix if truncated.
    
    Args:
        text: The string to truncate
        max_length: Maximum length of the result (excluding suffix)
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string with suffix if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
        
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
        
    return f"{size:.1f} {units[unit_index]}"


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    if not email:
        return False
        
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def calculate_time_diff(start: datetime, end: datetime) -> float:
    """
    Calculate time difference in seconds.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Time difference in seconds
    """
    diff = end - start
    return diff.total_seconds()


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get configuration value from environment variables.
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    return os.getenv(key, default)


def parse_bool_config(value: str) -> bool:
    """
    Parse string value to boolean.
    
    Args:
        value: String value to parse
        
    Returns:
        Boolean value
    """
    if not value:
        return False
        
    return value.lower() in ("true", "1", "yes", "on", "enabled")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    # Ensure it's not empty
    if not sanitized:
        sanitized = "unnamed_file"
    return sanitized


def generate_uuid_str() -> str:
    """
    Generate a UUID string.
    
    Returns:
        UUID string
    """
    import uuid
    return str(uuid.uuid4())


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    Mask sensitive data, showing only first and last few characters.
    
    Args:
        data: Sensitive data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked string
    """
    if len(data) <= visible_chars * 2:
        return mask_char * len(data)
        
    start = data[:visible_chars]
    end = data[-visible_chars:]
    middle = mask_char * (len(data) - visible_chars * 2)
    
    return f"{start}{middle}{end}"


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def deep_merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
            
    return result


def retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        backoff_factor: Backoff multiplier
        
    Returns:
        Function result or raises last exception
    """
    import time
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)
            else:
                raise last_exception