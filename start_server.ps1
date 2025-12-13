# PowerShell script to start VediSpeak server
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "venv_new\Scripts\Activate.ps1"
Write-Host "Starting VediSpeak server..." -ForegroundColor Green
python run.py