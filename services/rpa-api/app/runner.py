"""Execution engine for running Robot Framework suites safely with concurrency control."""

import logging
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from app.config import Settings

logger = logging.getLogger("rpa-api.runner")


class RPARunnerBusyError(RuntimeError):
    """Raised when a Robot Framework execution is already running."""


class RPASuiteNotFoundError(FileNotFoundError):
    """Raised when the configured `.robot` suite file does not exist."""


class RPATimeoutError(TimeoutError):
    """Raised when the Robot Framework process exceeds the configured timeout."""


class RPABinaryMissingError(FileNotFoundError):
    """Raised when the `robot` CLI executable is unavailable."""


@dataclass(frozen=True)
class ExecutionResult:
    """Outcome of a single Robot Framework subprocess invocation."""

    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float


class RobotRunner:
    """Thread-safe wrapper around Robot Framework CLI execution."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._running: bool = False
        self._last_run_at: str | None = None
        self._last_status: str | None = None
        self._last_returncode: int | None = None

    def get_status(self) -> dict[str, object]:
        """Return a snapshot of runner state and last execution metadata."""
        with self._state_lock:
            return {
                "running": self._running,
                "last_run_at": self._last_run_at,
                "last_status": self._last_status,
                "last_returncode": self._last_returncode,
            }

    def run(self, settings: Settings) -> ExecutionResult:
        """Execute the configured Robot Framework suite while preventing overlapping runs."""
        if not settings.robot_suite_path.exists():
            logger.error("Robot suite not found at %s", settings.robot_suite_path)
            raise RPASuiteNotFoundError(
                f"Archivo de suite Robot Framework no encontrado: {settings.robot_suite_path}"
            )

        if not self._lock.acquire(blocking=False):
            logger.warning("Rejected concurrent RPA execution request because a run is active.")
            raise RPARunnerBusyError(
                "Ya existe una ejecución del bot en curso. Intenta nuevamente en unos segundos."
            )

        with self._state_lock:
            self._running = True

        started_at = time.monotonic()
        try:
            settings.robot_output_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                "robot",
                "--outputdir",
                str(settings.robot_output_dir),
                str(settings.robot_suite_path),
            ]
            logger.info("Starting Robot Framework suite: %s", settings.robot_suite_path.name)

            try:
                completed = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=settings.rpa_timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                self._record_state(status="timeout", returncode=None)
                logger.exception(
                    "Robot Framework execution exceeded timeout (%ss).",
                    settings.rpa_timeout_seconds,
                )
                raise RPATimeoutError(
                    f"La ejecución del bot excedió el tiempo límite de "
                    f"{settings.rpa_timeout_seconds}s."
                ) from exc
            except FileNotFoundError as exc:
                self._record_state(status="error", returncode=None)
                logger.exception("Robot Framework executable ('robot') not found in PATH.")
                raise RPABinaryMissingError(
                    "El ejecutable 'robot' no está disponible en el entorno."
                ) from exc

            duration = round(time.monotonic() - started_at, 2)
            status = "success" if completed.returncode == 0 else "error"
            self._record_state(status=status, returncode=completed.returncode)
            logger.info(
                "Finished Robot Framework suite with returncode=%s in %.2fs",
                completed.returncode,
                duration,
            )

            return ExecutionResult(
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_seconds=duration,
            )
        finally:
            with self._state_lock:
                self._running = False
            self._lock.release()

    def _record_state(self, status: str, returncode: int | None) -> None:
        with self._state_lock:
            self._last_run_at = datetime.now(timezone.utc).isoformat()
            self._last_status = status
            self._last_returncode = returncode
