import httpx

from src.ingestion.exceptions import IngestionError, TransientFetchError, PermanentFetchError, AuthRefreshRequiredError


def parse_retry_after(header_value: str | None) -> float | None:
    if header_value is None:
        return None
    try:
        return max(0,float(header_value.strip()))
    except ValueError:
        return None

def classify_exception(exc: httpx.RequestError) -> IngestionError:
    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError)):
        return TransientFetchError(f"Network/timeout error: {exc}")
    else:
        return PermanentFetchError(f"Invalid request configuration {exc}")

def classify_response(response: httpx.Response) -> dict:
    if 200 <= response.status_code < 300:
        try:
            return response.json()
        except ValueError:
            raise TransientFetchError(f"Invalid JSON in {response.status_code} response")
    if response.status_code == 401:
        raise AuthRefreshRequiredError("Access token rejected (401)")
    if response.status_code == 429:
        retry_after = parse_retry_after(response.headers.get("Retry-After"))
        raise TransientFetchError("Rate limit exceeded (429)", retry_after=retry_after)
    if 500 <= response.status_code < 600:
        raise TransientFetchError(f"Upstream server error ({response.status_code})")
    if 400 <= response.status_code < 500:
        raise PermanentFetchError(f"Client error {response.status_code}: {response.text[:200]}")