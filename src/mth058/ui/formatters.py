"""Utility for formatting UI components as HTML using minijinja templates."""

from importlib.resources import files

from minijinja import Environment

import mth058.data
from mth058.ui.theme import _format_label


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
) -> str:
    """Render incident triage data as an HTML card.

    Args:
        severity: The incident severity level (e.g., Critical, High).
        team: The assigned response team.
        impact: A summary of the incident's impact.
        is_safe: Boolean indicating if the redaction is safe (no PII leak).

    Returns:
        str: A string containing the rendered HTML of the triage card.
    """
    severity_class = f"triage-card-{severity.lower()}"

    return _env.render_template(
        "triage_card",
        severity=_format_label(severity),
        severity_class=severity_class,
        team=_format_label(team),
        impact=impact,
        is_safe=is_safe,
    )
