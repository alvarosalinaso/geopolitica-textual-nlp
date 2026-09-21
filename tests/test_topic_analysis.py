"""Tests for topic_analysis module."""

import json
import pandas as pd
from pathlib import Path
import pytest

from src.topic_analysis import _clean, analyze_topics


def test_clean_removes_stopwords():
    """Test _clean removes Spanish stopwords."""
    text = "el presidente de Chile habló sobre la paz"
    result = _clean(text)
    result_words = result.split()
    assert "el" not in result_words
    assert "de" not in result_words
    assert "la" not in result_words
    assert "sobre" not in result_words
    assert "presidente" in result_words
    assert "chile" in result_words
    assert "paz" in result_words


def test_clean_lowercases():
    """Test _clean lowercases text."""
    text = "CHILE Y ARGENTINA"
    result = _clean(text)
    assert result == result.lower()


def test_clean_removes_punctuation():
    """Test _clean removes punctuation."""
    text = "Chile, Argentina; Brasil!"
    result = _clean(text)
    assert "," not in result
    assert ";" not in result
    assert "!" not in result


def test_analyze_topics_returns_dict(tmp_path, monkeypatch):
    """Test analyze_topics returns expected structure."""
    # Change BASE to tmp_path
    import src.topic_analysis as topic_module
    monkeypatch.setattr(topic_module, "BASE", tmp_path)

    data_dir = tmp_path / "data" / "processed"
    data_dir.mkdir(parents=True)

    csv_path = data_dir / "speeches.csv"
    pd.DataFrame({
        "year": [2020, 2021, 2022],
        "speaker": ["A", "B", "C"],
        "text": [
            "Chile y Argentina firmaron un acuerdo de paz.",
            "Brasil y Perú discutieron comercio regional.",
            "Bolivia y Chile conversaron sobre acceso al mar."
        ]
    }).to_csv(csv_path, index=False)

    result = analyze_topics(n_topics=3)
    assert isinstance(result, dict)
    assert "total_documents" in result
    assert "bigrams" in result
    assert "topics" in result
    assert "document_topics" in result
    assert result["total_documents"] == 3


def test_analyze_topics_no_data(tmp_path, monkeypatch):
    """Test analyze_topics with missing CSV."""
    import src.topic_analysis as topic_module
    monkeypatch.setattr(topic_module, "BASE", tmp_path)

    result = analyze_topics()
    assert result is None