"""A transparent, deterministic multi-step policy workflow.

This is an orchestrated workflow, not an autonomous agent. It retrieves an
approved official page, analyzes its text, and returns source provenance.
"""
from urllib.parse import urlparse
from backend.app.government_data_service import fetch_official_source_text
from backend.app.ai_service import AIService

def analyze_official_policy(source_url: str, language: str = "English") -> dict:
    text = fetch_official_source_text(source_url)
    analysis = AIService().analyze_policy(text, language)
    parsed = urlparse(source_url)
    return {
        "analysis": analysis.model_dump(),
        "source": {
            "url": source_url,
            "domain": parsed.hostname,
            "retrieval_method": "live HTTPS fetch from approved government domain",
        },
        "disclaimer": (
            "Informational summary only. Verify current eligibility, deadlines, "
            "and application instructions with the linked official source."
        ),
    }
