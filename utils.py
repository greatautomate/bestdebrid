import re
from typing import Optional

def is_valid_url(url: str) -> bool:
    """Enhanced URL validation"""
    if not url or not isinstance(url, str):
        return False

    # Basic URL pattern matching
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None

def is_valid_ip(ip: str) -> bool:
    """Enhanced IP address validation"""
    if not ip or not isinstance(ip, str):
        return False

    # IPv4 pattern
    ipv4_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )

    # IPv6 pattern (basic)
    ipv6_pattern = re.compile(
        r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    )

    return ipv4_pattern.match(ip) is not None or ipv6_pattern.match(ip) is not None

def format_file_size(size_str: str) -> str:
    """Format file size for better display"""
    if not size_str:
        return "N/A"

    # Common size abbreviations mapping
    size_mapping = {
        'B': 'B',
        'KB': 'KB', 'KiB': 'KB',
        'MB': 'MB', 'MiB': 'MB',
        'GB': 'GB', 'GiB': 'GB',
        'TB': 'TB', 'TiB': 'TB'
    }

    for old, new in size_mapping.items():
        if old in size_str:
            return size_str.replace(old, new)

    return size_str

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for display"""
    if not filename:
        return "N/A"

    # Remove or replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return sanitized[:100] + "..." if len(sanitized) > 100 else sanitized

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None
