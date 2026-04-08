import json
import logging
import os
from typing import Any

import requests


logger = logging.getLogger(__name__)

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_API_BASE_URL = os.getenv(
    "GEMINI_API_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/models",
)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "30"))
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))

SYSTEM_PROMPT = """
Actua como un analista de riesgo fintech senior de un banco digital.
Evalua exclusivamente los datos provistos del cliente.

Debes analizar:
- coherencia entre ingresos declarados y montos operados
- consistencia fiscal
- categoria de monotributo
- comportamiento economico observable en los datos

Reglas de negocio obligatorias:
- Si el monto operado mensual supera 1.5 veces el ingreso declarado mensual, aumenta el riesgo.
- Si el monto operado anual es inconsistente respecto del ingreso declarado mensual por 12 meses, aumenta el riesgo.
- Si falta la categoria de monotributo y la condicion fiscal es MONOTRIBUTO, aumenta el riesgo.
- Si el monto operado anual supera el limite de la categoria de monotributo informada, consideralo alto riesgo.

Instrucciones de estilo:
- No inventes datos.
- No agregues supuestos no respaldados por la entrada.
- No uses lenguaje generico.
- Redacta las observaciones con estilo de informe bancario, de forma concreta y profesional.

Responde siempre y solo con JSON valido usando exactamente esta estructura:
{
  "score": 0,
  "nivel_riesgo": "BAJO",
  "dictamen": "Cumple",
  "observaciones": "texto"
}
""".strip()

ALLOWED_NIVELES = {"BAJO", "MEDIO", "ALTO"}
ALLOWED_DICTAMENES = {"Cumple", "Cumple con observaciones", "No cumple"}


def _build_request_payload(cliente: dict[str, Any]) -> dict[str, Any]:
    prompt_usuario = (
        "Evalua este cliente y devuelve solo JSON valido.\n\n"
        f"cliente = {json.dumps(cliente, ensure_ascii=True)}"
    )
    return {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_PROMPT,
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt_usuario,
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": GEMINI_TEMPERATURE,
            "responseMimeType": "application/json",
        },
    }


def _extract_response_text(response_data: dict[str, Any]) -> str:
    candidates = response_data.get("candidates") or []
    if not candidates:
        prompt_feedback = response_data.get("promptFeedback")
        if prompt_feedback:
            raise ValueError(f"Gemini no devolvio candidates: {prompt_feedback}")
        raise ValueError("Gemini no devolvio candidates")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    fragmentos: list[str] = []

    for part in parts:
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            fragmentos.append(part["text"])

    texto = "".join(fragmentos).strip()
    if not texto:
        raise ValueError("Gemini no devolvio texto util")
    return texto


def _parse_response_json(raw_content: str) -> dict[str, Any]:
    contenido = raw_content.strip()
    if contenido.startswith("```"):
        lineas = [line for line in contenido.splitlines() if not line.strip().startswith("```")]
        contenido = "\n".join(lineas).strip()

    data = json.loads(contenido)
    if not isinstance(data, dict):
        raise ValueError("La respuesta de IA no es un objeto JSON")
    return data


def _normalize_result(data: dict[str, Any]) -> dict[str, Any]:
    score = int(float(data["score"]))
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    nivel_riesgo = str(data["nivel_riesgo"]).strip().upper()
    if nivel_riesgo not in ALLOWED_NIVELES:
        raise ValueError("nivel_riesgo invalido")

    dictamen = str(data["dictamen"]).strip()
    if dictamen not in ALLOWED_DICTAMENES:
        raise ValueError("dictamen invalido")

    observaciones = str(data.get("observaciones") or "").strip() or "Sin observaciones"

    return {
        "score": score,
        "nivel_riesgo": nivel_riesgo,
        "dictamen": dictamen,
        "observaciones": observaciones,
    }


def analizar_con_ia(cliente: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv(GEMINI_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"{GEMINI_API_KEY_ENV} no configurada")

    url = f"{GEMINI_API_BASE_URL}/{GEMINI_MODEL}:generateContent"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json=_build_request_payload(cliente),
        timeout=GEMINI_TIMEOUT,
    )
    response.raise_for_status()

    response_data = response.json()
    raw_content = _extract_response_text(response_data)
    resultado = _parse_response_json(raw_content)
    return _normalize_result(resultado)


def analizar_con_ia_detallado(cliente: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return analizar_con_ia(cliente), None
    except requests.Timeout:
        mensaje = "Timeout al consultar Gemini"
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "desconocido"
        mensaje = f"Error HTTP de Gemini: {status}"
    except Exception as exc:
        mensaje = str(exc)

    logger.exception("Fallo el analisis con Gemini: %s", mensaje)
    return None, mensaje


def analizar_con_ia_seguro(cliente: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return analizar_con_ia(cliente)
    except Exception as exc:
        logger.exception("Fallo el analisis con Gemini: %s", exc)
        return None
