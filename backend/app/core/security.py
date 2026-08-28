import ipaddress
import socket
from urllib.parse import urlparse

from app.core.exceptions import InvalidLinkedInURL, SSRFProtectionError

ALLOWED_DOMAINS = {"linkedin.com", "www.linkedin.com", "mobile.linkedin.com"}


def is_private_ip(hostname: str) -> bool:
    """Checks if a hostname resolves to a private, loopback, or link-local IP address."""
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        # Not a direct IP literal, resolve DNS
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return True
        except socket.gaierror:
            # Cannot resolve hostname, reject for security
            return True
    return False


def validate_and_sanitize_linkedin_url(url: str) -> str:
    """Validates that a URL is a valid LinkedIn profile URL and protects against SSRF.

    Raises:
        InvalidLinkedInURL: If the URL format or domain is invalid.
        SSRFProtectionError: If the URL points to private/internal IPs or unallowed hosts.
    """
    if not url or not isinstance(url, str):
        raise InvalidLinkedInURL("URL must be a non-empty string.")

    cleaned_url = url.strip()

    if not (cleaned_url.startswith("http://") or cleaned_url.startswith("https://")):
        cleaned_url = "https://" + cleaned_url

    parsed = urlparse(cleaned_url)
    hostname = parsed.hostname

    if not hostname:
        raise InvalidLinkedInURL("Invalid URL: Hostname could not be parsed.")

    hostname_lower = hostname.lower()

    # Domain restriction
    if hostname_lower not in ALLOWED_DOMAINS and not hostname_lower.endswith(".linkedin.com"):
        raise InvalidLinkedInURL(
            f"Domain '{hostname}' is not allowed. Only LinkedIn profile URLs "
            "(e.g., https://www.linkedin.com/in/...) are accepted."
        )

    # SSRF Protection: Check for IP literals and internal address resolution
    if is_private_ip(hostname_lower):
        raise SSRFProtectionError(
            "Security error: Target address resolves to private or loopback IP range."
        )

    # Path validation: Must be a profile path e.g. /in/vanity-name
    path = parsed.path
    if not path or not path.startswith("/in/"):
        raise InvalidLinkedInURL(
            "Invalid LinkedIn profile URL path. Expected format: https://www.linkedin.com/in/<profile-id>/"
        )

    # Normalize to standard https URL
    normalized = f"https://www.linkedin.com{path}"
    if not normalized.endswith("/"):
        normalized += "/"

    return normalized
