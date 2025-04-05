@echo off
if not exist myenv (
    python -m venv myenv
)

call myenv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
