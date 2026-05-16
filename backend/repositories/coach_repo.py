"""Coach Repository - missing in original implementation."""
import json
from typing import Optional
from repositories.database import Database


class CoachRepository:
    def __init__(self) -> None:
        self.db = Database.get_instance()

    def upsert(self, coach_data: dict) -> None:
        data = coach_data.copy()
        for field in ["achievements", "trophies"]:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field])
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = [json.dumps(v) if isinstance(v, list) else v for v in data.values()]
        sql = f"INSERT OR REPLACE INTO coaches ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_by_id(self, coach_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM coaches WHERE coach_id = ?", (coach_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_by_team(self, team_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM coaches WHERE team_id = ?", (team_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all(self) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM coaches ORDER BY name")
            return [dict(r) for r in cur.fetchall()]

    def search(self, keyword: str) -> list[dict]:
        kw = f"%{keyword}%"
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM coaches WHERE name LIKE ? OR name_cn LIKE ? LIMIT 20",
                (kw, kw)
            )
            return [dict(r) for r in cur.fetchall()]

    def delete(self, coach_id: str) -> bool:
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM coaches WHERE coach_id = ?", (coach_id,))
            return cur.rowcount > 0