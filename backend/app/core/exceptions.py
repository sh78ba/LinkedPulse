class BaseAPIException(Exception):
    """Base exception for all application API errors."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class InvalidLinkedInURL(BaseAPIException):
    """Raised when an invalid or disallowed URL is provided."""

    def __init__(self, message: str = "Invalid LinkedIn profile URL provided.") -> None:
        super().__init__(code="INVALID_URL", message=message, status_code=400)


class SSRFProtectionError(BaseAPIException):
    """Raised when a request violates Server-Side Request Forgery protection."""

    def __init__(self, message: str = "Target URL is not permitted for security reasons.") -> None:
        super().__init__(code="SSRF_VIOLATION", message=message, status_code=403)


class LinkedInAuthenticationError(BaseAPIException):
    """Raised when LinkedIn authentication fails or session cookie is missing/expired."""

    def __init__(
        self,
        message: str = "LinkedIn session authentication failed or cookie expired.",
    ) -> None:
        super().__init__(code="AUTHENTICATION_FAILED", message=message, status_code=401)


class LinkedInRateLimitError(BaseAPIException):
    """Raised when LinkedIn rate limits or anti-bot challenge is encountered."""

    def __init__(
        self,
        message: str = "LinkedIn rate limit exceeded or access challenge encountered.",
    ) -> None:
        super().__init__(code="RATE_LIMIT_EXCEEDED", message=message, status_code=429)


class LinkedInProfileNotFound(BaseAPIException):
    """Raised when the requested profile is not found or is private."""

    def __init__(self, message: str = "Unable to retrieve the requested LinkedIn profile.") -> None:
        super().__init__(code="PROFILE_NOT_FOUND", message=message, status_code=404)


class LinkedInRequestError(BaseAPIException):
    """Raised when an HTTP error occurs while communicating with LinkedIn."""

    def __init__(
        self, message: str = "Failed to communicate with LinkedIn HTTP endpoints."
    ) -> None:
        super().__init__(code="LINKEDIN_REQUEST_FAILED", message=message, status_code=502)


class LinkedInResponseParseError(BaseAPIException):
    """Raised when parsing LinkedIn's HTTP response data fails."""

    def __init__(self, message: str = "Failed to parse profile data from response.") -> None:
        super().__init__(code="PARSE_ERROR", message=message, status_code=502)
