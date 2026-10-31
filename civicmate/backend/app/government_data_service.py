# backend/services/government_data_service.py

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


load_dotenv()

DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY", "").strip()

DATA_GOV_IN_RESOURCE_ID = os.getenv(
    "DATA_GOV_IN_RESOURCE_ID", ""
).strip()

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

DATA_GOV_IN_BASE_URL = "https://api.data.gov.in/resource"


class GovernmentDataError(Exception):
    """Raised when a government data source cannot be retrieved."""


def fetch_data_gov_in_records(
    resource_id: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[dict]:
    """
    Fetch records from a configured Data.gov.in resource.

    Args:
        resource_id: Dataset resource ID.
        filters: Optional API filters supported by that resource.
        limit: Maximum number of records to request.
        offset: Pagination offset.

    Returns:
        A list of records returned by the government API.

    Note:
        These are source records, not automatically approved scheme records.
    """

    api_key = DATA_GOV_IN_API_KEY
    dataset_id = resource_id or DATA_GOV_IN_RESOURCE_ID

    if not api_key:
        raise GovernmentDataError(
            "DATA_GOV_IN_API_KEY is not configured in .env."
        )

    if not dataset_id:
        raise GovernmentDataError(
            "DATA_GOV_IN_RESOURCE_ID is not configured in .env."
        )

    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000.")

    if offset < 0:
        raise ValueError("offset cannot be negative.")

    # Resource IDs are identifiers, not arbitrary URLs.
    if "/" in dataset_id or "\\" in dataset_id or ".." in dataset_id:
        raise ValueError("Invalid Data.gov.in resource ID.")

    endpoint = f"{DATA_GOV_IN_BASE_URL}/{dataset_id}"

    params = {
        "api-key": api_key,
        "format": "json",
        "limit": limit,
        "offset": offset,
    }

    if filters:
        # Data.gov.in supports resource-specific filter parameters.
        # Confirm the filter syntax against the selected dataset.
        for key, value in filters.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Filter names must be non-empty strings.")

            params[f"filters[{key}]"] = value

    try:
        response = requests.get(
            endpoint,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        payload = response.json()

    except requests.RequestException as exc:
        raise GovernmentDataError(
            "Could not retrieve records from Data.gov.in. "
            "Check connectivity, the resource ID, and API access."
        ) from exc

    except ValueError as exc:
        raise GovernmentDataError(
            "Data.gov.in returned an invalid JSON response."
        ) from exc

    records = payload.get("records", [])

    if not isinstance(records, list):
        raise GovernmentDataError(
            "The government API returned an unexpected records format."
        )

    return records


def fetch_official_source_text(
    source_url: str,
    allowed_domains: Optional[List[str]] = None,
) -> str:
    """
    Fetch readable text from an approved official HTML page.

    This function deliberately does not crawl arbitrary URLs.
    Restrict source domains and review content before using it as evidence.

    PDF files should be uploaded as bytes and processed by ai_service.py.
    """

    if not source_url:
        raise ValueError("An official source URL is required.")

    parsed = urlparse(source_url)

    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Only HTTPS source URLs are accepted.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not accepted.")

    allowed_domains = allowed_domains or [
        "india.gov.in",
        "myscheme.gov.in",
        "pib.gov.in",
        "egazette.gov.in",
        "data.gov.in",
    ]

    hostname = parsed.hostname.lower().rstrip(".")

    if not any(
        hostname == domain or hostname.endswith("." + domain)
        for domain in allowed_domains
    ):
        raise ValueError(
            "This domain is not in the approved government source list."
        )

    try:
        response = requests.get(
            source_url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "CivicMate/1.0 (official-source retrieval)"
            },
            allow_redirects=False,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise GovernmentDataError(
            "Unable to retrieve the official government source."
        ) from exc

    content_type = response.headers.get("Content-Type", "").lower()

    if "text/html" not in content_type:
        raise GovernmentDataError(
            "The URL did not return an HTML page. "
            "For PDFs, upload the PDF and use analyze_policy()."
        )

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)

    if not text:
        raise GovernmentDataError(
            "No readable text was found on the official source page."
        )

    return text