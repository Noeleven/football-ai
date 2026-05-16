"""SQLite 数据库连接与初始化."""
import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from core.config import config


class Database:
    _instance: Optional["Database"] = None

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    @classmethod
    def get_instance(cls) -> "Database":
        if cls._instance is None:
            cls._instance = cls(config.db_path)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    @contextmanager
    def cursor(self):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


def init_db() -> None:
    """初始化数据库表结构."""
    db = Database.get_instance()
    with db.cursor() as cur:
        # Teams
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_cn TEXT DEFAULT '',
                short_name TEXT DEFAULT '',
                logo_url TEXT DEFAULT '',
                founded_year INTEGER,
                stadium TEXT DEFAULT '',
                stadium_capacity INTEGER DEFAULT 0,
                city TEXT DEFAULT '',
                country TEXT DEFAULT '',
                league TEXT DEFAULT '',
                competition_id TEXT DEFAULT '',
                is_national INTEGER DEFAULT 0,
                style TEXT DEFAULT 'balanced',
                formation TEXT DEFAULT '4-3-3',
                manager_name TEXT DEFAULT '',
                manager_nationality TEXT DEFAULT '',
                total_market_value REAL DEFAULT 0.0,
                avg_player_age REAL DEFAULT 0.0,
                squad_size INTEGER DEFAULT 0,
                updated_at TEXT
            )
        """)
        # Players
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_cn TEXT DEFAULT '',
                nationality TEXT DEFAULT '',
                birth_date TEXT,
                height_cm INTEGER,
                weight_kg INTEGER,
                position TEXT DEFAULT 'MF',
                preferred_foot TEXT DEFAULT 'right',
                team_id TEXT,
                team_name TEXT DEFAULT '',
                jersey_number INTEGER DEFAULT 0,
                market_value REAL DEFAULT 0.0,
                is_key_player INTEGER DEFAULT 0,
                strengths TEXT DEFAULT '[]',
                weaknesses TEXT DEFAULT '[]',
                injury_status TEXT DEFAULT 'fit',
                injury_history TEXT DEFAULT '[]',
                contract_until TEXT,
                photo_url TEXT DEFAULT '',
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)
        # Coaches
        cur.execute("""
            CREATE TABLE IF NOT EXISTS coaches (
                coach_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_cn TEXT DEFAULT '',
                nationality TEXT DEFAULT '',
                birth_date TEXT,
                preferred_formation TEXT DEFAULT '4-3-3',
                coaching_style TEXT DEFAULT 'balanced',
                team_id TEXT,
                team_name TEXT DEFAULT '',
                tenure_start TEXT DEFAULT '',
                contract_until TEXT,
                achievements TEXT DEFAULT '[]',
                win_rate REAL DEFAULT 0.0,
                total_matches INTEGER DEFAULT 0,
                trophies TEXT DEFAULT '[]',
                photo_url TEXT DEFAULT '',
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)
        # Matches
        cur.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id TEXT PRIMARY KEY,
                competition_id TEXT NOT NULL,
                competition_name TEXT DEFAULT '',
                round TEXT DEFAULT '',
                match_time TEXT NOT NULL,
                venue TEXT DEFAULT '',
                referee TEXT DEFAULT '',
                status TEXT DEFAULT 'scheduled',
                home_team_id TEXT NOT NULL,
                away_team_id TEXT NOT NULL,
                home_team_name TEXT DEFAULT '',
                away_team_name TEXT DEFAULT '',
                home_score INTEGER DEFAULT 0,
                away_score INTEGER DEFAULT 0,
                formation_home TEXT DEFAULT '',
                formation_away TEXT DEFAULT '',
                starting_xi_home TEXT DEFAULT '[]',
                starting_xi_away TEXT DEFAULT '[]',
                substitutes_home TEXT DEFAULT '[]',
                substitutes_away TEXT DEFAULT '[]',
                attendance INTEGER DEFAULT 0,
                updated_at TEXT,
                FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
                FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
            )
        """)
        # Match Events
        cur.execute("""
            CREATE TABLE IF NOT EXISTS match_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT NOT NULL,
                minute INTEGER,
                event_type TEXT,
                player TEXT DEFAULT '',
                team_id TEXT DEFAULT '',
                detail TEXT DEFAULT '',
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        # News
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news (
                news_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                summary TEXT DEFAULT '',
                news_type TEXT DEFAULT 'general',
                competition_id TEXT DEFAULT '',
                team_ids TEXT DEFAULT '[]',
                player_ids TEXT DEFAULT '[]',
                source TEXT DEFAULT '',
                source_url TEXT DEFAULT '',
                published_at TEXT,
                created_at TEXT,
                tags TEXT DEFAULT '[]',
                image_urls TEXT DEFAULT '[]',
                is_top INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0
            )
        """)
        # Predictions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id TEXT PRIMARY KEY,
                match_id TEXT NOT NULL,
                competition_id TEXT DEFAULT '',
                home_team_id TEXT NOT NULL,
                away_team_id TEXT NOT NULL,
                home_team_name TEXT DEFAULT '',
                away_team_name TEXT DEFAULT '',
                match_time TEXT,
                prediction_type TEXT DEFAULT 'pre_match',
                win_probabilities TEXT DEFAULT '[]',
                recommendation TEXT DEFAULT '',
                confidence_level TEXT DEFAULT '',
                predicted_formation_home TEXT DEFAULT '',
                predicted_formation_away TEXT DEFAULT '',
                predicted_starting_xi_home TEXT DEFAULT '[]',
                predicted_starting_xi_away TEXT DEFAULT '[]',
                score_prediction TEXT DEFAULT '{}',
                dimension_scores TEXT DEFAULT '[]',
                key_factors TEXT DEFAULT '[]',
                analysis_summary TEXT DEFAULT '',
                report_markdown TEXT DEFAULT '',
                generated_at TEXT,
                created_at TEXT
            )
        """)
        # Post-match analyses
        cur.execute("""
            CREATE TABLE IF NOT EXISTS post_match_analyses (
                analysis_id TEXT PRIMARY KEY,
                match_id TEXT NOT NULL,
                competition_id TEXT DEFAULT '',
                home_team_id TEXT NOT NULL,
                away_team_id TEXT NOT NULL,
                home_team_name TEXT DEFAULT '',
                away_team_name TEXT DEFAULT '',
                home_score INTEGER DEFAULT 0,
                away_score INTEGER DEFAULT 0,
                final_score TEXT DEFAULT '',
                prediction_accuracy TEXT DEFAULT '',
                偏差分析 TEXT DEFAULT '',
                match_events_summary TEXT DEFAULT '',
                tactical_summary TEXT DEFAULT '',
                key_performers TEXT DEFAULT '[]',
                turning_points TEXT DEFAULT '[]',
                stats_comparison TEXT DEFAULT '{}',
                report_markdown TEXT DEFAULT '',
                generated_at TEXT,
                created_at TEXT
            )
        """)
        # Query history
        cur.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT,
                query_type TEXT,
                results_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        # User preferences for personalized recommendations
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT '',
                team_ids TEXT DEFAULT '[]',
                player_ids TEXT DEFAULT '[]',
                competition_ids TEXT DEFAULT '[]',
                viewed_teams TEXT DEFAULT '[]',
                viewed_players TEXT DEFAULT '[]',
                viewed_matches TEXT DEFAULT '[]',
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Data source tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_url TEXT DEFAULT '',
                data_type TEXT NOT NULL,
                last_fetched_at TEXT,
                record_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT
            )
        """)

        # Notification subscriptions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notification_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT '',
                subscription_type TEXT NOT NULL,
                target_id TEXT DEFAULT '',
                channel TEXT DEFAULT 'websocket',
                is_active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)

        # Indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_type ON news(news_type)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_comp ON news(competition_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_matches_comp ON matches(competition_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_matches_time ON matches(match_time)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id)")

    print("[DB] Database initialized.")
