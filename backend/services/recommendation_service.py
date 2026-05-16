"""Personalized recommendation service based on user preferences and browsing history."""
import json
from typing import Optional
from datetime import datetime, timezone
from repositories.database import Database


class RecommendationService:
    """Generate personalized recommendations based on user behavior."""

    def __init__(self) -> None:
        self.db = Database.get_instance()

    def record_view(self, user_id: str, view_type: str, target_id: str) -> None:
        """Record a user view action for recommendation tracking."""
        now = datetime.now(timezone.utc).isoformat()
        with self.db.cursor() as cur:
            # Update user preferences based on view
            cur.execute(
                """SELECT id FROM user_preferences WHERE user_id = ?""",
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                # Update existing preferences
                field_map = {
                    "team": "viewed_teams",
                    "player": "viewed_players",
                    "match": "viewed_matches",
                }
                field = field_map.get(view_type)
                if field:
                    cur.execute(
                        f"""UPDATE user_preferences SET {field} = {field} || ? WHERE user_id = ?""",
                        (json.dumps([target_id]), user_id)
                    )
                cur.execute(
                    "UPDATE user_preferences SET updated_at = ? WHERE user_id = ?",
                    (now, user_id)
                )
            else:
                # Create new preferences record
                field_map = {
                    "team": ["viewed_teams", "[]"],
                    "player": ["viewed_players", "[]"],
                    "match": ["viewed_matches", "[]"],
                }
                team_field, team_default = field_map.get(view_type, ["viewed_teams", "[]"])
                cur.execute(
                    """INSERT INTO user_preferences (user_id, team_ids, player_ids, competition_ids, viewed_teams, viewed_players, viewed_matches, created_at, updated_at)
                       VALUES (?, '[]', '[]', '[]', ?, ?, ?, ?, ?)""",
                    (user_id, team_default, team_default, team_default, now, now)
                )

    def get_followed_teams(self, user_id: str) -> list[str]:
        """Get teams the user follows."""
        with self.db.cursor() as cur:
            cur.execute("SELECT team_ids FROM user_preferences WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row and row["team_ids"]:
                return json.loads(row["team_ids"])
            return []

    def get_recommended_teams(self, user_id: str, limit: int = 10) -> list[dict]:
        """Get recommended teams based on user preferences."""
        followed = self.get_followed_teams(user_id)
        if not followed:
            # Return popular teams
            with self.db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM teams ORDER BY total_market_value DESC LIMIT ?",
                    (limit,)
                )
                return [dict(r) for r in cur.fetchall()]

        # Get teams similar to followed teams (same competition/style)
        with self.db.cursor() as cur:
            placeholders = ",".join(["?" for _ in followed])
            cur.execute(
                f"""SELECT * FROM teams WHERE competition_id IN
                    (SELECT competition_id FROM teams WHERE team_id IN ({placeholders}))
                    AND team_id NOT IN ({placeholders})
                    ORDER BY total_market_value DESC LIMIT ?""",
                (*followed, *followed, limit)
            )
            return [dict(r) for r in cur.fetchall()]

    def get_recommended_matches(self, user_id: str, limit: int = 10) -> list[dict]:
        """Get recommended matches based on followed teams."""
        followed = self.get_followed_teams(user_id)
        if not followed:
            # Return upcoming matches
            with self.db.cursor() as cur:
                now = datetime.now(timezone.utc).isoformat()
                cur.execute(
                    "SELECT * FROM matches WHERE match_time > ? AND status = 'scheduled' ORDER BY match_time LIMIT ?",
                    (now, limit)
                )
                return [dict(r) for r in cur.fetchall()]

        with self.db.cursor() as cur:
            now = datetime.now(timezone.utc).isoformat()
            placeholders = ",".join(["?" for _ in followed])
            cur.execute(
                f"""SELECT * FROM matches WHERE match_time > ? AND status = 'scheduled'
                    AND (home_team_id IN ({placeholders}) OR away_team_id IN ({placeholders}))
                    ORDER BY match_time LIMIT ?""",
                (now, *followed, *followed, limit)
            )
            return [dict(r) for r in cur.fetchall()]

    def get_recommended_news(self, user_id: str, limit: int = 10) -> list[dict]:
        """Get recommended news based on followed teams and recent views."""
        followed = self.get_followed_teams(user_id)
        with self.db.cursor() as cur:
            if followed:
                placeholders = ",".join(["?" for _ in followed])
                cur.execute(
                    f"""SELECT * FROM news WHERE team_ids LIKE '%' || (
                        SELECT team_id FROM teams WHERE team_id IN ({placeholders}) LIMIT 1
                    ) || '%' ORDER BY published_at DESC LIMIT ?""",
                    (*followed, limit)
                )
                return [dict(r) for r in cur.fetchall()]
            else:
                cur.execute(
                    "SELECT * FROM news ORDER BY published_at DESC, view_count DESC LIMIT ?",
                    (limit,)
                )
                return [dict(r) for r in cur.fetchall()]

    def get_personalized_feed(self, user_id: str) -> dict:
        """Get complete personalized feed."""
        return {
            "teams": self.get_recommended_teams(user_id),
            "matches": self.get_recommended_matches(user_id),
            "news": self.get_recommended_news(user_id),
        }

    def follow_team(self, user_id: str, team_id: str) -> None:
        """Add a team to user's followed list."""
        with self.db.cursor() as cur:
            cur.execute("SELECT team_ids FROM user_preferences WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row:
                current = json.loads(row["team_ids"]) if row["team_ids"] else []
                if team_id not in current:
                    current.append(team_id)
                    cur.execute(
                        "UPDATE user_preferences SET team_ids = ?, updated_at = ? WHERE user_id = ?",
                        (json.dumps(current), datetime.now(timezone.utc).isoformat(), user_id)
                    )
            else:
                cur.execute(
                    """INSERT INTO user_preferences (user_id, team_ids, created_at, updated_at)
                       VALUES (?, ?, ?, ?)""",
                    (user_id, json.dumps([team_id]), datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat())
                )

    def unfollow_team(self, user_id: str, team_id: str) -> None:
        """Remove a team from user's followed list."""
        with self.db.cursor() as cur:
            cur.execute("SELECT team_ids FROM user_preferences WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row and row["team_ids"]:
                current = json.loads(row["team_ids"])
                if team_id in current:
                    current.remove(team_id)
                    cur.execute(
                        "UPDATE user_preferences SET team_ids = ?, updated_at = ? WHERE user_id = ?",
                        (json.dumps(current), datetime.now(timezone.utc).isoformat(), user_id)
                    )

    def subscribe_notification(self, user_id: str, subscription_type: str, target_id: str = "") -> None:
        """Subscribe user to notifications."""
        now = datetime.now(timezone.utc).isoformat()
        with self.db.cursor() as cur:
            cur.execute(
                """INSERT OR REPLACE INTO notification_subscriptions
                   (user_id, subscription_type, target_id, channel, is_active, created_at)
                   VALUES (?, ?, ?, 'websocket', 1, ?)""",
                (user_id, subscription_type, target_id, now)
            )

    def unsubscribe_notification(self, user_id: str, subscription_type: str, target_id: str = "") -> None:
        """Unsubscribe user from notifications."""
        with self.db.cursor() as cur:
            if target_id:
                cur.execute(
                    "DELETE FROM notification_subscriptions WHERE user_id = ? AND subscription_type = ? AND target_id = ?",
                    (user_id, subscription_type, target_id)
                )
            else:
                cur.execute(
                    "DELETE FROM notification_subscriptions WHERE user_id = ? AND subscription_type = ?",
                    (user_id, subscription_type)
                )