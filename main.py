import csv
from io import StringIO

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

LIMITES_MONOTRIBUTO = {
    "A": 5000000,
    "B": 7000000,
    "C": 10000000,
    "D": 13000000,
}


def parse_float(value):
    texto = (value or "").strip().replace(",", ".")
    if not texto:
        return 0.0
    return float(texto)


def analizar_riesgo(cliente):
    score = 0
    observaciones = []

    condicion_fiscal = (cliente.get("condicion_fiscal") or "").strip().upper()
    categoria_monotributo = (cliente.get("categoria_monotributo") or "").strip().upper()
    ingreso_declarado_mensual = parse_float(cliente.get("ingreso_declarado_mensual"))
    monto_operado_mensual = parse_float(cliente.get("monto_operado_mensual"))
    monto_operado_anual = parse_float(cliente.get("monto_operado_anual"))

    if condicion_fiscal == "MONOTRIBUTO" and not categoria_monotributo:
        observaciones.append("Categoria de monotributo no informada")
        score += 30

    if condicion_fiscal == "MONOTRIBUTO" and categoria_monotributo:
        limite_categoria = LIMITES_MONOTRIBUTO.get(categoria_monotributo)
        if limite_categoria is None:
            observaciones.append("Categoria de monotributo invalida")
            score += 20
        elif monto_operado_anual > limite_categoria:
            observaciones.append(
                "El monto operado anual supera el limite permitido para la categoria de monotributo"
            )
            score += 40

    if monto_operado_mensual > ingreso_declarado_mensual * 1.5:
        observaciones.append("Monto operado supera significativamente el ingreso declarado")
        score += 25

    if monto_operado_anual > ingreso_declarado_mensual * 12 * 1.5:
        observaciones.append("Monto anual inconsistente con ingresos declarados")
        score += 25

    if score < 30:
        nivel_riesgo = "BAJO"
        dictamen = "Cumple"
    elif score < 60:
        nivel_riesgo = "MEDIO"
        dictamen = "Cumple con observaciones"
    else:
        nivel_riesgo = "ALTO"
        dictamen = "No cumple"

    return {
        "score": score,
        "nivel_riesgo": nivel_riesgo,
        "dictamen": dictamen,
        "observaciones": " | ".join(observaciones) if observaciones else "Sin observaciones",
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {},
    )


@app.post("/analizar", response_class=HTMLResponse)
async def analizar_archivo(request: Request, archivo: UploadFile = File(None)):
    if archivo is None or not archivo.filename:
        return templates.TemplateResponse(
            request,
            "resultado.html",
            {
                "filename": "No se recibio ningun archivo",
                "headers": [],
                "rows": [],
                "error": "Debes seleccionar un archivo CSV antes de continuar",
            },
            status_code=400,
        )

    try:
        contenido = await archivo.read()
        if not contenido.strip():
            raise ValueError("El archivo esta vacio")

        texto_csv = contenido.decode("utf-8-sig")
        lector = csv.reader(StringIO(texto_csv))

        # La primera fila define los encabezados de la tabla.
        headers = next(lector, None)
        if not headers:
            raise ValueError("El archivo no contiene encabezados")

        rows = []
        for fila in lector:
            if len(fila) != len(headers):
                raise ValueError("El archivo CSV tiene filas con diferente cantidad de columnas")
            cliente = dict(zip(headers, fila))
            cliente.update(analizar_riesgo(cliente))
            rows.append(cliente)

        headers = headers + ["score", "nivel_riesgo", "dictamen", "observaciones"]

        return templates.TemplateResponse(
            request,
            "resultado.html",
            {
                "filename": archivo.filename,
                "headers": headers,
                "rows": rows,
                "error": None,
            },
        )
    except UnicodeDecodeError:
        error = "No se pudo leer el archivo. Verifica que sea un CSV en UTF-8."
    except (csv.Error, ValueError) as exc:
        error = str(exc)

    return templates.TemplateResponse(
        request,
        "resultado.html",
        {
            "filename": archivo.filename,
            "headers": [],
            "rows": [],
            "error": error,
        },
        status_code=400,
    )
