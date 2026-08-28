import asyncio

import httpx

from app.core.logging import get_logger

logger = get_logger("retry_util")


async def execute_with_retry(
    func,
    *args,
    max_retries: int = 2,
    base_delay: float = 1.0,
    **kwargs,
) -> httpx.Response:
    """Executes an async HTTP request function with exponential backoff for transient failures."""
    attempt = 0
    while True:
        try:
            attempt += 1
            response: httpx.Response = await func(*args, **kwargs)
            # Re-try on transient server errors (502, 503, 504)
            if response.status_code in {502, 503, 504} and attempt <= max_retries:
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning(
                    "transient_http_error_retrying",
                    status_code=response.status_code,
                    attempt=attempt,
                    max_retries=max_retries,
                    delay_seconds=delay,
                )
                await asyncio.sleep(delay)
                continue
            return response
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            if attempt <= max_retries:
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning(
                    "http_network_exception_retrying",
                    error=str(exc),
                    attempt=attempt,
                    max_retries=max_retries,
                    delay_seconds=delay,
                )
                await asyncio.sleep(delay)
                continue
            raise
