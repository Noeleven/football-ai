"""WebSocket endpoints for real-time notifications."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Any
import json

from services.notification_service import NotificationService
from utils.logger import get_logger

_logger = get_logger("websocket")

router = APIRouter()

# Global connection manager
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        _logger.info(f"WebSocket connected: user_id={user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
            except ValueError:
                pass
        _logger.info(f"WebSocket disconnected: user_id={user_id}")

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> None:
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    _logger.error(f"Failed to send to {user_id}: {e}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    _logger.error(f"Failed to broadcast to {user_id}: {e}")

    def get_connection_count(self) -> int:
        return sum(len(v) for v in self.active_connections.values())


manager = ConnectionManager()


@router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time notifications."""
    # Get user_id from query params or generate a temp one
    user_id = websocket.query_params.get("user_id", f"anon-{id(websocket)}")
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Handle subscription messages
                if msg.get("action") == "subscribe":
                    # Handle subscription logic
                    pass
                elif msg.get("action") == "unsubscribe":
                    # Handle unsubscription logic
                    pass
            except json.JSONDecodeError:
                _logger.warn(f"Invalid JSON from {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        _logger.error(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(websocket, user_id)


@router.websocket("/ws/match/{match_id}")
async def match_websocket(websocket: WebSocket, match_id: str) -> None:
    """WebSocket for match-specific updates."""
    user_id = websocket.query_params.get("user_id", f"anon-{id(websocket)}")
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive, handle match updates
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        _logger.error(f"Match WebSocket error for {user_id}: {e}")
        manager.disconnect(websocket, user_id)


@router.get("/ws/status")
async def ws_status() -> dict[str, Any]:
    """Get WebSocket connection status."""
    return {
        "active_connections": manager.get_connection_count(),
        "status": "healthy",
    }