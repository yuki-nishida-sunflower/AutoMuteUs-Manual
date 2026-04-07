import os
import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
from dotenv import load_dotenv
import discord
from discord.ext import commands

# 設定の読み込み
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

class MuteApp(tk.Tk):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.title("AutoMuteUs-Manual")
        self.geometry("400x500")
        
        # UIパーツの作成
        self.label = tk.Label(self, text="Among Us Phase Control", font=("Arial", 14))
        self.label.pack(pady=10)

        # フェーズ変更ボタン
        tk.Button(self, text="待機 (全員解除)", command=lambda: self.change_phase("waiting"), bg="lightgray", width=20).pack(pady=5)
        tk.Button(self, text="タスク (生存者ミュート)", command=lambda: self.change_phase("task"), bg="red", fg="white", width=20).pack(pady=5)
        tk.Button(self, text="会議 (死亡者マイクオフ)", command=lambda: self.change_phase("meeting"), bg="skyblue", width=20).pack(pady=5)

    def change_phase(self, phase):
        # ここでBotのミュート処理を呼び出す
        print(f"Phase changed to: {phase}")
        # 非同期処理を実行するためのブリッジ
        self.bot.loop.create_task(self.sync_discord(phase))

    async def sync_discord(self, phase):
        # ここにDiscord操作のロジックを実装していく
        print(f"Discord Syncing for {phase}...")

# Discord Botの設定
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# GUIとBotを同時に動かすためのスレッド設定
def run_tk(bot):
    app = MuteApp(bot)
    app.mainloop()

if __name__ == "__main__":
    # Botを別スレッドで動かさないとGUIが固まるため、工夫が必要
    # 今回は簡単な構成として、BotのループをメインにGUIをスレッド化します
    t = threading.Thread(target=run_tk, args=(bot,))
    t.start()
    bot.run(TOKEN)