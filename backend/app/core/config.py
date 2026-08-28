from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App Config
    APP_NAME: str = "LinkedIn Profile API"
    APP_ENV: str = Field(
        default="development", description="Environment mode: development, staging, production"
    )
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    HOST: str = Field(default="0.0.0.0", description="Bind host IP")
    PORT: int = Field(default=8000, description="Bind port")

    # LinkedIn Direct HTTP Client Config
    LINKEDIN_SESSION_COOKIE: str = Field(
        default="",
        description="Value of the 'li_at' cookie from an authorized LinkedIn session",
    )
    LINKEDIN_CSRF_TOKEN: str = Field(
        default="",
        description="Value of the 'JSESSIONID' cookie (e.g., 'ajax:1234567890123456789')",
    )
    LINKEDIN_USER_AGENT: str = Field(
        default=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        description="User-Agent string for direct HTTP requests to LinkedIn",
    )
    LINKEDIN_TIMEOUT_SECONDS: float = Field(
        default=15.0,
        description="HTTP request timeout in seconds",
    )
    HTTP_MAX_RETRIES: int = Field(
        default=2,
        description="Maximum HTTP retries for transient network errors",
    )


settings = Settings()
