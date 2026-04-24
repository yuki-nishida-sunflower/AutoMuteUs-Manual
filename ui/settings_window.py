import tkinter as tk
from tkinter import messagebox
from core.config import ConfigManager
from core.locales import t

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk, config_manager: ConfigManager):
        super().__init__(parent)
        self.title(t("window_settings_title"))
        self.geometry("450x250")
        self.config_manager = config_manager
        
        # モーダルウィンドウ（元の画面を触れなくする）設定
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_current_settings()

    def _create_widgets(self) -> None:
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        # Token
        tk.Label(frame, text=t("label_token"), anchor="w").pack(fill="x")
        self.ent_token = tk.Entry(frame, width=50)
        self.ent_token.pack(pady=(0, 10))

        # Guild ID
        tk.Label(frame, text=t("label_guild"), anchor="w").pack(fill="x")
        self.ent_guild = tk.Entry(frame, width=50)
        self.ent_guild.pack(pady=(0, 10))

        # Voice ID
        tk.Label(frame, text=t("label_voice"), anchor="w").pack(fill="x")
        self.ent_voice = tk.Entry(frame, width=50)
        self.ent_voice.pack(pady=(0, 20))

        # Save Button
        btn_save = tk.Button(frame, text=t("btn_save"), bg="#ccffcc", command=self._save_settings, width=15)
        btn_save.pack()

    def _load_current_settings(self) -> None:
        """現在の設定ファイルから値を読み込んでテキストボックスに入れる"""
        # 一度ロードして最新状態にする
        self.config_manager.load()
        settings = self.config_manager.get_discord_settings()
        
        self.ent_token.insert(0, settings.get("token", ""))
        self.ent_guild.insert(0, str(settings.get("guild_id", "")))
        self.ent_voice.insert(0, str(settings.get("voice_id", "")))

    def _save_settings(self) -> None:
        """入力された値を設定ファイルに保存して窓を閉じる"""
        token = self.ent_token.get().strip()
        guild_id = self.ent_guild.get().strip()
        voice_id = self.ent_voice.get().strip()

        self.config_manager.save_discord_settings(token, guild_id, voice_id)
        
        messagebox.showinfo(t("dialog_saved_title"), t("dialog_saved_body"), parent=self)
        self.destroy() # 小窓を閉じる