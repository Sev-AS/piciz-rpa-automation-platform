"""FastAPI application exposing HTTP endpoints to trigger and monitor PICIZ RPA flows."""

import logging
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import Settings
from app.models import HealthResponse, RPAResponse, RPAStatusResponse
from app.runner import (
    RobotRunner,
    RPABinaryMissingError,
    RPARunnerBusyError,
    RPASuiteNotFoundError,
    RPATimeoutError,
)

settings = Settings.from_env()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rpa-api")

runner = RobotRunner()

app = FastAPI(
    title="PICIZ RPA Automation API",
    description=(
        "Microservicio FastAPI para orquestar, proteger y monitorear flujos RPA en "
        "Robot Framework (Playwright + PostgreSQL) hacia el portal PICIZ."
    ),
    version="2.0.0",
)


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Validate the X-API-Key header when API_KEY is configured in the environment."""
    current_settings = Settings.from_env()
    if not current_settings.api_key:
        logger.warning(
            "API_KEY is not configured; RPA endpoints are running without authentication."
        )
        return

    if not x_api_key or not secrets.compare_digest(x_api_key, current_settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credencial inválida o ausente en la cabecera X-API-Key.",
        )


def _execute_rpa() -> JSONResponse:
    """Run the Robot Framework suite and map execution outcomes to HTTP responses."""
    current_settings = Settings.from_env()
    try:
        result = runner.run(current_settings)
    except RPARunnerBusyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except RPATimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except (RPASuiteNotFoundError, RPABinaryMissingError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    is_success = result.returncode == 0
    payload = RPAResponse(
        status="success" if is_success else "error",
        mensaje="Bot ejecutado correctamente" if is_success else "La ejecución del bot falló",
        returncode=result.returncode,
        duration_seconds=result.duration_seconds,
        salida=result.stdout,
        error_log=result.stderr,
    )
    http_status = status.HTTP_200_OK if is_success else status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(status_code=http_status, content=payload.model_dump())


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Monitoring"],
    summary="Verificar salud del servicio",
)
def health_check() -> HealthResponse:
    """Return service liveness state."""
    return HealthResponse(status="ok", service=settings.service_name)


@app.get(
    "/api/v1/rpa/status",
    response_model=RPAStatusResponse,
    tags=["Monitoring"],
    summary="Consultar estado de ejecución del bot",
    dependencies=[Depends(verify_api_key)],
)
def rpa_status() -> RPAStatusResponse:
    """Return whether an RPA job is currently running and metadata from the last run."""
    return RPAStatusResponse(**runner.get_status())


@app.post(
    "/api/v1/rpa/register-visitor",
    response_model=RPAResponse,
    tags=["RPA"],
    summary="Ejecutar registro del último visitante en PICIZ",
    dependencies=[Depends(verify_api_key)],
)
def register_visitor() -> JSONResponse:
    """Trigger the Robot Framework workflow to register the latest visitor in PICIZ."""
    return _execute_rpa()


@app.get(
    "/ejecutar-login",
    response_model=RPAResponse,
    tags=["RPA (Compatibilidad)"],
    summary="Alias GET compatible para integraciones existentes en n8n",
    dependencies=[Depends(verify_api_key)],
)
def ejecutar_login() -> JSONResponse:
    """Backward-compatible GET endpoint for existing n8n webhook integrations."""
    return _execute_rpa()
