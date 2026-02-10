"""
Configuration for the Fingrid Open Data application.
Loads API key from environment variable FINGRID_API_KEY.
"""
import os

# Fingrid Open Data API
API_BASE_URL = "https://data.fingrid.fi/api"
API_KEY_ENV_VAR = "FINGRID_API_KEY"
DEFAULT_PAGE_SIZE = 10000
# Rate limit: 10 requests per minute - use a small delay between paginated requests
REQUEST_DELAY_SECONDS = 6.5


def get_api_key():
    # Returns str or None
    """Return the API key from environment, or None if not set."""
    return os.environ.get(API_KEY_ENV_VAR) or os.environ.get("FINGRID_OPENDATA_API_KEY")
