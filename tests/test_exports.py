"""Tests de las exportaciones editoriales (Datawrapper / Flourish)."""

import pandas as pd
import pytest

from scripts.generate_synthetic_sample import build_synthetic_speeches
from src.export_editorial_data import MAX_BYTES, REQUIRED_COLUMNS, export_editorial


@pytest.fixture(scope="module")
def editorial_csvs(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("editorial")
    extra = pd.DataFrame(
        {
            "year": [1990, 2010],
            "speaker": ["Presidente A", "Presidente B"],
            "text": [
                "Con Argentina y Perú firmamos acuerdos desde Santiago. Arica y Perú crecen.",
                "Argentina y Perú comercian con Valparaíso. Estados Unidos invierte en Arica.",
            ],
        }
    )
    df = pd.concat([build_synthetic_speeches(n=12, seed=42), extra], ignore_index=True)
    return export_editorial(df, out_dir=out_dir)


def test_all_expected_files_are_written(editorial_csvs):
    assert set(editorial_csvs) == set(REQUIRED_COLUMNS)


@pytest.mark.parametrize("name", sorted(REQUIRED_COLUMNS))
def test_csv_not_empty_and_has_required_columns(editorial_csvs, name):
    path = editorial_csvs[name]
    assert path.stat().st_size <= MAX_BYTES
    df = pd.read_csv(path, dtype=str)
    assert not df.empty, f"{name} está vacío"
    missing = [c for c in REQUIRED_COLUMNS[name] if c not in df.columns]
    assert not missing, f"{name}: faltan columnas {missing}"
    assert "text" not in df.columns and "source_url" not in df.columns


def test_region_map_has_all_iso_codes(editorial_csvs):
    df = pd.read_csv(editorial_csvs["dw_mapa_regiones_chile.csv"])
    assert len(df) == 16
    assert df["iso_code"].str.match(r"^CL-[A-Z]{2}$").all()


def test_comuna_codes_keep_leading_zero(editorial_csvs):
    df = pd.read_csv(
        editorial_csvs["dw_mapa_comunas_chile.csv"], dtype={"cut_comuna": str}
    )
    assert df["cut_comuna"].str.fullmatch(r"\d{5}").all()
