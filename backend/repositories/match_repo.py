"""比赛 Repository."""
import json
from typing import Optional
from repositories.database import Database


class MatchRepository:
    def __init__(self) -> None:
        self.db = Database.get_instance()

    def upsert(self, match_data: dict) -> None:
        data = match_data.copy()
        for field in ["starting_xi_home", "starting_xi_away", "substitutes_home", "substitutes_away"]:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field])
        fields = list(data.keys())
        cols = ", ".join(fields)
        placeholders = ", ".join(["?" for _ in fields])
        vals = [json.dumps(v) if isinstance(v, list) else v for v in data.values()]
        sql = f"INSERT OR REPLACE INTO matches ({cols}) VALUES ({placeholders})"
        with self.db.cursor() as cur:
            cur.execute(sql, vals)

    def get_by_id(self, match_id: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_upcoming(self, competition_id: str = "", limit: int = 20) -> list[dict]:
        from datetime import datetime
        now = datetime.now().isoformat()
        with self.db.cursor() as cur:
            if competition_id:
                cur.execute(
                    "SELECT * FROM matches WHERE competition_id = ? AND match_time > ? AND status = 'scheduled' ORDER BY match_time LIMIT ?",
                    (competition_id, now, limit)
                )
            else:
                cur.execute(
                    "SELECT * FROM matches WHERE match_time > ? AND status = 'scheduled' ORDER BY match_time LIMIT ?",
                    (now, limit)
                )
            return [dict(r) for r in cur.fetchall()]

    def get_recent(self, competition_id: str = "", limit: int = 20) -> list[dict]:
        from datetime import datetime
        now = datetime.now().isoformat()
        with self.db.cursor() as cur:
            if competition_id:
                cur.execute(
                    "SELECT * FROM matches WHERE competition_id = ? AND match_time <= ? AND status = 'finished' ORDER BY match_time DESC LIMIT ?",
                    (competition_id, now, limit)
                )
            else:
                cur.execute(
                    "SELECT * FROM matches WHERE match_time <= ? AND status = 'finished' ORDER BY match_time DESC LIMIT ?",
                    (now, limit)
                )
            return [dict(r) for r in cur.fetchall()]

    def get_by_team(self, team_id: str, limit: int = 30) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM matches WHERE (home_team_id = ? OR away_team_id = ?) ORDER BY match_time DESC LIMIT ?",
                (team_id, team_id, limit)
            )
            return [dict(r) for r in cur.fetchall()]

    def get_h2h(self, team1_id: str, team2_id: str, limit: int = 10) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                """SELECT * FROM matches WHERE
                ((home_team_id = ? AND away_team_id = ?) OR (home_team_id = ? AND away_team_id = ?))
                AND status = 'finished'
                ORDER BY match_time DESC LIMIT ?""",
                (team1_id, team2_id, team2_id, team1_id, limit)
            )
            return [dict(r) for r in cur.fetchall()]

    def get_by_competition(self, competition_id: str, status: str = "") -> list[dict]:
        with self.db.cursor() as cur:
            if status:
                cur.execute(
                    "SELECT * FROM matches WHERE competition_id = ? AND status = ? ORDER BY match_time DESC",
                    (competition_id, status)
                )
            else:
                cur.execute(
                    "SELECT * FROM matches WHERE competition_id = ? ORDER BY match_time DESC",
                    (competition_id,)
                )
            return [dict(r) for r in cur.fetchall()]
