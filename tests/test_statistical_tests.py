"""Tests for statistical_tests module."""

import json
from pathlib import Path
import pytest

from src.statistical_tests import run_statistical_tests


def test_run_statistical_tests_returns_dict(tmp_path):
    """Test that run_statistical_tests returns a dict."""
    # Create mock ner_entities.json
    data_dir = tmp_path / "data"
    export_dir = tmp_path / "export"
    data_dir.mkdir()
    export_dir.mkdir()

    ner_file = data_dir / "ner_entities.json"
    ner_file.write_text(json.dumps({
        "total_entities": 10,
        "top_entities": [
            {"entity": "Chile", "label": "GPE", "count": 5},
            {"entity": "Argentina", "label": "GPE", "count": 3},
            {"entity": "ONU", "label": "ORG", "count": 2}
        ]
    }))

    result = run_statistical_tests(data_dir=data_dir, output_dir=export_dir)
    assert isinstance(result, dict)


def test_run_statistical_tests_no_data(tmp_path):
    """Test run_statistical_tests with missing data returns empty dict."""
    data_dir = tmp_path / "data"
    export_dir = tmp_path / "export"
    data_dir.mkdir()
    export_dir.mkdir()

    result = run_statistical_tests(data_dir=data_dir, output_dir=export_dir)
    assert isinstance(result, dict)
    assert result == {}


def test_run_statistical_tests_creates_output_file(tmp_path):
    """Test that run_statistical_tests creates statistical_tests.json."""
    data_dir = tmp_path / "data"
    export_dir = tmp_path / "export"
    data_dir.mkdir()
    export_dir.mkdir()

    ner_file = data_dir / "ner_entities.json"
    ner_file.write_text(json.dumps({
        "total_entities": 10,
        "top_entities": [
            {"entity": "Chile", "label": "GPE", "count": 5},
            {"entity": "Argentina", "label": "GPE", "count": 3},
            {"entity": "ONU", "label": "ORG", "count": 2}
        ]
    }))

    result = run_statistical_tests(data_dir=data_dir, output_dir=export_dir)
    output_file = export_dir / "statistical_tests.json"
    assert output_file.exists()

    with open(output_file) as f:
        content = json.load(f)
    assert "chi_squared_entity_types" in content