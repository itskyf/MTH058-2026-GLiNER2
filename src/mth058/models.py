"""Pydantic models for the incident intake and triage copilot.

This module defines the data structures for entities, incidents, and UI-
friendly incident cards.
"""

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Represents a named entity found in the raw text.

    Attributes:
        label (str): The entity label (e.g., PERSON, DATE).
        text (str): The actual text content of the entity.
        start (int): The starting index of the entity in the raw text.
        end (int): The ending index of the entity in the raw text.
        score (float): Confidence score of the extraction.
    """

    label: str
    text: str
    start: int
    end: int
    score: float


class Incident(BaseModel):
    """Model representing an incident reported via the system.

    Attributes:
        raw_text (str): The full raw text of the incident report.
        sections (dict[str, str]): Key-value pairs of extracted sections
            (e.g., summary, impact).
        entities (list[Entity]): A list of extracted named entities.
        severity (str): Assessed severity level (e.g., Low, Medium, High, Critical).
        team (str): The team assigned to handle the incident.
        impact (str): The impact summary.
    """

    raw_text: str
    sections: dict[str, str] = Field(default_factory=dict)
    entities: list[Entity] = Field(default_factory=list)
    severity: str
    team: str
    impact: str


class IncidentCard(BaseModel):
    """Model for a summarized incident card in the UI.

    Attributes:
        title (str): A short, descriptive title for the incident.
        summary (str): A concise summary of the incident.
        key_entities (list[str]): A list of key entities for quick context.
        status (str): Current status of the incident (e.g., New, Triaged, Resolved).
    """

    title: str
    summary: str
    key_entities: list[str] = Field(default_factory=list)
    status: str
