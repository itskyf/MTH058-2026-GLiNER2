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


@dataclass
class TriageUI:
    """Container for Triage tab components."""

    case_selector: gr.Dropdown
    run_btn: gr.Button
    raw_input: gr.Textbox
    evidence_timeline: gr.Markdown
    entity_display: gr.HighlightedText
    incident_card: gr.JSON
    incident_id_state: gr.State
    triage_card_html: gr.HTML
    edit_btn: gr.Button
    override_group: gr.Group
    override_severity: gr.Dropdown
    override_team: gr.Dropdown
    override_impact: gr.Textbox
    override_safety: gr.Checkbox
    manual_edit_toggle: gr.Checkbox
    redacted_text: gr.Textbox
    routing_logic: gr.Markdown
    similar_cases: gr.DataFrame
    gliner_comparison: gr.HighlightedText
    trad_comparison: gr.HighlightedText


@dataclass
class SchemaUI:
    """Container for Schema tab components."""

    table: gr.DataFrame
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


def analyze_incident(
    text: str,
    schema_df: pl.DataFrame,
    orchestrator: Orchestrator,
    ui: TriageUI,
    redacted_ui: RedactedUI,
) -> dict[
    gr.components.Component,
    str | dict[str, str | int | float | bool] | list[list[str | float]],
]:
    """Analyze the incident text using the provided orchestrator and schema.

    Returns a dictionary mapping components to their new values.
    """
    if not text:
        gr.Info("Please enter incident text before running analysis.")
        return {
            ui.entity_display: gr.update(),
            ui.incident_card: gr.update(),
            ui.incident_id_state: gr.update(),
            ui.triage_card_html: format_triage_card_html(
                "Unknown",
                "None",
                "Please enter incident text above.",
                is_safe=True,
                incident_id="INC-PENDING",
            ),
            ui.override_severity: gr.update(),
            ui.override_team: gr.update(),
            ui.override_impact: gr.update(),
            ui.override_safety: gr.update(),
            ui.redacted_text: gr.update(),
            ui.similar_cases: gr.update(),
            ui.evidence_timeline: gr.update(),
            ui.routing_logic: gr.update(),
            redacted_ui.final_prompt: gr.update(),
            redacted_ui.validation_status: gr.update(),
            ui.gliner_comparison: gr.update(),
            ui.trad_comparison: gr.update(),
        }

    try:
        # Prepare configuration from Polars DataFrame
        active_labels = (
            schema_df.filter(pl.col("Active")).get_column("Label Name").to_list()
        )

        # For simplicity, we'll use these as PII labels if they match common PII types
        pii_candidates = [
            "Person",
            "Email",
            "Phone",
            "IP Address",
            "Account Id",
            "Customer Info",
        ]
        pii_labels = [label for label in active_labels if label in pii_candidates]

        config = {
            "extraction_labels": active_labels,
            "pii_labels": pii_labels,
            "severity_labels": SEVERITY_LABELS,
            "team_labels": TEAM_LABELS,
        }

        # Run analysis
        incident, similar_incidents = orchestrator.run_analysis(text, config)

        # 1. Entity Display
        entities = [
            {"entity": e.label, "start": e.start, "end": e.end}
            for e in incident.entities
        ]

        # 2. Incident Card
        incident_card_data: dict[str, str | int | float | bool] = {
            "severity": incident.severity,
            "team": incident.team,
            "impact": incident.impact,
            "is_safe": incident.is_safe,
            "entity_count": len(incident.entities),
        }

        # 3. Similar Cases
        similar_df: list[list[str | float]] = [
            [f"INC-{i}", 0.85, "Resolved"]  # Mocking some values for display
            for i, _ in enumerate(similar_incidents)
        ]

        # 4. Evidence Timeline (Mocked for now)
        timeline = "### Evidence Timeline\n"
        for e in incident.entities:
            if e.label in ["Date", "Time"]:
                timeline += f"* **{e.text}**: {e.label} detected.\n"
        if timeline == "### Evidence Timeline\n":
            timeline += "*No timeline events detected.*"

        # 5. Routing Logic
        routing = (
            "### Routing Logic\n"
            f"* Severity: **{incident.severity}**\n"
            f"* Assigned Team: **{incident.team}**"
        )

        # 6. Final Prompt Output
        final_prompt_val = {
            "role": "system",
            "content": (
                f"Analyze the following redacted incident:\n\n{incident.redacted_text}"
            ),
            "metadata": incident_card_data,
        }

        # 7. Validation Status
        validation = "SAFE" if incident.is_safe else "UNSAFE - PII LEAK"

        # 8. Baseline Comparison (GLiNER2 vs Traditional NER)
        # Mocking traditional NER (e.g., only Person and Email)
        trad_entities = [
            {"entity": e.label, "start": e.start, "end": e.end}
            for e in incident.entities
            if e.label in ["Person", "Email"]
        ]

        incident_id = f"INC-2026-{uuid.uuid4().hex[:4].upper()}"

        return {
            ui.entity_display: {"text": text, "entities": entities},
            ui.incident_card: incident_card_data,
            ui.incident_id_state: incident_id,
            ui.triage_card_html: format_triage_card_html(
                incident.severity,
                incident.team,
                incident.impact,
                is_safe=incident.is_safe,
                incident_id=incident_id,
            ),
            ui.override_severity: incident.severity,
            ui.override_team: incident.team,
            ui.override_impact: incident.impact,
            ui.override_safety: incident.is_safe,
            ui.redacted_text: incident.redacted_text,
            ui.similar_cases: similar_df,
            ui.evidence_timeline: timeline,
            ui.routing_logic: routing,
            redacted_ui.final_prompt: json.dumps(final_prompt_val, indent=2),
            redacted_ui.validation_status: validation,
            ui.gliner_comparison: {"text": text, "entities": entities},
            ui.trad_comparison: {"text": text, "entities": trad_entities},
        }

    except (ValueError, KeyError, TypeError) as e:
        logger.exception("Analysis failed due to data/configuration error")
        gr.Error(f"Analysis failed: {e!s}")
        # Empty updates for all components to satisfy Gradio's expected output count
        return {
            ui.entity_display: gr.update(),
            ui.incident_card: gr.update(),
            ui.incident_id_state: gr.update(),
            ui.triage_card_html: gr.update(),
            ui.override_severity: gr.update(),
            ui.override_team: gr.update(),
            ui.override_impact: gr.update(),
            ui.override_safety: gr.update(),
            ui.redacted_text: gr.update(),
            ui.similar_cases: gr.update(),
            ui.evidence_timeline: gr.update(),
            ui.routing_logic: gr.update(),
            redacted_ui.final_prompt: gr.update(),
            redacted_ui.validation_status: gr.update(),
            ui.gliner_comparison: gr.update(),
            ui.trad_comparison: gr.update(),
        }
    except RuntimeError as e:
        logger.exception("Model execution failed during analysis")
        gr.Error(f"Model error: {e!s}")
        return {
            ui.entity_display: gr.update(),
            ui.incident_card: gr.update(),
            ui.incident_id_state: gr.update(),
            ui.triage_card_html: gr.update(),
            ui.override_severity: gr.update(),
            ui.override_team: gr.update(),
            ui.override_impact: gr.update(),
            ui.override_safety: gr.update(),
            ui.redacted_text: gr.update(),
            ui.similar_cases: gr.update(),
            ui.evidence_timeline: gr.update(),
            ui.routing_logic: gr.update(),
            redacted_ui.final_prompt: gr.update(),
            redacted_ui.validation_status: gr.update(),
            ui.gliner_comparison: gr.update(),
            ui.trad_comparison: gr.update(),
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
            # Left Column: Input
            with gr.Column(scale=1):
                gr.Markdown("### 1. Input")
                raw_input = gr.Textbox(
                    label="Raw Text (Logs / Chat / Email)",
                    placeholder="Paste incident raw text here...",
                    lines=12,
                    elem_id="raw-input-box",
                )

                evidence_timeline = gr.Markdown(
                    "### Evidence Timeline\n*Waiting for analysis...*",
                    label="Evidence Timeline",
                )

            # Center Column: Triage Decision
            with gr.Column(scale=1):
                incident_id_state = gr.State(value="INC-PENDING")
                gr.Markdown("### 2. Intelligence & Triage")

                entity_display = gr.HighlightedText(
                    label="GLiNER2 Extracted Intelligence",
                    color_map={
                        "Person": "red",
                        "Email": "blue",
                        "IP Address": "green",
                        "Account Id": "red",
                        "Customer Info": "magenta",
                        "Tenant Id": "purple",
                        "Service Name": "cyan",
                        "Release Version": "blue",
                        "Feature Flag": "green",
                        "Exception Type": "orange",
                    },
                    combine_adjacent=True,
                    show_legend=True,
                )

                triage_card_html = gr.HTML(
                    value=format_triage_card_html(
                        "Unknown",
                        "None",
                        "Awaiting analysis...",
                        is_safe=True,
                        incident_id="INC-PENDING",
                    ),
                    label="Triage Card",
                )

                edit_btn = gr.Button("Edit Predictions", size="sm")

                with gr.Group(visible=False) as override_group:
                    override_severity = gr.Dropdown(
                        choices=SEVERITY_LABELS,
                        label="Manual Severity",
                    )
                    override_team = gr.Dropdown(
                        choices=TEAM_LABELS,
                        label="Manual Team",
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

            # Right Column: Triage/Output
            with gr.Column(scale=1):
                gr.Markdown("### 3. Triage & Redaction")
                with gr.Row():
                    manual_edit_toggle = gr.Checkbox(
                        label="Manual Redaction Edit",
                        value=False,
                    )

                redacted_text = gr.Textbox(
                    label="Redacted Text",
                    lines=10,
                    interactive=False,
                    buttons=["copy"],
                )

                routing_logic = gr.Markdown(
                    "### Routing Logic\n*Analysis not yet performed.*",
                    label="Routing Logic",
                )

                similar_cases = gr.DataFrame(
                    headers=["Case ID", "Similarity", "Outcome"],
                    datatype=["str", "number", "str"],
                    label="Similar Cases",
                    interactive=False,
                    type="polars",
                )

        with gr.Accordion("Baseline Comparison", open=False), gr.Row():
            with gr.Column():
                gr.Markdown("#### GLiNER2 (Zero-shot)")
                gliner_comparison = gr.HighlightedText(
                    label="GLiNER2 Output",
                    show_legend=True,
                )
            with gr.Column():
                gr.Markdown("#### Traditional NER (Static)")
                trad_comparison = gr.HighlightedText(
                    label="spaCy / Static Output",
                    show_legend=True,
                )

    return TriageUI(
        case_selector=case_selector,
        run_btn=run_btn,
        raw_input=raw_input,
        evidence_timeline=evidence_timeline,
        entity_display=entity_display,
        incident_card=incident_card,
        incident_id_state=incident_id_state,
        triage_card_html=triage_card_html,
        edit_btn=edit_btn,
        override_group=override_group,
        override_severity=override_severity,
        override_team=override_team,
        override_impact=override_impact,
        override_safety=override_safety,
        manual_edit_toggle=manual_edit_toggle,
        redacted_text=redacted_text,
        routing_logic=routing_logic,
        similar_cases=similar_cases,
        gliner_comparison=gliner_comparison,
        trad_comparison=trad_comparison,
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
                        {"Label Name": label, "Description": "", "Active": True}
                        for label in DEFAULT_ENTITY_LABELS
                    ],
                ),
                label="Entity Labels",
                interactive=True,
                wrap=True,
                type="polars",
            )

        with gr.Row():
            save_btn = gr.Button("Save Configuration", variant="primary")
            reset_btn = gr.Button("Reset to Defaults")

    return SchemaUI(table=schema_table, save_btn=save_btn, reset_btn=reset_btn)


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
            triage_ui.incident_id_state,
        ]

        for inp in override_inputs[:-1]:  # exclude incident_id_state from triggers
            inp.change(
                fn=lambda sev, team, imp, safe, inc_id: format_triage_card_html(
                    sev,
                    team,
                    imp,
                    is_safe=safe,
                    incident_id=inc_id,
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
                triage_ui.incident_card,
                triage_ui.incident_id_state,
                triage_ui.triage_card_html,
                triage_ui.override_severity,
                triage_ui.override_team,
                triage_ui.override_impact,
                triage_ui.override_safety,
                triage_ui.redacted_text,
                triage_ui.similar_cases,
                triage_ui.evidence_timeline,
                triage_ui.routing_logic,
                redacted_ui.final_prompt,
                redacted_ui.validation_status,
                triage_ui.gliner_comparison,
                triage_ui.trad_comparison,
            ],
        )

        schema_ui.save_btn.click(
            fn=lambda: gr.Info("Configuration saved!"),
        )

        schema_ui.reset_btn.click(
            fn=lambda: pl.DataFrame(
                [
                    {"Label Name": label, "Description": "", "Active": True}
                    for label in DEFAULT_ENTITY_LABELS
                ],
            ),
            outputs=[schema_ui.table],
        )

        triage_ui.manual_edit_toggle.change(
            fn=lambda x: gr.update(interactive=x),
            inputs=[triage_ui.manual_edit_toggle],
            outputs=[triage_ui.redacted_text],
        )

    return demo
