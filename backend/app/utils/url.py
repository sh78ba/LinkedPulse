import re
from urllib.parse import urlparse


def extract_vanity_name(profile_url: str) -> str:
    """Extracts the vanity name / public identifier from a LinkedIn profile URL.

    Example:
        https://www.linkedin.com/in/williamhgates/ -> williamhgates
        https://linkedin.com/in/satyanadella -> satyanadella
    """
    parsed = urlparse(profile_url)
    path = parsed.path.strip("/")
    parts = path.split("/")

    if len(parts) >= 2 and parts[0] == "in":
        vanity = parts[1]
        # Remove any trailing query params or matrix params if present
        vanity = re.sub(r"[?#].*$", "", vanity)
        return vanity

    raise ValueError(f"Could not extract vanity name from profile URL: {profile_url}")


def clean_profile_url(url: str) -> str:
    """Cleans and standardizes a LinkedIn profile URL."""
    vanity = extract_vanity_name(url)
    return f"https://www.linkedin.com/in/{vanity}/"
