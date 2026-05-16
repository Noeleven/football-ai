"""球员数据模型."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PlayerBase(BaseModel):
    player_id: str
    name: str
    name_cn: str = ""
    nationality: str = ""
    birth_date: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    position: str = "MF"
    preferred_foot: str = "right"
    team_id: str = ""
    team_name: str = ""
    jersey_number: int = 0
    market_value: float = 0.0
    is_key_player: bool = False


class PlayerStats(BaseModel):
    goals: int = 0
    assists: int = 0
    appearances: int = 0
    minutes_played: int = 0
    pass_accuracy: float = Field(ge=0.0, le=100.0, default=0.0)
    tackles: int = 0
    interceptions: int = 0
    shots_per_game: float = 0.0
    key_passes: float = 0.0
    dribble_success: float = Field(ge=0.0, le=100.0, default=0.0)
    rating: float = Field(ge=0.0, le=10.0, default=0.0)


class Player(PlayerBase):
    strengths: list[str] = []
    weaknesses: list[str] = []
    current_stats: Optional[PlayerStats] = None
    injury_status: str = "fit"
    injury_history: list[str] = []
    contract_until: Optional[str] = None
    photo_url: str = ""


class PlayerCreate(PlayerBase):
    pass
