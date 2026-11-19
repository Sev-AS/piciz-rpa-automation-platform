*** Settings ***
Documentation     Keywords modulares y reutilizables para la automatización del portal PICIZ.
Library           Browser
Library           DatabaseLibrary
Library           String

*** Variables ***
${DB_NAME}                %{DB_NAME=gestion_usuarios}
${DB_USER}                %{DB_USER=piciz_admin}
${DB_PASSWORD}            %{DB_PASSWORD=}
${DB_HOST}                %{DB_HOST=postgres}
${DB_PORT}                %{DB_PORT=5432}
${TABLE_NAME}             usuarios

${PICIZ_URL}              %{PICIZ_URL=https://picizweb31.grupozfb.com/picizweb/#/home}
${PICIZ_ZONA_FRANCA}      %{PICIZ_ZONA_FRANCA=Zona Franca Permanente Santander}
${PICIZ_COMPANY}          %{PICIZ_COMPANY=CAMPUSLANDS S.A.S. BIC}
${PICIZ_USER}             %{PICIZ_USER=}
${PICIZ_PASSWORD}         %{PICIZ_PASSWORD=}
${PICIZ_PERSONA_VISITA}   %{PICIZ_PERSONA_VISITA=Campuslands}

${RPA_HEADLESS}           %{RPA_HEADLESS=true}
${RPA_DRY_RUN}            %{RPA_DRY_RUN=true}

*** Keywords ***
Validar Configuracion Requerida
    [Documentation]    Verifica que las credenciales obligatorias estén presentes en variables de entorno.
    Should Not Be Empty    ${PICIZ_USER}        msg=La variable de entorno PICIZ_USER es obligatoria.
    Should Not Be Empty    ${PICIZ_PASSWORD}    msg=La variable de entorno PICIZ_PASSWORD es obligatoria.
    Should Not Be Empty    ${DB_PASSWORD}       msg=La variable de entorno DB_PASSWORD es obligatoria.

Obtener Ultimo Visitante Desde BD
    [Documentation]    Consulta el registro más reciente en PostgreSQL usando COALESCE para campos opcionales.
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}    ${DB_HOST}    ${DB_PORT}
    ${sql}=    Catenate    SEPARATOR=${SPACE}
    ...    SELECT "id", COALESCE("nombre", ''), COALESCE("email", ''), COALESCE("numero_contacto", ''),
    ...    COALESCE("tipo_documento", 'CEDULA CIUDADANIA'), COALESCE("numero_documento", ''),
    ...    COALESCE("tiene_vehiculo", FALSE), COALESCE("numero_placa", ''), COALESCE("nombre_empresa", ''),
    ...    COALESCE("puesto_cargo", ''), COALESCE("fecha_visita", ''), COALESCE("hora_entrada", '08:00'),
    ...    COALESCE("hora_salida", '17:00'), COALESCE("created_at", '')
    ...    FROM ${TABLE_NAME} ORDER BY "inserted_at" DESC LIMIT 1;
    ${query_result}=       Query    ${sql}
    Should Not Be Empty    ${query_result}    msg=No hay registros en la tabla ${TABLE_NAME}.
    ${row}=                Set Variable    ${query_result[0]}
    &{visitante}=          Create Dictionary
    ...    id=${row[0]}
    ...    nombre=${row[1]}
    ...    email=${row[2]}
    ...    numero_contacto=${row[3]}
    ...    tipo_documento=${row[4]}
    ...    numero_documento=${row[5]}
    ...    tiene_vehiculo=${row[6]}
    ...    numero_placa=${row[7]}
    ...    nombre_empresa=${row[8]}
    ...    puesto_cargo=${row[9]}
    ...    fecha_visita=${row[10]}
    ...    hora_entrada=${row[11]}
    ...    hora_salida=${row[12]}
    ...    created_at=${row[13]}
    RETURN    ${visitante}

Iniciar Sesion En PICIZ
    [Documentation]    Abre Chromium y autentica en PICIZ enmascarando la contraseña con Fill Secret.
    ${headless}=    Convert To Boolean    ${RPA_HEADLESS}
    New Browser     chromium    headless=${headless}
    New Context     viewport={'width': 1920, 'height': 1800}
    New Page        ${PICIZ_URL}

    Select Options By    id=ZONAFRANCA    text    ${PICIZ_ZONA_FRANCA}
    Select Options By    id=COMPANYID     text    ${PICIZ_COMPANY}
    Fill Text            id=LOGIN         ${PICIZ_USER}
    Fill Secret          id=PASSWORD      $PICIZ_PASSWORD
    Click                "Ingresar"
    Sleep                2s
    Run Keyword And Ignore Error    Handle Future Dialogs    action=ACCEPT
    Run Keyword And Ignore Error    Click    "Regresar"

