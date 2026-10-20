"""Tests for sentiment_analysis module."""

import importlib.util
import json

import pytest

TEXTBLOB_AVAILABLE = importlib.util.find_spec("textblob") is not None

from src.sentiment_analysis import (
    analyze_sentiment_lexicon,
    analyze_sentiment_textblob,
    run_sentiment_analysis,
    score_spanish_lexicon,
)


def test_analyze_sentiment_lexicon():
    """Test léxico español: textos claramente direccionales."""
    texts = [
        "Este discurso celebra la paz, la cooperación y el progreso de la nación.",
        "La guerra y el sufrimiento causan una crisis terrible e inhumana.",
        "El Congreso Nacional sesionó el martes en Santiago.",
    ]
    results = analyze_sentiment_lexicon(texts)
    assert len(results) == 3
    assert results[0]["label"] == "positivo"
    assert results[1]["label"] == "negativo"
    assert results[2]["label"] == "neutral"
    for r in results:
        assert "polarity" in r
        assert "subjectivity" in r
        assert r["label"] in ["positivo", "negativo", "neutral"]


def test_score_spanish_lexicon_negation():
    """Una negación invierte la polaridad de la palabra siguiente."""
    positive = score_spanish_lexicon("Fue una victoria gloriosa y un éxito.")
    negated = score_spanish_lexicon("No fue una victoria gloriosa ni un éxito.")
    assert positive["polarity"] > 0
    assert negated["polarity"] <= 0


def test_score_spanish_lexicon_ignores_accents():
    """El léxico normaliza acentos: 'éxito' y 'exito' puntúan igual."""
    with_accent = score_spanish_lexicon("Éxito y progreso para el país.")
    without = score_spanish_lexicon("Exito y progreso para el pais.")
    assert with_accent["polarity"] == without["polarity"]


def test_analyze_sentiment_lexicon_empty():
    """Test with empty list."""
    results = analyze_sentiment_lexicon([])
    assert results == []


def test_analyze_sentiment_lexicon_no_deps():
    """El léxico español funciona sin TextBlob ni pandas (sin dependencias)."""
    results = analyze_sentiment_lexicon(["paz y progreso"])
    assert len(results) == 1
    assert results[0]["label"] == "positivo"


@pytest.mark.skipif(not TEXTBLOB_AVAILABLE, reason="TextBlob not available")
def test_analyze_sentiment_textblob():
    """TextBlob (método secundario) devuelve la misma estructura de campos."""
    results = analyze_sentiment_textblob(["This is a great and wonderful speech."])
    assert len(results) == 1
    for key in ("polarity", "subjectivity", "label"):
        assert key in results[0]


def test_run_sentiment_analysis_returns_dict(tmp_path):
    """Test that run_sentiment_analysis returns a dict con method lexicon_es."""
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    import pandas as pd

    fallback = data_dir / "sample_speeches.csv"
    pd.DataFrame(
        {
            "speaker": ["Speaker A", "Speaker B"],
            "year": [2020, 2021],
            "text": [
                (
                    "Este discurso celebra la cooperación regional, la paz "
                    "duradera y el progreso de la nación para las generaciones "
                    "venideras con esperanza y optimismo."
                ),
                (
                    "Este discurso describe la guerra, el conflicto y el "
                    "sufrimiento terrible causado por la violencia y la crisis "
                    "en los países vecinos de la región."
                ),
            ],
        }
    ).to_csv(fallback, index=False)

    result = run_sentiment_analysis(data_dir=data_dir, output_dir=output_dir)
    assert isinstance(result, dict)
    assert "method" in result
    assert "n_documents" in result
    assert "polarity_distribution" in result
    assert result["method"] == "lexicon_es"
    assert result["thresholds_uncalibrated"] is True


def test_run_sentiment_analysis_creates_output_file(tmp_path):
    """Test that run_sentiment_analysis creates sentiment_results.json."""
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    import pandas as pd

    fallback = data_dir / "sample_speeches.csv"
    pd.DataFrame(
        {
            "speaker": ["Speaker A"],
            "year": [2020],
            "text": [
                (
                    "Este discurso positivo habla de cooperación, paz, "
                    "prosperidad, bienestar y entendimiento mutuo entre los "
                    "países vecinos de todo el continente."
                ),
            ],
        }
    ).to_csv(fallback, index=False)

    run_sentiment_analysis(data_dir=data_dir, output_dir=output_dir)
    output_file = output_dir / "sentiment_results.json"
    assert output_file.exists()

    with open(output_file) as f:
        content = json.load(f)
    assert content["method"] == "lexicon_es"
    assert content["n_documents"] >= 1
