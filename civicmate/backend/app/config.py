import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SAMPLE_DIR = BASE_DIR / "sample_data"
RECEIPT_DIR = BASE_DIR / "receipts"
RECEIPT_DIR.mkdir(exist_ok=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() not in {"0", "false", "no"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_DOM_ACTIONS = 10
SELECTOR_TIMEOUT_MS = 5000
