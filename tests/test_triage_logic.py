"""Tests for redaction and similarity services."""

from mth058.models import Entity, Incident
from mth058.services.redactor import RedactorService
from mth058.services.similarity import SimilarityService


def test_redactor_service_redact() -> None:
    """Test PII redaction from text."""
    service = RedactorService()
    text = "John Doe (john.doe@example.com) reported an incident at 555-0199."
    entities = [
        Entity(label="PERSON", text="John Doe", start=0, end=8, score=0.99),
        Entity(
            label="EMAIL",
            text="john.doe@example.com",
            start=10,
            end=30,
            score=0.99,
        ),
        Entity(label="PHONE", text="555-0199", start=55, end=63, score=0.99),
    ]
    pii_labels = ["PERSON", "EMAIL", "PHONE"]

    redacted_text = service.redact(text, entities, pii_labels)

    assert "[PERSON]" in redacted_text
    assert "[EMAIL]" in redacted_text
    assert "[PHONE]" in redacted_text
    assert "John Doe" not in redacted_text
    assert "john.doe@example.com" not in redacted_text
    assert "555-0199" not in redacted_text


def test_redactor_service_redact_with_template() -> None:
    """Test custom template redaction for manual verification."""
    service = RedactorService()
    text = "John Doe reported an incident."
    entities = [
        Entity(label="PERSON", text="John Doe", start=0, end=8, score=0.99),
    ]
    pii_labels = ["PERSON"]
    template = "[[{label}:{text}]]"

    redacted_text = service.redact(text, entities, pii_labels, template=template)

    assert "[[PERSON:John Doe]]" in redacted_text


def test_similarity_service_find_similar() -> None:
    """Test finding similar incidents."""
    service = SimilarityService()

    current_incident = Incident(
        raw_text="Database outage in production.",
        sections={"summary": "Database outage", "impact": "High"},
        entities=[
            Entity(label="ORG", text="Production", start=19, end=29, score=0.9),
            Entity(label="ISSUE", text="Database outage", start=0, end=15, score=0.9),
        ],
        severity="High",
        team="DBA",
        impact="Production is down",
    )

    fixtures = [
        Incident(
            raw_text="Database connection issues in staging.",
            sections={"summary": "DB issues", "impact": "Low"},
            entities=[
                Entity(
                    label="ISSUE",
                    text="Database outage",
                    start=0,
                    end=15,
                    score=0.9,
                ),
            ],
            severity="Low",
            team="DBA",
            impact="Staging is slow",
        ),
        Incident(
            raw_text="UI bug on login page.",
            sections={"summary": "UI bug", "impact": "Low"},
            entities=[
                Entity(label="ISSUE", text="UI bug", start=0, end=6, score=0.9),
            ],
            severity="Low",
            team="Frontend",
            impact="Users can't login",
        ),
    ]

    similar = service.find_similar(current_incident, fixtures, top_k=1)

    assert len(similar) == 1
    assert "Database" in similar[0].raw_text
