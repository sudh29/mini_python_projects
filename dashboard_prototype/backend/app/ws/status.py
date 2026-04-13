"""
WebSocket handler for real-time bot status updates.

Clients connect at /ws/status?token=<jwt> and receive push updates
whenever a bot status changes.
"""

import asyncio
from typing import Dict, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt

from app.config import settings

router = APIRouter()

# ── Connection Manager ───────────────────────────────────────────
class ConnectionManager:
    """Manages WebSocket connections grouped by client_id."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        async with self._lock:
            if client_id not in self._connections:
                self._connections[client_id] = set()
            self._connections[client_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, client_id: str):
        async with self._lock:
            if client_id in self._connections:
                self._connections[client_id].discard(websocket)
                if not self._connections[client_id]:
                    del self._connections[client_id]

    async def broadcast_to_client(self, client_id: str, message: dict):
        """Send a message to all connections for a specific client."""
        async with self._lock:
            connections = self._connections.get(client_id, set()).copy()

        dead = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        # Clean up dead connections
        for ws in dead:
            await self.disconnect(ws, client_id)

    async def broadcast_all(self, message: dict):
        """Broadcast to all connected clients."""
        async with self._lock:
            all_clients = list(self._connections.keys())

        for client_id in all_clients:
            await self.broadcast_to_client(client_id, message)

    @property
    def active_connections(self) -> int:
        return sum(len(conns) for conns in self._connections.values())


# Singleton
manager = ConnectionManager()


# ── WebSocket Endpoint ───────────────────────────────────────────
@router.websocket("/ws/status")
async def websocket_status(
    websocket: WebSocket,
    token: str = Query(default=""),
):
    """
    WebSocket endpoint for real-time status updates.
    Authenticates via JWT token in query param.
    """
    # Authenticate
    client_id = _authenticate_ws(token)
    if not client_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(websocket, client_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "Real-time status updates active",
        })

        # Keep connection alive — listen for client messages
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0,
                )
                # Handle ping/pong keepalive
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, client_id)


def _authenticate_ws(token: str) -> Optional[str]:
    """Validate JWT and return client_id, or None if invalid."""
    if not token:
        return None

    # Allow demo-token in debug mode so the dashboard is always demo-able
    if settings.DEBUG and token == "demo-token":
        return "demo-client"

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("client_id")
    except (JWTError, KeyError):
        return None
