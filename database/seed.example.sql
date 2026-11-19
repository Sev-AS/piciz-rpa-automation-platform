-- =============================================================================
-- Datos sintéticos de ejemplo para pruebas locales (sin datos reales / PII)
-- Uso: make seed
-- =============================================================================

INSERT INTO usuarios (
    id,
    nombre,
    email,
    numero_contacto,
    tipo_documento,
    numero_documento,
    tiene_vehiculo,
    numero_placa,
    nombre_empresa,
    puesto_cargo,
    fecha_visita,
    hora_entrada,
    hora_salida,
    created_at
) VALUES (
    'demo-001',
    'Ana Sofia Demo',
    'ana.demo@example.com',
    '3001234567',
    'CEDULA CIUDADANIA',
    '1000000001',
    TRUE,
    'ABC123',
    'Empresa Demo S.A.S.',
    'Ingeniera de Software',
    '2026-05-15',
    '09:00',
    '17:00',
    '15/05/2026 09:00 AM'
)
ON CONFLICT (id) DO NOTHING;
