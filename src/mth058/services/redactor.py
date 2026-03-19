"""PII Redactor service.

This module provides a service to mask personally identifiable
information (PII) in incident reports.
"""

from mth058.models import Entity


class RedactorService:
    """Service for redacting PII from text based on extracted entities."""

    def redact(
        self,
        text: str,
        entities: list[Entity],
        pii_labels: list[str],
        template: str = "[{label}]",
    ) -> str:
        """Redact entities labeled as PII from the provided text.

        Args:
            text (str): The original text to redact.
            entities (list[Entity]): List of extracted entities.
            pii_labels (list[str]): List of entity labels to be considered PII.
            template (str): Template for the redaction marker.
                Supports {label} and {text} placeholders.

        Returns:
            str: The redacted text where PII is replaced by the template.
        """
        # Sort entities by start index in reverse to avoid offset shifts
        sorted_entities = sorted(entities, key=lambda x: x.start, reverse=True)

        redacted_text = text
        for entity in sorted_entities:
            if entity.label in pii_labels:
                marker = template.format(label=entity.label, text=entity.text)
                redacted_text = (
                    redacted_text[: entity.start] + marker + redacted_text[entity.end :]
                )

        return redacted_text
