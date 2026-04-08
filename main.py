import csv
import logging
import os
from io import StringIO

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from services.ai_scoring import analizar_con_ia_detallado
from services.config import load_dotenv
from services.scoring import analizar_riesgo, combinar_resultados, requiere_validacion_ia

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)
USE_AI = os.getenv("USE_AI", "true").strip().lower() in {"1", "true", "yes", "on"}


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
        ai_warning = None
        for fila in lector:
            if len(fila) != len(headers):
                raise ValueError("El archivo CSV tiene filas con diferente cantidad de columnas")
            cliente = dict(zip(headers, fila))
            resultado_base = analizar_riesgo(cliente)
            resultado_ia = None
            ai_error = None
            consultar_ia = USE_AI and requiere_validacion_ia(cliente, resultado_base)
            if consultar_ia:
                resultado_ia, ai_error = analizar_con_ia_detallado(cliente)
            fuente_scoring = "base"
            ai_estado = "desactivada"
            if USE_AI and not consultar_ia:
                ai_estado = "omitida"
            elif USE_AI and resultado_ia is None:
                logger.warning("Se utilizo fallback al scoring base para el cliente %s", cliente.get("cuit"))
                fuente_scoring = "fallback"
                ai_estado = "error"
                if ai_warning is None and ai_error:
                    ai_warning = ai_error
            elif resultado_ia is not None:
                fuente_scoring = "ia"
                ai_estado = "ok"

            resultado_final = combinar_resultados(resultado_base, resultado_ia)
            cliente.update(resultado_final)
            cliente["score_base"] = resultado_base.get("score")
            cliente["score_ia"] = resultado_ia.get("score") if resultado_ia else None
            cliente["observaciones_base"] = resultado_base.get("observaciones", "Sin observaciones")
            cliente["observaciones_ia"] = (
                resultado_ia.get("observaciones", "Sin observaciones") if resultado_ia else "Sin observaciones"
            )
            cliente["fuente_scoring"] = fuente_scoring
            cliente["ai_estado"] = ai_estado
            cliente["ai_error"] = ai_error or "-"
            cliente["ai_consultada"] = "si" if consultar_ia else "no"
            rows.append(cliente)

        headers = headers + [
            "score",
            "nivel_riesgo",
            "dictamen",
            "observaciones",
            "fuente_scoring",
            "score_base",
            "score_ia",
            "observaciones_base",
            "observaciones_ia",
            "ai_estado",
            "ai_error",
            "ai_consultada",
        ]

        return templates.TemplateResponse(
            request,
            "resultado.html",
            {
                "filename": archivo.filename,
                "headers": headers,
                "rows": rows,
                "ai_warning": ai_warning,
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
            "ai_warning": None,
            "error": error,
        },
        status_code=400,
    )
