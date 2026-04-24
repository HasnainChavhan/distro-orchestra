"""
DistroOrchestra — FastAPI Routes
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel

from app.api.websocket import dashboard_ws_endpoint
from app.orchestrator.command_orchestrator import CommandOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()
orchestrator = CommandOrchestrator()


class DispatchRequest(BaseModel):
    command: str
    environment_ids: Optional[list[str]] = None

    model_config = {"json_schema_extra": {
        "example": {
            "command": "echo 'Hello from DistroOrchestra'",
            "environment_ids": None,
        }
    }}


class ChaosRequest(BaseModel):
    environment_id: str


@router.post("/dispatch")
async def dispatch_command(request: DispatchRequest):
    """Fan-out a command to all target environments simultaneously."""
    dispatch = await orchestrator.dispatch(
        command=request.command,
        environment_ids=request.environment_ids,
    )
    return dispatch.to_dict()


@router.get("/dispatch/{command_id}")
async def get_dispatch(command_id: str):
    """Get the result of a dispatched command."""
    dispatch = orchestrator.get_dispatch(command_id)
    if not dispatch:
        raise HTTPException(status_code=404, detail=f"Command '{command_id}' not found")
    return dispatch.to_dict()


@router.get("/environments/health")
async def environment_health():
    """Get health metrics for all environments."""
    return {
        "environments": orchestrator.get_environment_health(),
        "circuit_breakers": orchestrator.get_circuit_breaker_status(),
        "dlq_size": orchestrator.get_dlq_size(),
    }


@router.post("/chaos/kill")
async def chaos_kill(request: ChaosRequest):
    """Chaos testing: kill a specific environment node."""
    orchestrator.simulate_environment_crash(request.environment_id)
    return {"message": f"Environment {request.environment_id} killed", "status": "unavailable"}


@router.post("/chaos/recover")
async def chaos_recover(request: ChaosRequest):
    """Recover a crashed environment node."""
    orchestrator.recover_environment(request.environment_id)
    return {"message": f"Environment {request.environment_id} recovered", "status": "healthy"}


@router.get("/dlq")
async def get_dlq():
    """Get current dead-letter queue contents."""
    return {"dlq_size": orchestrator.get_dlq_size()}


@router.delete("/dlq/drain")
async def drain_dlq():
    """Drain all entries from the dead-letter queue."""
    entries = orchestrator.drain_dlq()
    return {"drained": len(entries), "entries": entries}


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """Real-time operator dashboard via WebSocket."""
    await dashboard_ws_endpoint(websocket, orchestrator)


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "DistroOrchestra"}
