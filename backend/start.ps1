# PowerShell startup script for Todo App Backend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Todo App Backend (FastAPI)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".venv\Scripts\Activate.ps1"

# Verify we're in the venv
Write-Host "Using Python from: $(Get-Command python | Select-Object -ExpandProperty Source)" -ForegroundColor Gray
Write-Host ""

# Start uvicorn server
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
