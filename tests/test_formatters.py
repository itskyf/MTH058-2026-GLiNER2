"""Tests for UI HTML formatters using minijinja."""

from mth058.ui.formatters import format_triage_card_html


def test_format_triage_card_html_critical() -> None:
    """Test triage card HTML for Critical severity."""
    html = format_triage_card_html(
        "Critical",
        "SRE",
        "Total outage",
        is_safe=True,
        incident_id="INC-001",
    )
    assert "triage-card-critical" in html
    assert "Critical" in html
    assert "SRE" in html
    assert "Total outage" in html
    assert "badge-safety-safe" in html
    assert "INC-001" in html


def test_format_triage_card_html_unsafe() -> None:
    """Test triage card HTML for unsafe safety status."""
    html = format_triage_card_html(
        "Low",
        "Billing",
        "Minor bug",
        is_safe=False,
        incident_id="INC-002",
    )
    assert "badge-safety-unsafe" in html
    assert "UNSAFE LEAK" in html
    assert "triage-card-low" in html
