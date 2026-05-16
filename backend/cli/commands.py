"""CLI commands - query, predict, seed, server."""
import sys
import json
import argparse
from datetime import datetime, timezone

from repositories.database import Database, init_db
from repositories.team_repo import TeamRepository
from repositories.player_repo import PlayerRepository
from repositories.match_repo import MatchRepository
from repositories.news_repo import NewsRepository
from services.ai.prediction_engine import PredictionEngine, PostMatchEngine
from utils.logger import get_logger, new_trace_id

logger = get_logger(__name__)


def cmd_list_teams(competition_id: str = "") -> None:
    repo = TeamRepository()
    teams = repo.get_all(competition_id)
    print(f"\n{'='*60}")
    print(f"球队列表 ({len(teams)} 支球队)")
    print(f"{'='*60}")
    for t in teams:
        print(f"  [{t['team_id']}] {t['name']} ({t.get('name_cn', '')}) - {t.get('style', 'N/A')}")
    print()


def cmd_list_matches(status: str = "upcoming", competition_id: str = "", limit: int = 10) -> None:
    repo = MatchRepository()
    if status == "upcoming":
        matches = repo.get_upcoming(competition_id, limit)
    else:
        matches = repo.get_recent(competition_id, limit)
    print(f"\n{'='*60}")
    label = "近期比赛" if status == "recent" else "即将开赛"
    print(f"{label} ({len(matches)} 场)")
    print(f"{'='*60}")
    for m in matches:
        time_str = m["match_time"][:16].replace("T", " ")
        print(f"  [{m['match_id']}] {m['home_team_name']} vs {m['away_team_name']}")
        print(f"    时间: {time_str} | 赛事: {m['competition_name']} | 阶段: {m.get('round', 'N/A')}")
    print()


def cmd_search(keyword: str) -> None:
    team_repo = TeamRepository()
    player_repo = PlayerRepository()
    news_repo = NewsRepository()

    print(f"\n搜索关键词: {keyword}")
    print(f"{'='*60}")

    teams = team_repo.search(keyword)
    print(f"\n球队 ({len(teams)}):")
    for t in teams[:5]:
        print(f"  [{t['team_id']}] {t['name']} ({t.get('name_cn', '')})")

    players = player_repo.search(keyword)
    print(f"\n球员 ({len(players)}):")
    for p in players[:5]:
        print(f"  [{p['player_id']}] {p['name']} - {p.get('team_name', '')} ({p.get('position', '')})")

    news = news_repo.search(keyword)
    print(f"\n资讯 ({len(news)}):")
    for n in news[:5]:
        print(f"  [{n['news_id']}] {n['title']}")


def cmd_predict(match_id: str) -> None:
    trace_id = new_trace_id()
    logger.info("cli predict", match_id=match_id, trace_id=trace_id)
    engine = PredictionEngine()
    try:
        result = engine.generate(match_id)
        print(f"\n{'='*60}")
        print(f"赛前预测报告")
        print(f"{'='*60}")
        print(f"比赛: {result.home_team_name} vs {result.away_team_name}")
        print(f"推荐: {result.recommendation} (置信度: {result.confidence_level})")
        print(f"比分预测: {result.score_prediction.home_goals}-{result.score_prediction.away_goals}")
        print(f"主队阵型: {result.predicted_formation_home}")
        print(f"客队阵型: {result.predicted_formation_away}")
        print(f"\n胜率:")
        for wp in result.win_probabilities:
            print(f"  {wp.outcome}: {wp.probability:.1%}")
        print(f"\n关键因素:")
        for f in result.key_factors:
            print(f"  - {f}")
        print(f"\n分析摘要: {result.analysis_summary}")
        print(f"\n{result.report_markdown}")
    except ValueError as e:
        print(f"错误: {e}")


def cmd_analyze(match_id: str) -> None:
    trace_id = new_trace_id()
    logger.info("cli analyze", match_id=match_id, trace_id=trace_id)
    engine = PostMatchEngine()
    try:
        result = engine.generate(match_id)
        print(f"\n{'='*60}")
        print(f"赛后总结报告")
        print(f"{'='*60}")
        print(f"比赛: {result.home_team_name} {result.home_score} - {result.away_score} {result.away_team_name}")
        print(f"\n预测准确性: {result.prediction_accuracy}")
        print(f"事件摘要: {result.match_events_summary}")
        print(f"战术分析: {result.tactical_summary}")
        print(f"关键球员: {', '.join(result.key_performers)}")
        print(f"\n{result.report_markdown}")
    except ValueError as e:
        print(f"错误: {e}")


def cmd_news(limit: int = 20) -> None:
    repo = NewsRepository()
    news = repo.get_recent(limit=limit)
    print(f"\n{'='*60}")
    print(f"最新资讯 ({len(news)} 条)")
    print(f"{'='*60}")
    for n in news:
        pub = n["published_at"][:16].replace("T", " ")
        print(f"  [{pub}] [{n['news_type']}] {n['title']}")
    print()


def cmd_seed() -> None:
    from data.mock.mock_data_generator import generate_all
    Database.get_instance()
    init_db()
    generate_all()
    print("数据初始化完成！")


def cmd_server() -> None:
    import uvicorn
    from api.routes import app
    print("启动 API 服务: http://0.0.0.0:8000")
    print("API 文档: http://0.0.0.0:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)


def main() -> None:
    parser = argparse.ArgumentParser(description="Football AI Platform CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # seed
    sub.add_parser("seed", help="初始化数据库并加载模拟数据")

    # teams
    teams_p = sub.add_parser("teams", help="列出球队")
    teams_p.add_argument("--competition", "-c", default="", help="按赛事筛选")

    # matches
    matches_p = sub.add_parser("matches", help="列出比赛")
    matches_p.add_argument("--status", "-s", choices=["upcoming", "recent"], default="upcoming")
    matches_p.add_argument("--competition", "-c", default="")
    matches_p.add_argument("--limit", "-n", type=int, default=10)

    # news
    news_p = sub.add_parser("news", help="最新资讯")
    news_p.add_argument("--limit", "-n", type=int, default=20)

    # search
    search_p = sub.add_parser("search", help="搜索")
    search_p.add_argument("keyword", help="搜索关键词")

    # predict
    pred_p = sub.add_parser("predict", help="赛前预测")
    pred_p.add_argument("match_id", help="比赛ID")

    # analyze
    ana_p = sub.add_parser("analyze", help="赛后分析")
    ana_p.add_argument("match_id", help="比赛ID")

    # server
    sub.add_parser("server", help="启动 API 服务")

    args = parser.parse_args()

    if args.cmd == "seed":
        cmd_seed()
    elif args.cmd == "teams":
        cmd_list_teams(args.competition)
    elif args.cmd == "matches":
        cmd_list_matches(args.status, args.competition, args.limit)
    elif args.cmd == "news":
        cmd_news(args.limit)
    elif args.cmd == "search":
        cmd_search(args.keyword)
    elif args.cmd == "predict":
        cmd_predict(args.match_id)
    elif args.cmd == "analyze":
        cmd_analyze(args.match_id)
    elif args.cmd == "server":
        cmd_server()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
