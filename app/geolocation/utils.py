import ipaddress
from urllib.parse import urlparse


def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_url(url: str) -> bool:
    try:
        urlparse(url)
        return True
    except ValueError:
        return False
