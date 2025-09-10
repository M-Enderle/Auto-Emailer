@echo off
setlocal

REM Change to the directory of this script
cd /d "%~dp0"

REM Ensure Poetry is available
where poetry >nul 2>&1
if errorlevel 1 (
  echo Poetry not found. Please install Poetry from https://python-poetry.org/
  exit /b 1
)

REM Install dependencies (idempotent)
poetry install -n

REM Run the API
poetry run uvicorn emailer.main:app --host 0.0.0.0 --port 8000

endlocal

