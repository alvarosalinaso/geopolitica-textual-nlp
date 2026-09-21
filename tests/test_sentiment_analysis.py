"""Tests for sentiment_analysis module."""

import json
from pathlib import Path
import pytest

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

from src.sentiment_analysis import (
    analyze_sentiment_lexicon,
    run_sentiment_analysis,
)


def test_analyze_sentiment_lexicon():
    """Test lexicon-based sentiment analysis."""
    if not TEXTBLOB_AVAILABLE:
        pytest.skip("TextBlob not available")
    texts = [
        "This is a great speech about peace.",
        "War is terrible and causes suffering.",
        "The meeting took place on Tuesday."
    ]
    results = analyze_sentiment_lexicon(texts)
    assert len(results) == 3
    for r in results:
        assert "polarity" in r
        assert "subjectivity" in r
        assert "label" in r
        assert r["label"] in ["positivo", "negativo", "neutral"]


def test_analyze_sentiment_lexicon_empty():
    """Test with empty list."""
    results = analyze_sentiment_lexicon([])
    assert results == []


def test_analyze_sentiment_lexicon_no_textblob():
    """Test analyze_sentiment_lexicon when TextBlob not available."""
    import src.sentiment_analysis as sa_module
    original_available = sa_module.TEXTBLOB_AVAILABLE
    sa_module.TEXTBLOB_AVAILABLE = False
    try:
        results = analyze_sentiment_lexicon(["test"])
        assert results == []
    finally:
        sa_module.TEXTBLOB_AVAILABLE = original_available


def test_run_sentiment_analysis_returns_dict(tmp_path):
    """Test that run_sentiment_analysis returns a dict."""
    if not TEXTBLOB_AVAILABLE:
        pytest.skip("TextBlob not available")
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    import pandas as pd
    fallback = data_dir / "sample_speeches.csv"
    pd.DataFrame({
        "speaker": ["Speaker A", "Speaker B"],
        "year": [2020, 2021],
        "text": [
            "This is a positive speech about cooperation and peace.",
            "This speech discusses conflict and war negatively."
        ]
    }).to_csv(fallback, index=False)

    result = run_sentiment_analysis(data_dir=data_dir, output_dir=output_dir)
    assert isinstance(result, dict)
    assert "method" in result
    assert "n_documents" in result
    assert "polarity_distribution" in result


def test_run_sentiment_analysis_creates_output_file(tmp_path):
    """Test that run_sentiment_analysis creates sentiment_results.json."""
    if not TEXTBLOB_AVAILABLE:
        pytest.skip("TextBlob not available")
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    import pandas as pd
    fallback = data_dir / "sample_speeches.csv"
    pd.DataFrame({
        "speaker": ["Speaker A"],
        "year": [2020],
        "text": ["This is a positive speech about cooperation and peace."]
    }).to_csv(fallback, index=False)

    result = run_sentiment_analysis(data_dir=data_dir, output_dir=output_dir)
    output_file = output_dir / "sentiment_results.json"
    assert output_file.exists()

    with open(output_file) as f:
        content = json.load(f)
    assert content["method"] in ["textblob", "openai"]
    assert content["n_documents"] >= 1