#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python -m venv .venv; fi
source .venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium
set -a; [ -f backend/.env ] && source backend/.env; set +a
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT
streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501
