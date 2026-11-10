"""Métricas puras (sin I/O) usadas por el pipeline.

Todas las divisiones vectorizadas usan ``denominador.replace(0, np.nan)`` para
evitar ``inf`` silenciosos; los escalares documentan su valor ante denominador 0.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

SENTIMENT_LABELS: tuple[str, ...] = ("positivo", "neutral", "negativo")


def safe_divide(numerator: pd.Series, denominator: pd.Series | float) -> pd.Series:
    """División elemento a elemento; denominador 0 -> NaN."""
    if isinstance(denominator, pd.Series):
        den = denominator.replace(0, np.nan)
    else:
        den = np.nan if denominator == 0 else denominator
    return numerator / den


def percentage(part: float, total: float, ndigits: int = 1) -> float:
    """Porcentaje redondeado de ``part`` sobre ``total``; 0.0 si ``total`` es 0."""
    if total == 0:
        return 0.0
    return round(100 * part / total, ndigits)


def lexicon_polarity(n_pos: int, n_neg: int, ndigits: int = 4) -> float:
    """Polaridad suavizada (n_pos - n_neg) / (n_pos + n_neg + 1), en [-1, 1]."""
    return round((n_pos - n_neg) / (n_pos + n_neg + 1), ndigits)


def lexicon_subjectivity(n_hits: int, n_tokens: int, ndigits: int = 4) -> float:
    """Fracción de tokens cubiertos por el léxico; 0.0 si no hay tokens."""
    return round(n_hits / max(n_tokens, 1), ndigits)


def polarity_label(score: float, pos_threshold: float, neg_threshold: float) -> str:
    """Etiqueta positivo/negativo/neutral según umbrales (heurísticos)."""
    if score > pos_threshold:
        return "positivo"
    if score < neg_threshold:
        return "negativo"
    return "neutral"


def label_distribution(
    labels: pd.Series, categories: Sequence[str] = SENTIMENT_LABELS
) -> dict[str, int]:
    """Conteo por categoría, incluyendo categorías con 0 apariciones."""
    counts = labels.value_counts()
    return {cat: int(counts.get(cat, 0)) for cat in categories}


def cramers_v(chi2: float, n: int, k: int) -> float:
    """V de Cramér para bondad de ajuste con ``k`` categorías y ``n`` observaciones."""
    if n <= 0 or k <= 1:
        return 0.0
    return float((chi2 / (n * (k - 1))) ** 0.5)


def uniform_expected(counts: Sequence[float]) -> list[float]:
    """Frecuencias esperadas bajo distribución uniforme."""
    if not counts:
        return []
    total = float(sum(counts))
    return [total / len(counts)] * len(counts)


def century_label(year: int) -> str:
    """Siglo en notación ordinal inglesa simple usada por los CSV (``19th``)."""
    return f"{(int(year) // 100) + 1}th"


def location_frequency_stats(places: pd.DataFrame) -> pd.DataFrame:
    """Menciones totales, discursos distintos y promedio por discurso por lugar.

    Espera columnas ``Mentioned_Location`` y ``Year``.
    """
    stats = (
        places.groupby("Mentioned_Location")
        .agg(
            total_mentions=("Mentioned_Location", "count"),
            speeches=("Year", "nunique"),
        )
        .reset_index()
    )
    stats["avg_per_speech"] = safe_divide(
        stats["total_mentions"], stats["speeches"]
    ).round(2)
    return stats
