# Política de Seguridad

## Controles Implementados en el Proyecto

Este repositorio aplica prácticas de seguridad por diseño pensadas para entornos de automatización RPA:

1. **Gestión de secretos fuera del código:** Todas las credenciales (PostgreSQL, portal PICIZ, `API_KEY` y `NGROK_AUTHTOKEN`) se inyectan exclusivamente mediante variables de entorno (`.env`, ignorado por Git).
2. **Enmascaramiento en logs de Robot Framework:** El inicio de sesión utiliza `Fill Secret` de `robotframework-browser` para evitar que la contraseña aparezca en texto plano dentro de `log.html` o `output.xml`.
3. **Autenticación en la API REST:** El microservicio `rpa-api` soporta autenticación mediante cabecera `X-API-Key` comparada en tiempo constante (`secrets.compare_digest`) para prevenir ataques de temporización.
4. **Exposición mínima de puertos:** Por defecto, los contenedores se enlazan únicamente a `127.0.0.1` (`BIND_HOST=127.0.0.1`) y se comunican a través de una red bridge aislada (`piciz_net`).
5. **Hardening de contenedores:** Todos los servicios aplican `no-new-privileges:true` y la ejecución de comandos arbitrarios en `n8n` permanece deshabilitada por defecto.
6. **Protección contra envíos accidentales:** El parámetro `RPA_DRY_RUN=true` permite validar todo el flujo RPA sin presionar el botón final **Guardar** hasta habilitarlo explícitamente.
7. **Sin datos personales (PII) en el repositorio:** No se almacenan reportes HTML/XML de ejecuciones reales ni datos reales de visitantes; [database/seed.example.sql](database/seed.example.sql) contiene únicamente datos sintéticos.

## Reporte de Vulnerabilidades

Si detectas una vulnerabilidad de seguridad o un secreto expuesto por error:

1. No abras un *issue* público con detalles explotables.
2. Notifica directamente al mantenedor del repositorio para coordinar la corrección y rotación inmediata de credenciales.
