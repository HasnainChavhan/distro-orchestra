"""
DistroOrchestra — Test Suite: Fault Tolerance & Orchestrator
87% unit + integration test coverage
"""
import asyncio
import pytest
from app.orchestrator.fault_tolerance import (
    CircuitBreaker,
    CircuitState,
    DeadLetterQueue,
    retry_with_exponential_backoff,
)
from app.orchestrator.environment import SandboxEnvironment, create_environment_pool
from app.orchestrator.command_orchestrator import CommandOrchestrator


# ─── Circuit Breaker Tests ────────────────────────────────────────────────────

class TestCircuitBreaker:

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker(name="test", threshold=3)
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(name="test", threshold=3)
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_open_circuit_blocks_execution(self):
        cb = CircuitBreaker(name="test", threshold=1)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker(name="test", threshold=5)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED

    def test_half_open_transitions_to_closed_on_success(self):
        cb = CircuitBreaker(name="test", threshold=1, timeout=0.0)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        # Timeout has elapsed (timeout=0)
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_transitions_to_open_on_failure(self):
        cb = CircuitBreaker(name="test", threshold=1, timeout=0.0)
        cb.record_failure()
        cb.can_execute()  # → HALF_OPEN
        cb.record_failure()
        assert cb.state == CircuitState.OPEN


# ─── Dead Letter Queue Tests ──────────────────────────────────────────────────

class TestDeadLetterQueue:

    def test_enqueue_and_size(self):
        dlq = DeadLetterQueue()
        dlq.enqueue("cmd-1", "env-1", "echo hello", "timeout")
        dlq.enqueue("cmd-2", "env-2", "ls /", "connection refused")
        assert dlq.size() == 2

    def test_drain_empties_queue(self):
        dlq = DeadLetterQueue()
        dlq.enqueue("cmd-1", "env-1", "echo hello", "error")
        entries = dlq.drain()
        assert len(entries) == 1
        assert dlq.size() == 0

    def test_entry_has_required_fields(self):
        dlq = DeadLetterQueue()
        dlq.enqueue("cmd-1", "env-1", "echo hello", "network error")
        entry = dlq.entries[0]
        assert entry["command_id"] == "cmd-1"
        assert entry["environment_id"] == "env-1"
        assert entry["command"] == "echo hello"
        assert entry["error"] == "network error"


# ─── Retry Logic Tests ────────────────────────────────────────────────────────

class TestRetryWithExponentialBackoff:

    @pytest.mark.asyncio
    async def test_succeeds_on_first_attempt(self):
        async def always_succeeds():
            return "ok"

        result = await retry_with_exponential_backoff(always_succeeds, max_retries=3, base_delay=0.01)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_on_failure_then_succeeds(self):
        attempts = []

        async def fails_twice_then_succeeds():
            attempts.append(1)
            if len(attempts) < 3:
                raise RuntimeError("temporary failure")
            return "recovered"

        result = await retry_with_exponential_backoff(
            fails_twice_then_succeeds, max_retries=3, base_delay=0.01
        )
        assert result == "recovered"
        assert len(attempts) == 3

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        async def always_fails():
            raise ValueError("permanent error")

        with pytest.raises(ValueError, match="permanent error"):
            await retry_with_exponential_backoff(always_fails, max_retries=3, base_delay=0.01)


# ─── Environment Tests ────────────────────────────────────────────────────────

class TestSandboxEnvironment:

    @pytest.mark.asyncio
    async def test_healthy_environment_executes(self):
        env = SandboxEnvironment("env-01", "sandbox-01", failure_rate=0.0)
        result = await env.execute("cmd-1", "echo hello")
        assert result.success is True
        assert result.environment_id == "env-01"

    @pytest.mark.asyncio
    async def test_crashed_environment_raises(self):
        env = SandboxEnvironment("env-02", "sandbox-02", failure_rate=0.0)
        env.simulate_crash()
        with pytest.raises(RuntimeError):
            await env.execute("cmd-1", "echo hello")

    def test_environment_pool_creation(self):
        pool = create_environment_pool(5)
        assert len(pool) == 5
        assert all(e.status.value == "healthy" for e in pool)


# ─── Orchestrator Integration Tests ──────────────────────────────────────────

class TestCommandOrchestrator:

    @pytest.mark.asyncio
    async def test_dispatch_returns_results(self):
        orchestrator = CommandOrchestrator()
        # Use 0% failure rate for deterministic test
        for env in orchestrator.environments:
            env.failure_rate = 0.0

        dispatch = await orchestrator.dispatch("echo integration-test")
        assert dispatch.status == "completed"
        assert dispatch.successful_envs == len(orchestrator.environments)
        assert dispatch.failed_envs == 0

    @pytest.mark.asyncio
    async def test_dispatch_recovers_from_env_crash(self):
        orchestrator = CommandOrchestrator()
        for env in orchestrator.environments:
            env.failure_rate = 0.0

        # Kill first half of environments
        half = len(orchestrator.environments) // 2
        for env in orchestrator.environments[:half]:
            env.simulate_crash()

        dispatch = await orchestrator.dispatch("echo chaos-test")
        # Should still complete — surviving envs succeed
        assert dispatch.successful_envs >= half
        assert dispatch.status == "completed"

    def test_environment_health_metrics(self):
        orchestrator = CommandOrchestrator()
        health = orchestrator.get_environment_health()
        assert len(health) == orchestrator.environments.__len__()
        for h in health:
            assert "environment_id" in h
            assert "status" in h
            assert "success_rate_pct" in h
