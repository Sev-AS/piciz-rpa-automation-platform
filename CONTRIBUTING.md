# Guía de Contribución

Gracias por tu interés en mejorar **PICIZ RPA Automation Platform**.

## Flujo de Trabajo

1. Crea una rama descriptiva desde `main`:
   ```bash
   git checkout -b feat/mi-mejora
   ```
2. Realiza tus cambios manteniendo el código modular, tipado y documentado.
3. Verifica localmente que las validaciones pasen:
   ```bash
   make validate
   make lint
   make test
   ```
4. Sigue convenciones de commits claras ([Conventional Commits](https://www.conventionalcommits.org/)):
   - `feat:` nueva funcionalidad
   - `fix:` corrección de error
   - `docs:` cambios en documentación
   - `refactor:` reestructuración sin cambiar comportamiento externo
   - `test:` adición o mejora de pruebas
   - `chore:` tareas de mantenimiento o CI/CD

## Reglas de Seguridad Obligatorias

- **Nunca** hagas commit del archivo `.env`, credenciales, tokens ni reportes generados por Robot Framework (`log.html`, `output.xml`, `report.html`, capturas `.png`).
- Usa únicamente datos ficticios en scripts de prueba o archivos `seed`.
