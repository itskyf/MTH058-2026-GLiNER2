"""Incident fixtures and loading logic.

This module provides helper functions to load sample incident data from
package resources with Pydantic validation.
"""

import json
import logging
from importlib.resources import files
from typing import Any

import mth058.data
from mth058.models import Incident

logger = logging.getLogger(__name__)


def load_sample_incident_raw() -> dict[str, Any]:
    """Loads the sample incident JSON fixture using importlib.resources.

    Returns:
        dict[str, Any]: The loaded incident data as a dictionary.

    Raises:
        FileNotFoundError: If the fixture file is missing.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    fixture_path = files(mth058.data) / "sample_incident.json"
    try:
        with fixture_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.exception("Fixture file not found at %s", fixture_path)
        raise
    except json.JSONDecodeError:
        logger.exception("Invalid JSON in fixture file at %s", fixture_path)
        raise


def load_sample_incident() -> Incident:
    """Loads and validates the sample incident from JSON fixture.

    Returns:
        Incident: The validated incident object.

    Raises:
        ValueError: If data fails validation or loading.
    """
    try:
        data = load_sample_incident_raw()
        return Incident.model_validate(data)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
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
        data = json.loads(json_str)
        return Incident.model_validate(data)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Failed to parse incident from JSON: %s", str(e))
        msg = "Invalid incident data"
        raise ValueError(msg) from e
