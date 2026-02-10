"""
Fingrid Open Data API client.
Handles HTTP requests, pagination, and common errors (missing key, network, rate limit).
"""
import time
from typing import Any, List
import urllib.request
import urllib.error
import json

from config import (
    API_BASE_URL,
    DEFAULT_PAGE_SIZE,
    REQUEST_DELAY_SECONDS,
    get_api_key,
)


class FingridAPIError(Exception):
    """Base exception for Fingrid API errors."""
    pass


class MissingAPIKeyError(FingridAPIError):
    """Raised when no API key is configured."""
    pass


class NetworkError(FingridAPIError):
    """Raised on connection or timeout errors."""
    pass


class RateLimitError(FingridAPIError):
    """Raised when API returns 429 Too Many Requests."""
    pass


class APIResponseError(FingridAPIError):
    """Raised when API returns an error status or invalid response."""
    def __init__(self, message: str, status_code=None):
        self.status_code = status_code
        super().__init__(message)


def _build_url(dataset_ids: List[str], start_time: str, end_time: str, page: int = 1) -> str:
    datasets_param = ",".join(dataset_ids)
    return (
        f"{API_BASE_URL}/data"
        f"?datasets={datasets_param}"
        f"&startTime={start_time}"
        f"&endTime={end_time}"
        f"&pageSize={DEFAULT_PAGE_SIZE}"
        f"&page={page}"
    )


def fetch_timeseries(
    dataset_ids: List[str],
    start_time: str,
    end_time: str,
) -> List[dict]:
    """
    Fetch time series data from Fingrid Open Data API for the given dataset IDs
    and time range. Handles pagination and rate limiting.

    Time format: ISO 8601, e.g. '2024-01-01T00:00' or '2024-01-01T00:00:00Z'.

    Raises:
        MissingAPIKeyError: If FINGRID_API_KEY is not set.
        NetworkError: On connection/timeout errors.
        RateLimitError: On HTTP 429.
        APIResponseError: On other HTTP errors or invalid JSON.
    """
    api_key = get_api_key()
    if not api_key:
        raise MissingAPIKeyError(
            "No API key found. Set the FINGRID_API_KEY (or FINGRID_OPENDATA_API_KEY) "
            "environment variable. Get a free key at https://data.fingrid.fi → Developer portal."
        )

    headers = {"x-api-key": api_key}
    all_data: List[dict] = []
    page = 1
    last_page = None

    while True:
        url = _build_url(dataset_ids, start_time, end_time, page)
        req = urllib.request.Request(url, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 429:
                    raise RateLimitError(
                        "Rate limit exceeded (10 requests/minute). Wait a minute and try again."
                    )
                if resp.status != 200:
                    raise APIResponseError(
                        f"API returned status {resp.status}",
                        status_code=resp.status,
                    )
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise RateLimitError(
                    "Rate limit exceeded (10 requests/minute). Wait a minute and try again."
                )
            msg = e.read().decode("utf-8") if e.fp else str(e)
            raise APIResponseError(
                f"API error: {e.code} - {msg}",
                status_code=e.code,
            )
        except urllib.error.URLError as e:
            raise NetworkError(
                f"Network error: {e.reason}. Check your connection and that "
                "https://data.fingrid.fi is reachable."
            )
        except TimeoutError:
            raise NetworkError("Request timed out. Try again later.")
        except OSError as e:
            raise NetworkError(f"Connection error: {e}")

        try:
            response = json.loads(body)
        except json.JSONDecodeError as e:
            raise APIResponseError(f"Invalid API response (not JSON): {e}")

        if not isinstance(response, dict):
            raise APIResponseError("Invalid API response structure.")
        data = response.get("data")
        if data is None:
            raise APIResponseError("API response missing 'data' field.")
        if not isinstance(data, list):
            raise APIResponseError("API 'data' field is not a list.")

        all_data.extend(data)

        pagination = response.get("pagination") or {}
        last_page = pagination.get("lastPage", 1)
        if page >= last_page:
            break
        page += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    return all_data
