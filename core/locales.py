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

from typing import Dict, Any

STRINGS: Dict[str, Dict[str, str]] = {
    "ja": {
        # --- UI Labels & Buttons ---
        "app_title": "AutoMuteUs-Manual",
        "btn_config_load": "① Config読み込み",
        "btn_discord_connect": "② Discord接続",
        "btn_discord_connecting": "接続中...",
        "btn_discord_connected": "② Discord接続完了",
        "btn_member_refresh": "メンバー更新",
        "frame_game_control": "Game Control",
        "status_unloaded": "🔴 未読込",
        "status_disconnected": "🔴 未接続",
        "status_config_ok": "🟢 Config OK",
        "status_connected": "🟢 接続OK: {bot_name}",
        "phase_waiting": "待機",
        "phase_task": "タスク",
        "phase_meeting": "会議",
        "info_startup": "local.configを編集して読み込んでください",
        "info_ready": "準備完了",
        "info_applying": "🔄 {phase} 適用中...",
        "info_done": "操作完了",
        
        # --- Dialogs (メッセージボックス) ---
        "dialog_created_title": "作成完了",
        "dialog_created_body": "{filename} を作成しました。設定後、再度押してください。",
        "dialog_token_error_title": "設定エラー",
        "dialog_token_error_body": "トークンを設定してください。",
        "dialog_conn_error_title": "接続エラー",
        "dialog_conn_error_body": "失敗: {error}",
        "dialog_vc_error_title": "エラー",
        "dialog_vc_error_body": "VCが見つかりません",
        "dialog_ready_title": "準備完了",
        "dialog_ready_body": "オンラインになりました",

        # --- Logs (コンソール出力) ---
        "log_phase_start": "\n--- [{phase} 開始] ---",
        "log_phase_skip": "--- [{phase} スキップ] 変更不要 ---",
        "log_target_count": "--- [{phase} 開始] 対象: {count}名 ---",
        "log_retry": "  [!] リトライ中 ({attempt}/3): {name} | 原因: {error} | {wait}s待機...",
        "log_fatal": "  [X] 最終失敗: {name} | エラー: {error}",
        "log_failed_users": "  [結果] 失敗者: {names}",
        "log_complete": "--- [反映完了] 成功: {success}/{total} ---",
        "log_time": "--- [全体所要時間: {time:.3f}s] ---\n",
        
        # --- Settings Window ---
        "btn_settings": "⚙️ 設定",
        "window_settings_title": "設定 (local.config)",
        "label_token": "Bot トークン:",
        "label_guild": "サーバー (Guild) ID:",
        "label_voice": "ボイスチャンネル ID:",
        "btn_save": "保存",
        "dialog_saved_title": "保存完了",
        "dialog_saved_body": "設定を保存しました。再度「① Config読み込み」を行ってください。",
    },
    "en": {
        "app_title": "AutoMuteUs-Manual",
        "btn_config_load": "1. Load Config",
        "btn_discord_connect": "2. Connect Discord",
    }
}

# 現在の言語設定
CURRENT_LANG: str = "ja"

def t(key: str, **kwargs: Any) -> str:
    """
    指定されたキーの翻訳テキストを取得します。
    kwargsが渡された場合は、文字列内の変数をフォーマットして返します。
    """
    # 現在の言語の辞書を取得
    lang_dict = STRINGS.get(CURRENT_LANG, STRINGS["ja"])
    # キーに対応するテキストを取得
    text = lang_dict.get(key, key)
    
    # 🌟 型の安全性を確保
    if not isinstance(text, str):
        text = str(text)

    # {bot_name} などの変数が渡されていれば埋め込む
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text