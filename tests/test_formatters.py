"""Tests for UI HTML formatters using minijinja."""

from mth058.ui.formatters import format_triage_card_html


def test_format_triage_card_html_critical() -> None:
    """Test triage card HTML for Critical severity."""
    html = format_triage_card_html(
        "Critical",
        "SRE",
        "Total outage",
        is_safe=True,
    )
    assert "triage-card-critical" in html
    assert "Critical" in html
    assert "Sre" in html
    assert "Total outage" in html
    assert "badge-safety-safe" in html


def test_format_triage_card_html_unsafe() -> None:
    """Test triage card HTML for unsafe safety status."""
    html = format_triage_card_html(
        "Low",
        "Billing",
        "Minor bug",
        is_safe=False,
    )
    assert "badge-safety-unsafe" in html
    assert "PII LEAK" in html
    assert "triage-card-low" in html
