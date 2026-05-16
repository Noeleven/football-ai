"""AI Prediction Engine - Pre-match & Post-match analysis."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from config import settings
from models.prediction import PreMatchPrediction, PostMatchAnalysis, WinProbItem, ScorePrediction, DimensionScore
from services.ai.llm_service import LLMService
from repositories.prediction_repo import PredictionRepository
from repositories.team_repo import TeamRepository
from repositories.match_repo import MatchRepository
from utils.logger import get_logger

_logger = get_logger("ai.prediction")


class PredictionEngine:
    """Pre-match prediction engine."""

    def __init__(self) -> None:
        self._llm = LLMService.get_instance()
        self._pred_repo = PredictionRepository()
        self._team_repo = TeamRepository()
        self._match_repo = MatchRepository()

    def generate(self, match_id: str) -> PreMatchPrediction:
        """Generate pre-match prediction with caching."""
        existing = self._pred_repo.get_by_match(match_id)
        if existing:
            _logger.info(f"returning cached prediction match_id={match_id}")
            return self._parse_cached(existing)

        match = self._match_repo.get_by_id(match_id)
        if not match:
            raise ValueError(f"Match not found: {match_id}")

        home = self._team_repo.get_by_id(match["home_team_id"]) or {}
        away = self._team_repo.get_by_id(match["away_team_id"]) or {}
        h2h = self._match_repo.get_h2h(match["home_team_id"], match["away_team_id"], limit=10)

        analysis_data = self._build_analysis(home, away, h2h)
        pred_data = self._llm_predict(analysis_data)

        pred = PreMatchPrediction(
            prediction_id=f"pred-{uuid.uuid4().hex[:12]}",
            match_id=match_id,
            competition_id=match["competition_id"],
            home_team_id=match["home_team_id"],
            away_team_id=match["away_team_id"],
            home_team_name=match["home_team_name"],
            away_team_name=match["away_team_name"],
            match_time=datetime.fromisoformat(match["match_time"]),
            prediction_type="pre_match",
            win_probabilities=[
                WinProbItem(outcome="home_win", probability=pred_data.get("home_win_prob", 0.33)),
                WinProbItem(outcome="draw", probability=pred_data.get("draw_prob", 0.33)),
                WinProbItem(outcome="away_win", probability=pred_data.get("away_win_prob", 0.33)),
            ],
            recommendation=pred_data.get("recommendation", "draw"),
            confidence_level=pred_data.get("confidence", "medium"),
            predicted_formation_home=pred_data.get("formation_home", "4-3-3"),
            predicted_formation_away=pred_data.get("formation_away", "4-4-2"),
            predicted_starting_xi_home=pred_data.get("xi_home", []),
            predicted_starting_xi_away=pred_data.get("xi_away", []),
            score_prediction=ScorePrediction(
                home_goals=pred_data.get("score_home", 1),
                away_goals=pred_data.get("score_away", 1),
                confidence=pred_data.get("score_confidence", 0.5),
            ),
            dimension_scores=self._compute_scores(home, away),
            key_factors=pred_data.get("key_factors", []),
            analysis_summary=pred_data.get("summary", ""),
            report_markdown=pred_data.get("report", ""),
            generated_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )

        self._pred_repo.upsert_prediction(self._to_dict(pred))
        _logger.info(f"prediction generated match_id={match_id}")
        return pred

    def _build_analysis(self, home: dict, away: dict, h2h: list[dict]) -> dict:
        hw = sum(1 for m in h2h if m["home_team_id"] == home.get("team_id") and m["home_score"] > m["away_score"])
        aw = sum(1 for m in h2h if m["away_team_id"] == away.get("team_id") and m["home_score"] < m["away_score"])
        dr = sum(1 for m in h2h if m["home_score"] == m["away_score"])
        return {
            "home_name": home.get("name", "Unknown"),
            "away_name": away.get("name", "Unknown"),
            "home_style": home.get("style", "balanced"),
            "away_style": away.get("style", "counter"),
            "home_formation": home.get("formation", "4-3-3"),
            "away_formation": away.get("formation", "4-4-2"),
            "home_h2h_wins": hw,
            "away_h2h_wins": aw,
            "draws": dr,
            "h2h_total": len(h2h),
        }

    def _llm_predict(self, data: dict) -> dict:
        system = (
            "你是一位资深足球预测分析师。基于数据生成JSON格式预测结果。"
            "输出严格JSON，不要任何其他文字。格式：{"
            "\"recommendation\": \"strong_home|home|draw|away|strong_away\","
            "\"confidence\": \"high|medium|low\","
            "\"home_win_prob\": 0.XX,"
            "\"draw_prob\": 0.XX,"
            "\"away_win_prob\": 0.XX,"
            "\"score_home\": N,"
            "\"score_away\": N,"
            "\"score_confidence\": 0.XX,"
            "\"formation_home\": \"4-3-3\","
            "\"formation_away\": \"4-4-2\","
            "\"xi_home\": [\"player1\"],"
            "\"xi_away\": [\"player1\"],"
            "\"key_factors\": [\"factor1\"],"
            "\"summary\": \"摘要\","
            "\"report\": \"## Markdown报告\"}"
        )
        user = (
            f"主队：{data['home_name']}（阵型：{data['home_formation']}，风格：{data['home_style']}）\n"
            f"客队：{data['away_name']}（阵型：{data['away_formation']}，风格：{data['away_style']}）\n"
            f"历史交锋：主队{data['home_h2h_wins']}胜，客队{data['away_h2h_wins']}胜，平局{data['draws']}场（共{data['h2h_total']}场）\n"
            "请输出预测结果（JSON格式）："
        )
        try:
            raw = self._llm.chat_with_prompt(system, user, temperature=0.4, max_tokens=2048)
            start, end = raw.find("{"), raw.rfind("}") + 1
            if start != -1 and end != 0:
                return json.loads(raw[start:end])
        except Exception as e:
            _logger.warn(f"LLM failed using fallback error={e}")
        return self._fallback(data)

    def _fallback(self, data: dict) -> dict:
        hw, aw, dr = data["home_h2h_wins"], data["away_h2h_wins"], data["draws"]
        total = hw + aw + 1
        hp = hw / total * 0.4 + 0.3
        ap = aw / total * 0.4 + 0.3
        dp = max(0.0, 1.0 - hp - ap)
        rec = "home" if hp > ap + 0.1 else ("away" if ap > hp + 0.1 else "draw")
        return {
            "recommendation": rec, "confidence": "low",
            "home_win_prob": hp, "draw_prob": dp, "away_win_prob": ap,
            "score_home": 2, "score_away": 1, "score_confidence": 0.4,
            "formation_home": data["home_formation"], "formation_away": data["away_formation"],
            "xi_home": ["主力球员A", "主力球员B"], "xi_away": ["主力球员X", "主力球员Y"],
            "key_factors": ["历史交锋", "主场因素", "近期状态"],
            "summary": "规则引擎兜底预测",
            "report": f"## {data['home_name']} vs {data['away_name']}\n\n（LLM不可用，使用规则引擎）",
        }

    def _compute_scores(self, home: dict, away: dict) -> list[DimensionScore]:
        return [
            DimensionScore(dimension="form", score=0.5, weight=settings.weight_form, weighted_score=0.5 * settings.weight_form),
            DimensionScore(dimension="head_to_head", score=0.5, weight=settings.weight_head_to_head, weighted_score=0.5 * settings.weight_head_to_head),
            DimensionScore(dimension="tactics", score=0.5, weight=settings.weight_tactics, weighted_score=0.5 * settings.weight_tactics),
        ]

    def _to_dict(self, pred: PreMatchPrediction) -> dict:
        return {
            "prediction_id": pred.prediction_id,
            "match_id": pred.match_id,
            "competition_id": pred.competition_id,
            "home_team_id": pred.home_team_id,
            "away_team_id": pred.away_team_id,
            "home_team_name": pred.home_team_name,
            "away_team_name": pred.away_team_name,
            "match_time": pred.match_time.isoformat(),
            "prediction_type": pred.prediction_type,
            "win_probabilities": [p.model_dump() for p in pred.win_probabilities],
            "recommendation": pred.recommendation,
            "confidence_level": pred.confidence_level,
            "predicted_formation_home": pred.predicted_formation_home,
            "predicted_formation_away": pred.predicted_formation_away,
            "predicted_starting_xi_home": pred.predicted_starting_xi_home,
            "predicted_starting_xi_away": pred.predicted_starting_xi_away,
            "score_prediction": pred.score_prediction.model_dump(),
            "dimension_scores": [d.model_dump() for d in pred.dimension_scores],
            "key_factors": pred.key_factors,
            "analysis_summary": pred.analysis_summary,
            "report_markdown": pred.report_markdown,
            "generated_at": pred.generated_at.isoformat(),
            "created_at": pred.created_at.isoformat(),
        }

    def _parse_cached(self, row: dict) -> PreMatchPrediction:
        wp = json.loads(row["win_probabilities"]) if row["win_probabilities"] else []
        sp = json.loads(row["score_prediction"]) if row["score_prediction"] else {}
        ds = json.loads(row["dimension_scores"]) if row["dimension_scores"] else []
        return PreMatchPrediction(
            prediction_id=row["prediction_id"], match_id=row["match_id"],
            competition_id=row["competition_id"], home_team_id=row["home_team_id"],
            away_team_id=row["away_team_id"], home_team_name=row["home_team_name"],
            away_team_name=row["away_team_name"],
            match_time=datetime.fromisoformat(row["match_time"]),
            prediction_type=row["prediction_type"],
            win_probabilities=[WinProbItem(**w) for w in wp],
            recommendation=row["recommendation"], confidence_level=row["confidence_level"],
            predicted_formation_home=row["predicted_formation_home"],
            predicted_formation_away=row["predicted_formation_away"],
            predicted_starting_xi_home=json.loads(row["predicted_starting_xi_home"]) if row["predicted_starting_xi_home"] else [],
            predicted_starting_xi_away=json.loads(row["predicted_starting_xi_away"]) if row["predicted_starting_xi_away"] else [],
            score_prediction=ScorePrediction(**sp),
            dimension_scores=[DimensionScore(**d) for d in ds],
            key_factors=json.loads(row["key_factors"]) if row["key_factors"] else [],
            analysis_summary=row["analysis_summary"], report_markdown=row["report_markdown"],
            generated_at=datetime.fromisoformat(row["generated_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class PostMatchEngine:
    """Post-match analysis engine."""

    def __init__(self) -> None:
        self._llm = LLMService.get_instance()
        self._pred_repo = PredictionRepository()
        self._match_repo = MatchRepository()

    def generate(self, match_id: str) -> PostMatchAnalysis:
        """Generate post-match analysis with caching."""
        existing = self._pred_repo.get_post_match_by_match(match_id)
        if existing:
            return self._parse_cached(existing)

        match = self._match_repo.get_by_id(match_id)
        if not match:
            raise ValueError(f"Match not found: {match_id}")

        pre = self._pred_repo.get_by_match(match_id)
        pre_score = ""
        if pre:
            sp = json.loads(pre["score_prediction"]) if pre["score_prediction"] else {}
            pre_score = f"{sp.get('home_goals', '?')}-{sp.get('away_goals', '?')}"

        system = (
            "你是一位专业足球解说专家。基于比赛数据撰写赛后总结。"
            "输出严格JSON格式：{"
            "\"match_events_summary\": \"事件摘要\","
            "\"tactical_summary\": \"战术分析\","
            "\"key_performers\": [\"球员1\"],"
            "\"turning_points\": [\"转折点\"],"
            "\"prediction_accuracy\": \"准确/有偏差\","
            "\"偏差分析\": \"说明\","
            "\"report\": \"## Markdown报告\"}"
        )
        user = (
            f"比赛：{match['home_team_name']} {match['home_score']} - {match['away_score']} {match['away_team_name']}\n"
            f"主队阵型：{match.get('formation_home', '未知')}；客队阵型：{match.get('formation_away', '未知')}\n"
            f"赛前预测比分：{pre_score or '无'}\n"
        )
        try:
            raw = self._llm.chat_with_prompt(system, user, temperature=0.5, max_tokens=2048)
            start, end = raw.find("{"), raw.rfind("}") + 1
            if start != -1 and end != 0:
                data = json.loads(raw[start:end])
            else:
                data = {}
        except Exception:
            data = {}

        report = data.get("report", "")
        if report and not report.startswith("#"):
            report = f"## 赛后总结：{match['home_team_name']} {match['home_score']} - {match['away_score']} {match['away_team_name']}\n\n{report}"

        analysis = PostMatchAnalysis(
            analysis_id=f"analysis-{uuid.uuid4().hex[:12]}",
            match_id=match_id,
            competition_id=match["competition_id"],
            home_team_id=match["home_team_id"],
            away_team_id=match["away_team_id"],
            home_team_name=match["home_team_name"],
            away_team_name=match["away_team_name"],
            home_score=match["home_score"],
            away_score=match["away_score"],
            final_score=f"{match['home_score']}-{match['away_score']}",
            prediction_accuracy=data.get("prediction_accuracy", ""),
            偏差分析=data.get("偏差分析", ""),
            match_events_summary=data.get("match_events_summary", ""),
            tactical_summary=data.get("tactical_summary", ""),
            key_performers=data.get("key_performers", []),
            turning_points=data.get("turning_points", []),
            stats_comparison={},
            report_markdown=report,
            generated_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )

        self._pred_repo.upsert_post_match(self._to_dict(analysis))
        return analysis

    def _to_dict(self, a: PostMatchAnalysis) -> dict:
        return {
            "analysis_id": a.analysis_id, "match_id": a.match_id,
            "competition_id": a.competition_id, "home_team_id": a.home_team_id,
            "away_team_id": a.away_team_id, "home_team_name": a.home_team_name,
            "away_team_name": a.away_team_name, "home_score": a.home_score,
            "away_score": a.away_score, "final_score": a.final_score,
            "prediction_accuracy": a.prediction_accuracy, "偏差分析": a.偏差分析,
            "match_events_summary": a.match_events_summary,
            "tactical_summary": a.tactical_summary,
            "key_performers": a.key_performers, "turning_points": a.turning_points,
            "stats_comparison": a.stats_comparison, "report_markdown": a.report_markdown,
            "generated_at": a.generated_at.isoformat(), "created_at": a.created_at.isoformat(),
        }

    def _parse_cached(self, row: dict) -> PostMatchAnalysis:
        return PostMatchAnalysis(
            analysis_id=row["analysis_id"], match_id=row["match_id"],
            competition_id=row["competition_id"], home_team_id=row["home_team_id"],
            away_team_id=row["away_team_id"], home_team_name=row["home_team_name"],
            away_team_name=row["away_team_name"], home_score=row["home_score"],
            away_score=row["away_score"], final_score=row["final_score"],
            prediction_accuracy=row["prediction_accuracy"], 偏差分析=row["偏差分析"],
            match_events_summary=row["match_events_summary"],
            tactical_summary=row["tactical_summary"],
            key_performers=json.loads(row["key_performers"]) if row["key_performers"] else [],
            turning_points=json.loads(row["turning_points"]) if row["turning_points"] else [],
            stats_comparison=json.loads(row["stats_comparison"]) if row["stats_comparison"] else {},
            report_markdown=row["report_markdown"],
            generated_at=datetime.fromisoformat(row["generated_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
