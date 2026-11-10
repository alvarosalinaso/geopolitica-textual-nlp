"""Genera una muestra sintética y determinista del corpus para tests.

Los discursos son plantillas con oradores ficticios: no reproducen texto real
de la BCN y sirven para ejercitar el pipeline sin red ni PDFs.

Uso:
    python scripts/generate_synthetic_sample.py
    python scripts/generate_synthetic_sample.py --n 30 --seed 7 --output ruta.csv
"""

from __future__ import annotations

import argparse
import logging
import random
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "tests" / "fixtures" / "synthetic_speeches.csv"

PLACES: tuple[str, ...] = (
    "Arica",
    "Iquique",
    "Antofagasta",
    "Copiapó",
    "La Serena",
    "Valparaíso",
    "Santiago",
    "Rancagua",
    "Talca",
    "Chillán",
    "Concepción",
    "Temuco",
    "Valdivia",
    "Puerto Montt",
    "Punta Arenas",
)
POSITIVE: tuple[str, ...] = ("progreso", "paz", "desarrollo", "bienestar", "unidad")
NEGATIVE: tuple[str, ...] = ("crisis", "pobreza", "sequía", "conflicto", "deuda")
TEMPLATES: tuple[str, ...] = (
    "El Gobierno informa avances en {p1} y {p2}, donde el {pos} es visible.",
    "La {neg} afectó a {p1}; el Estado reforzará su apoyo a {p2}.",
    "Desde {p1} hasta {p2} buscamos {pos} y superar la {neg}.",
    "Los puertos de {p1} y la ciudad de {p2} son claves para el {pos} nacional.",
)
SOURCE = "SINTÉTICO: generado por scripts/generate_synthetic_sample.py"


def build_synthetic_speeches(n: int = 12, seed: int = 42) -> pd.DataFrame:
    """Construye ``n`` discursos sintéticos con el esquema del corpus real."""
    if n <= 0:
        raise ValueError("n debe ser positivo")
    rng = random.Random(seed)
    years = sorted(rng.sample(range(1832, 2023), n))
    rows = []
    for i, year in enumerate(years, start=1):
        sentences = []
        for _ in range(rng.randint(3, 6)):
            p1, p2 = rng.sample(PLACES, 2)
            sentences.append(
                rng.choice(TEMPLATES).format(
                    p1=p1, p2=p2, pos=rng.choice(POSITIVE), neg=rng.choice(NEGATIVE)
                )
            )
        rows.append(
            {
                "year": year,
                "speaker": f"Presidente Sintético {i:02d}",
                "text": " ".join(sentences),
                "description": f"Mensaje sintético {year}",
                "source_url": "",
                "source": SOURCE,
            }
        )
    return pd.DataFrame(rows)


def write_sample(output: Path = DEFAULT_OUTPUT, n: int = 12, seed: int = 42) -> Path:
    """Escribe la muestra en CSV UTF-8 y devuelve la ruta."""
    df = build_synthetic_speeches(n=n, seed=seed)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False, encoding="utf-8")
    logger.info("Muestra sintética: %d discursos -> %s", len(df), output)
    return output


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, default=12, help="Número de discursos")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    write_sample(args.output, n=args.n, seed=args.seed)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
    )
    main()
