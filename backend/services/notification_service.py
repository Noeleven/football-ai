"""Notification service for WebSocket, email, push notifications."""
import json
import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

from utils.logger import get_logger

_logger = get_logger("notification")


class WebSocketChannel:
    """WebSocket notification channel using connection manager."""

    def __init__(self) -> None:
        self._enabled = True

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> None:
        from api.websocket import manager
        await manager.send_to_user(user_id, message)

    async def broadcast(self, message: dict[str, Any]) -> None:
        from api.websocket import manager
        await manager.broadcast(message)


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
            _logger.info(f"Email disabled, would send to {to}: {subject}")
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
            _logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            _logger.error(f"Email send failed: {e}")
            return False


class NotificationService:
    """Main notification service coordinating all channels."""

    def __init__(self) -> None:
        self._ws_channel = WebSocketChannel()
        self._email_channel = EmailChannel()

    async def notify_match_reminder(self, match_info: dict[str, Any]) -> None:
        """Send match reminder notification."""
        msg = {
            "type": "match_reminder",
            "data": match_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        _logger.info(f"Match reminder sent: {match_info.get('match_id')}")

    async def notify_transfer_alert(self, transfer_info: dict[str, Any]) -> None:
        """Send transfer alert notification."""
        msg = {
            "type": "transfer_alert",
            "data": transfer_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        _logger.info(f"Transfer alert sent: {transfer_info.get('player_name')}")

    async def notify_injury_update(self, player_info: dict[str, Any]) -> None:
        """Send injury update notification."""
        msg = {
            "type": "injury_update",
            "data": player_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        _logger.info(f"Injury update sent: {player_info.get('player_name')}")

    async def notify_prediction_ready(self, match_id: str, prediction: dict[str, Any]) -> None:
        """Notify that AI prediction is ready."""
        msg = {
            "type": "prediction_ready",
            "match_id": match_id,
            "data": prediction,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._ws_channel.broadcast(msg)
        _logger.info(f"Prediction ready: {match_id}")

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email notification."""
        return self._email_channel.send(to, subject, body)


notification_service = NotificationService()