Navegar A Registro De Personas
    [Documentation]    Accede al módulo de registro de visitantes dentro del portal.
    Click    "MODULO VISITANTES"
    Click    "REGISTRO DE PERSONAS"

Diligenciar Formulario Visitante
    [Documentation]    Completa los datos personales y de vehículo del visitante.
    [Arguments]    ${visitante}
    Select Options By    [placeholder="Tipo Documento"]    text    ${visitante}[tipo_documento]
    Fill Text            id=nroDocumento                    ${visitante}[numero_documento]
    Sleep                2s
    Fill Text            css=[name="personaVisita"]         ${PICIZ_PERSONA_VISITA}
    Sleep                1s
    Click                "Buscar"
    Sleep                2s
    Run Keyword And Ignore Error    Handle Future Dialogs    action=ACCEPT
    Sleep                1s

    Fill Text            css=[name="nombre"]               ${visitante}[nombre]
    Sleep                1s
    Fill Text            css=[name="email"]                ${visitante}[email]
    Sleep                1s
    Fill Text            [placeholder="Teléfono"]          ${visitante}[numero_contacto]
    Select Options By    css=[name="tipovisitante"]        text    VISITANTE

    IF    ${visitante}[tiene_vehiculo]
        Click        css=[name="vehiculo"]
        Fill Text    css=[placeholder="Placa"]    ${visitante}[numero_placa]
    END

Configurar Fecha Y Horario
    [Documentation]    Sincroniza horario y fecha en los controles AngularJS del calendario.
    [Arguments]    ${visitante}
    Click    id=Tiempo1
    Evaluate JavaScript    css=[name="horasDesde"]    (el) => {
    ...    const scope = angular.element(el).scope();
    ...    const [hDesde, mDesde] = '${visitante}[hora_entrada]'.split(':');
    ...    const [hHasta, mHasta] = '${visitante}[hora_salida]'.split(':');
    ...    scope.$apply(() => {
    ...        scope.horas.desde.horas   = hDesde;
    ...        scope.horas.desde.minutos = mDesde;
    ...        scope.horas.hasta.horas   = hHasta;
    ...        scope.horas.hasta.minutos = mHasta;
    ...        scope.cambiarHorasCalendario();
    ...    });
    ...    }

    Evaluate JavaScript    css=[ng-model="activeDate"]    (el) => {
    ...    const scope = angular.element(el).scope();
    ...    const [y, m, d] = '${visitante}[fecha_visita]'.split('-');
    ...    scope.$apply(() => {
    ...        scope.activeDate = new Date(Number(y), Number(m) - 1, Number(d));
    ...        scope.cambiarHorasCalendario();
    ...    });
    ...    el.dispatchEvent(new Event('input'));
    ...    el.dispatchEvent(new Event('change'));
    ...    }

    Evaluate JavaScript    css=table    (table) => {
    ...    const day = Number('${visitante}[fecha_visita]'.split('-')[2]);
    ...    const buttons = table.querySelectorAll('td button span');
    ...    for (const span of buttons) {
    ...        if (span.textContent.trim() === String(day)) {
    ...            span.closest('button').click();
    ...            break;
    ...        }
    ...    }
    ...    }

Guardar Y Verificar Registro
    [Documentation]    Toma evidencia visual y, si RPA_DRY_RUN=false, envía y verifica la alerta de éxito.
    Sleep                      1s
    Take Screenshot            comprobacion
    Wait For Elements State    "Guardar"    enabled    timeout=5s

    ${dry_run}=    Convert To Boolean    ${RPA_DRY_RUN}
    IF    not ${dry_run}
        Click                      "Guardar"
        Sleep                      2s
        Wait For Elements State    css=.alert-success    visible    timeout=10s
        ${mensaje}=                Get Text    css=.alert-success
        Should Contain             ${mensaje}    Operacion se completo con exito
    ELSE
        Log    Modo RPA_DRY_RUN activo: se omitió el clic final en "Guardar".    level=INFO
    END

Cerrar Recursos
    [Documentation]    Garantiza cierre ordenado de la conexión a BD y navegador Playwright.
    Run Keyword And Ignore Error    Disconnect From Database
    Run Keyword And Ignore Error    Close Browser
