"""
DistroOrchestra — Sandboxed Environment Model
Represents an isolated execution environment node.
"""
import asyncio
import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EnvironmentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    BUSY = "busy"


@dataclass
class ExecutionResult:
    environment_id: str
    command_id: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    exit_code: int = 0

    def to_dict(self) -> dict:
        return {
            "environment_id": self.environment_id,
            "command_id": self.command_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "exit_code": self.exit_code,
        }


class SandboxEnvironment:
    """
    Represents an isolated sandboxed execution environment.

    In production, this wraps a Docker container, VM, or Lambda function.
    Provides an async execute() interface that the orchestrator calls.
    """

    def __init__(self, env_id: str, name: str, failure_rate: float = 0.05):
        self.env_id = env_id
        self.name = name
        self.failure_rate = failure_rate  # Simulated failure rate for testing
        self.status = EnvironmentStatus.HEALTHY
        self.commands_executed = 0
        self.commands_failed = 0
        self.total_execution_time_ms = 0.0

    async def execute(self, command_id: str, command: str) -> ExecutionResult:
        """
        Execute a command in this sandboxed environment.

        Simulates realistic execution with variable latency and
        configurable failure rate for chaos testing.
        """
        import time
        start = time.monotonic()

        # Simulate execution latency (10–200ms)
        await asyncio.sleep(random.uniform(0.01, 0.2))

        # Simulate environment failures for chaos testing
        if random.random() < self.failure_rate or self.status == EnvironmentStatus.UNAVAILABLE:
            self.commands_failed += 1
            elapsed = (time.monotonic() - start) * 1000
            self.total_execution_time_ms += elapsed
            raise RuntimeError(
                f"Environment '{self.env_id}' execution failed (simulated fault)"
            )

        elapsed = (time.monotonic() - start) * 1000
        self.commands_executed += 1
        self.total_execution_time_ms += elapsed

        return ExecutionResult(
            environment_id=self.env_id,
            command_id=command_id,
            success=True,
            output=f"[{self.name}] OK: {command}",
            execution_time_ms=elapsed,
            exit_code=0,
        )

    def simulate_crash(self):
        """Mark this environment as unavailable (for chaos testing)."""
        self.status = EnvironmentStatus.UNAVAILABLE

    def recover(self):
        """Restore this environment to healthy status."""
        self.status = EnvironmentStatus.HEALTHY

    def health_metrics(self) -> dict:
        total = self.commands_executed + self.commands_failed
        success_rate = (self.commands_executed / total * 100) if total > 0 else 100.0
        avg_latency = (
            self.total_execution_time_ms / self.commands_executed
            if self.commands_executed > 0
            else 0.0
        )
        return {
            "environment_id": self.env_id,
            "name": self.name,
            "status": self.status.value,
            "commands_executed": self.commands_executed,
            "commands_failed": self.commands_failed,
            "success_rate_pct": round(success_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
        }


def create_environment_pool(count: int = 20) -> list[SandboxEnvironment]:
    """Create a pool of sandboxed environments."""
    return [
        SandboxEnvironment(
            env_id=str(uuid.uuid4())[:8],
            name=f"sandbox-{i:02d}",
            failure_rate=0.05,  # 5% simulated failure rate
        )
        for i in range(1, count + 1)
    ]
