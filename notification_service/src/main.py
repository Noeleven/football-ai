"""Notification service - WebSocket, email channels with Redis pub/sub."""
import json
import asyncio
from datetime import datetime, timezone
from typing import Any, Optional
import redis.asyncio as redis

from utils.logger import get_logger

_logger = get_logger("notification")


class WebSocketChannel:
    """WebSocket notification channel."""

    def __init__(self) -> None:
        self._connections: dict[str, list[Any]] = {}

    async def connect(self, user_id: str, websocket: Any) -> None:
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)
        _logger.info(f"ws connect user_id={user_id}")

    async def disconnect(self, user_id: str, websocket: Any) -> None:
        if user_id in self._connections:
            try:
                self._connections[user_id].remove(websocket)
            except ValueError:
                pass

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> None:
        if user_id in self._connections:
            for ws in self._connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    _logger.error(f"ws send failed: {e}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        for user_id, connections in self._connections.items():
            for ws in connections:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    _logger.error(f"ws broadcast failed: {e}")

    def get_connection_count(self) -> int:
        return sum(len(v) for v in self._connections.values())


class EmailChannel:
    """Email notification channel."""

    def __init__(self, smtp_host: str = "", smtp_port: int = 587, smtp_user: str = "", smtp_password: str = "") -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self._enabled = bool(smtp_host and smtp_user)

    def send(self, to: str, subject: str, body: str) -> bool:
        if not self._enabled:
            _logger.info(f"email disabled, would send to {to}: {subject}")
            return True
        try:
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(body, "html")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            _logger.info(f"email sent to {to}")
            return True
        except Exception as e:
            _logger.error(f"email send failed: {e}")
            return False

    def send_match_reminder(self, to: str, match_info: dict[str, Any]) -> None:
        home = match_info.get("home_team_name", "Home")
        away = match_info.get("away_team_name", "Away")
        time = match_info.get("match_time", "TBD")
        subject = f"⚽ Match Reminder: {home} vs {away}"
        body = f"""
        <h2>Match Reminder</h2>
        <p><strong>{home}</strong> vs <strong>{away}</strong></p>
        <p>Time: {time}</p>
        <p>Don't miss the match!</p>
        """
        self.send(to, subject, body)

    def send_transfer_alert(self, to: str, transfer_info: dict[str, Any]) -> None:
        player = transfer_info.get("player_name", "Player")
        from_team = transfer_info.get("from_team", "")
        to_team = transfer_info.get("to_team", "")
        subject = f"🔄 Transfer Alert: {player}"
        body = f"""
        <h2>Transfer News</h2>
        <p><strong>{player}</strong> is moving from {from_team} to {to_team}!</p>
        """
        self.send(to, subject, body)


class NotificationTemplates:
    """HTML templates for notifications."""

    @staticmethod
    def match_reminder(match: dict[str, Any]) -> str:
        return f"""
        <html><body>
        <h2>⚽ Match Reminder</h2>
        <p><strong>{match['home_team_name']}</strong> vs <strong>{match['away_team_name']}</strong></p>
        <p>📅 Time: {match['match_time']}</p>
        <p>🏆 Competition: {match.get('competition_name', 'N/A')}</p>
        </body></html>
        """

    @staticmethod
    def transfer_alert(transfer: dict[str, Any]) -> str:
        return f"""
        <html><body>
        <h2>🔄 Transfer Alert</h2>
        <p><strong>{transfer['player_name']}</strong></p>
        <p>From: {transfer.get('from_team', 'N/A')}</p>
        <p>To: {transfer.get('to_team', 'N/A')}</p>
        <p>Fee: {transfer.get('transfer_fee', 'N/A')}</p>
        </body></html>
        """

    @staticmethod
    def injury_update(player: dict[str, Any]) -> str:
        return f"""
        <html><body>
        <h2>🏥 Injury Update</h2>
        <p><strong>{player['player_name']}</strong> - {player.get('injury_status', 'unknown')}</p>
        <p>Expected return: {player.get('expected_return', 'TBD')}</p>
        </body></html>
        """


class SubscriptionManager:
    """Manage user notification subscriptions."""

    def __init__(self) -> None:
        self._subs: dict[str, list[dict[str, Any]]] = {}

    def subscribe(self, user_id: str, subscription_type: str, target_id: str = "", channel: str = "websocket") -> None:
        if user_id not in self._subs:
            self._subs[user_id] = []
        self._subs[user_id].append({
            "type": subscription_type,
            "target_id": target_id,
            "channel": channel,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        _logger.info(f"subscribe user_id={user_id} type={subscription_type} target={target_id}")

    def unsubscribe(self, user_id: str, subscription_type: str, target_id: str = "") -> None:
        if user_id in self._subs:
            self._subs[user_id] = [
                s for s in self._subs[user_id]
                if not (s["type"] == subscription_type and (not target_id or s["target_id"] == target_id))
            ]

    def get_subscriptions(self, user_id: str) -> list[dict[str, Any]]:
        return self._subs.get(user_id, [])

    def get_users_for_target(self, subscription_type: str, target_id: str) -> list[str]:
        users = []
        for user_id, subs in self._subs.items():
            for s in subs:
                if s["type"] == subscription_type and s["target_id"] == target_id:
                    users.append(user_id)
                    break
        return users


class NotificationService:
    """Main notification service orchestrating all channels."""

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379) -> None:
        self._ws_channel = WebSocketChannel()
        self._email_channel = EmailChannel()
        self._subscription_manager = SubscriptionManager()
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.PubSub] = None
        try:
            self._redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        except Exception as e:
            _logger.warn(f"Redis unavailable: {e}")

    async def start(self) -> None:
        if self._redis:
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe("notifications")
            _logger.info("Notification service started with Redis pub/sub")
        else:
            _logger.info("Notification service started (without Redis)")

    async def stop(self) -> None:
        if self._pubsub:
            await self._pubsub.unsubscribe("notifications")
        _logger.info("Notification service stopped")

    async def notify_match_reminder(self, match_info: dict[str, Any]) -> None:
        """Send match reminder to subscribed users."""
        msg = {
            "type": "match_reminder",
            "data": match_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        if self._redis:
            await self._redis.publish("notifications", json.dumps(msg))

    async def notify_transfer(self, transfer_info: dict[str, Any]) -> None:
        """Send transfer alert."""
        msg = {
            "type": "transfer_alert",
            "data": transfer_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        if self._redis:
            await self._redis.publish("notifications", json.dumps(msg))

    async def notify_injury_update(self, player_info: dict[str, Any]) -> None:
        """Send injury update notification."""
        msg = {
            "type": "injury_update",
            "data": player_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        if self._redis:
            await self._redis.publish("notifications", json.dumps(msg))

    async def notify_prediction_ready(self, match_id: str, prediction: dict[str, Any]) -> None:
        """Notify that AI prediction is ready."""
        msg = {
            "type": "prediction_ready",
            "match_id": match_id,
            "data": prediction,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        if self._redis:
            await self._redis.publish("notifications", json.dumps(msg))

    def subscribe_user(self, user_id: str, subscription_type: str, target_id: str = "") -> None:
        self._subscription_manager.subscribe(user_id, subscription_type, target_id)

    def unsubscribe_user(self, user_id: str, subscription_type: str, target_id: str = "") -> None:
        self._subscription_manager.unsubscribe(user_id, subscription_type, target_id)

    def get_connection_count(self) -> int:
        return self._ws_channel.get_connection_count()


if __name__ == "__main__":
    async def main():
        service = NotificationService()
        await service.start()
        await asyncio.Future()
    asyncio.run(main())