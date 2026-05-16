"""FastAPI routes - all endpoints."""
from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Any
from datetime import datetime, timezone

from config import settings
from repositories.team_repo import TeamRepository
from repositories.player_repo import PlayerRepository
from repositories.match_repo import MatchRepository
from repositories.news_repo import NewsRepository
from repositories.prediction_repo import PredictionRepository
from services.ai.prediction_engine import PredictionEngine, PostMatchEngine
from utils.logger import get_logger

_logger = get_logger("api")

app = FastAPI(title="Football AI Platform", version="1.0.0", docs_url="/docs")


# === Health ===
@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "time": datetime.now(timezone.utc).isoformat()}


# === Teams ===
@app.get("/api/teams")
def list_teams(competition_id: str = ""):
    repo = TeamRepository()
    teams = repo.get_all(competition_id)
    return {"code": "SUCCESS", "data": teams, "total": len(teams)}


@app.get("/api/teams/{team_id}")
def get_team(team_id: str):
    repo = TeamRepository()
    team = repo.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"code": "SUCCESS", "data": team}


@app.get("/api/teams/search/{keyword}")
def search_teams(keyword: str):
    repo = TeamRepository()
    results = repo.search(keyword)
    return {"code": "SUCCESS", "data": results, "total": len(results)}


# === Players ===
@app.get("/api/players/{team_id}")
def list_players(team_id: str):
    repo = PlayerRepository()
    players = repo.get_by_team(team_id)
    return {"code": "SUCCESS", "data": players, "total": len(players)}


@app.get("/api/players/key/{team_id}")
def key_players(team_id: str):
    repo = PlayerRepository()
    players = repo.get_key_players(team_id)
    return {"code": "SUCCESS", "data": players, "total": len(players)}


@app.get("/api/players/search/{keyword}")
def search_players(keyword: str):
    repo = PlayerRepository()
    results = repo.search(keyword)
    return {"code": "SUCCESS", "data": results, "total": len(results)}


# === Matches ===
@app.get("/api/matches/upcoming")
def upcoming_matches(competition_id: str = "", limit: int = Query(default=20, le=100)):
    repo = MatchRepository()
    matches = repo.get_upcoming(competition_id, limit)
    return {"code": "SUCCESS", "data": matches, "total": len(matches)}


@app.get("/api/matches/recent")
def recent_matches(competition_id: str = "", limit: int = Query(default=20, le=100)):
    repo = MatchRepository()
    matches = repo.get_recent(competition_id, limit)
    return {"code": "SUCCESS", "data": matches, "total": len(matches)}


@app.get("/api/matches/{match_id}")
def get_match(match_id: str):
    repo = MatchRepository()
    match = repo.get_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"code": "SUCCESS", "data": match}


@app.get("/api/matches/h2h/{team1}/{team2}")
def head_to_head(team1: str, team2: str, limit: int = 10):
    repo = MatchRepository()
    matches = repo.get_h2h(team1, team2, limit)
    return {"code": "SUCCESS", "data": matches, "total": len(matches)}


# === News ===
@app.get("/api/news")
def list_news(
    news_type: str = "",
    competition_id: str = "",
    limit: int = Query(default=50, le=200),
):
    repo = NewsRepository()
    news = repo.get_recent(news_type, competition_id, limit)
    return {"code": "SUCCESS", "data": news, "total": len(news)}


@app.get("/api/news/{news_id}")
def get_news(news_id: str):
    repo = NewsRepository()
    news = repo.get_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return {"code": "SUCCESS", "data": news}


# === AI Predictions ===
@app.post("/api/predict/{match_id}")
def predict_match(match_id: str):
    try:
        engine = PredictionEngine()
        result = engine.generate(match_id)
        return {"code": "SUCCESS", "data": result.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _logger.error(f"prediction failed match_id={match_id} error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/recent")
def recent_predictions(limit: int = Query(default=20, le=50)):
    repo = PredictionRepository()
    preds = repo.get_recent(limit)
    return {"code": "SUCCESS", "data": preds, "total": len(preds)}


@app.post("/api/analysis/{match_id}")
def analyze_match(match_id: str):
    try:
        engine = PostMatchEngine()
        result = engine.generate(match_id)
        return {"code": "SUCCESS", "data": result.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _logger.error(f"analysis failed match_id={match_id} error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/recent")
def recent_analyses(limit: int = Query(default=20, le=50)):
    repo = PredictionRepository()
    analyses = repo.get_post_match_recent(limit)
    return {"code": "SUCCESS", "data": analyses, "total": len(analyses)}


# === Competitions ===
@app.get("/api/competitions")
def list_competitions():
    from core.constants import COMPETITIONS
    data = [{"id": k, **v} for k, v in COMPETITIONS.items()]
    return {"code": "SUCCESS", "data": data}
