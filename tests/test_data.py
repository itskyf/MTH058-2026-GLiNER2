"""Tests for incident data models and fixtures."""

from mth058.data.fixtures import load_sample_incident
from mth058.models import Incident


def test_load_sample_incident() -> None:
    """Test loading a sample incident from JSON fixture."""
    incident_data = load_sample_incident()
    assert isinstance(incident_data, dict)

    # This should be able to be parsed by the Incident model
    incident = Incident.model_validate(incident_data)
    assert isinstance(incident, Incident)
    assert incident.raw_text is not None
    assert len(incident.entities) >= 0
