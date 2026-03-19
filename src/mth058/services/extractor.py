"""Service for entity extraction using GLiNER2.

This module provides an ExtractorService class that uses the
fastino/gliner2-large-v1 model to perform zero-shot entity extraction on
raw text. It handles text chunking for large inputs to stay within model
limits.
"""

from functools import lru_cache

from gliner2 import GLiNER2

from mth058.models import Entity, GlinerEntityResults


@lru_cache(maxsize=1)
def get_gliner_model() -> GLiNER2:
    """Loads and returns the shared GLiNER model instance.

    Returns:
        GLiNER: The loaded GLiNER model instance.
    """
    return GLiNER2.from_pretrained("fastino/gliner2-large-v1")


class ExtractorService:
    """Service for extracting entities from text using GLiNER2."""

    def __init__(
        self,
        model: GLiNER2 | None = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> None:
        """Initializes the ExtractorService with a shared model.

        Args:
            model (GLiNER): The shared GLiNER model instance.
            chunk_size (int): Max number of characters per chunk for long texts.
            chunk_overlap (int): Number of characters to overlap between chunks.
        """
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _chunk_text(self, text: str) -> list[str]:
        """Splits long text into manageable chunks.

        Args:
            text (str): The input text to be chunked.

        Returns:
            list[str]: A list of text chunks.
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def extract(self, text: str, labels: list[str]) -> list[Entity]:
        """Extracts named entities from the given text using GLiNER2.

        Args:
            text (str): The raw text from which to extract entities.
            labels (list[str]): A list of entity labels to search for.

        Returns:
            list[Entity]: A list of Entity objects representing the extracted entities.
        """
        if not text or not labels:
            return []

        chunks = self._chunk_text(text)
        all_entities = []

        current_offset = 0
        for chunk in chunks:
            # The model returns a dict {'entities': {label: [matches]}}
            # Each match is a dict with 'text', 'start', 'end', 'confidence'
            # because we pass include_confidence=True and include_spans=True
            results_dict = self.model.extract_entities(
                chunk,
                labels,
                threshold=0.5,
                include_confidence=True,
                include_spans=True,
            )

            # Use Pydantic model for static typing instead of raw string keys
            results = GlinerEntityResults.model_validate(results_dict)
            entity_dict = results.entities

            for label, entities in entity_dict.items():
                for pred in entities:
                    # Adjust start/end positions based on current_offset
                    entity = Entity(
                        label=label,
                        text=pred.text,
                        start=pred.start + current_offset,
                        end=pred.end + current_offset,
                        score=pred.confidence,
                    )

                    # Basic deduplication for overlapping chunks
                    if not any(
                        e.text == entity.text and e.start == entity.start
                        for e in all_entities
                    ):
                        all_entities.append(entity)

            current_offset += self.chunk_size - self.chunk_overlap

        return all_entities
