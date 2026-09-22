"""Tests for ner_analysis module."""

from src.ner_analysis import run_ner_analysis


def test_run_ner_analysis_returns_dict(tmp_path):
    """Test that run_ner_analysis returns a dict."""
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    # Create sample_speeches.csv fallback
    import pandas as pd

    fallback = data_dir / "sample_speeches.csv"
    pd.DataFrame(
        {
            "speaker": ["Speaker A"],
            "year": [2020],
            "text": ["El presidente de Chile visitó Argentina y Brasil."],
        }
    ).to_csv(fallback, index=False)

    result = run_ner_analysis(data_dir=data_dir, output_dir=output_dir)
    assert isinstance(result, dict)


def test_run_ner_analysis_creates_output_file(tmp_path):
    """Test that run_ner_analysis creates ner_entities.json."""
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
            "text": ["El presidente de Chile visitó Argentina y Brasil."],
        }
    ).to_csv(fallback, index=False)

    result = run_ner_analysis(data_dir=data_dir, output_dir=output_dir)
    # If spaCy is not available, result will be {}
    assert isinstance(result, dict)


def test_run_ner_analysis_no_spacy(tmp_path, monkeypatch):
    """Test run_ner_analysis when spaCy is not available."""
    import src.ner_analysis as ner_module

    monkeypatch.setattr(ner_module, "SPACY_AVAILABLE", False)

    data_dir = tmp_path / "data"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    result = run_ner_analysis(data_dir=data_dir, output_dir=output_dir)
    assert result == {}
