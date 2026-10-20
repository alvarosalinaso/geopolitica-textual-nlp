"""Tests for topic_analysis module."""

import pandas as pd

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
    pd.DataFrame(
        {
            "year": [2020, 2021, 2022],
            "speaker": ["A", "B", "C"],
            "text": [
                "Chile y Argentina firmaron un acuerdo de paz.",
                "Brasil y Perú discutieron comercio regional.",
                "Bolivia y Chile conversaron sobre acceso al mar.",
            ],
        }
    ).to_csv(csv_path, index=False)

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


def test_umass_coherence_returns_tuple():
    """_umass_coherence returns (scores, avg) and handles degenerate topics."""
    from scipy.sparse import csr_matrix

    from src.topic_analysis import _umass_coherence

    # Matriz 3 docs x 4 palabras: presencia binaria.
    word_matrix = csr_matrix(
        [
            [1, 1, 0, 0],  # doc 0: a, b
            [1, 0, 1, 0],  # doc 1: a, c
            [0, 1, 1, 0],  # doc 2: b, c
        ]
    )
    feature_names = ["a", "b", "c", "d"]
    topics_words = [
        {"words": ["a", "b", "c", "d"]},  # d no está en ningún doc
        {"words": ["x"]},  # < 2 palabras -> score 0
    ]
    scores, avg = _umass_coherence(topics_words, word_matrix, feature_names)
    assert isinstance(scores, list)
    assert len(scores) == 2
    assert scores[1] == 0.0
    assert isinstance(avg, float)


def test_analyze_topics_reports_coherence_and_best_k(tmp_path, monkeypatch):
    """El resultado expone coherence_umass, best_k, k_candidates y coherence_method."""
    import src.topic_analysis as topic_module

    monkeypatch.setattr(topic_module, "BASE", tmp_path)

    data_dir = tmp_path / "data" / "processed"
    data_dir.mkdir(parents=True)

    csv_path = data_dir / "speeches.csv"
    pd.DataFrame(
        {
            "year": [2020, 2021, 2022, 2023, 2024],
            "speaker": ["A", "B", "C", "D", "E"],
            "text": [
                "Chile y Argentina firmaron un acuerdo de paz y comercio regional.",
                "Brasil y Perú discutieron comercio regional y cooperación económica.",
                "Bolivia y Chile conversaron sobre acceso al mar y comercio.",
                "Perú y Colombia firmaron acuerdos de comercio y paz regional.",
                "Argentina y Brasil promovieron comercio y cooperación económica.",
            ],
        }
    ).to_csv(csv_path, index=False)

    result = analyze_topics(n_topics=2)
    assert "coherence_umass" in result
    assert "best_k" in result
    assert "k_candidates" in result
    assert "coherence_method" in result
    assert result["coherence_method"] == "umass_local"
    assert result["best_k"] in result["k_candidates"]
    assert len(result["topics"]) == result["best_k"]


def test_clean_lemmatize_optional():
    """_clean(lemmatize=True) funciona con spaCy si está disponible; no truena si no."""
    from src.topic_analysis import _clean

    result = _clean("Los presidentes hablaron sobre la educación.", lemmatize=True)
    assert isinstance(result, str)
    # Sin lematizar (por defecto), los tokens se conservan tal cual tras quitar stopwords.
    result_off = _clean("Los presidentes hablaron sobre la educación.", lemmatize=False)
    assert "presidentes" in result_off
