"""业务常量与枚举."""
from enum import Enum
from typing import Final


# ====== 赛事 ======
COMPETITIONS: Final[dict] = {
    "wc2026": {"name": "FIFA World Cup 2026", "short": "世界杯", "type": "international", "teams": 48},
    "euro2028": {"name": "UEFA Euro 2028", "short": "欧洲杯", "type": "international", "teams": 24},
    "asian_cup": {"name": "AFC Asian Cup", "short": "亚洲杯", "type": "international", "teams": 24},
    "copa_america": {"name": "Copa America", "short": "美洲杯", "type": "international", "teams": 12},
    "ucl": {"name": "UEFA Champions League", "short": "欧冠", "type": "club", "teams": 36},
    "premier": {"name": "Premier League", "short": "英超", "type": "club", "teams": 20},
    "laliga": {"name": "La Liga", "short": "西甲", "type": "club", "teams": 20},
    "bundesliga": {"name": "Bundesliga", "short": "德甲", "type": "club", "teams": 18},
    "seriea": {"name": "Serie A", "short": "意甲", "type": "club", "teams": 20},
    "ligue1": {"name": "Ligue 1", "short": "法甲", "type": "club", "teams": 18},
    "csl": {"name": "Chinese Super League", "short": "中超", "type": "club", "teams": 16},
}


# ====== Enums ======
class CompetitionType(str, Enum):
    INTERNATIONAL = "international"
    CLUB = "club"


class NewsType(str, Enum):
    TRANSFER = "transfer"       # 转会
    INJURY = "injury"          # 伤病
    SCHEDULE = "schedule"       # 赛程
    OPERATION = "operation"    # 运营
    MATCH_REPORT = "match_report"  # 赛事报告
    TACTICAL = "tactical"       # 战术
    GENERAL = "general"         # 综合


class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    HALFTIME = "halftime"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class PredictionType(str, Enum):
    PRE_MATCH = "pre_match"
    HALF_TIME = "half_time"
    LIVE = "live"
    POST_MATCH = "post_match"


class WinProbability(str, Enum):
    HOME_WIN = "home_win"
    DRAW = "draw"
    AWAY_WIN = "away_win"


class Recommendation(str, Enum):
    STRONG_HOME = "strong_home"
    HOME = "home"
    DRAW = "draw"
    AWAY = "away"
    STRONG_AWAY = "strong_away"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TeamStyle(str, Enum):
    POSSESSION = "possession"
    COUNTER = "counter"
    HIGH_PRESS = "high_press"
    DIRECT = "direct"
    BALANCED = "balanced"


class FormationType(str, Enum):
    FOUR_FOUR_TWO = "4-4-2"
    FOUR_THREE_THREE = "4-3-3"
    THREE_FIVE_TWO = "3-5-2"
    FOUR_TWO_THREE_ONE = "4-2-3-1"
    THREE_FOUR_THREE = "3-4-3"


class PlayerPosition(str, Enum):
    GK = "GK"
    DF = "DF"
    MF = "MF"
    FW = "FW"


# ====== 阶段 ======
MATCH_ROUNDS: Final[dict] = {
    "wc2026": ["Group Stage", "Round of 16", "Quarter Finals", "Semi Finals", "Third Place", "Final"],
    "ucl": ["League Phase", "Knockout Round", "Quarter Finals", "Semi Finals", "Final"],
    "premier": ["Matchday 1-38"],
}
