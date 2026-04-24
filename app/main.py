"""
DistroOrchestra — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"⚡ {settings.app_name} v{settings.app_version} starting up")
    yield
    logger.info("DistroOrchestra shutting down")


app = FastAPI(
    title="DistroOrchestra",
    description=(
        "Distributed Command Orchestration Platform. "
        "Fan-out commands to 20+ isolated environments simultaneously, "
        "collect results, reconcile with full fault tolerance, "
        "and stream live progress via WebSocket."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "DistroOrchestra",
        "version": settings.app_version,
        "docs": "/docs",
        "ws_dashboard": "/api/v1/ws/dashboard",
    }
