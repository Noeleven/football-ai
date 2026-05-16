"""球队数据模型."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TeamBase(BaseModel):
    team_id: str
    name: str
    name_cn: str = ""
    short_name: str = ""
    logo_url: str = ""
    founded_year: Optional[int] = None
    stadium: str = ""
    stadium_capacity: int = 0
    city: str = ""
    country: str = ""
    league: str = ""
    competition_id: str = ""
    is_national: bool = False


class TeamStats(BaseModel):
    """技术统计."""
    avg_possession: float = Field(ge=0.0, le=100.0, description="平均控球率%")
    avg_shots_per_game: float = Field(ge=0.0)
    avg_shots_on_target: float = Field(ge=0.0)
    avg_goals_scored: float = Field(ge=0.0)
    avg_goals_conceded: float = Field(ge=0.0)
    pass_accuracy: float = Field(ge=0.0, le=100.0)
    avg_goals_scored_last5: float = Field(ge=0.0)
    win_rate: float = Field(ge=0.0, le=1.0)
    clean_sheet_rate: float = Field(ge=0.0, le=1.0)
    home_win_rate: float = Field(ge=0.0, le=1.0)
    away_win_rate: float = Field(ge=0.0, le=1.0)


class Team(TeamBase):
    style: str = "balanced"
    formation: str = "4-3-3"
    manager_name: str = ""
    manager_nationality: str = ""
    total_market_value: float = 0.0
    avg_player_age: float = 0.0
    stats: Optional[TeamStats] = None
    squad_size: int = 0
    updated_at: Optional[datetime] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    stadium: Optional[str] = None
    style: Optional[str] = None
    formation: Optional[str] = None
    manager_name: Optional[str] = None
    stats: Optional[TeamStats] = None
