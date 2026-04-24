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

import os
import configparser

# --- 定数 ---
DEFAULT_TOKEN = 'PASTE_YOUR_TOKEN_HERE'
DEFAULT_ID = '0'
SECTION_DISCORD = 'DISCORD'

class ConfigManager:
    def __init__(self, filename: str = "local.config") -> None:
        self.filename: str = filename
        self.config: configparser.ConfigParser = configparser.ConfigParser()

    def load(self) -> tuple[bool, str]:
        """設定ファイルを読み込む。結果のステータス(成功可否, 状態メッセージ)を返す。"""
        if not os.path.exists(self.filename):
            self.config[SECTION_DISCORD] = {
                'BOT_TOKEN': DEFAULT_TOKEN, 
                'GUILD_ID': DEFAULT_ID, 
                'VOICE_CHANNEL_ID': DEFAULT_ID
            }
            with open(self.filename, 'w') as f: 
                self.config.write(f)
            return False, "CREATED"
        
        self.config.read(self.filename)
        if self.config[SECTION_DISCORD].get('BOT_TOKEN') == DEFAULT_TOKEN:
            return False, "TOKEN_NOT_SET"
            
        return True, "OK"

    def get_discord_settings(self) -> dict[str, str | int]:
        """Discordの接続に必要な設定値を辞書で返す"""
        return {
            'token': self.config[SECTION_DISCORD].get('BOT_TOKEN', ''),
            'guild_id': int(self.config[SECTION_DISCORD].get('GUILD_ID', 0)),
            'voice_id': int(self.config[SECTION_DISCORD].get('VOICE_CHANNEL_ID', 0))
        }

    def save_discord_settings(self, token: str, guild_id: str, voice_id: str) -> None:
        """UIから受け取った設定値をファイルに保存する"""
        if not self.config.has_section(SECTION_DISCORD):
            self.config.add_section(SECTION_DISCORD)
            
        self.config[SECTION_DISCORD]['BOT_TOKEN'] = token
        self.config[SECTION_DISCORD]['GUILD_ID'] = str(guild_id)
        self.config[SECTION_DISCORD]['VOICE_CHANNEL_ID'] = str(voice_id)
        
        with open(self.filename, 'w') as f:
            self.config.write(f)