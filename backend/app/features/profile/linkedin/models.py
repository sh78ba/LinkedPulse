from dataclasses import dataclass, field
from typing import Any


@dataclass
class LinkedInRawResponse:
    """Holds raw HTTP response data fetched from LinkedIn endpoints."""

    status_code: int
    url: str
    json_data: dict[str, Any] | None = None
    html_content: str | None = None
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class LinkedInProfilePayload:
    """Container aggregating responses from LinkedIn endpoints for a single profile."""

    public_id: str
    profile_url: str
    dash_response: LinkedInRawResponse | None = None
    view_response: LinkedInRawResponse | None = None
    html_response: LinkedInRawResponse | None = None
