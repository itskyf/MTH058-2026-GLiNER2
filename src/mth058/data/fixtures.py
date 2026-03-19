"""Incident fixtures and loading logic.

This module provides helper functions to load sample incident data from
package resources with Pydantic validation.
"""

import logging
from importlib.resources import files

from pydantic import ValidationError

import mth058.data
from mth058.models import Incident

logger = logging.getLogger(__name__)


def load_sample_incident() -> Incident:
    """Loads and validates the sample incident from JSON fixture.

    Returns:
        Incident: The validated incident object.

    Raises:
        ValueError: If data fails validation or loading.
    """
    fixture_path = files(mth058.data) / "sample_incident.json"
    try:
        # Use model_validate_json for high-performance parsing and validation
        return Incident.model_validate_json(fixture_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValidationError) as e:
        logger.exception("Failed to load and validate sample incident")
        msg = f"Failed to load sample incident: {e}"
        raise ValueError(msg) from e


def load_incident_from_json(json_str: str) -> Incident:
    """Parses and validates an incident from a JSON string.

    Args:
        json_str (str): The JSON string to parse.

    Returns:
        Incident: The validated incident object.

    Raises:
        ValueError: If parsing or validation fails.
    """
    try:
        return Incident.model_validate_json(json_str)
    except ValidationError as e:
        logger.warning("Failed to parse incident from JSON: %s", str(e))
        msg = "Invalid incident data"
        raise ValueError(msg) from e
