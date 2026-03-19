"""Tests for incident data models and fixtures."""

import pytest

from mth058.data.fixtures import load_sample_incidents
from mth058.models import Incident

_incidents = load_sample_incidents()


@pytest.mark.parametrize("incident", _incidents)
def test_load_sample_incidents(incident: Incident) -> None:
    """Test loading sample incidents from JSON fixture."""
    assert isinstance(incident, Incident)
    assert incident.raw_text is not None
    assert len(incident.entities) >= 0
