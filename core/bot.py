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

import discord
from discord.ext import commands
import asyncio
from typing import Callable, Any
from core.locales import t

class DiscordClient:
    def __init__(self, token: str, guild_id: int, voice_id: int) -> None:
        self.token: str = token
        self.guild_id: int = guild_id
        self.voice_id: int = voice_id
        self.bot: commands.Bot | None = None

    def start(self, on_ready_callback: Callable[[str], None], on_error_callback: Callable[[Exception], None]) -> None:
        """同期的にBotを起動する（別スレッドから呼ばれる想定）"""
        intents = discord.Intents.default()
        intents.members = True
        intents.voice_states = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready() -> None:
            if self.bot and self.bot.user:
                on_ready_callback(self.bot.user.name)

        try:
            self.bot.run(self.token)
        except Exception as e:
            on_error_callback(e)

    def get_vc_members(self) -> list[discord.Member] | None:
        """設定されたVCのメンバーを取得する"""
        if not self.bot: return None
        guild = self.bot.get_guild(self.guild_id)
        vc = guild.get_channel(self.voice_id) if guild else None
        
        # vcがボイスチャンネルであればメンバーを返す
        if isinstance(vc, discord.VoiceChannel):
            return vc.members
        return None

    def submit_actions(self, target_actions: list[tuple[discord.Member, bool, bool]], on_complete_callback: Callable[[list[tuple[bool, str]]], None]) -> None:
        """別スレッドのイベントループにミュート処理を投げ、終わったら通知する"""
        if not self.bot or not self.bot.loop:
            return

        async def wrapper() -> None:
            results = await self._execute_actions(target_actions)
            on_complete_callback(results)

        asyncio.run_coroutine_threadsafe(wrapper(), self.bot.loop)

    async def _execute_actions(self, target_actions: list[tuple[discord.Member, bool, bool]]) -> list[tuple[bool, str]]:
        """リトライ付きのミュート並列処理（レート制限回避版）"""
        total = len(target_actions)
        
        # 🌟 引数に 'index' を追加
        async def safe_edit(member: discord.Member, m: bool, d: bool, index: int, attempt: int = 1) -> tuple[bool, str]:
            try:
                # 🌟 10名を超える場合は、順番に応じて 0.1秒ずつずらして開始する
                if total > 10 and attempt == 1:
                    await asyncio.sleep(0.1 * index)
                
                await member.edit(mute=m, deafen=d)
                return True, member.display_name
            except Exception as e:
                # ... (以下、リトライ処理は変更なし) ...
                if attempt <= 3:
                    wait_time = attempt * 0.5
                    print(t("log_retry", attempt=attempt, name=member.display_name, error=e, wait=wait_time))
                    await asyncio.sleep(wait_time)
                    return await safe_edit(member, m, d, index, attempt + 1)
                else:
                    print(t("log_fatal", name=member.display_name, error=e))
                    return False, member.display_name

        # 🌟 enumerate を使って index を渡し、並列実行を開始
        tasks = [safe_edit(m, mute, deaf, i) for i, (m, mute, deaf) in enumerate(target_actions)]
        return await asyncio.gather(*tasks)