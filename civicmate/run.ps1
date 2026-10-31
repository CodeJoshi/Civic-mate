$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (!(Test-Path .venv)) { python -m venv .venv }
. .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
playwright install chromium
if (Test-Path backend/.env) { Get-Content backend/.env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1],$matches[2]) } } }
$api = Start-Process -PassThru -NoNewWindow python -ArgumentList '-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000'
try { streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501 }
finally { Stop-Process -Id $api.Id -ErrorAction SilentlyContinue }
