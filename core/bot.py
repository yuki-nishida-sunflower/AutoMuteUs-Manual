import discord
from discord.ext import commands
import asyncio

class DiscordClient:
    def __init__(self, token, guild_id, voice_id):
        self.token = token
        self.guild_id = guild_id
        self.voice_id = voice_id
        self.bot = None

    def start(self, on_ready_callback, on_error_callback):
        """同期的にBotを起動する（別スレッドから呼ばれる想定）"""
        intents = discord.Intents.default()
        intents.members = True
        intents.voice_states = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            # 接続完了時にUI側に名前を伝える
            on_ready_callback(self.bot.user.name)

        try:
            self.bot.run(self.token)
        except Exception as e:
            # 失敗時にUI側にエラーを伝える
            on_error_callback(e)

    def get_vc_members(self):
        """設定されたVCのメンバーを取得する"""
        if not self.bot: return None
        guild = self.bot.get_guild(self.guild_id)
        vc = guild.get_channel(self.voice_id) if guild else None
        return vc.members if vc else None

    def submit_actions(self, target_actions, on_complete_callback):
        """別スレッドのイベントループにミュート処理を投げ、終わったら通知する"""
        if not self.bot or not self.bot.loop:
            return

        async def wrapper():
            results = await self._execute_actions(target_actions)
            on_complete_callback(results)

        asyncio.run_coroutine_threadsafe(wrapper(), self.bot.loop)

    async def _execute_actions(self, target_actions):
        """リトライ付きのミュート並列処理（元の main.py からお引越し）"""
        total = len(target_actions)
        
        async def safe_edit(member, m, d, attempt=1):
            try:
                if total > 10:
                    await asyncio.sleep(0.05 * (attempt - 1)) 
                
                await member.edit(mute=m, deafen=d)
                return True, member.display_name
            except Exception as e:
                if attempt <= 3:
                    wait_time = attempt * 0.5
                    print(f"  [!] リトライ中 ({attempt}/3): {member.display_name} | 原因: {e} | {wait_time}s待機...")
                    await asyncio.sleep(wait_time)
                    return await safe_edit(member, m, d, attempt + 1)
                else:
                    print(f"  [X] 最終失敗: {member.display_name} | エラー: {e}")
                    return False, member.display_name

        tasks = [safe_edit(m, mute, deaf) for m, mute, deaf in target_actions]
        return await asyncio.gather(*tasks)