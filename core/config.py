import os
import configparser

class ConfigManager:
    def __init__(self, filename="local.config"):
        self.filename = filename
        self.config = configparser.ConfigParser()

    def load(self):
        """設定ファイルを読み込む。結果のステータスを返す。"""
        if not os.path.exists(self.filename):
            self.config['DISCORD'] = {'BOT_TOKEN': 'PASTE_YOUR_TOKEN_HERE', 'GUILD_ID': '0123456789', 'VOICE_CHANNEL_ID': '0123456789'}
            with open(self.filename, 'w') as f: 
                self.config.write(f)
            return False, "CREATED" # 新規作成した
        
        self.config.read(self.filename)
        if self.config['DISCORD']['BOT_TOKEN'] == 'PASTE_YOUR_TOKEN_HERE':
            return False, "TOKEN_NOT_SET" # トークンが初期値のまま
            
        return True, "OK"

    def get_discord_settings(self):
        """Discordの接続に必要な設定値を辞書で返す"""
        return {
            'token': self.config['DISCORD']['BOT_TOKEN'],
            'guild_id': int(self.config['DISCORD']['GUILD_ID']),
            'voice_id': int(self.config['DISCORD']['VOICE_CHANNEL_ID'])
        }