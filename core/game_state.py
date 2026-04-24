from typing import Any

class GameState:
    def __init__(self) -> None:
        # メンバーのID(int)をキーにして、オブジェクト(Any)と生死状態(bool)を管理
        self.members: dict[int, dict[str, Any]] = {}

    def set_members(self, member_list: list[Any]) -> None:
        """Discordから取得したメンバー一覧をセットする"""
        self.members.clear()
        if not member_list:
            return
            
        for m in member_list:
            self.members[m.id] = {"object": m, "is_dead": False}

    def toggle_dead(self, member_id: int) -> bool:
        """指定されたメンバーの生死を反転させ、新しい状態(bool)を返す"""
        if member_id in self.members:
            self.members[member_id]["is_dead"] = not self.members[member_id]["is_dead"]
            return self.members[member_id]["is_dead"]
        return False

    def get_target_actions(self, phase: str) -> list[tuple[Any, bool, bool]]:
        """指定されたフェーズに基づき、ミュート変更が必要なメンバーのリストを生成して返す"""
        target_actions: list[tuple[Any, bool, bool]] = []
        
        for data in self.members.values():
            member = data["object"]
            t_mute: bool = False
            t_deaf: bool = False
            
            # --- Among Us のミュートルール ---
            if phase == "task":
                if not data["is_dead"]:
                    t_mute, t_deaf = True, True  # 生存者は強ミュート
            elif phase == "meeting":
                if data["is_dead"]:
                    t_mute = True                # 死者はマイクミュートのみ
                    
            # 変更が必要な場合のみリストに追加
            v = member.voice
            if v and (v.mute != t_mute or v.deaf != t_deaf):
                target_actions.append((member, t_mute, t_deaf))
                
        return target_actions