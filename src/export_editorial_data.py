"""Exportaciones editoriales ligeras para Datawrapper y Flourish.

Lee el corpus procesado con ``src.data_loader`` y produce CSV agregados, sin
texto de discursos ni URLs, listos para pegar en:

* Datawrapper - mapa coroplético de regiones de Chile (clave ISO 3166-2).
* Datawrapper - mapa de símbolos por comuna (clave CUT).
* Datawrapper - mapa mundial de países mencionados (clave ISO 3166-1 alfa-3).
* Flourish     - red presidente -> lugar (Source, Target, Value).
* Flourish     - red de co-ocurrencia de lugares por oración (Source, Target, Weight).

El reconocimiento de lugares usa un diccionario curado (no spaCy): es
determinista, rápido y no requiere modelos ni re-entrenamiento.

Uso::

    python -m src.export_editorial_data
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd

try:
    from src.data_loader import EXPORT_DIR, load_speeches
except ImportError:  # ejecución directa: python src/export_editorial_data.py
    from data_loader import EXPORT_DIR, load_speeches

logger = logging.getLogger(__name__)

EDITORIAL_DIR = EXPORT_DIR / "editorial"
MAX_BYTES = 2 * 1024 * 1024  # 2 MB por archivo

# --------------------------------------------------------------------------- #
# Gazetteers
# --------------------------------------------------------------------------- #

REGIONS: dict[str, str] = {
    "CL-AP": "Arica y Parinacota",
    "CL-TA": "Tarapacá",
    "CL-AN": "Antofagasta",
    "CL-AT": "Atacama",
    "CL-CO": "Coquimbo",
    "CL-VS": "Valparaíso",
    "CL-RM": "Metropolitana de Santiago",
    "CL-LI": "Libertador General Bernardo O'Higgins",
    "CL-ML": "Maule",
    "CL-NB": "Ñuble",
    "CL-BI": "Biobío",
    "CL-AR": "La Araucanía",
    "CL-LR": "Los Ríos",
    "CL-LL": "Los Lagos",
    "CL-AI": "Aysén",
    "CL-MA": "Magallanes y la Antártica Chilena",
}

# término en el texto -> (lugar canónico, ISO región, CUT comuna o None)
CHILE_PLACES: dict[str, tuple[str, str, str | None]] = {
    # comunas (código único territorial, CUT 2018)
    "Arica": ("Arica", "CL-AP", "15101"),
    "Iquique": ("Iquique", "CL-TA", "01101"),
    "Antofagasta": ("Antofagasta", "CL-AN", "02101"),
    "Calama": ("Calama", "CL-AN", "02201"),
    "Copiapó": ("Copiapó", "CL-AT", "03101"),
    "La Serena": ("La Serena", "CL-CO", "04101"),
    "Coquimbo": ("Coquimbo", "CL-CO", "04102"),
    "Valparaíso": ("Valparaíso", "CL-VS", "05101"),
    "Viña del Mar": ("Viña del Mar", "CL-VS", "05109"),
    "San Antonio": ("San Antonio", "CL-VS", "05601"),
    "Santiago": ("Santiago", "CL-RM", "13101"),
    "Rancagua": ("Rancagua", "CL-LI", "06101"),
    "Talca": ("Talca", "CL-ML", "07101"),
    "Curicó": ("Curicó", "CL-ML", "07301"),
    "Linares": ("Linares", "CL-ML", "07401"),
    "Chillán": ("Chillán", "CL-NB", "16101"),
    "Concepción": ("Concepción", "CL-BI", "08101"),
    "Talcahuano": ("Talcahuano", "CL-BI", "08110"),
    "Los Ángeles": ("Los Ángeles", "CL-BI", "08301"),
    "Temuco": ("Temuco", "CL-AR", "09101"),
    "Valdivia": ("Valdivia", "CL-LR", "14101"),
    "Osorno": ("Osorno", "CL-LL", "10301"),
    "Puerto Montt": ("Puerto Montt", "CL-LL", "10101"),
    "Coyhaique": ("Coyhaique", "CL-AI", "11101"),
    "Punta Arenas": ("Punta Arenas", "CL-MA", "12101"),
    # regiones / provincias históricas (sin comuna)
    "Tarapacá": ("Tarapacá", "CL-TA", None),
    "Atacama": ("Atacama", "CL-AT", None),
    "Aconcagua": ("Aconcagua", "CL-VS", None),
    "Colchagua": ("Colchagua", "CL-LI", None),
    "Maule": ("Maule", "CL-ML", None),
    "Ñuble": ("Ñuble", "CL-NB", None),
    "Biobío": ("Biobío", "CL-BI", None),
    "Bío-Bío": ("Biobío", "CL-BI", None),
    "Bío Bío": ("Biobío", "CL-BI", None),
    "Arauco": ("Arauco", "CL-BI", None),
    "Araucanía": ("Araucanía", "CL-AR", None),
    "Chiloé": ("Chiloé", "CL-LL", None),
    "Llanquihue": ("Llanquihue", "CL-LL", None),
    "Aysén": ("Aysén", "CL-AI", None),
    "Aisén": ("Aysén", "CL-AI", None),
    "Magallanes": ("Magallanes", "CL-MA", None),
}

# término -> (país canónico, ISO 3166-1 alfa-3). Chile se excluye a propósito:
# es autorreferencia y aplastaría la escala del mapa mundial.
COUNTRIES: dict[str, tuple[str, str]] = {
    "Argentina": ("Argentina", "ARG"),
    "Bolivia": ("Bolivia", "BOL"),
    "Perú": ("Perú", "PER"),
    "Brasil": ("Brasil", "BRA"),
    "Colombia": ("Colombia", "COL"),
    "Ecuador": ("Ecuador", "ECU"),
    "Paraguay": ("Paraguay", "PRY"),
    "Uruguay": ("Uruguay", "URY"),
    "Venezuela": ("Venezuela", "VEN"),
    "México": ("México", "MEX"),
    "Cuba": ("Cuba", "CUB"),
    "Estados Unidos": ("Estados Unidos", "USA"),
    "EE.UU.": ("Estados Unidos", "USA"),
    "EEUU": ("Estados Unidos", "USA"),
    "Norteamérica": ("Estados Unidos", "USA"),
    "Canadá": ("Canadá", "CAN"),
    "España": ("España", "ESP"),
    "Francia": ("Francia", "FRA"),
    "Inglaterra": ("Reino Unido", "GBR"),
    "Gran Bretaña": ("Reino Unido", "GBR"),
    "Reino Unido": ("Reino Unido", "GBR"),
    "Alemania": ("Alemania", "DEU"),
    "Italia": ("Italia", "ITA"),
    "Rusia": ("Rusia", "RUS"),
    "China": ("China", "CHN"),
    "Japón": ("Japón", "JPN"),
    "India": ("India", "IND"),
    "Australia": ("Australia", "AUS"),
}

REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "dw_mapa_regiones_chile.csv": (
        "iso_code",
        "region",
        "menciones",
        "menciones_por_discurso",
        "discursos_con_mencion",
        "tooltip",
    ),
    "dw_mapa_comunas_chile.csv": (
        "cut_comuna",
        "comuna",
        "iso_region",
        "menciones",
        "tooltip",
    ),
    "dw_mapa_mundo_paises.csv": ("iso3", "pais", "menciones", "tooltip"),
    "flourish_red_presidente_lugar.csv": (
        "Source",
        "Target",
        "Value",
        "source_group",
        "target_group",
    ),
    "flourish_red_coocurrencia_lugares.csv": ("Source", "Target", "Weight"),
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+|\n+")


def _compile(terms: list[str]) -> re.Pattern[str]:
    """Regex sensible a mayúsculas con límites Unicode; términos largos primero."""
    alts = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    return re.compile(rf"(?<!\w)(?:{alts})(?!\w)")


_CHILE_RE = _compile(list(CHILE_PLACES))
_COUNTRY_RE = _compile(list(COUNTRIES))


def extract_mentions(df: pd.DataFrame) -> pd.DataFrame:
    """Una fila por mención: speech_id, sentence_id, year, speaker, lugar, tipo, códigos."""
    rows: list[dict] = []
    for speech_id, rec in enumerate(df.itertuples(index=False)):
        text = rec.text if isinstance(rec.text, str) else ""
        for sent_id, sentence in enumerate(_SENTENCE_SPLIT.split(text)):
            for m in _CHILE_RE.finditer(sentence):
                place, iso, cut = CHILE_PLACES[m.group(0)]
                rows.append(
                    {
                        "speech_id": speech_id,
                        "sentence_id": sent_id,
                        "year": int(rec.year),
                        "speaker": str(rec.speaker).strip(),
                        "place": place,
                        "kind": "Chile",
                        "iso_region": iso,
                        "cut_comuna": cut,
                        "iso3": "CHL",
                    }
                )
            for m in _COUNTRY_RE.finditer(sentence):
                country, iso3 = COUNTRIES[m.group(0)]
                rows.append(
                    {
                        "speech_id": speech_id,
                        "sentence_id": sent_id,
                        "year": int(rec.year),
                        "speaker": str(rec.speaker).strip(),
                        "place": country,
                        "kind": "Internacional",
                        "iso_region": None,
                        "cut_comuna": None,
                        "iso3": iso3,
                    }
                )
    cols = [
        "speech_id",
        "sentence_id",
        "year",
        "speaker",
        "place",
        "kind",
        "iso_region",
        "cut_comuna",
        "iso3",
    ]
    return pd.DataFrame(rows, columns=cols)


def _fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


def build_region_map(mentions: pd.DataFrame, n_speeches: int) -> pd.DataFrame:
    """Coroplético: las 16 regiones siempre presentes (0 si no hay menciones)."""
    chile = mentions[mentions["kind"] == "Chile"]
    agg = chile.groupby("iso_region").agg(
        menciones=("place", "size"), discursos_con_mencion=("speech_id", "nunique")
    )
    top_place = (
        chile.groupby(["iso_region", "place"])
        .size()
        .reset_index(name="n")
        .sort_values(["iso_region", "n"], ascending=[True, False])
        .drop_duplicates("iso_region")
        .set_index("iso_region")["place"]
    )
    out = pd.DataFrame({"iso_code": list(REGIONS), "region": list(REGIONS.values())})
    out = out.join(agg, on="iso_code").join(
        top_place.rename("lugar_principal"), on="iso_code"
    )
    out[["menciones", "discursos_con_mencion"]] = (
        out[["menciones", "discursos_con_mencion"]].fillna(0).astype(int)
    )
    out["lugar_principal"] = out["lugar_principal"].fillna("—")
    out["menciones_por_discurso"] = (out["menciones"] / max(n_speeches, 1)).round(2)
    out["tooltip"] = [
        f"{r}: {_fmt(m)} menciones en {d} de {n_speeches} discursos"
        for r, m, d in zip(
            out["region"], out["menciones"], out["discursos_con_mencion"]
        )
    ]
    return out.sort_values("menciones", ascending=False).reset_index(drop=True)


def build_comuna_map(mentions: pd.DataFrame) -> pd.DataFrame:
    """Mapa de símbolos por comuna (clave CUT, con cero a la izquierda)."""
    com = mentions.dropna(subset=["cut_comuna"])
    out = (
        com.groupby(["cut_comuna", "place", "iso_region"])
        .agg(
            menciones=("speech_id", "size"),
            primer_anio=("year", "min"),
            ultimo_anio=("year", "max"),
        )
        .reset_index()
        .rename(columns={"place": "comuna"})
    )
    out["tooltip"] = [
        f"{c}: {_fmt(m)} menciones ({a}–{b})"
        for c, m, a, b in zip(
            out["comuna"], out["menciones"], out["primer_anio"], out["ultimo_anio"]
        )
    ]
    return out.sort_values("menciones", ascending=False).reset_index(drop=True)


def build_world_map(mentions: pd.DataFrame) -> pd.DataFrame:
    """Mapa mundial de países mencionados (excluye Chile)."""
    intl = mentions[mentions["kind"] == "Internacional"]
    out = (
        intl.groupby(["iso3", "place"])
        .agg(menciones=("speech_id", "size"), discursos=("speech_id", "nunique"))
        .reset_index()
        .rename(columns={"place": "pais"})
    )
    out["tooltip"] = [
        f"{p}: {_fmt(m)} menciones en {d} discursos"
        for p, m, d in zip(out["pais"], out["menciones"], out["discursos"])
    ]
    return out.sort_values("menciones", ascending=False).reset_index(drop=True)


def build_speaker_place_network(
    mentions: pd.DataFrame, top_places: int = 25
) -> pd.DataFrame:
    """Red bipartita presidente -> lugar (Sankey / red en Flourish)."""
    keep = mentions["place"].value_counts().head(top_places).index
    sub = mentions[mentions["place"].isin(keep)]
    first_year = sub.groupby("speaker")["year"].min()
    out = (
        sub.groupby(["speaker", "place", "kind"])
        .size()
        .reset_index(name="Value")
        .rename(
            columns={"speaker": "Source", "place": "Target", "kind": "target_group"}
        )
    )
    out["source_group"] = "Presidente"
    out["source_first_year"] = out["Source"].map(first_year).astype(int)
    out = out[
        [
            "Source",
            "Target",
            "Value",
            "source_group",
            "target_group",
            "source_first_year",
        ]
    ]
    return out.sort_values(
        ["source_first_year", "Value"], ascending=[True, False]
    ).reset_index(drop=True)


def build_cooccurrence_network(
    mentions: pd.DataFrame, min_weight: int = 2, max_edges: int = 300
) -> pd.DataFrame:
    """Aristas no dirigidas entre lugares que co-aparecen en la misma oración."""
    pairs: Counter[tuple[str, str]] = Counter()
    for _, grp in mentions.groupby(["speech_id", "sentence_id"]):
        places = sorted(set(grp["place"]))
        pairs.update(combinations(places, 2))
    out = pd.DataFrame(
        [(a, b, w) for (a, b), w in pairs.items() if w >= min_weight],
        columns=["Source", "Target", "Weight"],
    )
    return (
        out.sort_values(["Weight", "Source", "Target"], ascending=[False, True, True])
        .head(max_edges)
        .reset_index(drop=True)
    )


def build_editorial_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Construye todas las tablas editoriales a partir del corpus validado."""
    mentions = extract_mentions(df)
    logger.info("Menciones detectadas: %d en %d discursos", len(mentions), len(df))
    return {
        "dw_mapa_regiones_chile.csv": build_region_map(mentions, len(df)),
        "dw_mapa_comunas_chile.csv": build_comuna_map(mentions),
        "dw_mapa_mundo_paises.csv": build_world_map(mentions),
        "flourish_red_presidente_lugar.csv": build_speaker_place_network(mentions),
        "flourish_red_coocurrencia_lugares.csv": build_cooccurrence_network(mentions),
    }


def export_editorial(
    df: pd.DataFrame | None = None, out_dir: Path | str = EDITORIAL_DIR
) -> dict[str, Path]:
    """Escribe los CSV en ``out_dir`` y devuelve {nombre: ruta}. Falla si alguno pesa >2 MB."""
    if df is None:
        df = load_speeches()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for name, table in build_editorial_tables(df).items():
        path = out_dir / name
        table.to_csv(path, index=False, encoding="utf-8")
        size = path.stat().st_size
        if size > MAX_BYTES:
            raise ValueError(f"{name} pesa {size} bytes (> {MAX_BYTES})")
        logger.info("Guardado %s (%d filas, %.1f KB)", path, len(table), size / 1024)
        written[name] = path
    return written


def main() -> None:
    try:
        from src.logging_config import setup_logging
    except ImportError:
        from logging_config import setup_logging
    setup_logging()
    for name, path in export_editorial().items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
