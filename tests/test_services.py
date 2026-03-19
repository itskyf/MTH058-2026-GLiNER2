"""Tests for extraction and classification services."""

from unittest.mock import MagicMock

import pytest

from mth058.services.classifier import ClassifierService
from mth058.services.extractor import ExtractorService


@pytest.fixture
def mock_model() -> MagicMock:
    """Provides a mocked GLiNER model for testing."""
    model = MagicMock()
    # Mocking the extract_entities method
    model.extract_entities.return_value = [
        {"start": 0, "end": 8, "label": "PERSON", "text": "John Doe", "score": 0.99},
    ]
    return model


def test_extractor_service_extract(mock_model: MagicMock) -> None:
    """Test entity extraction from text."""
    service = ExtractorService(model=mock_model)
    text = "John Doe reported an incident."
    labels = ["PERSON", "ORG"]

    entities = service.extract(text, labels)

    assert len(entities) == 1
    assert entities[0].label == "PERSON"
    assert entities[0].text == "John Doe"
    mock_model.extract_entities.assert_called_once()


def test_extractor_chunking_via_public_api(mock_model: MagicMock) -> None:
    """Test that long text is processed across multiple chunks."""
    service = ExtractorService(model=mock_model, chunk_size=10, chunk_overlap=2)
    text = "This is a long text for testing."
    labels = ["PERSON"]

    service.extract(text, labels)

    assert mock_model.extract_entities.call_count > 1


def test_classifier_service_classify(mock_model: MagicMock) -> None:
    """Test text classification using GLiNER."""
    # Mock specific return for classification
    mock_model.extract_entities.return_value = [
        {"label": "Critical", "score": 0.95},
    ]

    service = ClassifierService(model=mock_model)
    text = "There is a massive database outage!"
    labels = ["Low", "Medium", "High", "Critical"]

    result = service.classify(text, labels)

    assert result == "Critical"
    mock_model.extract_entities.assert_called_once()
