"""AI预测结果数据模型."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WinProbItem(BaseModel):
    outcome: str
    probability: float = Field(ge=0.0, le=1.0)


class ScorePrediction(BaseModel):
    home_goals: int = Field(ge=0)
    away_goals: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)


class DimensionScore(BaseModel):
    dimension: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float
    weighted_score: float


class PreMatchPrediction(BaseModel):
    prediction_id: str
    match_id: str
    competition_id: str = ""
    home_team_id: str
    away_team_id: str
    home_team_name: str = ""
    away_team_name: str = ""
    match_time: datetime

    prediction_type: str = "pre_match"
    win_probabilities: list[WinProbItem] = []
    recommendation: str
    confidence_level: str
    predicted_formation_home: str = ""
    predicted_formation_away: str = ""
    predicted_starting_xi_home: list[str] = []
    predicted_starting_xi_away: list[str] = []
    score_prediction: ScorePrediction
    dimension_scores: list[DimensionScore] = []
    key_factors: list[str] = []
    analysis_summary: str = ""
    report_markdown: str = ""

    generated_at: datetime
    created_at: datetime


class PostMatchAnalysis(BaseModel):
    analysis_id: str
    match_id: str
    competition_id: str = ""
    home_team_id: str
    away_team_id: str
    home_team_name: str = ""
    away_team_name: str = ""

    home_score: int
    away_score: int
    final_score: str = ""

    prediction_accuracy: str = ""
    prediction偏差分析: str = ""

    match_events_summary: str = ""
    tactical_summary: str = ""
    key_performers: list[str] = []
    turning_points: list[str] = []

    stats_comparison: dict = {}

    report_markdown: str = ""
    generated_at: datetime
    created_at: datetime


class PredictionRequest(BaseModel):
    match_id: str
    home_team_id: str
    away_team_id: str
    analysis_dimensions: list[str] = []
