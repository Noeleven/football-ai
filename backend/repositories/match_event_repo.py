"""Match Event Repository - for storing match events (goals, cards, etc)."""
import json
from typing import Optional
from repositories.database import Database


class MatchEventRepository:
    def __init__(self) -> None:
        self.db = Database.get_instance()

    def insert(self, event_data: dict) -> None:
        data = event_data.copy()
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = list(data.values())
        sql = f"INSERT INTO match_events ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_by_match(self, match_id: str) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM match_events WHERE match_id = ? ORDER BY minute",
                (match_id,)
            )
            return [dict(r) for r in cur.fetchall()]

    def upsert_batch(self, events: list[dict]) -> None:
        with self.db.cursor() as cur:
            for event in events:
                cols = ", ".join(event.keys())
                placeholders = ", ".join(["?" for _ in event])
                vals = list(event.values())
                sql = f"INSERT OR REPLACE INTO match_events ({cols}) VALUES ({placeholders})"
                cur.execute(sql, vals)

    def delete_by_match(self, match_id: str) -> None:
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM match_events WHERE match_id = ?", (match_id,))