import httpx

from app.core.config import settings
from app.core.exceptions import (
    LinkedInAuthenticationError,
    LinkedInProfileNotFound,
    LinkedInRateLimitError,
    LinkedInRequestError,
)
from app.core.logging import get_logger
from app.features.profile.linkedin.endpoints import LinkedInEndpoints
from app.features.profile.linkedin.models import LinkedInProfilePayload, LinkedInRawResponse
from app.utils.retry import execute_with_retry

logger = get_logger("linkedin_client")


class LinkedInClient:
    """Direct HTTP client for communicating with LinkedIn endpoints using httpx.AsyncClient."""

    def __init__(
        self,
        session_cookie: str | None = None,
        csrf_token: str | None = None,
        user_agent: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.session_cookie = session_cookie or settings.LINKEDIN_SESSION_COOKIE
        self.csrf_token = csrf_token or settings.LINKEDIN_CSRF_TOKEN
        self.user_agent = user_agent or settings.LINKEDIN_USER_AGENT
        self.timeout = timeout or settings.LINKEDIN_TIMEOUT_SECONDS
        self.max_retries = max_retries if max_retries is not None else settings.HTTP_MAX_RETRIES

        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Constructs request headers including CSRF token if present."""
        clean_token = self.csrf_token.strip('"') if self.csrf_token else ""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/vnd.linkedin.normalized+json+2.0, text/html, application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "x-restli-protocol-version": "2.0.0",
            "x-li-lang": "en_US",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        if clean_token:
            headers["csrf-token"] = clean_token
        return headers

    def _get_cookies(self) -> dict[str, str]:
        """Constructs session cookies for authentication."""
        cookies: dict[str, str] = {}
        if self.session_cookie:
            cookies["li_at"] = self.session_cookie
        if self.csrf_token:
            clean_token = self.csrf_token.strip('"')
            cookies["JSESSIONID"] = f'"{clean_token}"'
        return cookies

    async def get_async_client(self) -> httpx.AsyncClient:
        """Returns or initializes the shared httpx.AsyncClient instance."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self._get_headers(),
                cookies=self._get_cookies(),
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )
        return self._client

    async def close(self) -> None:
        """Closes the underlying HTTP client session."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def make_request(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> LinkedInRawResponse:
        """Executes a direct HTTP request to a LinkedIn endpoint."""
        client = await self.get_async_client()
        logger.info("linkedin_request_started", url=url)

        try:
            response = await execute_with_retry(
                client.get,
                url,
                headers=headers,
                params=params,
                max_retries=self.max_retries,
            )
        except httpx.TimeoutException as exc:
            logger.error("linkedin_request_timeout", url=url, error=str(exc))
            raise LinkedInRequestError("Request to LinkedIn timed out.") from exc
        except httpx.RequestError as exc:
            logger.error("linkedin_request_failed", url=url, error=str(exc))
            raise LinkedInRequestError("Failed to establish connection to LinkedIn.") from exc

        logger.info(
            "linkedin_request_completed",
            url=url,
            status_code=response.status_code,
        )

        if response.status_code in {401, 403}:
            if "checkpoint" in str(response.url) or "challenge" in str(response.url):
                raise LinkedInRateLimitError(
                    "LinkedIn access challenge or verification checkpoint encountered."
                )
            raise LinkedInAuthenticationError(
                "Invalid or expired LinkedIn session cookie. Update LINKEDIN_SESSION_COOKIE."
            )
        elif response.status_code == 429:
            raise LinkedInRateLimitError("LinkedIn HTTP 429 Rate limit exceeded.")
        elif response.status_code == 404:
            raise LinkedInProfileNotFound("Requested LinkedIn profile not found.")
        elif response.status_code >= 500:
            raise LinkedInRequestError(
                f"LinkedIn server returned HTTP status {response.status_code}."
            )

        json_data = None
        html_content = None
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type or "vnd.linkedin" in content_type:
            try:
                json_data = response.json()
            except Exception:
                html_content = response.text
        else:
            html_content = response.text
            # Try parsing HTML as JSON if possible
            if html_content.strip().startswith("{") and html_content.strip().endswith("}"):
                try:
                    import json

                    json_data = json.loads(html_content)
                except Exception:
                    pass

        return LinkedInRawResponse(
            status_code=response.status_code,
            url=str(response.url),
            json_data=json_data,
            html_content=html_content,
            headers=dict(response.headers),
        )

    async def get_profile(self, public_id: str) -> LinkedInRawResponse:
        """Fetches basic profile endpoint response for a given public ID."""
        url = LinkedInEndpoints.build_dash_url(public_id)
        return await self.make_request(url)

    async def get_experience(self, public_id: str) -> LinkedInRawResponse:
        """Fetches experience profile view response for a given public ID."""
        url = LinkedInEndpoints.build_profile_view_url(public_id)
        return await self.make_request(url)

    async def get_education(self, public_id: str) -> LinkedInRawResponse:
        """Fetches education data response for a given public ID."""
        url = LinkedInEndpoints.build_profile_view_url(public_id)
        return await self.make_request(url)

    async def get_skills(self, public_id: str) -> LinkedInRawResponse:
        """Fetches skills data response for a given public ID."""
        url = LinkedInEndpoints.build_profile_view_url(public_id)
        return await self.make_request(url)

    async def get_certifications(self, public_id: str) -> LinkedInRawResponse:
        """Fetches certifications response for a given public ID."""
        url = LinkedInEndpoints.build_profile_view_url(public_id)
        return await self.make_request(url)

    async def get_languages(self, public_id: str) -> LinkedInRawResponse:
        """Fetches languages response for a given public ID."""
        url = LinkedInEndpoints.build_profile_view_url(public_id)
        return await self.make_request(url)

    async def fetch_profile_payload(self, public_id: str) -> LinkedInProfilePayload:
        """Orchestrates fetching profile raw payloads across direct LinkedIn endpoints."""
        dash_res = None
        view_res = None
        html_res = None

        # Primary: Dash / Voyager REST Endpoint
        try:
            dash_res = await self.get_profile(public_id)
        except (LinkedInRequestError, LinkedInProfileNotFound) as exc:
            logger.warning(
                "voyager_dash_fetch_failed_trying_fallbacks", public_id=public_id, error=str(exc)
            )

        # Secondary: Profile View API Endpoint
        try:
            view_res = await self.get_experience(public_id)
        except (LinkedInRequestError, LinkedInProfileNotFound) as exc:
            logger.warning("voyager_view_fetch_failed", public_id=public_id, error=str(exc))

        # Fallback: HTML Endpoint
        try:
            html_url = LinkedInEndpoints.build_html_url(public_id)
            html_res = await self.make_request(html_url)
        except (LinkedInRequestError, LinkedInProfileNotFound) as exc:
            logger.warning("html_fetch_failed", public_id=public_id, error=str(exc))

        # If all fetches failed or returned empty, raise profile not found
        if not dash_res and not view_res and not html_res:
            raise LinkedInProfileNotFound(f"Unable to retrieve profile data for '{public_id}'.")

        return LinkedInProfilePayload(
            public_id=public_id,
            profile_url=f"https://www.linkedin.com/in/{public_id}/",
            dash_response=dash_res,
            view_response=view_res,
            html_response=html_res,
        )
