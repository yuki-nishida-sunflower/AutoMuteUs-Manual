import os
import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
from core.config import ConfigManager
from core.bot import DiscordClient
from core.game_state import GameState  # 状態管理の専門家を追加
from core.locales import t

class AutoMuteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(t("app_title"))
        self.geometry("480x650")
        self.font = "sans-serif"
        self._font_init()
        
        # 専門家（クラス）の初期化
        self.config_manager = ConfigManager()
        self.discord_client = None
        self.game_state = GameState()
        
        # UIパーツ（ボタン）だけを保存する辞書
        self.member_buttons = {}

        self._create_widgets()
        self.after(100, self._late_init)

    def _font_init(self):
        font_candidates = [
            "Meiryo", "Hiragino Kaku Gothic ProN", "AppleGothic", 
            "Noto Sans CJK JP", "Droid Sans Fallback", "sans-serif"
        ]
        available_fonts = tkfont.families()
        for f in font_candidates:
            if f in available_fonts:
                self.font = f
                break
        self.option_add("*font", (self.font, 10))
        self.title(t("app_title"))
        self.geometry("480x650")
    
    def _late_init(self):
        self._setup_icon()
        print(f"DEBUG: アプリ起動完了 (Late Init)")

    def _setup_icon(self):
        if not os.path.exists("icon.ico"): return
        try:
            if os.name == 'nt': self.iconbitmap("icon.ico")
        except Exception: pass

    def _create_widgets(self):
        # --- Config & Connection ---
        self.btn_load_config = tk.Button(self, text=t("btn_config_load"), command=self.load_config_file, bg="#ffcccc", width=30, height=1)
        self.btn_load_config.pack(pady=5)
        self.lbl_config_status = tk.Label(self, text=t("status_unloaded"), fg="red")
        self.lbl_config_status.pack()

        self.btn_connect = tk.Button(self, text=t("btn_discord_connect"), command=self.start_bot_thread, state="disabled", bg="#eeeeee", width=30, height=1)
        self.btn_connect.pack(pady=5)
        self.lbl_bot_status = tk.Label(self, text=t("status_disconnected"), fg="red")
        self.lbl_bot_status.pack()

        # --- Game Control ---
        self.control_frame = tk.LabelFrame(self, text=t("frame_game_control"), padx=10, pady=10)
        self.control_frame.pack(pady=10, fill="both", expand=True)

        self.btn_refresh = tk.Button(self.control_frame, text=t("btn_member_refresh"), command=self.refresh_members, state="disabled", width=15)
        self.btn_refresh.pack(pady=10)

        self.members_area = tk.Frame(self.control_frame)
        self.members_area.pack(anchor="n", pady=10)

        # --- Phase Buttons ---
        self.phase_frame = tk.Frame(self.control_frame)
        self.phase_frame.pack(side="bottom", pady=10)
        
        phases = [
            (t("phase_waiting"), "#e1e1e1", "waiting"), 
            (t("phase_task"), "#ff9999", "task"), 
            (t("phase_meeting"), "#99ccff", "meeting")
        ]
        for text, color, p_id in phases:
            btn = tk.Button(self.phase_frame, text=text, bg=color, font=(self.font, 10, "bold"),
                            width=10, height=2, command=lambda p=p_id: self.apply_phase(p), state="disabled")
            btn.pack(side="left", padx=5)

        self.lbl_info = tk.Label(self, text=t("info_startup"), font=(self.font, 8))
        self.lbl_info.pack(side="bottom", pady=5)

    def load_config_file(self):
        success, status = self.config_manager.load()
        if status == "CREATED":
            messagebox.showinfo(t("dialog_created_title"), t("dialog_created_body", filename=self.config_manager.filename))
            return
        elif status == "TOKEN_NOT_SET":
            messagebox.showwarning(t("dialog_token_error_title"), t("dialog_token_error_body"))
            return
        if success:
            self.lbl_config_status.config(text=t("status_config_ok"), fg="green")
            self.btn_load_config.config(bg="#ccffcc")
            self.btn_connect.config(state="normal", bg="#ffffcc")

    def start_bot_thread(self):
        self.btn_connect.config(state="disabled", text=t("btn_discord_connecting"))
        settings = self.config_manager.get_discord_settings()
        
        self.discord_client = DiscordClient(
            settings['token'], settings['guild_id'], settings['voice_id']
        )
        threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        self.discord_client.start(
            on_ready_callback=lambda name: self.after(0, self._on_bot_ready, name),
            on_error_callback=lambda e: self.after(0, self._on_bot_error, e)
        )

    def _on_bot_error(self, e):
        messagebox.showerror(t("dialog_conn_error_title"), t("dialog_conn_error_body", error=str(e)))
        self.btn_connect.config(state="normal", text=t("btn_discord_connect"))

    def _on_bot_ready(self, bot_name):
        self.lbl_bot_status.config(text=t("status_connected", bot_name=bot_name), fg="green")
        self.btn_connect.config(bg="#ccffcc", text=t("btn_discord_connected"))
        self.set_buttons_state("normal")
        messagebox.showinfo(t("dialog_ready_title"), t("dialog_ready_body"))
        self.lbl_info.config(text=t("info_ready"), fg="blue")

    def set_buttons_state(self, state):
        for child in self.phase_frame.winfo_children(): child.config(state=state)
        self.btn_refresh.config(state=state)

    def refresh_members(self):
        if not self.discord_client: return
        for widget in self.members_area.winfo_children(): widget.destroy()
        
        self.member_buttons = {} # UIボタンの初期化
        members = self.discord_client.get_vc_members()
        
        if members is None:
            messagebox.showerror(t("dialog_vc_error_title"), t("dialog_vc_error_body"))
            return

        # 専門家にデータを渡す
        self.game_state.set_members(members)

        # UIを描画する
        for i, m in enumerate(members):
            m_id = m.id
            col, row = i // 5, i % 5
            btn = tk.Button(self.members_area, text=m.display_name, bg="white", 
                            width=16, height=1, pady=5, 
                            command=lambda mid=m_id: self.toggle_dead(mid))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.member_buttons[m_id] = btn

    def toggle_dead(self, m_id):
        # 専門家に状態反転をお願いし、新しい状態を受け取る
        is_dead = self.game_state.toggle_dead(m_id)
        
        # 受け取った状態に応じてUI(色)を更新する
        if m_id in self.member_buttons:
            self.member_buttons[m_id].config(bg="#ff4444" if is_dead else "white")

    def apply_phase(self, phase):
        if not self.discord_client: return
        self.start_time = time.time()
        
        print(t("log_phase_start", phase=phase.upper()))
        self.set_buttons_state("disabled")
        self.lbl_info.config(text=t("info_applying", phase=t(f"phase_{phase}")), fg="blue")
        
        # 専門家に「このフェーズでミュートすべき人のリスト」を作ってもらう！(UIは考えない)
        target_actions = self.game_state.get_target_actions(phase)

        if not target_actions:
            print(t("log_phase_skip", phase=phase.upper()))
            self._unlock_ui()
            return

        print(t("log_target_count", phase=phase.upper(), count=len(target_actions)))
        
        self.discord_client.submit_actions(
            target_actions, 
            on_complete_callback=lambda results: self.after(0, self._on_sync_complete, results, len(target_actions))
        )

    def _on_sync_complete(self, results, target_count):
        success_names = [name for success, name in results if success]
        failed_names = [name for success, name in results if not success]
        if failed_names: print(t("log_failed_users", names=', '.join(failed_names)))
        print(t("log_complete", success=len(success_names), total=target_count))
        print(t("log_time", time=time.time() - self.start_time))
        self._unlock_ui()
        
    def _unlock_ui(self):
        self.set_buttons_state("normal")
        self.lbl_info.config(text=t("info_done"), fg="green")