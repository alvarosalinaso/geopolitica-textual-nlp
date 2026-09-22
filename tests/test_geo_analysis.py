"""Tests for geo_analysis module."""

import json

from src.geo_analysis import ENTITY_COORDS, run_geo_analysis


def test_entity_coords_dict():
    """Test that ENTITY_COORDS has expected entries."""
    assert "Chile" in ENTITY_COORDS
    assert "Argentina" in ENTITY_COORDS
    assert "Brasil" in ENTITY_COORDS
    assert isinstance(ENTITY_COORDS["Chile"], tuple)
    assert len(ENTITY_COORDS["Chile"]) == 2


def test_run_geo_analysis_returns_dict(tmp_path):
    """Test that run_geo_analysis returns a dict."""
    data_dir = tmp_path / "export"
    output_dir = tmp_path / "export_out"
    data_dir.mkdir()
    output_dir.mkdir()

    ner_file = data_dir / "ner_entities.json"
    ner_file.write_text(
        json.dumps(
            {
                "total_entities": 5,
                "top_entities": [
                    {"entity": "Chile", "label": "GPE", "count": 10},
                    {"entity": "Argentina", "label": "GPE", "count": 5},
                    {"entity": "Brasil", "label": "GPE", "count": 3},
                ],
            }
        )
    )

    result = run_geo_analysis(data_dir=data_dir, output_dir=output_dir)
    assert isinstance(result, dict)
    if "entities_plotted" in result:
        assert result["entities_plotted"] >= 0


def test_run_geo_analysis_no_folium(tmp_path, monkeypatch):
    """Test run_geo_analysis when folium is not available."""
    import src.geo_analysis as geo_module

    monkeypatch.setattr(geo_module, "FOLIUM_AVAILABLE", False)

    data_dir = tmp_path / "export"
    output_dir = tmp_path / "export_out"
    data_dir.mkdir()
    output_dir.mkdir()

    result = run_geo_analysis(data_dir=data_dir, output_dir=output_dir)
    assert result == {}


def test_run_geo_analysis_no_data(tmp_path):
    """Test run_geo_analysis with missing ner_entities.json."""
    data_dir = tmp_path / "export"
    output_dir = tmp_path / "export_out"
    data_dir.mkdir()
    output_dir.mkdir()

    result = run_geo_analysis(data_dir=data_dir, output_dir=output_dir)
    assert result == {}
