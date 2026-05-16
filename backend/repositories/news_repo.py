"""新闻 Repository."""
import json
from typing import Optional
from repositories.database import Database


class NewsRepository:
    def __init__(self) -> None:
        self.db = Database.get_instance()

    def upsert(self, news_data: dict) -> None:
        data = news_data.copy()
        for field in ["team_ids", "player_ids", "tags", "image_urls"]:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field])
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = [json.dumps(v) if isinstance(v, list) else v for v in data.values()]
        sql = f"INSERT OR REPLACE INTO news ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_by_id(self, news_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM news WHERE news_id = ?", (news_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_recent(self, news_type: str = "", competition_id: str = "", limit: int = 50) -> list[dict]:
        with self.db.cursor() as cur:
            query = "SELECT * FROM news WHERE 1=1"
            params = []
            if news_type:
                query += " AND news_type = ?"
                params.append(news_type)
            if competition_id:
                query += " AND competition_id = ?"
                params.append(competition_id)
            query += " ORDER BY published_at DESC LIMIT ?"
            params.append(limit)
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def get_by_team(self, team_id: str, limit: int = 30) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM news WHERE team_ids LIKE ? ORDER BY published_at DESC LIMIT ?",
                (f"%{team_id}%", limit)
            )
            return [dict(r) for r in cur.fetchall()]

    def search(self, keyword: str, limit: int = 30) -> list[dict]:
        kw = f"%{keyword}%"
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM news WHERE title LIKE ? OR content LIKE ? ORDER BY published_at DESC LIMIT ?",
                (kw, kw, limit)
            )
            return [dict(r) for r in cur.fetchall()]

    def delete(self, news_id: str) -> bool:
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM news WHERE news_id = ?", (news_id,))
            return cur.rowcount > 0
