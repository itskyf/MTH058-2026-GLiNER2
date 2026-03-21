"""Tests for the Orchestrator service."""

from unittest.mock import MagicMock

import pytest

from mth058.models import Entity, Incident
from mth058.services.orchestrator import Orchestrator

# Test constants
EXPECTED_ENTITY_COUNT = 2


@pytest.fixture
def mock_extractor() -> MagicMock:
    """Create a mock extractor service."""
    service = MagicMock()

    def side_effect(text: str, _labels: list[str]) -> list[Entity]:
        # If text looks redacted, return no entities
        if "[PERSON]" in text or "Redacted" in text:
            return []
        # Otherwise return mock entities
        return [
            Entity(label="PERSON", text="John Doe", start=0, end=8, score=0.99),
            Entity(label="ORG", text="Acme Corp", start=12, end=21, score=0.95),
        ]

    service.extract.side_effect = side_effect
    return service


@pytest.fixture
def mock_classifier() -> MagicMock:
    """Create a mock classifier service."""
    service = MagicMock()
    # Simple mock that returns based on the first label in the list for testing
    service.classify.side_effect = lambda _text, labels, _threshold=0.3: (
        labels[0] if labels else "Unknown"
    )

    def mock_dist(
        _text: str,
        labels: list[str],
        *,
        normalize: bool = False,
    ) -> dict[str, float]:
        _ = normalize  # Dummy use to satisfy linter
        if not labels:
            return {}
        # Assign 0.9 to first label, split 0.1 among others
        d = {labels[0]: 0.9}
        if len(labels) > 1:
            for i in range(1, len(labels)):
                d[labels[i]] = 0.1 / (len(labels) - 1)
        return d

    service.classify_with_distribution.side_effect = mock_dist
    return service


@pytest.fixture
def mock_redactor() -> MagicMock:
    """Create a mock redactor service."""
    service = MagicMock()
    service.redact.return_value = "Redacted text"
    return service


@pytest.fixture
def mock_similarity() -> MagicMock:
    """Create a mock similarity service."""
    service = MagicMock()
    service.find_similar.return_value = []
    return service


@pytest.fixture
def orchestrator(
    mock_extractor: MagicMock,
    mock_classifier: MagicMock,
    mock_redactor: MagicMock,
    mock_similarity: MagicMock,
) -> Orchestrator:
    """Create an Orchestrator instance with mock services."""
    return Orchestrator(
        extractor=mock_extractor,
        classifier=mock_classifier,
        redactor=mock_redactor,
        similarity=mock_similarity,
    )


def test_run_analysis_returns_incident_and_similar_list(
    orchestrator: Orchestrator,
) -> None:
    """Test that run_analysis returns the expected tuple."""
    text = "John Doe from Acme Corp reported an issue."
    config = {
        "extraction_labels": ["PERSON", "ORG"],
        "pii_labels": ["PERSON"],
        "severity_labels": ["Low", "Medium", "High"],
        "team_labels": ["IT", "HR"],
    }

    incident, similar = orchestrator.run_analysis(text, config)

    assert isinstance(incident, Incident)
    assert isinstance(similar, list)
    assert incident.raw_text == text
    assert len(incident.entities) == EXPECTED_ENTITY_COUNT
    assert incident.redacted_text == "Redacted text"
    assert incident.is_safe is True


def test_run_analysis_pii_safety_check(
    orchestrator: Orchestrator,
    mock_redactor: MagicMock,
) -> None:
    """Test that is_safe is False if PII labels remain in redacted text."""
    text = "John Doe reported an issue."
    config = {
        "extraction_labels": ["PERSON"],
        "pii_labels": ["PERSON"],
        "severity_labels": ["Low"],
        "team_labels": ["IT"],
    }

    # Mock redactor to fail to redact everything
    mock_redactor.redact.return_value = "John Doe reported an issue."

    incident, _ = orchestrator.run_analysis(text, config)
    assert incident.is_safe is False


def test_run_analysis_validation_empty_text(orchestrator: Orchestrator) -> None:
    """Test that run_analysis raises ValueError for empty text."""
    with pytest.raises(ValueError, match="Text cannot be empty"):
        orchestrator.run_analysis("", {})


def test_run_analysis_validation_missing_config(orchestrator: Orchestrator) -> None:
    """Test that run_analysis raises ValueError for missing config labels."""
    with pytest.raises(ValueError, match="Missing required labels in config"):
        orchestrator.run_analysis("Some text", {})
