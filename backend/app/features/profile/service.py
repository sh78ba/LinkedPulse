from app.core.logging import get_logger
from app.core.security import validate_and_sanitize_linkedin_url
from app.features.profile.linkedin.client import LinkedInClient
from app.features.profile.linkedin.parser import LinkedInParser
from app.features.profile.schemas import ProfileResponse
from app.utils.url import extract_vanity_name

logger = get_logger("profile_service")


class ProfileService:
    """Service layer orchestrating URL validation, LinkedIn direct HTTP fetching,
    and response parsing.
    """

    def __init__(
        self,
        linkedin_client: LinkedInClient | None = None,
        parser: LinkedInParser | None = None,
    ) -> None:
        self.client = linkedin_client or LinkedInClient()
        self.parser = parser or LinkedInParser()

    async def get_profile(self, profile_url: str) -> ProfileResponse:
        """Retrieves and normalizes profile data from a LinkedIn profile URL."""
        logger.info("profile_fetch_started", raw_url=profile_url)

        # 1. Validate URL and enforce SSRF Protection
        sanitized_url = validate_and_sanitize_linkedin_url(profile_url)

        # 2. Extract public vanity identifier
        public_id = extract_vanity_name(sanitized_url)

        # 3. Fetch raw payload from direct LinkedIn HTTP endpoints
        payload = await self.client.fetch_profile_payload(public_id)

        # 4. Parse payload into normalized response
        response = self.parser.parse(payload)

        logger.info("profile_fetch_completed", public_id=public_id)
        return response
