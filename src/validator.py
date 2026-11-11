"""Validación fail-fast de esquemas para el corpus y artefactos intermedios."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

REQUIRED_SPEECH_COLUMNS: tuple[str, ...] = ("year", "speaker", "text")
REQUIRED_PLACES_COLUMNS: tuple[str, ...] = ("Year", "Speaker", "Mentioned_Location")
REQUIRED_ENTITY_KEYS: tuple[str, ...] = ("entity", "label", "count")


class SchemaError(ValueError):
    """El dataset no cumple el esquema mínimo esperado."""


def validate_columns(
    df: pd.DataFrame, required: Iterable[str], name: str = "dataset"
) -> pd.DataFrame:
    """Falla si faltan columnas requeridas. Devuelve el mismo DataFrame."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise SchemaError(
            f"{name}: faltan columnas requeridas {missing}; "
            f"disponibles: {list(df.columns)}"
        )
    return df


def validate_not_empty(df: pd.DataFrame, name: str = "dataset") -> pd.DataFrame:
    """Falla si el DataFrame no tiene filas."""
    if df.empty:
        raise SchemaError(f"{name}: el dataset está vacío")
    return df


def validate_speeches(df: pd.DataFrame, name: str = "speeches") -> pd.DataFrame:
    """Valida el corpus de discursos: columnas, filas, año entero y texto presente."""
    validate_columns(df, REQUIRED_SPEECH_COLUMNS, name)
    validate_not_empty(df, name)

    years = pd.to_numeric(df["year"], errors="coerce")
    if years.isna().any():
        bad = df.loc[years.isna(), "year"].tolist()[:5]
        raise SchemaError(f"{name}: valores de 'year' no numéricos: {bad}")
    if (years % 1 != 0).any():
        raise SchemaError(f"{name}: 'year' debe contener enteros")

    if df["text"].isna().all():
        raise SchemaError(f"{name}: la columna 'text' no tiene contenido")
    return df


def validate_places(df: pd.DataFrame, name: str = "places") -> pd.DataFrame:
    """Valida la tabla de menciones geográficas producida por el extractor NER."""
    return validate_columns(df, REQUIRED_PLACES_COLUMNS, name)


def validate_entities(
    entities: Iterable[Mapping[str, Any]], name: str = "top_entities"
) -> list[Mapping[str, Any]]:
    """Valida que cada entidad NER tenga ``entity``, ``label`` y ``count``."""
    items = list(entities)
    for i, ent in enumerate(items):
        missing = [k for k in REQUIRED_ENTITY_KEYS if k not in ent]
        if missing:
            raise SchemaError(f"{name}[{i}]: faltan claves {missing}")
    return items
