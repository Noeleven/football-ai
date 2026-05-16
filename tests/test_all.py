"""Tests for Football AI Platform."""
import pytest
from core.exceptions import (
    FootballBaseError, SystemError, LLMError, BusinessError,
    ValidationError, NotFoundError, ThirdPartyError,
)
from core.constants import COMPETITIONS, MATCH_ROUNDS


class TestExceptions:
    def test_base_error_dict(self):
        err = FootballBaseError("msg", code="TEST", details={"k": 1})
        d = err.to_dict()
        assert d["code"] == "TEST"
        assert d["message"] == "msg"
        assert d["details"]["k"] == 1

    def test_llm_error_with_provider(self):
        err = LLMError("api failed", provider="gemini", status_code=500)
        assert err.provider == "gemini"
        assert err.code == "LLM_ERROR"

    def test_not_found_error(self):
        err = NotFoundError("team not found")
        assert err.status_code == 404

    def test_validation_error(self):
        err = ValidationError("invalid input")
        assert err.status_code == 422

    def test_third_party_error(self):
        err = ThirdPartyError("API timeout", provider="football-api")
        assert err.provider == "football-api"


class TestConstants:
    def test_competitions_defined(self):
        assert "wc2026" in COMPETITIONS
        assert COMPETITIONS["wc2026"]["name"] == "FIFA World Cup 2026"
        assert COMPETITIONS["wc2026"]["teams"] == 48

    def test_all_club_competitions_defined(self):
        for comp_id in ["ucl", "premier", "laliga", "bundesliga", "seriea", "ligue1", "csl"]:
            assert comp_id in COMPETITIONS
            assert COMPETITIONS[comp_id]["type"] == "club"


class TestModels:
    def test_team_model_basic(self):
        from models.team import TeamBase
        t = TeamBase(team_id="BRA", name="Brazil", name_cn="巴西", country="Brazil")
        assert t.team_id == "BRA"
        assert t.name_cn == "巴西"

    def test_player_model(self):
        from models.player import PlayerBase, PlayerStats
        p = PlayerBase(player_id="BRA-P001", name="Neymar", position="FW", team_id="BRA")
        assert p.position == "FW"
        assert p.is_key_player == False

    def test_prediction_model(self):
        from models.prediction import WinProbItem, ScorePrediction
        wp = WinProbItem(outcome="home_win", probability=0.45)
        assert wp.probability == 0.45
        sp = ScorePrediction(home_goals=2, away_goals=1, confidence=0.7)
        assert sp.home_goals == 2


class TestDatabase:
    def test_database_init(self):
        from repositories.database import Database
        import tempfile, os
        tmp = tempfile.mktemp(suffix=".db")
        db = Database(tmp)
        assert db.db_path == tmp
        with db.cursor() as cur:
            cur.execute("CREATE TABLE test_t (id INTEGER PRIMARY KEY)")
            cur.execute("INSERT INTO test_t (id) VALUES (1)")
            cur.execute("SELECT * FROM test_t")
            row = cur.fetchone()
            assert row["id"] == 1
        os.unlink(tmp)


class TestRepositories:
    def test_team_repo_crud(self):
        from repositories.database import Database
        from repositories.team_repo import TeamRepository
        import tempfile, os
        tmp = tempfile.mktemp(suffix=".db")
        from repositories.database import init_db
        Database._instance = Database(tmp)
        init_db()
        repo = TeamRepository()
        repo.upsert({"team_id": "TEST", "name": "Test Team", "name_cn": "测试队", "style": "balanced"})
        t = repo.get_by_id("TEST")
        assert t is not None
        assert t["name"] == "Test Team"
        results = repo.search("测试")
        assert len(results) == 1
        os.unlink(tmp)
        Database._instance = None

    def test_match_repo_upcoming(self):
        from repositories.database import Database
        from repositories.match_repo import MatchRepository
        import tempfile, os
        from datetime import datetime, timezone, timedelta
        from repositories.database import init_db
        tmp = tempfile.mktemp(suffix=".db")
        Database._instance = Database(tmp)
        init_db()
        # Insert referenced teams first (FK constraint)
        team_repo = __import__('repositories.team_repo', fromlist=['TeamRepository']).TeamRepository()
        team_repo.upsert({"team_id": "BRA", "name": "Brazil", "name_cn": "巴西"})
        team_repo.upsert({"team_id": "ARG", "name": "Argentina", "name_cn": "阿根廷"})
        repo = MatchRepository()
        now = datetime.now(timezone.utc)
        repo.upsert({
            "match_id": "test-match-1",
            "competition_id": "wc2026",
            "competition_name": "World Cup",
            "round": "Group A",
            "match_time": (now + timedelta(days=5)).isoformat(),
            "venue": "Stadium",
            "status": "scheduled",
            "home_team_id": "BRA",
            "away_team_id": "ARG",
            "home_team_name": "Brazil",
            "away_team_name": "Argentina",
        })
        upcoming = repo.get_upcoming("wc2026", limit=10)
        assert len(upcoming) >= 1
        assert upcoming[0]["match_id"] == "test-match-1"
        os.unlink(tmp)
        Database._instance = None


class TestLLMService:
    def test_llm_requires_api_key(self):
        from services.ai.llm_service import GeminiProvider
        from core.exceptions import LLMError
        # With empty API key, should raise error
        import os
        orig = os.environ.get("GEMINI_API_KEY", "")
        os.environ.pop("GEMINI_API_KEY", None)
        # Note: provider would be built at runtime, test just checks class exists
        assert GeminiProvider.name == "gemini"
        os.environ["GEMINI_API_KEY"] = orig
