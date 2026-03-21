"""MTH058 Gradio UI layout using gr.Blocks."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

import gradio as gr
import polars as pl

from mth058.ui.formatters import format_triage_card_html
from mth058.ui.theme import (
    APP_TITLE,
    DEFAULT_ENTITY_LABELS,
    SEVERITY_LABELS,
    TAB_REDACTED,
    TAB_SCHEMA,
    TAB_TRIAGE,
    TEAM_LABELS,
)

if TYPE_CHECKING:
    from mth058.models import Incident
    from mth058.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


SCHEMA_DESCRIPTIONS = {
    "Person": "Full name or alias of an individual.",
    "Email": "Email address of a user or service.",
    "Phone": "Phone number or contact number.",
    "Organization": "Company, team, or group name.",
    "Location": "Geographic location or office address.",
    "IP Address": "IP address or network identifier.",
    "Date": "Date or time period.",
    "Service Name": "Name of the software service or microservice.",
    "Release Version": "Software version or build number (e.g., v1.2.3).",
    "Feature Flag": "Toggle or feature flag name.",
    "Tenant Id": "Unique identifier for a customer tenant.",
    "Exception Type": "Error name or stack trace exception.",
    "Account Id": "Internal account or user ID.",
    "Customer Info": "Sensitive customer-specific information.",
    "Severity Indicator": (
        "A key phrase indicating the urgency or scale "
        "(e.g., 'multiple alerts', 'critical outage')."
    ),
    "Assignment Reason": (
        "Contextual reason for team routing (e.g., 'billing-db', 'iOS users')."
    ),
}

BASE_COLOR_MAP = {
    "Person": "red",
    "Email": "blue",
    "Phone": "green",
    "Organization": "yellow",
    "Location": "cyan",
    "IP Address": "green",
    "Date": "purple",
    "Service Name": "cyan",
    "Release Version": "blue",
    "Feature Flag": "green",
    "Tenant Id": "purple",
    "Exception Type": "orange",
    "Account Id": "red",
    "Customer Info": "magenta",
    "Severity Indicator": "red",
    "Assignment Reason": "blue",
}


def add_schema_row(df: pl.DataFrame) -> pl.DataFrame:
    """Add an empty row to the schema Polars DataFrame."""
    new_row = pl.DataFrame(
        {
            "Label Name": ["New Label"],
            "Description": ["Extract this info..."],
            "Active": [True],
        },
    )
    return pl.concat([df, new_row])


@dataclass
class TriageUI:
    """Container for Triage tab components."""

    case_selector: gr.Dropdown
    run_btn: gr.Button
    raw_input: gr.Textbox
    evidence_timeline: gr.Markdown
    entity_display: gr.HighlightedText
    severity_distribution: gr.Label
    team_distribution: gr.Label
    incident_card: gr.JSON
    incident_id_state: gr.State
    triage_card_html: gr.HTML
    edit_btn: gr.Button
    override_group: gr.Group
    override_severity: gr.Dropdown
    override_team: gr.Dropdown
    override_impact: gr.Textbox
    override_safety: gr.Checkbox
    redacted_text: gr.Markdown
    routing_logic: gr.Markdown
    active_schema_display: gr.JSON


@dataclass
class SchemaUI:
    """Container for Schema tab components."""

    table: gr.DataFrame
    add_btn: gr.Button
    save_btn: gr.Button
    reset_btn: gr.Button


@dataclass
class RedactedUI:
    """Container for Redacted Summary tab components."""

    final_prompt: gr.Code
    validation_status: gr.Label


def on_case_select(choice: str, fixtures: list[Incident]) -> str:
    """Handle case selection from the dropdown."""
    if choice == "[New Incident]":
        return ""
    # Find the matching fixture
    for f in fixtures:
        if choice == f"Sample: {f.raw_text[:30]}...":
            return f.raw_text
    return ""


def sync_redacted_prompt(
    severity: str,
    team: str,
    impact: str,
    *,
    is_safe: bool,
    redacted_text: str,
) -> str:
    """Synchronize the final redacted prompt with manual override values."""
    metadata = {
        "severity": severity,
        "team": team,
        "impact": impact,
        "is_safe": is_safe,
    }
    final_prompt_val = {
        "role": "system",
        "content": f"Analyze the following redacted incident:\n\n{redacted_text}",
        "metadata": metadata,
    }
    return json.dumps(final_prompt_val, indent=2)


def _prepare_analysis_config(schema_df: pl.DataFrame) -> dict:
    """Prepare the configuration dictionary from the schema DataFrame."""
    active_rows = schema_df.filter(pl.col("Active"))
    active_labels = active_rows.get_column("Label Name").to_list()

    schema_with_desc = {}
    for row in active_rows.to_dicts():
        name = row["Label Name"]
        desc = row["Description"].strip()
        if not desc or desc == "Custom label added by user.":
            desc = f"Extract {name} from the incident report."
        schema_with_desc[name] = desc

    pii_candidates = [
        "Person",
        "Email",
        "Phone",
        "IP Address",
        "Account Id",
        "Customer Info",
    ]
    pii_labels = [label for label in active_labels if label in pii_candidates]

    return {
        "extraction_labels": schema_with_desc,
        "pii_labels": pii_labels,
        "severity_labels": SEVERITY_LABELS,
        "team_labels": TEAM_LABELS,
    }


def _format_ui_results(
    incident: Incident,
) -> dict:
    """Format the raw analysis results for UI components."""
    entities = [
        {"entity": e.label, "start": e.start, "end": e.end} for e in incident.entities
    ]

    found_labels = {e["entity"] for e in entities}
    filtered_color_map = {
        label: BASE_COLOR_MAP.get(label, "gray") for label in found_labels
    }

    incident_card_data = {
        "severity": incident.severity,
        "team": incident.team,
        "impact": incident.impact,
        "is_safe": incident.is_safe,
        "entity_count": len(incident.entities),
    }

    final_prompt_val = {
        "role": "system",
        "content": (
            f"Analyze the following redacted incident:\n\n{incident.redacted_text}"
        ),
        "metadata": incident_card_data,
    }

    return {
        "entities": entities,
        "color_map": filtered_color_map,
        "card_data": incident_card_data,
        "final_prompt": json.dumps(final_prompt_val, indent=2),
        "validation": "SAFE" if incident.is_safe else "UNSAFE - PII LEAK",
    }


def analyze_incident(
    text: str,
    schema_df: pl.DataFrame,
    orchestrator: Orchestrator,
    ui: TriageUI,
    redacted_ui: RedactedUI,
) -> dict:
    """Analyze the incident text using the provided orchestrator and schema."""
    if not text:
        gr.Info("Please enter incident text before running analysis.")
        return {
            ui.triage_card_html: format_triage_card_html(
                "Unknown",
                "None",
                "Please enter incident text above.",
                is_safe=True,
            ),
            ui.entity_display: gr.update(),
            ui.severity_distribution: gr.update(),
            ui.team_distribution: gr.update(),
            ui.incident_card: gr.update(),
            ui.incident_id_state: gr.update(),
            ui.override_severity: gr.update(),
            ui.override_team: gr.update(),
            ui.override_impact: gr.update(),
            ui.override_safety: gr.update(),
            ui.redacted_text: gr.update(),
            ui.evidence_timeline: gr.update(),
            ui.routing_logic: gr.update(),
            redacted_ui.final_prompt: gr.update(),
            redacted_ui.validation_status: gr.update(),
            ui.active_schema_display: gr.update(),
        }

    try:
        config = _prepare_analysis_config(schema_df)
        incident, _ = orchestrator.run_analysis(text, config)

        # Evidence Timeline
        timeline = "### Evidence Timeline\n"
        for e in incident.entities:
            if e.label in ["Date", "Time"]:
                timeline += f"* **{e.text}**: {e.label} detected.\n"
        if timeline == "### Evidence Timeline\n":
            timeline += "*No timeline events detected.*"

        # Routing Logic
        routing = (
            f"### Routing Logic\n* Severity: **{incident.severity}**\n"
            f"* Assigned Team: **{incident.team}**"
        )
        indicators = [
            e.text for e in incident.entities if e.label == "Severity Indicator"
        ]
        reasons = [e.text for e in incident.entities if e.label == "Assignment Reason"]
        if indicators:
            routing += f"\n\n**Severity Evidence**: _{', '.join(indicators[:2])}_"
        if reasons:
            routing += f"\n\n**Routing Evidence**: _{', '.join(reasons[:2])}_"

        res = _format_ui_results(incident)
        incident_id = f"INC-2026-{uuid.uuid4().hex[:4].upper()}"

        return {
            ui.entity_display: gr.update(
                value={"text": text, "entities": res["entities"]},
                label=f"GLiNER2 Intelligence ({len(res['entities'])} entities)",
                color_map=res["color_map"],
            ),
            ui.severity_distribution: incident.severity_distribution,
            ui.team_distribution: incident.team_distribution,
            ui.incident_card: res["card_data"],
            ui.incident_id_state: incident_id,
            ui.triage_card_html: format_triage_card_html(
                incident.severity,
                incident.team,
                incident.impact,
                is_safe=incident.is_safe,
            ),
            ui.override_severity: incident.severity,
            ui.override_team: incident.team,
            ui.override_impact: incident.impact,
            ui.override_safety: incident.is_safe,
            ui.redacted_text: incident.redacted_text,
            ui.evidence_timeline: timeline,
            ui.routing_logic: routing,
            redacted_ui.final_prompt: res["final_prompt"],
            redacted_ui.validation_status: res["validation"],
            ui.active_schema_display: config["extraction_labels"],
        }
    except Exception as e:
        logger.exception("Analysis failed")
        gr.Error(f"Analysis failed: {e!s}")
        return {
            ui.entity_display: gr.update(),
            ui.severity_distribution: gr.update(),
            ui.team_distribution: gr.update(),
            ui.incident_card: gr.update(),
            ui.incident_id_state: gr.update(),
            ui.triage_card_html: gr.update(),
            ui.override_severity: gr.update(),
            ui.override_team: gr.update(),
            ui.override_impact: gr.update(),
            ui.override_safety: gr.update(),
            ui.redacted_text: gr.update(),
            ui.evidence_timeline: gr.update(),
            ui.routing_logic: gr.update(),
            redacted_ui.final_prompt: gr.update(),
            redacted_ui.validation_status: gr.update(),
            ui.active_schema_display: gr.update(),
        }


def create_triage_tab(fixture_names: list[str]) -> TriageUI:
    """Create the Triage tab content."""
    with gr.TabItem(TAB_TRIAGE):
        with gr.Row(elem_classes="header-row"):
            with gr.Column(scale=4):
                case_selector = gr.Dropdown(
                    choices=fixture_names,
                    value="[New Incident]",
                    label="Case Selector",
                    info="Select a pre-loaded incident.",
                )
            with gr.Column(scale=1):
                run_btn = gr.Button("Run Analysis", variant="primary")

        with gr.Row():
            # Left Column: Input & Redaction
            with gr.Column(scale=1):
                gr.Markdown("### 1. Input")
                raw_input = gr.Textbox(
                    label="Raw Text (Logs / Chat / Email)",
                    placeholder="Paste incident raw text here...",
                    lines=8,
                    elem_id="raw-input-box",
                )

                evidence_timeline = gr.Markdown(
                    "### Evidence Timeline\n*Waiting for analysis...*",
                    label="Evidence Timeline",
                )

                gr.Markdown("### Redaction")

                redacted_text = gr.Markdown(
                    "*Waiting for analysis...*",
                    label="Redacted Text",
                )

            # Center Column: Intelligence
            with gr.Column(scale=1):
                incident_id_state = gr.State(value="INC-PENDING")
                gr.Markdown("### 2. Intelligence & Triage")

                entity_display = gr.HighlightedText(
                    label="GLiNER2 Extracted Intelligence",
                    color_map=BASE_COLOR_MAP,
                    combine_adjacent=True,
                    show_legend=True,
                )

                triage_card_html = gr.HTML(
                    value=format_triage_card_html(
                        "Unknown",
                        "None",
                        "Awaiting analysis...",
                        is_safe=True,
                    ),
                    label="Triage Card",
                )

                edit_btn = gr.Button("Edit Predictions", size="sm")

                with gr.Group(visible=False) as override_group:
                    override_severity = gr.Dropdown(
                        choices=SEVERITY_LABELS,
                        label="Manual Severity",
                        allow_custom_value=True,
                    )
                    override_team = gr.Dropdown(
                        choices=TEAM_LABELS,
                        label="Manual Team",
                        allow_custom_value=True,
                    )
                    override_impact = gr.Textbox(label="Manual Impact Summary", lines=2)
                    override_safety = gr.Checkbox(
                        label="PII Safety Status (Checked = Safe)",
                        value=True,
                    )

                with gr.Accordion("Show Raw Analytical Data", open=False):
                    incident_card = gr.JSON(
                        label="Incident Card",
                        value={"status": "Awaiting Analysis"},
                    )

            # Right Column: Analysis Results
            with gr.Column(scale=1):
                routing_logic = gr.Markdown(
                    "### Routing Logic\n*Analysis not yet performed.*",
                    label="Routing Logic",
                )

                with gr.Column():
                    gr.Markdown("#### Confidence Distribution")
                    severity_distribution = gr.Label(
                        label="Severity Confidence",
                        num_top_classes=4,
                    )
                    team_distribution = gr.Label(
                        label="Team Routing Confidence",
                        num_top_classes=5,
                    )

        with gr.Accordion("Schema Information", open=False), gr.Row(), gr.Column():
            gr.Markdown("#### Active Model Schema & Configuration")
            active_schema_display = gr.JSON(
                label="Input Labels (Schema with Descriptions)",
                value={},
            )

    return TriageUI(
        case_selector=case_selector,
        run_btn=run_btn,
        raw_input=raw_input,
        evidence_timeline=evidence_timeline,
        entity_display=entity_display,
        severity_distribution=severity_distribution,
        team_distribution=team_distribution,
        incident_card=incident_card,
        incident_id_state=incident_id_state,
        triage_card_html=triage_card_html,
        edit_btn=edit_btn,
        override_group=override_group,
        override_severity=override_severity,
        override_team=override_team,
        override_impact=override_impact,
        override_safety=override_safety,
        redacted_text=redacted_text,
        routing_logic=routing_logic,
        active_schema_display=active_schema_display,
    )


def create_schema_tab() -> SchemaUI:
    """Create the Schema Configuration tab."""
    with gr.TabItem(TAB_SCHEMA):
        gr.Markdown("## Dynamic Schema Configuration")
        gr.Markdown("Modify GLiNER2 labels at runtime.")

        with gr.Row():
            schema_table = gr.DataFrame(
                headers=["Label Name", "Description", "Active"],
                datatype=["str", "str", "bool"],
                value=pl.DataFrame(
                    [
                        {
                            "Label Name": label,
                            "Description": SCHEMA_DESCRIPTIONS.get(label, ""),
                            "Active": True,
                        }
                        for label in DEFAULT_ENTITY_LABELS
                    ],
                ),
                label="Entity Labels",
                interactive=True,
                wrap=True,
                type="polars",
                column_count=(3, "fixed"),
                row_count=(1, "dynamic"),
            )

        with gr.Row():
            add_btn = gr.Button("Add New Label", variant="secondary")
            save_btn = gr.Button("Save Configuration", variant="primary")
            reset_btn = gr.Button("Reset to Defaults")

    return SchemaUI(
        table=schema_table,
        add_btn=add_btn,
        save_btn=save_btn,
        reset_btn=reset_btn,
    )


def create_redacted_tab() -> RedactedUI:
    """Create the Redacted Summary tab."""
    with gr.TabItem(TAB_REDACTED):
        gr.Markdown("## Redacted Summary for LLM Interaction")

        with gr.Row():
            final_prompt_output = gr.Code(
                label="Final Redacted Prompt",
                language="json",
                lines=25,
            )

        with gr.Row():
            validation_status = gr.Label(label="PII Leak Check")

    return RedactedUI(
        final_prompt=final_prompt_output,
        validation_status=validation_status,
    )


def create_ui(orchestrator: Orchestrator, fixtures: list[Incident]) -> gr.Blocks:
    """Construct the Gradio Blocks UI."""
    fixture_names = ["[New Incident]"] + [
        f"Sample: {f.raw_text[:30]}..." for f in fixtures
    ]

    with gr.Blocks(analytics_enabled=False) as demo:
        gr.Markdown(f"# {APP_TITLE}")

        with gr.Tabs():
            triage_ui = create_triage_tab(fixture_names)
            schema_ui = create_schema_tab()
            redacted_ui = create_redacted_tab()

        # Event Wiring
        triage_ui.case_selector.change(
            fn=lambda c: on_case_select(c, fixtures),
            inputs=[triage_ui.case_selector],
            outputs=[triage_ui.raw_input],
        )

        # Toggle Manual Override Group
        triage_ui.edit_btn.click(
            fn=lambda visible: gr.update(visible=not visible),
            inputs=[triage_ui.override_group],
            outputs=[triage_ui.override_group],
        )

        # Live Update Triage Summary on Manual Override
        override_inputs = [
            triage_ui.override_severity,
            triage_ui.override_team,
            triage_ui.override_impact,
            triage_ui.override_safety,
        ]

        for inp in override_inputs:
            inp.change(
                fn=lambda sev, team, imp, safe: format_triage_card_html(
                    sev,
                    team,
                    imp,
                    is_safe=safe,
                ),
                inputs=override_inputs,
                outputs=[triage_ui.triage_card_html],
            )
            # Update Redacted Tab Prompt on any override change
            inp.change(
                fn=lambda sev, team, imp, safe, text: sync_redacted_prompt(
                    sev,
                    team,
                    imp,
                    is_safe=safe,
                    redacted_text=text,
                ),
                inputs=[
                    triage_ui.override_severity,
                    triage_ui.override_team,
                    triage_ui.override_impact,
                    triage_ui.override_safety,
                    triage_ui.redacted_text,
                ],
                outputs=[redacted_ui.final_prompt],
            )

        triage_ui.run_btn.click(
            fn=lambda t, s: analyze_incident(
                t,
                s,
                orchestrator,
                triage_ui,
                redacted_ui,
            ),
            inputs=[triage_ui.raw_input, schema_ui.table],
            outputs=[
                triage_ui.entity_display,
                triage_ui.severity_distribution,
                triage_ui.team_distribution,
                triage_ui.incident_card,
                triage_ui.incident_id_state,
                triage_ui.triage_card_html,
                triage_ui.override_severity,
                triage_ui.override_team,
                triage_ui.override_impact,
                triage_ui.override_safety,
                triage_ui.redacted_text,
                triage_ui.evidence_timeline,
                triage_ui.routing_logic,
                redacted_ui.final_prompt,
                redacted_ui.validation_status,
                triage_ui.active_schema_display,
            ],
        )

        schema_ui.save_btn.click(
            fn=lambda: gr.Info("Configuration saved!"),
        )

        schema_ui.reset_btn.click(
            fn=lambda: pl.DataFrame(
                [
                    {
                        "Label Name": label,
                        "Description": SCHEMA_DESCRIPTIONS.get(label, ""),
                        "Active": True,
                    }
                    for label in DEFAULT_ENTITY_LABELS
                ],
            ),
            outputs=[schema_ui.table],
        )

        schema_ui.add_btn.click(
            fn=add_schema_row,
            inputs=[schema_ui.table],
            outputs=[schema_ui.table],
        )

    return demo
