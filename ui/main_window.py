import os
import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont

from core.config import ConfigManager
from core.bot import DiscordClient
from core.game_state import GameState
from core.locales import t

# --- 定数 (マジックナンバー・マジックストリングの排除) ---
WINDOW_SIZE = "480x650"
COLOR_BTN_NORMAL = "white"
COLOR_BTN_DEAD = "#ff4444"
COLOR_PHASE_WAITING = "#e1e1e1"
COLOR_PHASE_TASK = "#ff9999"
COLOR_PHASE_MEETING = "#99ccff"
COLOR_SUCCESS = "#ccffcc"
COLOR_ERROR = "#ffcccc"
COLOR_WARNING = "#ffffcc"

class AutoMuteApp(tk.Tk):
    # ==========================================
    # 1. 初期化系メソッド
    # ==========================================
    def __init__(self) -> None:
        super().__init__()
        
        # メンバ変数の宣言（初期化漏れの防止と型ヒント）
        self.font: str = "sans-serif"
        self.config_manager: ConfigManager = ConfigManager()
        self.discord_client: DiscordClient | None = None
        self.game_state: GameState = GameState()
        self.member_buttons: dict[int, tk.Button] = {}
        self.start_time: float = 0.0

        # UI構築プロセス
        self._setup_window()
        self._create_widgets()
        self.after(100, self._late_init)

    def _setup_window(self) -> None:
        """ウィンドウ設定とフォントの初期化（冗長性の排除）"""
        self.title(t("app_title"))
        self.geometry(WINDOW_SIZE)
        
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

    def _create_widgets(self) -> None:
        """UIコンポーネントの生成"""
        # --- Config & Connection ---
        self.btn_load_config = tk.Button(self, text=t("btn_config_load"), command=self.load_config_file, bg=COLOR_ERROR, width=30, height=1)
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
            (t("phase_waiting"), COLOR_PHASE_WAITING, "waiting"), 
            (t("phase_task"), COLOR_PHASE_TASK, "task"), 
            (t("phase_meeting"), COLOR_PHASE_MEETING, "meeting")
        ]
        for text, color, p_id in phases:
            btn = tk.Button(self.phase_frame, text=text, bg=color, font=(self.font, 10, "bold"),
                            width=10, height=2, command=lambda p=p_id: self.apply_phase(p), state="disabled")
            btn.pack(side="left", padx=5)

        self.lbl_info = tk.Label(self, text=t("info_startup"), font=(self.font, 8))
        self.lbl_info.pack(side="bottom", pady=5)

    def _late_init(self) -> None:
        """バックグラウンドで行う初期化処理"""
        self._setup_icon()
        print("DEBUG: アプリ起動完了 (Late Init)")

    def _setup_icon(self) -> None:
        """アイコン読み込み"""
        if not os.path.exists("icon.ico"): return
        try:
            if os.name == 'nt': self.iconbitmap("icon.ico")
        except Exception: pass

    # ==========================================
    # 2. ユーザーアクション系メソッド (窓口)
    # ==========================================
    def load_config_file(self) -> None:
        success, status = self.config_manager.load()
        if status == "CREATED":
            messagebox.showinfo(t("dialog_created_title"), t("dialog_created_body", filename=self.config_manager.filename))
            return
        elif status == "TOKEN_NOT_SET":
            messagebox.showwarning(t("dialog_token_error_title"), t("dialog_token_error_body"))
            return
        if success:
            self.lbl_config_status.config(text=t("status_config_ok"), fg="green")
            self.btn_load_config.config(bg=COLOR_SUCCESS)
            self.btn_connect.config(state="normal", bg=COLOR_WARNING)

    def start_bot_thread(self) -> None:
        self.btn_connect.config(state="disabled", text=t("btn_discord_connecting"))
        settings = self.config_manager.get_discord_settings()
        
        self.discord_client = DiscordClient(
            str(settings['token']), int(settings['guild_id']), int(settings['voice_id'])
        )
        threading.Thread(target=self.run_bot, daemon=True).start()

    def refresh_members(self) -> None:
        if not self.discord_client: return
        for widget in self.members_area.winfo_children(): widget.destroy()
        
        self.member_buttons.clear()
        members = self.discord_client.get_vc_members()
        
        if members is None:
            messagebox.showerror(t("dialog_vc_error_title"), t("dialog_vc_error_body"))
            return

        self.game_state.set_members(members)

        for i, m in enumerate(members):
            col, row = i // 5, i % 5
            btn = tk.Button(self.members_area, text=m.display_name, bg=COLOR_BTN_NORMAL, 
                            width=16, height=1, pady=5, 
                            command=lambda mid=m.id: self.toggle_dead(mid))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.member_buttons[m.id] = btn

    def toggle_dead(self, m_id: int) -> None:
        is_dead = self.game_state.toggle_dead(m_id)
        if m_id in self.member_buttons:
            self.member_buttons[m_id].config(bg=COLOR_BTN_DEAD if is_dead else COLOR_BTN_NORMAL)

    def apply_phase(self, phase: str) -> None:
        if not self.discord_client: return
        self.start_time = time.time()
        
        print(t("log_phase_start", phase=phase.upper()))
        self.set_buttons_state("disabled")
        self.lbl_info.config(text=t("info_applying", phase=t(f"phase_{phase}")), fg="blue")
        
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

    # ==========================================
    # 3. 内部処理・コールバック系メソッド
    # ==========================================
    def run_bot(self) -> None:
        if not self.discord_client: return
        self.discord_client.start(
            on_ready_callback=lambda name: self.after(0, self._on_bot_ready, name),
            on_error_callback=lambda e: self.after(0, self._on_bot_error, e)
        )

    def _on_bot_error(self, e: Exception) -> None:
        messagebox.showerror(t("dialog_conn_error_title"), t("dialog_conn_error_body", error=str(e)))
        self.btn_connect.config(state="normal", text=t("btn_discord_connect"))

    def _on_bot_ready(self, bot_name: str) -> None:
        self.lbl_bot_status.config(text=t("status_connected", bot_name=bot_name), fg="green")
        self.btn_connect.config(bg=COLOR_SUCCESS, text=t("btn_discord_connected"))
        self.set_buttons_state("normal")
        messagebox.showinfo(t("dialog_ready_title"), t("dialog_ready_body"))
        self.lbl_info.config(text=t("info_ready"), fg="blue")

    def set_buttons_state(self, state: str) -> None:
        for child in self.phase_frame.winfo_children(): 
            child.config(state=state)
        self.btn_refresh.config(state=state)

    def _on_sync_complete(self, results: list[tuple[bool, str]], target_count: int) -> None:
        success_names = [name for success, name in results if success]
        failed_names = [name for success, name in results if not success]
        if failed_names: 
            print(t("log_failed_users", names=', '.join(failed_names)))
        print(t("log_complete", success=len(success_names), total=target_count))
        print(t("log_time", time=time.time() - self.start_time))
        self._unlock_ui()
        
    def _unlock_ui(self) -> None:
        self.set_buttons_state("normal")
        self.lbl_info.config(text=t("info_done"), fg="green")