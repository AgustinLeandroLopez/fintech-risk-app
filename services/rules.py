import json
from pathlib import Path
from typing import Any


DEFAULT_LIMITES_MONOTRIBUTO = {
    "A": 5000000,
    "B": 7000000,
    "C": 10000000,
    "D": 13000000,
}

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "reglas_monotributo.json"


def cargar_limites_monotributo() -> dict[str, float]:
    if not DATA_PATH.exists():
        return DEFAULT_LIMITES_MONOTRIBUTO.copy()

    try:
        contenido = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_LIMITES_MONOTRIBUTO.copy()

    if not isinstance(contenido, dict):
        return DEFAULT_LIMITES_MONOTRIBUTO.copy()

    limites: dict[str, float] = {}
    for categoria, limite in contenido.items():
        try:
            limites[str(categoria).strip().upper()] = float(limite)
        except (TypeError, ValueError):
            continue

    return limites or DEFAULT_LIMITES_MONOTRIBUTO.copy()


LIMITES_MONOTRIBUTO = cargar_limites_monotributo()


def parse_float(value: Any) -> float:
    texto = str(value or "").strip().replace(",", ".")
    if not texto:
        return 0.0
    return float(texto)
