"""Tests de validación fail-fast y del data_loader."""

import pandas as pd
import pytest

from scripts.generate_synthetic_sample import build_synthetic_speeches, write_sample
from src.data_loader import find_corpus, load_speeches, read_table, write_json
from src.validator import (
    SchemaError,
    validate_columns,
    validate_entities,
    validate_speeches,
)


def test_synthetic_sample_is_valid_and_deterministic():
    a = build_synthetic_speeches(n=8, seed=1)
    b = build_synthetic_speeches(n=8, seed=1)
    pd.testing.assert_frame_equal(a, b)
    assert validate_speeches(a) is a
    assert a["year"].is_monotonic_increasing


def test_missing_columns_fail_fast():
    df = pd.DataFrame({"year": [1900], "text": ["x"]})
    with pytest.raises(SchemaError, match="speaker"):
        validate_columns(df, ("year", "speaker", "text"))


def test_empty_speeches_fail():
    df = pd.DataFrame({"year": [], "speaker": [], "text": []})
    with pytest.raises(SchemaError, match="vacío"):
        validate_speeches(df)


def test_non_numeric_year_fails():
    df = pd.DataFrame({"year": ["mil"], "speaker": ["A"], "text": ["t"]})
    with pytest.raises(SchemaError, match="year"):
        validate_speeches(df)


def test_validate_entities_requires_keys():
    with pytest.raises(SchemaError, match="count"):
        validate_entities([{"entity": "Chile", "label": "GPE"}])


def test_load_speeches_from_synthetic_csv(tmp_path):
    path = write_sample(tmp_path / "s.csv", n=5, seed=3)
    df = load_speeches(path)
    assert len(df) == 5


def test_find_corpus_prefers_processed(tmp_path):
    write_sample(tmp_path / "sample_speeches.csv", n=3)
    assert find_corpus(tmp_path).name == "sample_speeches.csv"
    write_sample(tmp_path / "processed" / "speeches.csv", n=3)
    assert find_corpus(tmp_path).parent.name == "processed"
    assert find_corpus(tmp_path / "vacio") is None


def test_read_table_rejects_unknown_format(tmp_path):
    path = tmp_path / "data.xyz"
    path.write_text("a", encoding="utf-8")
    with pytest.raises(ValueError, match="no soportado"):
        read_table(path)


def test_read_table_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_table(tmp_path / "no.csv")


def test_write_json_roundtrip(tmp_path):
    out = write_json({"ñ": 1}, tmp_path / "sub" / "x.json")
    assert out.read_text(encoding="utf-8").strip().startswith("{")
