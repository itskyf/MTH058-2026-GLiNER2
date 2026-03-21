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


TUPLE_PAIR_LENGTH = 2


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
        dist = self.classify_with_distribution(text, labels, normalize=False)
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
        *,
        normalize: bool = False,
    ) -> dict[str, float]:
        """Categorizes text and returns the full probability distribution.

        Args:
            text (str): The raw text to classify.
            labels (list[str]): The candidate labels for classification.
            normalize (bool): Whether to normalize scores to sum to 1.0.

        Returns:
            dict[str, float]: A mapping of labels to their confidence scores.
        """
        if not text or not labels:
            return {}

        results_dict = self.model.classify_text(
            text,
            {
                "category": {
                    "labels": labels,
                    "multi_label": True,
                    "cls_threshold": 0.0,
                },
            },
            threshold=0.0,
            include_confidence=True,
        )

        dist = self._process_raw_results(results_dict.get("category", []), labels)

        if normalize:
            total = sum(dist.values())
            if total > 0:
                dist = {label: score / total for label, score in dist.items()}

        logger.info(
            "Classification distribution for labels %s (normalized=%s): %s",
            labels,
            normalize,
            dist,
        )
        return dist

    def _process_raw_results(
        self,
        raw_results: list | dict,
        labels: list[str],
    ) -> dict[str, float]:
        """Processes raw results into a distribution dictionary."""
        if isinstance(raw_results, dict):
            raw_results = [raw_results]
        elif not isinstance(raw_results, list):
            logger.warning("Unexpected GLiNER2 result format: %s", type(raw_results))
            return dict.fromkeys(labels, 0.0)

        dist = {}
        for item in raw_results:
            if isinstance(item, dict) and "label" in item and "confidence" in item:
                dist[item["label"]] = item["confidence"]
            elif isinstance(item, (list, tuple)) and len(item) == TUPLE_PAIR_LENGTH:
                # Handle tuple return format (label, confidence)
                dist[item[0]] = item[1]

        # Ensure all requested labels are present (even if 0.0)
        for label in labels:
            if label not in dist:
                dist[label] = 0.0
        return dist
