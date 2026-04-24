# AutoMuteUs-Manual Build Script

# 0. 実行ポリシーの設定 (スクリプト実行を許可)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 1. 以前のビルド成果物を削除 (クリーンビルドのため)
# ファイルやフォルダがない場合でもエラーを出さずに進めます
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item AutoMuteUs-Manual.spec, AutoMuteUs-Manual-Portable.spec, AutoMuteUs-Manual-Standalone.spec -ErrorAction SilentlyContinue

# 2. 仮想環境の有効化
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "仮想環境が見つかりません。venvを作成してください。" -ForegroundColor Red
}

# 3. 必要なライブラリのインストール/更新
pip install discord.py Pillow pyinstaller

# 4. ポータブル版 (onedir) のビルド
# 起動爆速。フォルダごとZipにして配布する用
python -m PyInstaller --onedir --noconsole --name "AutoMuteUs-Manual-Portable" --icon="icon.ico" main.py

# 5. 単一EXE版 (onefile) のビルド
# 手軽さ重視。ファイル1つで持ち運びたい人用
python -m PyInstaller --onefile --noconsole --name "AutoMuteUs-Manual-Standalone" --icon="icon.ico" main.py

# 6. ポータブル版 (onedir/ログあり) のビルド
# 開発・デバッグ用。コンソールが表示される
python -m PyInstaller --onedir --console --name "AutoMuteUs-Manual-Portable-ConsoleLog" --icon="icon.ico" main.py

Write-Host "--------------------------------------------------"
Write-Host "ビルドが完了しました。dist フォルダを確認してください。" -ForegroundColor Green