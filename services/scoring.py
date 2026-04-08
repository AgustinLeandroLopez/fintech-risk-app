from typing import Any

from services.rules import LIMITES_MONOTRIBUTO, parse_float


RiskResult = dict[str, Any]


def clasificar_riesgo(score: int) -> tuple[str, str]:
    if score < 30:
        return "BAJO", "Cumple"
    if score < 60:
        return "MEDIO", "Cumple con observaciones"
    return "ALTO", "No cumple"


def analizar_riesgo(cliente: dict[str, Any]) -> RiskResult:
    score = 0
    observaciones: list[str] = []

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

    nivel_riesgo, dictamen = clasificar_riesgo(score)
    return {
        "score": score,
        "nivel_riesgo": nivel_riesgo,
        "dictamen": dictamen,
        "observaciones": " | ".join(observaciones) if observaciones else "Sin observaciones",
    }


def requiere_validacion_ia(cliente: dict[str, Any], base: RiskResult) -> bool:
    condicion_fiscal = (cliente.get("condicion_fiscal") or "").strip().upper()
    categoria_monotributo = (cliente.get("categoria_monotributo") or "").strip().upper()
    ingreso_declarado_mensual = parse_float(cliente.get("ingreso_declarado_mensual"))
    monto_operado_mensual = parse_float(cliente.get("monto_operado_mensual"))
    monto_operado_anual = parse_float(cliente.get("monto_operado_anual"))

    if int(base.get("score", 0)) >= 25:
        return True

    if condicion_fiscal == "MONOTRIBUTO" and not categoria_monotributo:
        return True

    if condicion_fiscal == "MONOTRIBUTO" and categoria_monotributo not in LIMITES_MONOTRIBUTO:
        return True

    if ingreso_declarado_mensual > 0 and monto_operado_mensual > ingreso_declarado_mensual * 1.2:
        return True

    if ingreso_declarado_mensual > 0 and monto_operado_anual > ingreso_declarado_mensual * 12 * 1.2:
        return True

    return False


def combinar_resultados(base: RiskResult, ia: RiskResult | None) -> RiskResult:
    if not ia:
        return dict(base)

    score = ia.get("score", base.get("score"))
    try:
        score = int(float(score))
    except (TypeError, ValueError):
        score = base.get("score", 0)

    observaciones: list[str] = []
    base_observaciones = (base.get("observaciones") or "").strip()
    ia_observaciones = (ia.get("observaciones") or "").strip()

    if base_observaciones and base_observaciones != "Sin observaciones":
        observaciones.append(base_observaciones)
    if ia_observaciones and ia_observaciones != "Sin observaciones":
        observaciones.append(ia_observaciones)

    return {
        "score": score,
        "nivel_riesgo": ia.get("nivel_riesgo") or base.get("nivel_riesgo", "BAJO"),
        "dictamen": ia.get("dictamen") or base.get("dictamen", "Cumple"),
        "observaciones": " | ".join(observaciones) if observaciones else "Sin observaciones",
    }
