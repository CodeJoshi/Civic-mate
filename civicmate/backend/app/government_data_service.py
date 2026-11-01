"""Live government-source retrieval for Civic Mate.

Data.gov.in resource IDs must be configured for a real, relevant dataset.
Records returned by this API are source data and must not automatically be
represented as verified welfare-scheme records.
"""
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://api.data.gov.in/resource"
DEFAULT_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
OFFICIAL_DOMAINS = (
    "india.gov.in", "myscheme.gov.in", "pib.gov.in",
    "egazette.gov.in", "data.gov.in",
)

class GovernmentDataError(RuntimeError):
    pass

def fetch_data_gov_in_records(
    resource_id: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[dict]:
    api_key = os.getenv("DATA_GOV_IN_API_KEY", "").strip()
    dataset_id = (resource_id or os.getenv("DATA_GOV_IN_RESOURCE_ID", "")).strip()
    if not api_key:
        raise GovernmentDataError("DATA_GOV_IN_API_KEY is not configured.")
    if not dataset_id:
        raise GovernmentDataError("DATA_GOV_IN_RESOURCE_ID is not configured.")
    if "/" in dataset_id or "\\" in dataset_id or ".." in dataset_id:
        raise ValueError("Invalid Data.gov.in resource ID.")
    if not 1 <= limit <= 1000 or offset < 0:
        raise ValueError("Use limit 1-1000 and a non-negative offset.")

    params = {"api-key": api_key, "format": "json", "limit": limit, "offset": offset}
    for key, value in (filters or {}).items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Filter names must be non-empty strings.")
        params[f"filters[{key}]"] = value

    try:
        response = requests.get(
            f"{BASE_URL}/{dataset_id}", params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise GovernmentDataError("Data.gov.in request failed; verify connectivity and API configuration.") from exc
    except ValueError as exc:
        raise GovernmentDataError("Data.gov.in returned invalid JSON.") from exc

    records = payload.get("records")
    if not isinstance(records, list):
        raise GovernmentDataError("Unexpected Data.gov.in response: 'records' is not a list.")
    return records

def fetch_official_source_text(source_url: str, allowed_domains=None) -> str:
    if not source_url:
        raise ValueError("An official source URL is required.")
    parsed = urlparse(source_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only credential-free HTTPS URLs are accepted.")

    domains = tuple(allowed_domains or OFFICIAL_DOMAINS)
    host = parsed.hostname.lower().rstrip(".")
    if not any(host == domain or host.endswith("." + domain) for domain in domains):
        raise ValueError("Source domain is not in Civic Mate's approved government-domain list.")

    try:
        response = requests.get(
            source_url, timeout=DEFAULT_TIMEOUT, allow_redirects=False,
            headers={"User-Agent": "CivicMate/1.0 policy-source-retrieval"},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GovernmentDataError("Could not retrieve the official government page.") from exc

    if "text/html" not in response.headers.get("Content-Type", "").lower():
        raise GovernmentDataError("The URL did not return HTML. Upload the PDF for document analysis.")

    soup = BeautifulSoup(response.text, "html.parser")
    for node in soup(["script", "style", "nav", "footer", "header"]):
        node.decompose()
    extracted = soup.get_text(separator="\n", strip=True)
    if not extracted:
        raise GovernmentDataError("No readable text was found on the official page.")
    return extracted
