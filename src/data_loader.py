"""Ingesta agnóstica de datos con ``pathlib.Path`` y logging.

Centraliza rutas del proyecto, la resolución corpus real -> muestra sintética
y la lectura/escritura de tablas y JSON. No contiene lógica de análisis.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable

import pandas as pd

try:
    from src.validator import validate_speeches
except ImportError:  # ejecución directa: python src/<script>.py
    from validator import validate_speeches

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "speeches"
PROCESSED_CSV = DATA_DIR / "processed" / "speeches.csv"
SAMPLE_CSV = DATA_DIR / "sample_speeches.csv"
EXPORT_DIR = DATA_DIR / "export"

_READERS: dict[str, Callable[..., pd.DataFrame]] = {
    ".csv": pd.read_csv,
    ".tsv": lambda p, **kw: pd.read_csv(p, sep="\t", **kw),
    ".parquet": pd.read_parquet,
    ".json": pd.read_json,
    ".xlsx": pd.read_excel,
}


def read_table(path: Path | str, **kwargs: Any) -> pd.DataFrame:
    """Lee una tabla eligiendo el lector por extensión (csv, tsv, parquet, json, xlsx)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    reader = _READERS.get(path.suffix.lower())
    if reader is None:
        raise ValueError(
            f"Formato no soportado '{path.suffix}' para {path}; "
            f"soportados: {sorted(_READERS)}"
        )
    df = reader(path, **kwargs)
    logger.info("Cargado %s (%d filas, %d columnas)", path.name, *df.shape)
    return df


def find_corpus(data_dir: Path | str = DATA_DIR) -> Path | None:
    """Devuelve el corpus real si existe; si no, la muestra sintética; si no, None."""
    data_dir = Path(data_dir)
    for candidate in (
        data_dir / "processed" / "speeches.csv",
        data_dir / "sample_speeches.csv",
    ):
        if candidate.exists():
            return candidate
    logger.warning("No se encontró corpus en %s", data_dir)
    return None


def load_speeches(
    path: Path | str | None = None,
    data_dir: Path | str = DATA_DIR,
    validate: bool = True,
) -> pd.DataFrame:
    """Carga el corpus de discursos y lo valida (fail-fast) por defecto."""
    resolved = Path(path) if path is not None else find_corpus(data_dir)
    if resolved is None:
        raise FileNotFoundError(
            f"No hay corpus en {data_dir}. Ejecuta: python src/collect_speeches.py "
            "o python scripts/generate_synthetic_sample.py"
        )
    df = read_table(resolved)
    return validate_speeches(df, name=resolved.name) if validate else df


def load_json(path: Path | str) -> Any:
    """Lee un JSON UTF-8."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(payload: Any, path: Path | str) -> Path:
    """Escribe un JSON UTF-8 legible, creando el directorio padre."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("Guardado %s", path)
    return path


def list_text_files(data_dir: Path | str) -> list[Path]:
    """Archivos .txt y .md bajo ``data_dir`` (orden determinista)."""
    data_dir = Path(data_dir)
    return sorted(data_dir.rglob("*.txt")) + sorted(data_dir.rglob("*.md"))
