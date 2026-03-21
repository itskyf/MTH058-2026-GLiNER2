"""Service for classification using GLiNER2.

This module provides a ClassifierService class that uses the GLiNER2
model to categorize incidents by severity, team, or other categories
using zero-shot extraction patterns.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gliner2 import GLiNER2

logger = logging.getLogger(__name__)


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
        dist = self.classify_with_distribution(text, labels, threshold)
        if not dist:
            return "Unknown"

        # Return the top label if it exceeds threshold (sorted by confidence)
        top_label = max(dist.items(), key=lambda item: item[1])
        if top_label[1] >= threshold:
            return top_label[0]

        return "Unknown"

    def classify_with_distribution(
        self,
        text: str,
        labels: list[str],
    ) -> dict[str, float]:
        """Categorizes text and returns the full probability distribution.

        Args:
            text (str): The raw text to classify.
            labels (list[str]): The candidate labels for classification.

        Returns:
            dict[str, float]: A mapping of labels to their confidence scores.
        """
        if not text or not labels:
            return {}

        # Use classify_text with multi_label=True and cls_threshold=0.0
        # to get scores for all labels instead of just the ones above default threshold.
        results_dict = self.model.classify_text(
            text,
            {
                "category": {
                    "labels": labels,
                    "multi_label": True,
                    "cls_threshold": 0.0,
                },
            },
            threshold=0.0,  # Get all scores
            include_confidence=True,
        )

        # The GLiNER2 engine returns a list of dictionaries when multi_label=True
        # and include_confidence=True: [{"label": "Sev-1", "confidence": 0.9}, ...]
        raw_results = results_dict.get("category", [])

        if not isinstance(raw_results, list):
            # Fallback for unexpected format
            return {}

        # Convert list of label/confidence dicts to a flat dict for gr.Label
        dist = {item["label"]: item["confidence"] for item in raw_results}

        # Ensure all requested labels are present (even if 0.0)
        for label in labels:
            if label not in dist:
                dist[label] = 0.0

        logger.info(
            "Classification distribution for labels %s: %s",
            labels,
            dist,
        )
        return dist
