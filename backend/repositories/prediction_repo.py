"""预测结果 Repository."""
import json
from typing import Optional
from repositories.database import Database


class PredictionRepository:
    def __init__(self) -> None:
        self.db = Database.get_instance()

    def upsert_prediction(self, pred_data: dict) -> None:
        data = pred_data.copy()
        for field in ["win_probabilities", "dimension_scores", "key_factors", "predicted_starting_xi_home", "predicted_starting_xi_away"]:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field])
        if isinstance(data.get("score_prediction"), dict):
            data["score_prediction"] = json.dumps(data["score_prediction"])
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = [json.dumps(v) if isinstance(v, list) else v for v in data.values()]
        sql = f"INSERT OR REPLACE INTO predictions ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_by_match(self, match_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM predictions WHERE match_id = ? ORDER BY generated_at DESC LIMIT 1", (match_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_recent(self, limit: int = 20) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM predictions ORDER BY generated_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]

    def upsert_post_match(self, analysis_data: dict) -> None:
        data = analysis_data.copy()
        for field in ["key_performers", "turning_points"]:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field])
        if isinstance(data.get("stats_comparison"), dict):
            data["stats_comparison"] = json.dumps(data["stats_comparison"])
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = [json.dumps(v) if isinstance(v, list) else v for v in data.values()]
        sql = f"INSERT OR REPLACE INTO post_match_analyses ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_post_match_by_match(self, match_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM post_match_analyses WHERE match_id = ? ORDER BY generated_at DESC LIMIT 1", (match_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_post_match_recent(self, limit: int = 20) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM post_match_analyses ORDER BY generated_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]
