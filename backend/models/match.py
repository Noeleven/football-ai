"""比赛数据模型."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MatchBase(BaseModel):
    match_id: str
    competition_id: str
    competition_name: str = ""
    round: str = ""
    match_time: datetime
    venue: str = ""
    referee: str = ""
    status: str = "scheduled"


class MatchTeamInfo(BaseModel):
    team_id: str
    team_name: str
    score: int = 0
    formation: str = ""
    starting_xi: list[str] = []
    substitutes: list[str] = []


class MatchStats(BaseModel):
    possession: dict[str, int] = {}  # {"home": 55, "away": 45}
    shots: dict[str, int] = {}
    shots_on_target: dict[str, int] = {}
    passes: dict[str, int] = {}
    pass_accuracy: dict[str, float] = {}
    tackles: dict[str, int] = {}
    interceptions: dict[str, int] = {}
    fouls: dict[str, int] = {}
    yellow_cards: dict[str, int] = {}
    red_cards: dict[str, int] = {}
    corners: dict[str, int] = {}


class MatchEvent(BaseModel):
    minute: int
    event_type: str  # goal, yellow_card, red_card, substitution
    player: str = ""
    team_id: str = ""
    detail: str = ""


class Match(MatchBase):
    home_team: MatchTeamInfo
    away_team: MatchTeamInfo
    home_score: int = 0
    away_score: int = 0
    stats: Optional[MatchStats] = None
    events: list[MatchEvent] = []
    attendance: int = 0
    updated_at: Optional[datetime] = None


class MatchCreate(MatchBase):
    home_team_id: str
    away_team_id: str
