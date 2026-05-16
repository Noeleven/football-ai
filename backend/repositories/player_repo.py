"""球员 Repository."""
import json
from typing import Optional
from repositories.database import Database


class PlayerRepository:
    def __init__(self) -> None:
        self.db = Database.get_instance()

    def upsert(self, player_data: dict) -> None:
        data = player_data.copy()
        # Serialize lists
        for field in ["strengths", "weaknesses", "injury_history"]:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field])
        if "current_stats" in data and data["current_stats"]:
            cs = data.pop("current_stats")
            for k, v in cs.model_dump().items():
                data[f"stats_{k}"] = v
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = [json.dumps(v) if isinstance(v, list) else v for v in data.values()]
        sql = f"INSERT OR REPLACE INTO players ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_by_id(self, player_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_by_team(self, team_id: str) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM players WHERE team_id = ? ORDER BY position, jersey_number", (team_id,))
            return [dict(r) for r in cur.fetchall()]

    def get_key_players(self, team_id: str) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM players WHERE team_id = ? AND is_key_player = 1 ORDER BY market_value DESC",
                (team_id,)
            )
            return [dict(r) for r in cur.fetchall()]

    def search(self, keyword: str) -> list[dict]:
        kw = f"%{keyword}%"
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM players WHERE name LIKE ? OR name_cn LIKE ? LIMIT 20",
                (kw, kw)
            )
            return [dict(r) for r in cur.fetchall()]

    def get_all(self) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM players ORDER BY team_id, position")
            return [dict(r) for r in cur.fetchall()]
