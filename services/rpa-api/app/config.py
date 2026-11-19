"""Centralized environment-based configuration for the RPA API service."""

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings loaded from environment variables."""

    service_name: str = "rpa-api"
    api_key: str = ""
    log_level: str = "INFO"
    robot_suite_path: Path = BASE_DIR / "robot" / "rpa_login.robot"
    robot_output_dir: Path = BASE_DIR / "results"
    rpa_timeout_seconds: int = 120

    @classmethod
    def from_env(cls) -> "Settings":
        """Build a Settings instance from the current process environment."""
        return cls(
            service_name=os.getenv("SERVICE_NAME", "rpa-api"),
            api_key=os.getenv("API_KEY", "").strip(),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            robot_suite_path=Path(
                os.getenv("ROBOT_SUITE_PATH", str(BASE_DIR / "robot" / "rpa_login.robot"))
            ),
            robot_output_dir=Path(
                os.getenv("ROBOT_OUTPUT_DIR", str(BASE_DIR / "results"))
            ),
            rpa_timeout_seconds=int(os.getenv("RPA_TIMEOUT_SECONDS", "120")),
        )
