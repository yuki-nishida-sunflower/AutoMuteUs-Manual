# AutoMuteUs-Manual

Among Usプレイ中のDiscordミュート状態を、手動で一括制御するためのツールです。
AutoMuteUsが動作しない時のバックアップとして機能します。

## 主な機能
- 参加者の生存/死亡状態をUI上で切り替え
- 「待機」「タスク」「会議」の3フェーズに合わせた一括ミュート制御

## セットアップ
1. `pip install -r requirements.txt`
2. `.env` ファイルを作成し、Bot Token等を設定
3. `python main.py` で実行