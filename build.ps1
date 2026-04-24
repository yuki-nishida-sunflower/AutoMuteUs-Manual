# Copyright 2026 Yuki Nishida
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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