"""Mock data generator for demonstration - 48 WC teams + top clubs + all data types."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from repositories.database import Database
from repositories.team_repo import TeamRepository
from repositories.player_repo import PlayerRepository
from repositories.match_repo import MatchRepository
from repositories.news_repo import NewsRepository
from utils.logger import get_logger

_logger = get_logger("mock_data")


# === WC 2026 48 teams ===
WC2026_TEAMS = [
    ("ARG", "Argentina", "阿根廷", "Messi International Stadium", "Argentina", "wc2026"),
    ("BRA", "Brazil", "巴西", "Maracanã", "Brazil", "wc2026"),
    ("FRA", "France", "法国", "Stade de France", "France", "wc2026"),
    ("GER", "Germany", "德国", "Allianz Arena", "Germany", "wc2026"),
    ("ENG", "England", "英格兰", "Wembley Stadium", "England", "wc2026"),
    ("ESP", "Spain", "西班牙", "Santiago Bernabéu", "Spain", "wc2026"),
    ("ITA", "Italy", "意大利", "San Siro", "Italy", "wc2026"),
    ("NED", "Netherlands", "荷兰", "Johan Cruyff Arena", "Netherlands", "wc2026"),
    ("POR", "Portugal", "葡萄牙", "Estádio da Luz", "Portugal", "wc2026"),
    ("BEL", "Belgium", "比利时", "King Baudouin Stadium", "Belgium", "wc2026"),
    ("URU", "Uruguay", "乌拉圭", "Estadio Centenario", "Uruguay", "wc2026"),
    ("CRO", "Croatia", "克罗地亚", "Stadion Maksimir", "Croatia", "wc2026"),
    ("DEN", "Denmark", "丹麦", "Parken Stadium", "Denmark", "wc2026"),
    ("COL", "Colombia", "哥伦比亚", "Estadio Metropolitano", "Colombia", "wc2026"),
    ("MEX", "Mexico", "墨西哥", "Estadio Azteca", "Mexico", "wc2026"),
    ("USA", "United States", "美国", "MetLife Stadium", "USA", "wc2026"),
    ("JPN", "Japan", "日本", "National Stadium", "Japan", "wc2026"),
    ("KOR", "South Korea", "韩国", "Seoul World Cup Stadium", "South Korea", "wc2026"),
    ("AUS", "Australia", "澳大利亚", "Stadium Australia", "Australia", "wc2026"),
    ("MAR", "Morocco", "摩洛哥", "Prince Moulay Abdellah", "Morocco", "wc2026"),
    ("SEN", "Senegal", "塞内加尔", "Stade de la Paix", "Senegal", "wc2026"),
    ("EGY", "Egypt", "埃及", "Cairo International Stadium", "Egypt", "wc2026"),
    ("GHA", "Ghana", "加纳", "Accra Sports Stadium", "Ghana", "wc2026"),
    ("CMR", "Cameroon", "喀麦隆", "Stade Omnisport", "Cameroon", "wc2026"),
    ("NGA", "Nigeria", "尼日利亚", "Teslim Balogun Stadium", "Nigeria", "wc2026"),
    ("ALG", "Algeria", "阿尔及利亚", "Stade 5 Juillet", "Algeria", "wc2026"),
    ("TUN", "Tunisia", "突尼斯", "Stade Olympique de Rades", "Tunisia", "wc2026"),
    ("ECU", "Ecuador", "厄瓜多尔", "Estadio Rodrigo Paz", "Ecuador", "wc2026"),
    ("CHI", "Chile", "智利", "Estadio Nacional", "Chile", "wc2026"),
    ("PER", "Peru", "秘鲁", "Estadio Nacional", "Peru", "wc2026"),
    ("PAR", "Paraguay", "巴拉圭", "Estadio Defensores del Chaco", "Paraguay", "wc2026"),
    ("VEN", "Venezuela", "委内瑞拉", "Estadio Monumental", "Venezuela", "wc2026"),
    ("IRN", "Iran", "伊朗", "Azadi Stadium", "Iran", "wc2026"),
    ("QAT", "Qatar", "卡塔尔", "Al Bayt Stadium", "Qatar", "wc2026"),
    ("KSA", "Saudi Arabia", "沙特阿拉伯", "King Fahd Stadium", "Saudi Arabia", "wc2026"),
    ("UAE", "UAE", "阿联酋", "Zabeel Stadium", "UAE", "wc2026"),
    ("IRQ", "Iraq", "伊拉克", "Al Madina Stadium", "Iraq", "wc2026"),
    ("AUSIA", "Australia (Asia)", "澳大利亚", "Stadium Australia", "Australia", "wc2026"),
    ("NZL", "New Zealand", "新西兰", "Eden Park", "New Zealand", "wc2026"),
    ("CRC", "Costa Rica", "哥斯达黎加", "Estadio Nacional", "Costa Rica", "wc2026"),
    ("PAN", "Panama", "巴拿马", "Estadio Rommel Fernández", "Panama", "wc2026"),
    ("HON", "Honduras", "洪都拉斯", "Estadio Olímpico", "Honduras", "wc2026"),
    ("JAM", "Jamaica", "牙买加", "Independence Park", "Jamaica", "wc2026"),
    ("CAN", "Canada", "加拿大", "BMO Field", "Canada", "wc2026"),
    ("POL", "Poland", "波兰", "National Stadium Warsaw", "Poland", "wc2026"),
    ("UKR", "Ukraine", "乌克兰", "NSK Olimpijskyj", "Ukraine", "wc2026"),
    ("SUI", "Switzerland", "瑞士", "Stade de Suisse", "Switzerland", "wc2026"),
    ("SWE", "Sweden", "瑞典", "Friends Arena", "Sweden", "wc2026"),
    ("NOR", "Norway", "挪威", "Ullevaal Stadion", "Norway", "wc2026"),
    ("AUT", "Austria", "奥地利", "Ernst-Happel-Stadion", "Austria", "wc2026"),
    ("CZE", "Czech Republic", "捷克", "Stadion Letná", "Czech Republic", "wc2026"),
    ("SCO", "Scotland", "苏格兰", "Hampden Park", "Scotland", "wc2026"),
    ("WAL", "Wales", "威尔士", "Cardiff City Stadium", "Wales", "wc2026"),
    ("SRB", "Serbia", "塞尔维亚", "Stadion Rajko Mitić", "Serbia", "wc2026"),
    ("GRE", "Greece", "希腊", "OPAP Arena", "Greece", "wc2026"),
    ("TUR", "Turkey", "土耳其", "Şanlıurfa Stadium", "Turkey", "wc2026"),
    ("ROU", "Romania", "罗马尼亚", "Arena Națională", "Romania", "wc2026"),
    ("HUN", "Hungary", "匈牙利", "Puskás Aréna", "Hungary", "wc2026"),
    ("SVK", "Slovakia", "斯洛伐克", "Stadion Národného", "Slovakia", "wc2026"),
    ("SLO", "Slovenia", "斯洛文尼亚", "Stadion Stožice", "Slovenia", "wc2026"),
    ("BIH", "Bosnia", "波黑", "Stadion Asim Ferhatović", "Bosnia", "wc2026"),
    ("ISL", "Iceland", "冰岛", "Laugardalsvöllur", "Iceland", "wc2026"),
    ("FIN", "Finland", "芬兰", "Helsinki Olympic Stadium", "Finland", "wc2026"),
    ("NIR", "Northern Ireland", "北爱尔兰", "Windsor Park", "Northern Ireland", "wc2026"),
    ("IRL", "Republic of Ireland", "爱尔兰", "Aviva Stadium", "Republic of Ireland", "wc2026"),
    ("BUL", "Bulgaria", "保加利亚", "Vasil Levski Stadium", "Bulgaria", "wc2026"),
    ("LTU", "Lithuania", "立陶宛", "LFF Stadium", "Lithuania", "wc2026"),
    ("LUX", "Luxembourg", "卢森堡", "Stade de Luxembourg", "Luxembourg", "wc2026"),
    ("EST", "Estonia", "爱沙尼亚", "A. Le Coq Arena", "Estonia", "wc2026"),
    ("LVA", "Latvia", "拉脱维亚", "Daugava Stadium", "Latvia", "wc2026"),
    ("MLT", "Malta", "马耳他", "Ta' Qali Stadium", "Malta", "wc2026"),
    ("CYP", "Cyprus", "塞浦路斯", "AEK Arena", "Cyprus", "wc2026"),
    ("AND", "Andorra", "安道尔", "Estadi Nacional", "Andorra", "wc2026"),
    ("SMR", "San Marino", "圣马力诺", "Stadio Olimpico", "San Marino", "wc2026"),
    ("LIE", "Liechtenstein", "列支敦士登", "Rheinpark Stadion", "Liechtenstein", "wc2026"),
    ("MKD", "North Macedonia", "北马其顿", "Toshe Proeski Arena", "North Macedonia", "wc2026"),
    ("ALB", "Albania", "阿尔巴尼亚", "Air Albania Stadium", "Albania", "wc2026"),
    ("MNE", "Montenegro", "黑山", "Stadion Pod Goricom", "Montenegro", "wc2026"),
]

STYLES = ["possession", "counter", "high_press", "direct", "balanced"]
FORMATIONS = ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "3-4-3"]

PLAYER_NAMES_CN = ["前锋A", "前锋B", "中场C", "中场D", "后卫E", "后卫F", "门将G"]
PLAYER_NAMES_EN = ["Striker One", "Striker Two", "Midfielder A", "Midfielder B", "Defender C", "Defender D", "Goalkeeper E"]

WC2026_GROUPS = {
    "A": ["USA", "CAN", "MEX", "CRC"],
    "B": ["BRA", "ARG", "COL", "PER"],
    "C": ["GER", "FRA", "NED", "BEL"],
    "D": ["ESP", "ITA", "ENG", "POR"],
    "E": ["URU", "ECU", "MAR", "EGY"],
    "F": ["CRO", "DEN", "POL", "UKR"],
    "G": ["SEN", "NGA", "GHA", "CMR"],
    "H": ["JPN", "KOR", "AUS", "KSA"],
}


def generate_all() -> None:
    """Generate all mock data."""
    Database.get_instance()
    team_repo = TeamRepository()
    player_repo = PlayerRepository()
    match_repo = MatchRepository()
    news_repo = NewsRepository()

    _logger.info("generating mock data...")

    # 1. Teams
    for i, (team_id, name, name_cn, stadium, country, comp) in enumerate(WC2026_TEAMS):
        team = {
            "team_id": team_id,
            "name": name,
            "name_cn": name_cn,
            "short_name": team_id,
            "founded_year": 1900 + (i * 3) % 124,
            "stadium": stadium,
            "stadium_capacity": 30000 + (i * 5000) % 80000,
            "city": stadium.split()[0] if stadium else country,
            "country": country,
            "league": comp,
            "competition_id": comp,
            "is_national": 1,
            "style": STYLES[i % len(STYLES)],
            "formation": FORMATIONS[i % len(FORMATIONS)],
            "manager_name": f"Manager {name}",
            "total_market_value": 100.0 + (i * 15.5) % 1500.0,
            "squad_size": 23,
        }
        team_repo.upsert(team)
        _logger.debug(f"team team_id={team_id} name={name}")

    # 2. Players (per team)
    for team_id, name, _, _, _, _ in WC2026_TEAMS:
        positions = ["GK", "DF", "DF", "MF", "MF", "MF", "FW"]
        for j, (pos, cn_name) in enumerate(zip(positions, PLAYER_NAMES_CN)):
            player = {
                "player_id": f"{team_id}-P{j+1:02d}",
                "name": f"{name} Player {j+1}",
                "name_cn": f"{cn_name}",
                "nationality": name.split()[0],
                "position": pos,
                "team_id": team_id,
                "team_name": name,
                "jersey_number": j + 1,
                "market_value": 5.0 + (j * 1.5),
                "is_key_player": 1 if j < 3 else 0,
                "strengths": ["传球", "跑位"] if j < 5 else ["防守"],
                "weaknesses": ["经验不足"],
                "injury_status": "fit",
                "injury_history": [],
            }
            player_repo.upsert(player)

    # 3. Matches (Group Stage WC 2026)
    now = datetime.now(timezone.utc)
    group_labels = list(WC2026_GROUPS.keys())
    match_day = 0
    for group, team_ids in WC2026_GROUPS.items():
        for i in range(len(team_ids)):
            for j in range(i + 1, len(team_ids)):
                match_day += 1
                match_time = now + timedelta(days=match_day, hours=14)
                m_id = f"WC2026-G{group}-{i+1}-{j+1}"
                home = team_repo.get_by_id(team_ids[i])
                away = team_repo.get_by_id(team_ids[j])
                match_repo.upsert({
                    "match_id": m_id,
                    "competition_id": "wc2026",
                    "competition_name": "FIFA World Cup 2026",
                    "round": f"Group {group}",
                    "match_time": match_time.isoformat(),
                    "venue": "USA/Canada/Mexico",
                    "status": "scheduled",
                    "home_team_id": team_ids[i],
                    "away_team_id": team_ids[j],
                    "home_team_name": home["name"] if home else team_ids[i],
                    "away_team_name": away["name"] if away else team_ids[j],
                })

    # 4. News
    news_items = [
        {
            "news_id": "news-001",
            "title": "世界杯2026赛程公布：48队分为8组",
            "content": "FIFA官方公布世界杯2026赛程，比赛将于2026年6月8日在美国开幕...",
            "news_type": "schedule",
            "competition_id": "wc2026",
            "team_ids": [],
            "source": "FIFA Official",
            "published_at": now.isoformat(),
            "created_at": now.isoformat(),
        },
        {
            "news_id": "news-002",
            "title": "阿根廷公布世界杯备战名单",
            "content": "阿根廷国家队主帅公布2026世界杯30人候选名单...",
            "news_type": "general",
            "competition_id": "wc2026",
            "team_ids": ["ARG"],
            "source": "AFA",
            "published_at": (now - timedelta(hours=5)).isoformat(),
            "created_at": now.isoformat(),
        },
        {
            "news_id": "news-003",
            "title": "皇马球员伤情更新：预计两周后复出",
            "content": "皇马队医确认主力中场伤情恢复良好...",
            "news_type": "injury",
            "competition_id": "ucl",
            "team_ids": ["BRA"],
            "player_ids": ["BRA-P003"],
            "source": "Real Madrid Official",
            "published_at": (now - timedelta(hours=2)).isoformat(),
            "created_at": now.isoformat(),
        },
    ]
    for n in news_items:
        news_repo.upsert(n)

    _logger.info(f"mock data generated teams={len(WC2026_TEAMS)} matches={match_day} news={len(news_items)}")


if __name__ == "__main__":
    generate_all()
