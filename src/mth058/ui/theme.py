"""UI theme constants and configuration for the MTH058 Ops Console."""

from enum import StrEnum, auto
from importlib.resources import files

import mth058.data


class EntityLabel(StrEnum):
    """Supported entity labels for extraction."""

    PERSON = auto()
    EMAIL = auto()
    PHONE = auto()
    ORGANIZATION = auto()
    LOCATION = auto()
    IP_ADDRESS = auto()
    DATE = auto()
    SERVICE_NAME = auto()
    ERROR_MESSAGE = auto()
    INCIDENT_ID = auto()


class Severity(StrEnum):
    """Incident severity levels."""

    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    INFORMATIONAL = auto()


class Team(StrEnum):
    """Assigned teams for incidents."""

    DEVOPS = auto()
    SECURITY = auto()
    SRE = auto()
    FRONTEND = auto()
    BACKEND = auto()
    DATA_SCIENCE = auto()
    COMPLIANCE = auto()


def load_custom_css() -> str:
    """Loads the custom CSS from the package resources.

    Returns:
        str: The CSS content.
    """
    css_path = files(mth058.data) / "theme.css"
    return css_path.read_text(encoding="utf-8")


def _format_label(label: str) -> str:
    """Formats an enum-style label into a more readable format for UI/Model.

    Example: "service_name" -> "Service Name"
    """
    return label.replace("_", " ").title()


# Default values as lists for UI components, formatted for GLiNER and UI
DEFAULT_ENTITY_LABELS = [_format_label(label.value) for label in EntityLabel]
SEVERITY_LABELS = [_format_label(s.value) for s in Severity]
TEAM_LABELS = [_format_label(t.value) for t in Team]

# UI Text Constants
APP_TITLE = "MTH058 - Local Incident Intake & PII-Safe Triage Copilot"
TAB_TRIAGE = "Incident Triage"
TAB_SCHEMA = "Schema Configuration"
TAB_REDACTED = "Redacted Summary"
