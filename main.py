import os
import asyncio
import threading
import configparser
import time  # 冒頭のインポートに追加してください
import tkinter as tk
from tkinter import messagebox
import discord
from discord.ext import commands

class AutoMuteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoMuteUs-Manual")
        self.geometry("400x600")
        
        # --- アイコンの設定 ---
        if os.path.exists("icon.ico"):
            try:
                if os.name == 'nt': # Windowsの場合
                    self.iconbitmap("icon.ico")
                else: # WSL / Linuxの場合
                    # Linuxでは.icoを直接使わず、PhotoImageとして読み込む
                    # (ただし、Tkinterのバージョンによりこれでもエラーが出る場合があります)
                    img = tk.PhotoImage(file="icon.ico") # もしエラーならここをコメントアウト
                    self.tk.call('wm', 'iconphoto', self._w, img)
            except Exception as e:
                print(f"アイコンの読み込みをスキップしました: {e}")
        
        self.bot = None
        self.config = configparser.ConfigParser()
        self.config_file = 'local.config'

        # --- UI Components ---
        # 1. Config Section
        self.btn_load_config = tk.Button(self, text="① Config読み込み", command=self.load_config_file, bg="#ffcccc", width=25)
        self.btn_load_config.pack(pady=10)
        self.lbl_config_status = tk.Label(self, text="🔴 未読込", fg="red")
        self.lbl_config_status.pack()

        # 2. Connection Section
        self.btn_connect = tk.Button(self, text="② Discord接続", command=self.start_bot_thread, state="disabled", bg="#eeeeee", width=25)
        self.btn_connect.pack(pady=10)
        self.lbl_bot_status = tk.Label(self, text="🔴 未接続", fg="red")
        self.lbl_bot_status.pack()

        # 3. Info Section
        self.lbl_info = tk.Label(self, text="local.configを編集して読み込んでください", font=("Arial", 8))
        self.lbl_info.pack(side="bottom", pady=10)

        # --- 4. Game Control Section (追加) ---
        self.control_frame = tk.LabelFrame(self, text="Game Control")
        self.control_frame.pack(pady=10, fill="both", expand=True)

        self.btn_refresh = tk.Button(self.control_frame, text="メンバー更新", command=self.refresh_members)
        self.btn_refresh.pack(pady=5)

        # メンバーのボタンを表示するエリア
        self.members_area = tk.Frame(self.control_frame)
        self.members_area.pack()

        # フェーズボタン
        self.phase_frame = tk.Frame(self.control_frame)
        self.phase_frame.pack(side="bottom", pady=10)
        
        tk.Button(self.phase_frame, text="待機", bg="#e1e1e1", command=lambda: self.apply_phase("waiting")).pack(side="left", padx=5)
        tk.Button(self.phase_frame, text="タスク", bg="#ff9999", command=lambda: self.apply_phase("task")).pack(side="left", padx=5)
        tk.Button(self.phase_frame, text="会議", bg="#99ccff", command=lambda: self.apply_phase("meeting")).pack(side="left", padx=5)

        self.member_data = {} # {member_id: {"name": str, "is_dead": bool, "button": widget}}


    # --- Logic ---
    def load_config_file(self):
        """local.configを読み込み、バリデーションを行う"""
        if not os.path.exists(self.config_file):
            # ファイルがなければテンプレート作成
            self.config['DISCORD'] = {
                'BOT_TOKEN': 'PASTE_YOUR_TOKEN_HERE',
                'GUILD_ID': '0000000000',
                'VOICE_CHANNEL_ID': '0000000000'
            }
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            messagebox.showinfo("作成完了", f"{self.config_file} を作成しました。中身を書き換えてから再度押してください。")
            return

        self.config.read(self.config_file)
        # 簡易チェック（デフォルト値のままじゃないか）
        if self.config['DISCORD']['BOT_TOKEN'] == 'PASTE_YOUR_TOKEN_HERE':
            messagebox.showwarning("設定エラー", "トークンを正しく設定してください。")
            return

        self.lbl_config_status.config(text="🟢 Config OK", fg="green")
        self.btn_load_config.config(bg="#ccffcc")
        self.btn_connect.config(state="normal", bg="#ffffcc")
        messagebox.showinfo("成功", "Configを読み込みました。Discordに接続できます。")

    def start_bot_thread(self):
        """GUIを止めないように別スレッドでBotを起動"""
        self.btn_connect.config(state="disabled", text="接続中...")
        thread = threading.Thread(target=self.run_bot, daemon=True)
        thread.start()

    def run_bot(self):
        """Discord Botの実行ループ"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        intents = discord.Intents.default()
        intents.members = True
        intents.voice_states = True
        
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            # GUI側の表示を更新（スレッドセーフな方法で）
            self.after(0, self.on_bot_ready)

        try:
            self.bot.run(self.config['DISCORD']['BOT_TOKEN'])
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("接続エラー", f"Botの起動に失敗しました:\n{e}"))
            self.after(0, lambda: self.btn_connect.config(state="normal", text="② Discord接続"))

    def on_bot_ready(self):
        """Bot接続成功時のGUI更新"""
        self.lbl_bot_status.config(text=f"🟢 接続OK: {self.bot.user.name}", fg="green")
        self.btn_connect.config(bg="#ccffcc", text="② Discord接続完了")
        messagebox.showinfo("準備完了", "Discord Botがオンラインになりました！")

    def refresh_members(self):
        """VCにいるメンバーを取得してボタンを作成"""
        if not self.bot: return
        
        # 既存のボタンを削除
        for widget in self.members_area.winfo_children():
            widget.destroy()
        self.member_data = {}

        guild_id = int(self.config['DISCORD']['GUILD_ID'])
        vc_id = int(self.config['DISCORD']['VOICE_CHANNEL_ID'])
        guild = self.bot.get_guild(guild_id)
        vc = guild.get_channel(vc_id)

        if not vc:
            messagebox.showerror("エラー", "ボイスチャンネルが見つかりません")
            return

        for m in vc.members:
            self.add_member_ui(m)

    def add_member_ui(self, member):
        """メンバー一人分のボタンを作成"""
        m_id = member.id
        self.member_data[m_id] = {"object": member, "is_dead": False}
        
        btn = tk.Button(self.members_area, text=member.display_name, 
                        bg="white", width=15,
                        command=lambda m_id=m_id: self.toggle_dead(m_id))
        btn.pack(side="top", pady=2)
        self.member_data[m_id]["button"] = btn

    def toggle_dead(self, m_id):
        """生存/死亡を切り替えて色を変える"""
        data = self.member_data[m_id]
        data["is_dead"] = not data["is_dead"]
        new_color = "#ff4444" if data["is_dead"] else "white"
        data["button"].config(bg=new_color)

    def apply_phase(self, phase):
        """フェーズに合わせてDiscord側を制御（ボタン制御追加）"""
        if not self.bot: return
        # 計測開始
        self.start_time = time.time()
        print(f"\n--- [{phase.upper()} フェーズ開始] ---")
        
        # --- ボタンを無効化して進行中を表示 ---
        self.set_buttons_state("disabled")
        self.lbl_info.config(text=f"🔄 {phase} フェーズ適用中...", fg="blue")
        
        # 非同期処理を実行
        asyncio.run_coroutine_threadsafe(self.sync_discord(phase), self.bot.loop)

    def set_buttons_state(self, state):
        """操作系ボタンの状態を一括変更"""
        for child in self.phase_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.config(state=state)
        self.btn_refresh.config(state=state)

    async def sync_discord(self, phase):
        """詳細なログを出力しながら同期を実行"""
        tasks = []
        sync_start = time.time()

        # 1. メンバーの状態チェック
        for m_id, data in self.member_data.items():
            member = data["object"]
            is_dead = data["is_dead"]
            
            target_mute, target_deafen = False, False
            if phase == "task":
                if not is_dead: target_mute, target_deafen = True, True
            elif phase == "meeting":
                if is_dead: target_mute = True

            current_state = member.voice
            if current_state:
                if current_state.mute != target_mute or current_state.deaf != target_deafen:
                    # 誰に対してどのような命令を出すかログ出し
                    print(f"[準備] {member.display_name}: Mute={target_mute}, Deafen={target_deafen}")
                    tasks.append(member.edit(mute=target_mute, deafen=target_deafen))

        prep_end = time.time()
        print(f"[完了] 命令の準備完了: {len(tasks)}件 (所要時間: {prep_end - sync_start:.3f}秒)")

        # 2. Discord APIへのリクエスト実行
        if tasks:
            print(f"[実行] Discord APIへ一斉送信中...")
            api_start = time.time()
            try:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
                api_end = time.time()
                print(f"[完了] Discord API処理完了 (所要時間: {api_end - api_start:.3f}秒)")
            except Exception as e:
                print(f"❌ 同期エラー: {e}")
        else:
            print("[スキップ] 変更が必要なメンバーはいませんでした")

        # 3. 全体の所要時間を表示
        total_end = time.time()
        print(f"--- [全体所要時間: {total_end - self.start_time:.3f}秒] ---\n")
        
        self.after(0, self.unlock_ui)
        
    def unlock_ui(self):
        """ボタンを再度活性化する"""
        for child in self.phase_frame.winfo_children():
            child.config(state="normal")
        self.btn_refresh.config(state="normal")
        self.lbl_info.config(text="操作完了", fg="green")
        
    def finish_phase_change(self, msg):
        """処理完了後のUI復帰"""
        self.set_buttons_state("normal")
        self.lbl_info.config(text=msg, fg="black")
    
if __name__ == "__main__":
    app = AutoMuteApp()
    app.mainloop()