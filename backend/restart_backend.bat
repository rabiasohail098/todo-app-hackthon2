@echo off
echo Stopping any running backend servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 2 /nobreak >nul

cd /d "%~dp0"

if not exist .env (
    echo ERROR: .env file not found!
    pause
    exit /b 1
)

echo Environment configuration:
findstr "OPENAI_API_KEY" .env
findstr "OPENAI_BASE_URL" .env
findstr "AI_MODEL" .env

echo.
echo Starting backend server...
echo ========================================
python -m uvicorn src.api.main:app --reload --port 8000 --host 0.0.0.0
pause
