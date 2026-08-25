"""Smoke tests for geopolitica-textual-nlp."""


def test_imports():
    from src.generate_report import generate_report
    from src.generate_tables import generate
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
    assert callable(generate)
    assert callable(generate_report)
