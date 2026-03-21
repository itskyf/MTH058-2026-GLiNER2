"""Orchestrator service for coordinating incident analysis.

This module provides the Orchestrator class which coordinates
extraction, classification, redaction, and similarity services to
process incident reports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mth058.models import Incident

if TYPE_CHECKING:
    from mth058.services.classifier import ClassifierService
    from mth058.services.extractor import ExtractorService
    from mth058.services.redactor import RedactorService
    from mth058.services.similarity import SimilarityService


class Orchestrator:
    """Coordinates services to analyze and triage incidents."""

    def __init__(
        self,
        extractor: ExtractorService,
        classifier: ClassifierService,
        redactor: RedactorService,
        similarity: SimilarityService,
        fixtures: list[Incident] | None = None,
    ) -> None:
        """Initializes the Orchestrator with required services.

        Args:
            extractor: Service for entity extraction.
            classifier: Service for classification.
            redactor: Service for PII redaction.
            similarity: Service for finding similar incidents.
            fixtures: Optional list of historical incidents for similarity search.
        """
        self.extractor = extractor
        self.classifier = classifier
        self.redactor = redactor
        self.similarity = similarity
        self.fixtures = fixtures or []

    def run_analysis(
        self,
        text: str,
        config: dict[str, list[str]],
    ) -> tuple[Incident, list[Incident]]:
        """Performs full analysis on the provided incident text.

        Args:
            text: The raw incident report text.
            config: Configuration dictionary containing labels for extraction,
                classification, and redaction.

        Returns:
            A tuple containing the analyzed Incident object and a list of
            similar incidents.

        Raises:
            ValueError: If text is empty or config is missing required labels.
        """
        if not text:
            msg = "Text cannot be empty"
            raise ValueError(msg)

        required_config_keys = [
            "extraction_labels",
            "pii_labels",
            "severity_labels",
            "team_labels",
        ]
        if not all(key in config for key in required_config_keys):
            msg = "Missing required labels in config"
            raise ValueError(msg)

        # 1. Extract Entities
        entities = self.extractor.extract(text, config["extraction_labels"])

        # 2. Classify Severity and Team
        severity = self.classifier.classify(text, config["severity_labels"])
        team = self.classifier.classify(text, config["team_labels"])

        # 3. Redact PII
        redacted_text = self.redactor.redact(text, entities, config["pii_labels"])

        # 4. Final PII Safety Check
        # Re-run extraction on redacted text to ensure no PII remains
        remaining_pii = self.extractor.extract(redacted_text, config["pii_labels"])
        is_safe = len(remaining_pii) == 0

        # 5. Create Incident Object
        # Note: impact is currently just a placeholder or could be classified
        incident = Incident(
            raw_text=text,
            entities=entities,
            severity=severity,
            team=team,
            impact="Yes (Assessed from report)",  # Placeholder
            redacted_text=redacted_text,
            is_safe=is_safe,
        )

        # 6. Find Similar Incidents
        similar_incidents = self.similarity.find_similar(incident, self.fixtures)

        return incident, similar_incidents
