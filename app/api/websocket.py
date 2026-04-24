"""
DistroOrchestra — WebSocket Real-Time Dashboard
Live task progress, error rates, and environment health per node.
"""
import asyncio
import json
import logging
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections for real-time dashboard.
    Broadcasts orchestration events to all connected operators.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WS client connected. Total: {len(self.active_connections)}")
        await self.send_personal(websocket, {
            "event": "connected",
            "message": "Connected to DistroOrchestra live dashboard",
            "active_connections": len(self.active_connections),
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WS client disconnected. Total: {len(self.active_connections)}")

    async def send_personal(self, websocket: WebSocket, data: dict):
        """Send a message to a single client."""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.warning(f"Failed to send personal WS message: {e}")

    async def broadcast(self, data: dict):
        """
        Broadcast a message to all connected dashboard clients.
        Automatically removes dead connections.
        """
        dead = set()
        for ws in self.active_connections:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.add(ws)

        for ws in dead:
            self.active_connections.discard(ws)

    def connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()


async def dashboard_ws_endpoint(websocket: WebSocket, orchestrator):
    """
    WebSocket endpoint for the real-time operator dashboard.

    Streams:
    - dispatch_started / dispatch_completed events
    - Per-environment health deltas
    - DLQ size changes
    - Circuit breaker state changes
    """
    await manager.connect(websocket)

    # Register broadcast callback on orchestrator
    orchestrator.register_ws_broadcast(manager.broadcast)

    try:
        while True:
            # Keep connection alive + handle client messages
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=10.0
                )
                msg = json.loads(data)

                # Handle client commands
                if msg.get("action") == "get_health":
                    await manager.send_personal(websocket, {
                        "event": "health_snapshot",
                        "environments": orchestrator.get_environment_health(),
                        "circuit_breakers": orchestrator.get_circuit_breaker_status(),
                        "dlq_size": orchestrator.get_dlq_size(),
                    })
                elif msg.get("action") == "ping":
                    await manager.send_personal(websocket, {"event": "pong"})

            except asyncio.TimeoutError:
                # Send heartbeat
                await manager.send_personal(websocket, {
                    "event": "heartbeat",
                    "active_connections": manager.connection_count(),
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
