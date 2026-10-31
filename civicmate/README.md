# CivicMate — Civic Scheme Explainer & Local Form Assistant

A working Streamlit + FastAPI demo implementing the uploaded CivicMate specification. It summarizes sample scheme criteria in English, Hindi, Tamil, Telugu and Marathi; applies income checks in deterministic Python; prepares a local mock application form with Playwright; pauses for explicit approval; and generates a PNG receipt.

> **Safety and scope:** This project deliberately automates only `backend/sample_data/mock_portal.html`. It does not navigate to real government websites, submit real applications, process payments, or connect to identity/biometric databases. The final approval creates a local demo receipt only (`submitted` remains `false`). Sample policy content is illustrative and is not official legal or eligibility advice.

## Requirements

- Python 3.10+ (3.11 recommended)
- Internet access for installing packages and optional Gemini requests
- Chromium installed through Playwright

## Quick start

### macOS / Linux

```bash
chmod +x run.sh
./run.sh
```

### Windows PowerShell

```powershell
.\run.ps1
```

The startup script installs dependencies and Chromium, starts FastAPI on `http://127.0.0.1:8000`, and launches Streamlit on `http://127.0.0.1:8501`.

### Manual start

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
playwright install chromium
# terminal 1
uvicorn backend.app.main:app --reload --port 8000
# terminal 2
streamlit run frontend/app.py
```

## Optional Gemini setup

Copy `backend/.env.example` to `backend/.env` and set `GEMINI_API_KEY` to your own key. Never commit `.env`. With no key (default), CivicMate uses deterministic offline summaries. If Gemini is configured but unavailable, the service falls back to the offline sample summary and labels the response accordingly.

For local runs, environment variables in `backend/.env` are loaded by `run.sh` / `run.ps1`. When starting services manually, export the variables yourself or use your preferred dotenv loader.

## User journey

1. Choose a language and sample scheme, or upload a PDF/TXT under 10 MB.
2. Enter applicant name, annual income, state and category.
3. Analyze. FastAPI validates the profile and the Python income gate compares income against the extracted cap.
4. If eligible, launch local Playwright preparation. The agent fills the local HTML mock and pauses at `awaiting_approval`.
5. Inspect the screenshot. Approve to generate a local PNG receipt, or abort. Approval does not submit any real application.
6. Clear the session to remove in-memory state and associated screenshots.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API, Playwright package and Gemini configuration status |
| GET | `/api/schemes/sample` | Sample PMAY and PM-Kisan data |
| POST | `/api/summarize` | Multipart profile + optional PDF/TXT; returns 3 bullets and income decision |
| POST | `/api/execute-form` | Starts local mock form preparation; returns `awaiting_approval` |
| POST | `/api/execute-form/{session_id}/confirm` | Form field `approve=true/false`; creates receipt or aborts |
| GET | `/api/sessions/{session_id}` | Read current in-memory session |
| GET | `/api/receipts/{session_id}` | Download PNG receipt after approval |
| DELETE | `/api/sessions/{session_id}` | Purge session and screenshots |

Interactive API docs: `http://127.0.0.1:8000/docs`.

## Tests

From the project root:

```bash
pytest -q
```

The tests cover positive-income validation, deterministic income gating, Tamil offline summaries, health and sample-scheme endpoints, and invalid profile rejection. A full Playwright integration run additionally requires Chromium installed; exercise the UI flow to verify the screenshot and approval boundary.

## Project structure

```text
civicmate/
├── backend/
│   ├── app/                 # FastAPI, Pydantic models, AI and agent services
│   ├── sample_data/         # Scheme data and local mock portal
│   ├── tests/               # Backend tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/app.py          # Streamlit dashboard
├── run.sh
├── run.ps1
├── pytest.ini
└── README.md
```

## Design notes and limitations

- Sessions are held in a process-local dictionary and are lost on restart. This is intentional for the requested ephemeral demo storage; run a single backend worker.
- Upload size is capped at 10 MiB. PDFs are parsed with `pypdf`; scanned/image-only PDFs may need OCR, which is not included.
- Gemini output is schema-validated, but extracted criteria can still be incomplete or wrong. Always verify official scheme notices.
- The offline PMAY cap of ₹3,00,000 and the three sample bullets are fixture data from the supplied project brief, not a statement of current official PMAY rules. The PM-Kisan content is deliberately cautious and does not invent an income cap.
- The initial automation path is fixed to the local mock portal. No arbitrary URL, external portal selector, credentials, or final government submit button is accepted.
- The selector timeout is 5,000 ms and the interaction trace is bounded to 10 actions. Sensitive profile values are not written to application logs.
- `HEADLESS_MODE` controls whether the Playwright browser is headless. The Streamlit user cannot override this backend setting.
