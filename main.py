import os
import asyncio
import threading
import configparser
import time
import tkinter as tk
from tkinter import messagebox
import discord
from discord.ext import commands

class AutoMuteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoMuteUs-Manual")
        self.geometry("400x600")
        self._setup_icon()
        
        self.bot = None
        self.config = configparser.ConfigParser()
        self.config_file = 'local.config'
        self.member_data = {} # {member_id: {"object": member, "is_dead": bool, "button": widget}}

        self._create_widgets()

    def _setup_icon(self):
        """OSごとのアイコン設定"""
        if os.path.exists("icon.ico"):
            try:
                if os.name == 'nt':
                    self.iconbitmap("icon.ico")
                else:
                    img = tk.PhotoImage(file="icon.ico")
                    self.tk.call('wm', 'iconphoto', self._w, img)
            except Exception as e:
                print(f"Icon Load Skip: {e}")

    def _create_widgets(self):
        """UIコンポーネントの生成"""
        # Config Section
        self.btn_load_config = tk.Button(self, text="① Config読み込み", command=self.load_config_file, bg="#ffcccc", width=25)
        self.btn_load_config.pack(pady=10)
        self.lbl_config_status = tk.Label(self, text="🔴 未読込", fg="red")
        self.lbl_config_status.pack()

        # Connection Section
        self.btn_connect = tk.Button(self, text="② Discord接続", command=self.start_bot_thread, state="disabled", bg="#eeeeee", width=25)
        self.btn_connect.pack(pady=10)
        self.lbl_bot_status = tk.Label(self, text="🔴 未接続", fg="red")
        self.lbl_bot_status.pack()

        # Game Control Section
        self.control_frame = tk.LabelFrame(self, text="Game Control")
        self.control_frame.pack(pady=10, fill="both", expand=True)

        self.btn_refresh = tk.Button(self.control_frame, text="メンバー更新", command=self.refresh_members, state="disabled")
        self.btn_refresh.pack(pady=5)

        self.members_area = tk.Frame(self.control_frame)
        self.members_area.pack()

        self.phase_frame = tk.Frame(self.control_frame)
        self.phase_frame.pack(side="bottom", pady=10)
        
        phases = [("待機", "#e1e1e1", "waiting"), ("タスク", "#ff9999", "task"), ("会議", "#99ccff", "meeting")]
        for text, color, p_id in phases:
            btn = tk.Button(self.phase_frame, text=text, bg=color, command=lambda p=p_id: self.apply_phase(p), state="disabled")
            btn.pack(side="left", padx=5)

        self.lbl_info = tk.Label(self, text="local.configを編集して読み込んでください", font=("Arial", 8))
        self.lbl_info.pack(side="bottom", pady=10)

    # --- Config & Bot Logic ---
    def load_config_file(self):
        if not os.path.exists(self.config_file):
            self.config['DISCORD'] = {'BOT_TOKEN': 'PASTE_YOUR_TOKEN_HERE', 'GUILD_ID': '0', 'VOICE_CHANNEL_ID': '0'}
            with open(self.config_file, 'w') as f: self.config.write(f)
            messagebox.showinfo("作成完了", f"{self.config_file} を作成しました。設定後、再度押してください。")
            return

        self.config.read(self.config_file)
        if self.config['DISCORD']['BOT_TOKEN'] == 'PASTE_YOUR_TOKEN_HERE':
            messagebox.showwarning("設定エラー", "トークンを設定してください。")
            return

        self.lbl_config_status.config(text="🟢 Config OK", fg="green")
        self.btn_load_config.config(bg="#ccffcc")
        self.btn_connect.config(state="normal", bg="#ffffcc")

    def start_bot_thread(self):
        self.btn_connect.config(state="disabled", text="接続中...")
        threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.voice_states = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            self.after(0, self._on_bot_ready)

        try:
            self.bot.run(self.config['DISCORD']['BOT_TOKEN'])
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("接続エラー", f"失敗: {e}"))
            self.after(0, lambda: self.btn_connect.config(state="normal", text="② Discord接続"))

    def _on_bot_ready(self):
        self.lbl_bot_status.config(text=f"🟢 接続OK: {self.bot.user.name}", fg="green")
        self.btn_connect.config(bg="#ccffcc", text="② Discord接続完了")
        self.set_buttons_state("normal")
        messagebox.showinfo("準備完了", "オンラインになりました")

    # --- Game Logic ---
    def set_buttons_state(self, state):
        """全ての操作ボタンの有効/無効を切り替え"""
        for child in self.phase_frame.winfo_children():
            child.config(state=state)
        self.btn_refresh.config(state=state)

    def refresh_members(self):
        if not self.bot: return
        for widget in self.members_area.winfo_children(): widget.destroy()
        self.member_data = {}

        guild = self.bot.get_guild(int(self.config['DISCORD']['GUILD_ID']))
        vc = guild.get_channel(int(self.config['DISCORD']['VOICE_CHANNEL_ID'])) if guild else None

        if not vc:
            messagebox.showerror("エラー", "VCが見つかりません")
            return

        for m in vc.members:
            m_id = m.id
            self.member_data[m_id] = {"object": m, "is_dead": False}
            btn = tk.Button(self.members_area, text=m.display_name, bg="white", width=15,
                            command=lambda mid=m_id: self.toggle_dead(mid))
            btn.pack(side="top", pady=2)
            self.member_data[m_id]["button"] = btn

    def toggle_dead(self, m_id):
        data = self.member_data[m_id]
        data["is_dead"] = not data["is_dead"]
        data["button"].config(bg="#ff4444" if data["is_dead"] else "white")

    def apply_phase(self, phase):
        if not self.bot: return
        self.start_time = time.time()
        print(f"\n--- [{phase.upper()} 開始] ---")
        self.set_buttons_state("disabled")
        self.lbl_info.config(text=f"🔄 {phase} 適用中...", fg="blue")
        asyncio.run_coroutine_threadsafe(self.sync_discord(phase), self.bot.loop)

    async def sync_discord(self, phase):
        tasks = []
        sync_start = time.time()

        for data in self.member_data.values():
            member = data["object"]
            t_mute, t_deaf = False, False
            if phase == "task":
                if not data["is_dead"]: t_mute, t_deaf = True, True
            elif phase == "meeting":
                if data["is_dead"]: t_mute = True

            v = member.voice
            if v and (v.mute != t_mute or v.deaf != t_deaf):
                print(f"[準備] {member.display_name}: Mute={t_mute}, Deaf={t_deaf}")
                tasks.append(member.edit(mute=t_mute, deafen=t_deaf))

        print(f"[完了] 命令準備: {len(tasks)}件 (所要時間: {time.time() - sync_start:.3f}秒)")

        if tasks:
            try:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
                print(f"[完了] Discord API処理完了 (所要時間: {time.time() - sync_start:.3f}秒)")
            except Exception as e: print(f"❌ エラー: {e}")
        
        print(f"--- [全体: {time.time() - self.start_time:.3f}s] ---\n")
        self.after(0, self._unlock_ui)
        
    def _unlock_ui(self):
        self.set_buttons_state("normal")
        self.lbl_info.config(text="操作完了", fg="green")
    
if __name__ == "__main__":
    AutoMuteApp().mainloop()