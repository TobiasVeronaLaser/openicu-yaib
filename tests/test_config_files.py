from pathlib import Path

import yaml


def test_mortality_dynamic_vars_config_exists():
    path = Path(__file__).resolve().parents[1] / "configs" / "mortality_dynamic_vars.yml"
    data = yaml.safe_load(path.read_text())
    assert "dynamic_vars" in data
    assert "hr" in data["dynamic_vars"]


def test_concept_mapping_config_exists():
    path = Path(__file__).resolve().parents[1] / "configs" / "concept_mapping.yml"
    data = yaml.safe_load(path.read_text())
    assert data["concept_mapping"]["hr"] == "heart_rate"
