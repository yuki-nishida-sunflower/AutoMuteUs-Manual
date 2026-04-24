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

from typing import Any

class GameState:
    def __init__(self) -> None:
        # メンバーのID(int)をキーにして、オブジェクト(Any)とステータス(str)を管理
        self.members: dict[int, dict[str, Any]] = {}

    def set_members(self, member_list: list[Any]) -> None:
        """Discordから取得したメンバー一覧をセットする"""
        self.members.clear()
        if not member_list:
            return
            
        for m in member_list:
            # 初期状態は全員 "alive" (生存)
            self.members[m.id] = {"object": m, "status": "alive"}

    def toggle_status(self, member_id: int) -> str:
        """指定されたメンバーのステータスを順に切り替え、新しい状態を返す"""
        if member_id in self.members:
            current = self.members[member_id]["status"]
            
            # 生存(alive) → 死亡(dead) → 観戦者(spectator) → 生存... とループ
            if current == "alive":
                new_status = "dead"
            elif current == "dead":
                new_status = "spectator"
            else:
                new_status = "alive"
                
            self.members[member_id]["status"] = new_status
            return new_status
            
        return "alive"

    def get_target_actions(self, phase: str) -> list[tuple[Any, bool, bool]]:
        """指定されたフェーズに基づき、ミュート変更が必要なメンバーのリストを生成して返す"""
        target_actions: list[tuple[Any, bool, bool]] = []
        
        for data in self.members.values():
            status = data["status"]
            
            # 🌟 観戦者(spectator) はミュート制御から完全に無視する！
            if status == "spectator":
                continue
                
            member = data["object"]
            t_mute: bool = False
            t_deaf: bool = False
            
            # --- Among Us のミュートルール ---
            if phase == "task":
                if status == "alive":
                    t_mute, t_deaf = True, True  # 生存者は強ミュート
            elif phase == "meeting":
                if status == "dead":
                    t_mute = True                # 死者はマイクミュートのみ
                    
            # 変更が必要な場合のみリストに追加
            v = member.voice
            if v and (v.mute != t_mute or v.deaf != t_deaf):
                target_actions.append((member, t_mute, t_deaf))
                
        return target_actions