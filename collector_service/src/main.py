"""Data collector service - news, matches, transfers with scheduler."""
import httpx
from datetime import datetime, timezone
from typing import Any
from bs4 import BeautifulSoup
import uuid
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers import interval

from utils.logger import get_logger

_logger = get_logger("collector")


class BaseCollector:
    """Base collector with common HTTP functionality."""

    def __init__(self, name: str, base_url: str) -> None:
        self.name = name
        self.base_url = base_url
        self._client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, path: str) -> str:
        url = f"{self.base_url}{path}"
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.text

    async def fetch_json(self, path: str) -> dict[str, Any]:
        resp = await self._client.get(path)
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        await self._client.aclose()


class NewsCollector(BaseCollector):
    """Collect sports news from configured sources."""

    def __init__(self) -> None:
        super().__init__("news", "https://api.espn.com/v3")

    async def collect(self) -> list[dict[str, Any]]:
        """Collect latest news."""
        news_items = []
        try:
            # Placeholder - in production, implement actual API calls
            _logger.info(f"[{self.name}] Collecting news...")
            news_items.append({
                "news_id": f"news-{uuid.uuid4().hex[:12]}",
                "title": "Collected news item",
                "content": "News content here",
                "news_type": "general",
                "source": self.name,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            _logger.error(f"[{self.name}] collection failed: {e}")
        return news_items


class MatchCollector(BaseCollector):
    """Collect match schedules and results."""

    def __init__(self) -> None:
        super().__init__("matches", "https://api.espn.com/v3")

    async def collect_upcoming(self, competition_id: str = "") -> list[dict[str, Any]]:
        """Collect upcoming matches."""
        matches = []
        try:
            _logger.info(f"[{self.name}] Collecting matches for {competition_id or 'all competitions'}...")
        except Exception as e:
            _logger.error(f"[{self.name}] collection failed: {e}")
        return matches


class TransferCollector(BaseCollector):
    """Collect transfer market information."""

    def __init__(self) -> None:
        super().__init__("transfers", "https://api.transfermarkt.com/v3")

    async def collect(self) -> list[dict[str, Any]]:
        """Collect transfer news."""
        transfers = []
        try:
            _logger.info(f"[{self.name}] Collecting transfers...")
        except Exception as e:
            _logger.error(f"[{self.name}] collection failed: {e}")
        return transfers


class DataWriter:
    """Write collected data to backend API."""

    def __init__(self, backend_url: str = "http://localhost:8000") -> None:
        self.backend_url = backend_url
        self._client = httpx.Client(timeout=30.0)

    def write_news(self, news_items: list[dict[str, Any]]) -> None:
        for item in news_items:
            try:
                self._client.post(f"{self.backend_url}/api/news", json=item)
                _logger.info(f"wrote news: {item['title']}")
            except Exception as e:
                _logger.error(f"failed to write news: {e}")

    def write_matches(self, matches: list[dict[str, Any]]) -> None:
        for match in matches:
            try:
                self._client.post(f"{self.backend_url}/api/matches", json=match)
                _logger.info(f"wrote match: {match.get('match_id', 'unknown')}")
            except Exception as e:
                _logger.error(f"failed to write match: {e}")

    def close(self) -> None:
        self._client.close()


class CronScheduler:
    """Scheduler for periodic data collection."""

    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()
        self._news_collector = NewsCollector()
        self._match_collector = MatchCollector()
        self._transfer_collector = TransferCollector()
        self._writer = DataWriter()

    async def job_collect_news(self) -> None:
        news = await self._news_collector.collect()
        if news:
            self._writer.write_news(news)

    async def job_collect_matches(self) -> None:
        matches = await self._match_collector.collect_upcoming()
        if matches:
            self._writer.write_matches(matches)

    def start(self, news_interval: int = 60, match_interval: int = 15) -> None:
        self._scheduler.add_job(self.job_collect_news, interval(minutes=news_interval), id="news_collector")
        self._scheduler.add_job(self.job_collect_matches, interval(minutes=match_interval), id="match_collector")
        self._scheduler.start()
        _logger.info(f"Scheduler started - news every {news_interval}m, matches every {match_interval}m")

    def stop(self) -> None:
        self._scheduler.shutdown()
        _logger.info("Scheduler stopped")


async def main() -> None:
    """Run collector service."""
    scheduler = CronScheduler()
    scheduler.start(news_interval=60, match_interval=15)
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())