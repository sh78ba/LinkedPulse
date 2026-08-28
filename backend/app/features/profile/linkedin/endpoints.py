"""LinkedIn API Endpoint Definitions & Documentation.

This module isolates all LinkedIn URL structures, HTTP methods, required headers,
and endpoint descriptions used by the reverse-engineered LinkedIn Client.
"""

from typing import Final


class LinkedInEndpoints:
    """Registry of verified LinkedIn endpoints and metadata."""

    BASE_URL: Final[str] = "https://www.linkedin.com"

    # Endpoint 1: Voyager Profile Dash API
    # Purpose: Fetches structured Voyager profile entity data.
    # Method: GET
    # Parameters: q=memberIdentity, memberIdentity={public_id}
    # Headers: csrf-token, x-restli-protocol-version: 2.0.0
    # Session: li_at cookie, JSESSIONID cookie
    # Response: JSON object with 'included' array of entities (Profile, Position, Education, Skill)
    # Data extracted: Name, Headline, Location, Summary/About, Experience, Education, Skills
    VOYAGER_PROFILE_DASH: Final[str] = "https://www.linkedin.com/voyager/api/identity/dash/profiles"

    # Endpoint 2: Voyager Profile View API
    # Purpose: Fetches legacy profile view payload for a vanity profile ID.
    # Method: GET
    # Headers: csrf-token, x-restli-protocol-version: 2.0.0
    # Session: li_at cookie, JSESSIONID cookie
    # Data extracted: Basic profile information, experiences, certification details
    VOYAGER_PROFILE_VIEW: Final[str] = (
        "https://www.linkedin.com/voyager/api/identity/profiles/{public_id}/profileView"
    )

    # Endpoint 3: Authenticated Profile HTML Page
    # Purpose: Fallback HTTP fetch of profile HTML containing embedded JSON-LD / code-tag state.
    # Method: GET
    # Session: li_at cookie
    # Data extracted: Profile avatar images, schema.org JSON-LD structured data,
    #                 basic profile attributes
    PROFILE_HTML: Final[str] = "https://www.linkedin.com/in/{public_id}/"

    @classmethod
    def build_dash_url(cls, public_id: str) -> str:
        return (
            f"{cls.VOYAGER_PROFILE_DASH}?q=memberIdentity&memberIdentity={public_id}"
            "&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-1"
        )

    @classmethod
    def build_profile_view_url(cls, public_id: str) -> str:
        return cls.VOYAGER_PROFILE_VIEW.format(public_id=public_id)

    @classmethod
    def build_html_url(cls, public_id: str) -> str:
        return cls.PROFILE_HTML.format(public_id=public_id)
