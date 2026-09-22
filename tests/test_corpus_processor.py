"""Tests for corpus_processor module."""

import pandas as pd
import pytest

try:
    from src.corpus_processor import GeopoliticalExtractor, create_sample_speeches

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


def test_geopolitical_extractor_init():
    """Test that GeopoliticalExtractor initializes correctly."""
    if not SPACY_AVAILABLE:
        pytest.skip("spaCy not available")
    extractor = GeopoliticalExtractor("es_core_news_sm")
    assert extractor is not None
    assert hasattr(extractor, "nlp")


def test_process_corpus_returns_dataframe(tmp_path):
    """Test that process_corpus returns a DataFrame."""
    if not SPACY_AVAILABLE:
        pytest.skip("spaCy not available")
    csv_path = tmp_path / "speeches.csv"
    pd.DataFrame(
        {
            "year": [2020, 2021],
            "speaker": ["Speaker A", "Speaker B"],
            "text": [
                "El presidente de Chile visitó Argentina.",
                "Mención a Brasil y Perú.",
            ],
        }
    ).to_csv(csv_path, index=False)

    extractor = GeopoliticalExtractor("es_core_news_sm")
    if extractor.nlp is None:
        pytest.skip("spaCy model not available")

    result = extractor.process_corpus(str(csv_path))
    assert isinstance(result, pd.DataFrame)
    assert "Year" in result.columns
    assert "Speaker" in result.columns
    assert "Mentioned_Location" in result.columns


def test_process_corpus_empty_csv(tmp_path):
    """Test processing an empty CSV returns empty DataFrame."""
    if not SPACY_AVAILABLE:
        pytest.skip("spaCy not available")
    csv_path = tmp_path / "empty.csv"
    pd.DataFrame({"year": [], "speaker": [], "text": []}).to_csv(csv_path, index=False)

    extractor = GeopoliticalExtractor("es_core_news_sm")
    if extractor.nlp is None:
        pytest.skip("spaCy model not available")

    result = extractor.process_corpus(str(csv_path))
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_extract_entities_with_confidence():
    """Test extract_entities_with_confidence returns detailed entity info."""
    if not SPACY_AVAILABLE:
        pytest.skip("spaCy not available")
    extractor = GeopoliticalExtractor("es_core_news_sm")
    if extractor.nlp is None:
        pytest.skip("spaCy model not available")

    text = "El presidente de Chile visitó Argentina y se reunió con el presidente de Brasil en Santiago."
    entities = extractor.extract_entities_with_confidence(text)

    assert isinstance(entities, list)
    assert len(entities) >= 3  # Chile, Argentina, Brasil, Santiago

    for ent in entities:
        assert "text" in ent
        assert "label" in ent
        assert "start_char" in ent
        assert "end_char" in ent
        assert "confidence" in ent
        assert ent["label"] in ["LOC", "GPE", "ORG", "PERSON", "NORP"]


def test_extract_entities_no_nlp():
    """Test extract_entities_with_confidence when NLP not available."""
    if not SPACY_AVAILABLE:
        pytest.skip("spaCy not available")
    extractor = GeopoliticalExtractor("es_core_news_sm")
    extractor.nlp = None  # Force no NLP

    entities = extractor.extract_entities_with_confidence("Chile y Argentina")
    assert entities == []


def test_create_sample_speeches():
    """Test create_sample_speeches returns valid DataFrame."""
    if not SPACY_AVAILABLE:
        pytest.skip("spaCy not available")
    df = create_sample_speeches()

    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 7
    assert "year" in df.columns
    assert "speaker" in df.columns
    assert "text" in df.columns
    assert df["year"].dtype in ["int64", "int32"]
    # Check we have real Chilean locations mentioned
    all_text = " ".join(df["text"].tolist())
    assert "Chile" in all_text
    assert "Santiago" in all_text
    assert "Valparaíso" in all_text or "Antofagasta" in all_text
