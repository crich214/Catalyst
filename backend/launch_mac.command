#!/bin/bash

cd "$(dirname "$0")"

PORT=8000
URL="http://127.0.0.1:${PORT}"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt

open "$URL"
python -m uvicorn app.main:app --reload --port "$PORT"
