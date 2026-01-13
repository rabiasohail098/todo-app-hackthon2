@echo off
echo ============================================================
echo Starting Todo App Backend (FastAPI)
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist .venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found!
    echo Please create it first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Verify Python location
echo Using Python from: %VIRTUAL_ENV%
echo.

REM Start uvicorn server
echo Starting FastAPI server on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
