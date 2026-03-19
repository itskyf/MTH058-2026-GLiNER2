"""Utility for formatting UI components as HTML using minijinja templates."""

from importlib.resources import files

from minijinja import Environment

import mth058.data


def _load_triage_template() -> str:
    """Loads the triage card template from package resources."""
    return (files(mth058.data) / "triage_card.html").read_text(encoding="utf-8")


# Initialize minijinja environment with pre-loaded template
_env = Environment(templates={"triage_card": _load_triage_template()})


def format_triage_card_html(
    severity: str,
    team: str,
    impact: str,
    *,
    is_safe: bool,
    incident_id: str,
) -> str:
    """Render incident triage data as an HTML card.

    Args:
        severity: The incident severity level (e.g., Critical, High).
        team: The assigned response team.
        impact: A summary of the incident's impact.
        is_safe: Boolean indicating if the redaction is safe (no PII leak).
        incident_id: The unique identifier for the incident.

    Returns:
        str: A string containing the rendered HTML of the triage card.
    """
    severity_class = f"triage-card-{severity.lower()}"
    safety_label = "PII SAFE" if is_safe else "UNSAFE LEAK"
    safety_badge_class = "badge-safety-safe" if is_safe else "badge-safety-unsafe"

    return _env.render_template(
        "triage_card",
        severity=severity,
        severity_class=severity_class,
        team=team,
        impact=impact,
        is_safe=is_safe,
        safety_label=safety_label,
        safety_badge_class=safety_badge_class,
        incident_id=incident_id,
    )
