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

CONFIDENCE_THRESHOLD = 0.3


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
        # Get raw scores for threshold logic
        severity_dist = self.classifier.classify_with_distribution(
            text,
            config["severity_labels"],
            normalize=False,
        )
        team_dist = self.classifier.classify_with_distribution(
            text,
            config["team_labels"],
            normalize=False,
        )

        severity = "Unknown"
        if severity_dist:
            top_sev = max(severity_dist.items(), key=lambda x: x[1])
            if top_sev[1] >= CONFIDENCE_THRESHOLD:
                severity = top_sev[0]

        team = "Unknown"
        if team_dist:
            top_team = max(team_dist.items(), key=lambda x: x[1])
            if top_team[1] >= CONFIDENCE_THRESHOLD:
                team = top_team[0]

        # Normalize distributions for UI display (sum to 100%)
        def normalize_dict(d: dict[str, float]) -> dict[str, float]:
            total = sum(d.values())
            if total > 0:
                return {k: v / total for k, v in d.items()}
            return d

        severity_dist_ui = normalize_dict(severity_dist)
        team_dist_ui = normalize_dict(team_dist)

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
            severity_distribution=severity_dist_ui,
            team=team,
            team_distribution=team_dist_ui,
            impact="Yes (Assessed from report)",  # Placeholder
            redacted_text=redacted_text,
            is_safe=is_safe,
        )

        # 6. Find Similar Incidents
        similar_incidents = self.similarity.find_similar(incident, self.fixtures)

        return incident, similar_incidents
