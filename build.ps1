# AutoMuteUs-Manual Build Script

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item *.spec -ErrorAction SilentlyContinue

$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    . $venvPath
} else {
    Write-Host "[Warning] venv not found. Using system Python." -ForegroundColor Yellow
}

pip install -r requirements.txt
pip install pyinstaller

python -m PyInstaller --onedir --noconsole --name "AutoMuteUs-Manual-Portable" --icon="icon.ico" main.py

python -m PyInstaller --onefile --noconsole --name "AutoMuteUs-Manual-Standalone" --icon="icon.ico" main.py

python -m PyInstaller --onedir --console --name "AutoMuteUs-Manual-Portable-ConsoleLog" --icon="icon.ico" main.py

Write-Host "--------------------------------------------------"
Write-Host "Build Complete! Check the 'dist' folder." -ForegroundColor Green