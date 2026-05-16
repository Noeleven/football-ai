"""教练数据模型."""
from pydantic import BaseModel
from typing import Optional


class CoachBase(BaseModel):
    coach_id: str
    name: str
    name_cn: str = ""
    nationality: str = ""
    birth_date: Optional[str] = None
    preferred_formation: str = "4-3-3"
    coaching_style: str = "balanced"
    team_id: str = ""
    team_name: str = ""
    photo_url: str = ""


class Coach(CoachBase):
    tenure_start: str = ""
    contract_until: Optional[str] = None
    achievements: list[str] = []
    win_rate: float = 0.0
    total_matches: int = 0
    trophies: list[str] = []
