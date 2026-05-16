"""球队 Repository."""
import json
from typing import Optional
from repositories.database import Database


class TeamRepository:
    def __init__(self) -> None:
        self.db = Database.get_instance()

    def upsert(self, team_data: dict) -> None:
        data = team_data.copy()
        if "stats" in data and data["stats"]:
            import json
            stats = data.pop("stats")
            for k, v in stats.model_dump().items():
                data[f"stats_{k}"] = v
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = [json.dumps(v) if isinstance(v, list) else v for v in data.values()]
        sql = f"INSERT OR REPLACE INTO teams ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_by_id(self, team_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all(self, competition_id: str = "") -> list[dict]:
        with self.db.cursor() as cur:
            if competition_id:
                cur.execute("SELECT * FROM teams WHERE competition_id = ? ORDER BY name", (competition_id,))
            else:
                cur.execute("SELECT * FROM teams ORDER BY name")
            return [dict(r) for r in cur.fetchall()]

    def search(self, keyword: str) -> list[dict]:
        kw = f"%{keyword}%"
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM teams WHERE name LIKE ? OR name_cn LIKE ? OR short_name LIKE ? LIMIT 20",
                (kw, kw, kw)
            )
            return [dict(r) for r in cur.fetchall()]

    def delete(self, team_id: str) -> bool:
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM teams WHERE team_id = ?", (team_id,))
            return cur.rowcount > 0
