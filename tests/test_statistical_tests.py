"""Tests for statistical_tests module."""

import json

from src.statistical_tests import run_statistical_tests


def test_run_statistical_tests_uses_label_totals(tmp_path):
    """Uses label_totals (complete counts) when present, not top_entities truncation."""
    data_dir = tmp_path / "data"
    export_dir = tmp_path / "export"
    data_dir.mkdir()
    export_dir.mkdir()

    ner_file = data_dir / "ner_entities.json"
    ner_file.write_text(
        json.dumps(
            {
                "total_entities": 10,
                "label_totals": {"GPE": 7, "LOC": 3, "ORG": 5, "PERSON": 8, "NORP": 2},
                "top_entities": [
                    {"entity": "Chile", "label": "GPE", "count": 5},
                    {"entity": "Andes", "label": "LOC", "count": 3},
                ],
            }
        )
    )

    result = run_statistical_tests(data_dir=data_dir, output_dir=export_dir)
    chi = result["chi_squared_entity_types"]
    # label_totals sum = 7+3+5+8+2 = 25, not top_entities sum 5+3=8
    assert chi["n_total"] == 25
    assert chi["observed_distribution"] == {
        "GPE": 7,
        "LOC": 3,
        "ORG": 5,
        "PERSON": 8,
        "NORP": 2,
    }
    assert "cramers_v" in chi
    assert isinstance(chi["caveats"], list)
    assert len(chi["caveats"]) >= 2


def test_run_statistical_tests_fallback_from_top_entities(tmp_path):
    """Falls back to summing top_entities counts when label_totals missing, with caveat."""
    data_dir = tmp_path / "data"
    export_dir = tmp_path / "export"
    data_dir.mkdir()
    export_dir.mkdir()

    ner_file = data_dir / "ner_entities.json"
    ner_file.write_text(
        json.dumps(
            {
                "total_entities": 10,
                "top_entities": [
                    {"entity": "Chile", "label": "GPE", "count": 5},
                    {"entity": "Argentina", "label": "GPE", "count": 3},
                    {"entity": "ONU", "label": "ORG", "count": 2},
                ],
            }
        )
    )

    result = run_statistical_tests(data_dir=data_dir, output_dir=export_dir)
    chi = result["chi_squared_entity_types"]
    # GPE=8, ORG=2
    assert chi["n_total"] == 10
    assert chi["observed_distribution"] == {"GPE": 8, "ORG": 2}
    # Fallback warning must be present in caveats
    assert any("label_totals ausente" in c for c in chi["caveats"])


def test_run_statistical_tests_no_data(tmp_path):
    """Missing ner_entities.json returns empty dict."""
    data_dir = tmp_path / "data"
    export_dir = tmp_path / "export"
    data_dir.mkdir()
    export_dir.mkdir()

    result = run_statistical_tests(data_dir=data_dir, output_dir=export_dir)
    assert result == {}


def test_run_statistical_tests_creates_output_file(tmp_path):
    """Creates statistical_tests.json on disk."""
    data_dir = tmp_path / "data"
    export_dir = tmp_path / "export"
    data_dir.mkdir()
    export_dir.mkdir()

    ner_file = data_dir / "ner_entities.json"
    ner_file.write_text(
        json.dumps(
            {
                "total_entities": 10,
                "label_totals": {"GPE": 7, "LOC": 3},
                "top_entities": [],
            }
        )
    )

    run_statistical_tests(data_dir=data_dir, output_dir=export_dir)
    output_file = export_dir / "statistical_tests.json"
    assert output_file.exists()

    with open(output_file) as f:
        content = json.load(f)
    assert "chi_squared_entity_types" in content
