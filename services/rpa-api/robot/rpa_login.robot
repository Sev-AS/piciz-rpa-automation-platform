*** Settings ***
Documentation     Automatización RPA para el registro de visitantes en el portal web PICIZ.
...               Lee el último visitante registrado en PostgreSQL y diligencia el formulario web.
Resource          resources/keywords.resource

Suite Teardown    Cerrar Recursos

*** Test Cases ***
Registrar Ultimo Visitante En PICIZ
    [Documentation]    Flujo completo: valida entorno, consulta BD, inicia sesión y registra visitante.
    [Tags]             rpa    piciz    visitantes
    Validar Configuracion Requerida
    ${visitante}=    Obtener Ultimo Visitante Desde BD
    Iniciar Sesion En PICIZ
    Navegar A Registro De Personas
    Diligenciar Formulario Visitante    ${visitante}
    Configurar Fecha Y Horario          ${visitante}
    Guardar Y Verificar Registro
