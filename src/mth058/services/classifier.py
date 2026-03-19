"""Service for classification using GLiNER2.

This module provides a ClassifierService class that uses the GLiNER2
model to categorize incidents by severity, team, or other categories
using zero-shot extraction patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mth058.models import GlinerClassificationResults

if TYPE_CHECKING:
    from gliner2 import GLiNER2


class ClassifierService:
    """Service for classifying text attributes using GLiNER2."""

    def __init__(self, model: GLiNER2) -> None:
        """Initializes the ClassifierService with a shared model.

        Args:
            model (GLiNER): The shared GLiNER model instance.
        """
        self.model = model

    def classify(self, text: str, labels: list[str], threshold: float = 0.3) -> str:
        """Categorizes text into one of the provided labels.

        Args:
            text (str): The raw text to classify.
            labels (list[str]): The candidate labels for classification.
            threshold (float): Score threshold for valid extraction.

        Returns:
            str: The best matching label, or "Unknown" if no match exceeds threshold.
        """
        if not text or not labels:
            return "Unknown"

        # Use classify_text for efficient categorization
        results_dict = self.model.classify_text(
            text,
            {"category": labels},
            threshold=threshold,
            include_confidence=True,
        )

        # Use Pydantic model for static typing instead of raw string keys
        results = GlinerClassificationResults.model_validate(results_dict)
        result = results.category

        if isinstance(result, str):
            return result or "Unknown"

        if result.confidence >= threshold:
            return result.label

        return "Unknown"
