"""Similarity service for finding related incidents.

This module provides a service to find previous incidents that are
similar to a current incident report.
"""

from mth058.models import Incident


class SimilarityService:
    """Service for finding similar incidents based on entity labels."""

    def find_similar(
        self,
        incident: Incident,
        fixtures: list[Incident],
        top_k: int = 3,
    ) -> list[Incident]:
        """Find the top-k similar incidents from a list of fixtures.

        Similarity is calculated based on the Jaccard similarity of the set of
        entity labels extracted from each incident.

        Args:
            incident (Incident): The current incident report.
            fixtures (list[Incident]): A list of historical incident fixtures.
            top_k (int): Number of similar incidents to return.

        Returns:
            list[Incident]: A list of top-k similar incidents sorted by
                decreasing similarity score.
        """
        if not fixtures:
            return []

        # Get unique labels from the current incident
        current_labels = {e.label for e in incident.entities}

        scores = []
        for fixture in fixtures:
            fixture_labels = {e.label for e in fixture.entities}

            # Calculate Jaccard Similarity: |A intersection B| / |A union B|
            intersection = current_labels.intersection(fixture_labels)
            union = current_labels.union(fixture_labels)

            score = 0.0 if not union else len(intersection) / len(union)

            scores.append((score, fixture))

        # Sort by score (descending) and return top_k
        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:top_k]]
