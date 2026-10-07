$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Mouse Mouse.py

Write-Host ""
Write-Host "Build complete: dist\\Mouse.exe" -ForegroundColor Green
