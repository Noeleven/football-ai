"""新闻/资讯数据模型."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NewsBase(BaseModel):
    news_id: str
    title: str
    content: str
    news_type: str  # transfer, injury, schedule, operation, match_report, tactical, general
    competition_id: str = ""
    team_ids: list[str] = []
    player_ids: list[str] = []
    source: str = ""
    source_url: str = ""
    published_at: datetime
    created_at: datetime


class News(NewsBase):
    summary: str = ""
    tags: list[str] = []
    image_urls: list[str] = []
    is_top: bool = False
    view_count: int = 0


class NewsCreate(NewsBase):
    pass
