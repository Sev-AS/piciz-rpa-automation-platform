-- =============================================================================
-- Esquema inicial de base de datos para gestión de visitantes y RPA PICIZ
-- Ejecutado automáticamente por PostgreSQL en el primer arranque del contenedor
-- =============================================================================

CREATE DATABASE gestion_usuarios;

\connect gestion_usuarios;

CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) DEFAULT '',
    numero_contacto VARCHAR(20) DEFAULT '',
    tipo_documento VARCHAR(50) DEFAULT 'CEDULA CIUDADANIA',
    numero_documento VARCHAR(30) UNIQUE NOT NULL,
    tiene_vehiculo BOOLEAN DEFAULT FALSE,
    numero_placa VARCHAR(10) DEFAULT '',
    nombre_empresa VARCHAR(100) DEFAULT '',
    puesto_cargo VARCHAR(100) DEFAULT '',
    fecha_visita VARCHAR(20) NOT NULL,
    hora_entrada VARCHAR(10) NOT NULL,
    hora_salida VARCHAR(10) NOT NULL,
    created_at VARCHAR(50) DEFAULT '',
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_usuarios_inserted_at ON usuarios (inserted_at DESC);
