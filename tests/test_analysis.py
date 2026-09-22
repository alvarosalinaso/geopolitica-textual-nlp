"""Smoke tests for geopolitica-textual-nlp."""

import pytest


def test_imports():
    from src.generate_report import generate_report
    from src.geo_analysis import run_geo_analysis
    from src.ner_analysis import run_ner_analysis
    from src.rag_analysis import run_rag_analysis
    from src.sentiment_analysis import run_sentiment_analysis
    from src.statistical_tests import run_statistical_tests

    assert callable(run_ner_analysis)
    assert callable(run_sentiment_analysis)
    assert callable(run_geo_analysis)
    assert callable(run_rag_analysis)
    assert callable(run_statistical_tests)
    assert callable(generate_report)


def test_import_generate_tables():
    """Test generate_tables import (may fail if great_tables not installed)."""
    try:
        from src.generate_tables import generate

        assert callable(generate)
    except ImportError:
        pytest.skip("great_tables not available")
