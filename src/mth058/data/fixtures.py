"""Incident fixtures and loading logic.

This module provides helper functions to load sample incident data from
package resources.
"""

import json
from importlib.resources import files
from typing import Any

import mth058.data


def load_sample_incident() -> dict[str, Any]:
    """Loads the sample incident JSON fixture using importlib.resources.

    Returns:
        dict[str, Any]: The loaded incident data as a dictionary.
    """
    # Using 'mth058.data' as the package name
    fixture_path = files(mth058.data) / "sample_incident.json"
    with fixture_path.open("r", encoding="utf-8") as f:
        return json.load(f)
