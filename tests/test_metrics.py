"""Tests de funciones puras en src/metrics.py."""

import math

import numpy as np
import pandas as pd

from src.metrics import (
    century_label,
    cramers_v,
    label_distribution,
    lexicon_polarity,
    lexicon_subjectivity,
    location_frequency_stats,
    percentage,
    polarity_label,
    safe_divide,
    uniform_expected,
)


def test_safe_divide_zero_denominator_is_nan():
    out = safe_divide(pd.Series([1.0, 4.0]), pd.Series([0, 2]))
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 2.0
    assert np.isinf(out).sum() == 0


def test_safe_divide_scalar_zero():
    assert safe_divide(pd.Series([3.0]), 0).isna().all()


def test_percentage():
    assert percentage(56, 5724) == 1.0
    assert percentage(1, 0) == 0.0


def test_lexicon_scores():
    assert lexicon_polarity(3, 1) == 0.4
    assert lexicon_polarity(0, 0) == 0.0
    assert lexicon_subjectivity(2, 0) == 2.0
    assert lexicon_subjectivity(2, 10) == 0.2


def test_polarity_label_thresholds():
    assert polarity_label(0.2, 0.1, -0.1) == "positivo"
    assert polarity_label(-0.2, 0.1, -0.1) == "negativo"
    assert polarity_label(0.1, 0.1, -0.1) == "neutral"


def test_label_distribution_includes_zero_categories():
    dist = label_distribution(pd.Series(["positivo", "positivo"]))
    assert dist == {"positivo": 2, "neutral": 0, "negativo": 0}


def test_cramers_v_and_uniform_expected():
    assert uniform_expected([10, 20, 30]) == [20.0, 20.0, 20.0]
    assert uniform_expected([]) == []
    assert math.isclose(cramers_v(8.0, 100, 3), 0.2)
    assert cramers_v(5.0, 0, 3) == 0.0
    assert cramers_v(5.0, 10, 1) == 0.0


def test_century_label():
    assert century_label(1832) == "19th"
    assert century_label(2022) == "21th"


def test_location_frequency_stats():
    places = pd.DataFrame(
        {
            "Mentioned_Location": ["Talca", "Talca", "Talca", "Arica"],
            "Year": [1900, 1900, 1950, 1990],
        }
    )
    stats = location_frequency_stats(places).set_index("Mentioned_Location")
    assert stats.loc["Talca", "total_mentions"] == 3
    assert stats.loc["Talca", "speeches"] == 2
    assert stats.loc["Talca", "avg_per_speech"] == 1.5
