@echo off
cd /d "%~dp0"

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

pause
