# AutoMuteUs-Manual 🚀

Among Us のボイスチャットを、ボタン一つで制御するための手動管理ツールです。
本家 Bot が停止した際のバックアップや、柔軟なミュート管理を目的として作成しました。

## ✨ 特徴
- **直感的な GUI**: メンバーを一覧表示し、生存/死亡をワンクリックで切り替え。
- **高速同期**: `asyncio.gather` による並列処理で、全員のステータスを瞬時に変更。
- **自動設定**: 初回起動時に設定ファイルのテンプレートを自動生成。

## 📦 インストールと実行
1. [Releases](リンクを貼る) から最新の `AutoMuteUs-Manual.exe` をダウンロードします。
2. 実行すると `local.config` が生成されます。
3. `local.config` に Discord Bot のトークンと各 ID を入力して保存します。
4. 再度実行し、「Config読み込み」→「Discord接続」の順に進めてください。

## 🛠️ 開発環境
- Python 3.12
- discord.py
- tkinter (GUI)
- PyInstaller (Build)