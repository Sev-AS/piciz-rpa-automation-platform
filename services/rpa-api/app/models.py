"""Pydantic v2 response schemas for the PICIZ RPA API."""

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Service liveness payload."""

    status: str = Field(examples=["ok"])
    service: str = Field(examples=["rpa-api"])


class RPAStatusResponse(BaseModel):
    """Current runtime status and metadata of the most recent RPA execution."""

    running: bool = Field(description="Indica si hay una ejecución activa en este momento.")
    last_run_at: str | None = Field(
        default=None,
        description="Marca de tiempo UTC (ISO 8601) de la última ejecución finalizada.",
        examples=["2026-05-15T14:30:00+00:00"],
    )
    last_status: str | None = Field(
        default=None,
        description="Resultado de la última ejecución (`success`, `error` o `timeout`).",
        examples=["success"],
    )
    last_returncode: int | None = Field(
        default=None,
        description="Código de salida del proceso `robot` en la última ejecución.",
        examples=[0],
    )


class RPAResponse(BaseModel):
    """Structured result returned after executing the Robot Framework suite."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "mensaje": "Bot ejecutado correctamente",
                "returncode": 0,
                "duration_seconds": 14.32,
                "salida": "Registrar Ultimo Visitante En PICIZ | PASS |",
                "error_log": "",
            }
        }
    )

    status: str = Field(description="Estado de la ejecución (`success` o `error`).")
    mensaje: str = Field(description="Resumen legible del resultado.")
    returncode: int = Field(description="Código de retorno del proceso Robot Framework.")
    duration_seconds: float = Field(description="Duración total de la ejecución en segundos.")
    salida: str = Field(description="Salida estándar (stdout) generada por Robot Framework.")
    error_log: str = Field(description="Salida de error estándar (stderr), si existe.")
