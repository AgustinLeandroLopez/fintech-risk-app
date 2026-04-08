# Analizador de Riesgo Fintech

Aplicacion web en Python con FastAPI para analizar coherencia economica y fiscal de clientes a partir de un archivo CSV.

El proyecto ahora soporta un esquema de scoring hibrido:

- motor base deterministico por reglas
- motor opcional asistido por IA con Google Gemini
- combinacion controlada de ambos resultados
- fallback automatico al scoring base si la IA falla

## Objetivo

Simular un motor de analisis de riesgo usado en fintechs o entidades financieras para:

- detectar inconsistencias fiscales
- evaluar capacidad economica
- clasificar clientes segun nivel de riesgo
- generar un dictamen preliminar automatizado

## Tecnologias

- Python 3
- FastAPI
- Jinja2
- Uvicorn
- HTML + CSS
- Gemini API opcional

## Estructura

```text
fintech-risk-app/
|-- main.py
|-- clientes.csv
|-- requirements.txt
|-- .env.example
|-- data/
|   `-- reglas_monotributo.json
|-- services/
|   |-- ai_scoring.py
|   |-- parser.py
|   |-- rules.py
|   `-- scoring.py
|-- static/
|   `-- styles.css
`-- templates/
    |-- index.html
    `-- resultado.html
```

## Como ejecutar

1. Clonar el repositorio.

```bash
git clone https://github.com/AgustinLeandroLopez/fintech-risk-app.git
cd fintech-risk-app
```

2. Crear entorno virtual.

```bash
python -m venv venv
```

3. Activar entorno en Windows.

```bash
venv\Scripts\activate
```

4. Instalar dependencias.

```bash
pip install -r requirements.txt
```

5. Ejecutar la aplicacion.

```bash
uvicorn main:app --reload
```

6. Abrir en el navegador.

```text
http://127.0.0.1:8000
```

## Configuracion de IA

La IA es opcional. Si no esta configurada o la llamada falla, el sistema usa solo el scoring base.

1. Crear un archivo `.env` tomando como base `.env.example`.
2. Levantar la app normalmente. `main.py` carga `.env` automaticamente al iniciar.

### Variables disponibles

- `USE_AI=true` activa la validacion con IA
- `GEMINI_API_KEY` define la API key de Gemini
- `GEMINI_MODEL=gemini-2.5-flash` define el modelo
- `GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/models` define la base del endpoint
- `GEMINI_TIMEOUT=30` define timeout en segundos
- `GEMINI_TEMPERATURE=0.2` define temperatura baja para respuestas consistentes

### Ejemplo usando `.env`

Crear `.env`:

```text
USE_AI=true
GEMINI_API_KEY=tu_api_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/models
GEMINI_TIMEOUT=30
GEMINI_TEMPERATURE=0.2
```

Luego ejecutar:

```powershell
uvicorn main:app --reload
```

### Ejemplo alternativo en PowerShell

```powershell
$env:USE_AI="true"
$env:GEMINI_API_KEY="tu_api_key"
$env:GEMINI_MODEL="gemini-2.5-flash"
uvicorn main:app --reload
```

Si queres correr sin IA:

```powershell
$env:USE_AI="false"
uvicorn main:app --reload
```

## Logica de scoring

### Motor base

Aplica reglas deterministicas:

- si el monto mensual supera 1.5x el ingreso declarado: +25
- si el monto anual es inconsistente con ingresos: +25
- si falta categoria de monotributo: +30
- si supera el limite de la categoria: +40

### Motor IA

Evalua:

- coherencia entre ingresos y montos operados
- consistencia fiscal
- categoria monotributo
- comportamiento economico observable

La integracion usa Google Gemini por REST y la respuesta debe volver en JSON valido con:

- `score`
- `nivel_riesgo`
- `dictamen`
- `observaciones`

### Combinacion

- usa score IA si existe
- usa scoring base como fallback si la IA falla
- concatena observaciones de ambos motores
- consulta Gemini solo cuando el motor base detecta senales de riesgo o inconsistencias

## Formato del CSV

Columnas esperadas:

```text
cuit,nombre,condicion_fiscal,categoria_monotributo,actividad,ingreso_declarado_mensual,monto_operado_mensual,monto_operado_anual
```

Ejemplo:

```text
20123456789,Juan Perez,MONOTRIBUTO,C,Servicios IT,450000,780000,9360000
```

## Resultado del analisis

Para cada cliente el sistema genera:

- score
- nivel de riesgo
- dictamen
- observaciones
- fuente del scoring (`base`, `ia` o `fallback`)
- score base y score IA en el detalle para auditoria rapida
- observaciones separadas del motor base y del motor IA
- estado de IA indicando si fue consultada, omitida o si hubo error

## Autor

Agustin Lopez
