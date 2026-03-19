"""MTH058 Gradio UI layout using gr.Blocks."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import gradio as gr

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


def on_case_select(choice: str, fixtures: list[Incident]) -> str:
    """Handle case selection from the dropdown."""
    if choice == "[New Incident]":
        return ""
    # Find the matching fixture
    for f in fixtures:
        if choice == f"Sample: {f.raw_text[:30]}...":
            return f.raw_text
    return ""


def run_analysis_ui(
    text: str,
    schema_df: gr.DataFrame,
    orchestrator: Orchestrator,
) -> list[Any] | tuple[Any, ...]:
    """Handle the analysis run event."""
    if not text:
        gr.Warning("Please enter incident text before running analysis.")
        return [None] * 12

    try:
        # Prepare configuration from schema table (list or DataFrame)
        if hasattr(schema_df, "to_dict"):
            active_labels = schema_df[schema_df["Active"]]["Label Name"].tolist()
        else:
            # Assume list of lists: [Label Name, Description, Active]
            active_labels = [row[0] for row in schema_df if row[2]]

        # For simplicity, we'll use these as PII labels if they match common PII types
        pii_candidates = ["Person", "Email", "Phone", "IP Address"]
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
        incident_card_data = {
            "severity": incident.severity,
            "team": incident.team,
            "impact": incident.impact,
            "is_safe": incident.is_safe,
            "entity_count": len(incident.entities),
        }

        # 3. Similar Cases
        similar_df = [
            [f"INC-{i}", 0.85, "Resolved"]  # Mocking some values for display
            for i, _ in enumerate(similar_incidents)
        ]

        # 4. Redacted Text
        redacted = incident.redacted_text

        # 5. Evidence Timeline (Mocked for now)
        timeline = "### Evidence Timeline\n"
        for e in incident.entities:
            if e.label in ["Date", "Time"]:
                timeline += f"* **{e.text}**: {e.label} detected.\n"
        if timeline == "### Evidence Timeline\n":
            timeline += "*No timeline events detected.*"

        # 6. Routing Logic
        routing = (
            "### Routing Logic\n"
            f"* Severity: **{incident.severity}**\n"
            f"* Assigned Team: **{incident.team}**"
        )

        # 7. Final Prompt Output
        final_prompt = {
            "role": "system",
            "content": (
                f"Analyze the following redacted incident:\n\n{incident.redacted_text}"
            ),
            "metadata": incident_card_data,
        }

        # 8. Validation Status
        validation = "SAFE" if incident.is_safe else "UNSAFE - PII LEAK"

        # 9. Baseline Comparison (GLiNER2 vs Traditional NER)
        # Mocking traditional NER (e.g., only Person and Email)
        trad_entities = [
            {"entity": e.label, "start": e.start, "end": e.end}
            for e in incident.entities
            if e.label in ["Person", "Email"]
        ]

        return (
            {"text": text, "entities": entities},  # entity_display
            incident_card_data,  # incident_card
            incident.severity,  # severity_indicator
            incident.team,  # team_indicator
            redacted,  # redacted_text
            similar_df,  # similar_cases
            timeline,  # evidence_timeline
            routing,  # routing_logic
            json.dumps(final_prompt, indent=2),  # final_prompt_output
            validation,  # validation_status
            {"text": text, "entities": entities},  # gliner_comparison
            {"text": text, "entities": trad_entities},  # trad_comparison
        )

    except (ValueError, KeyError, TypeError) as e:
        logger.exception("Analysis failed due to data/configuration error")
        gr.Error(f"Analysis failed: {e!s}")
        return [None] * 12
    except Exception as e:
        logger.exception("An unexpected error occurred during analysis")
        gr.Error(f"An unexpected error occurred: {e!s}")
        return [None] * 12


def create_triage_tab(fixture_names: list[str]) -> tuple[Any, ...]:
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
                    lines=20,
                    elem_id="raw-input-box",
                )
                evidence_timeline = gr.Markdown(
                    "### Evidence Timeline\n*Waiting for analysis...*",
                    label="Evidence Timeline",
                )

            # Center Column: Extraction
            with gr.Column(scale=1):
                gr.Markdown("### 2. Extraction")
                with gr.Group():
                    entity_display = gr.HighlightedText(
                        label="Extracted Entities",
                        color_map={
                            "Person": "red",
                            "Email": "blue",
                            "IP Address": "green",
                        },
                        combine_adjacent=True,
                        show_legend=True,
                    )

                incident_card = gr.JSON(
                    label="Incident Card",
                    value={"status": "Awaiting Analysis"},
                )

                with gr.Row():
                    severity_indicator = gr.Label(label="Severity", value="Unknown")
                    team_indicator = gr.Label(label="Target Team", value="None")

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
                )

        with gr.Accordion("Baseline Comparison", open=False), gr.Row():
            with gr.Column():
                gr.Markdown("#### GLiNER2 (Zero-shot)")
                gliner_comparison = gr.HighlightedText(label="GLiNER2 Output")
            with gr.Column():
                gr.Markdown("#### Traditional NER (Static)")
                trad_comparison = gr.HighlightedText(label="spaCy / Static Output")

    return (
        case_selector,
        run_btn,
        raw_input,
        evidence_timeline,
        entity_display,
        incident_card,
        severity_indicator,
        team_indicator,
        manual_edit_toggle,
        redacted_text,
        routing_logic,
        similar_cases,
        gliner_comparison,
        trad_comparison,
    )


def create_ui(orchestrator: Orchestrator, fixtures: list[Incident]) -> gr.Blocks:
    """Construct the Gradio Blocks UI."""
    fixture_names = ["[New Incident]"] + [
        f"Sample: {f.raw_text[:30]}..." for f in fixtures
    ]

    # Note: css is moved to demo.launch() in Gradio 6.0
    with gr.Blocks() as demo:
        gr.Markdown(f"# {APP_TITLE}")

        with gr.Tabs():
            (
                case_selector,
                run_btn,
                raw_input,
                evidence_timeline,
                entity_display,
                incident_card,
                severity_indicator,
                team_indicator,
                manual_edit_toggle,
                redacted_text,
                routing_logic,
                similar_cases,
                gliner_comparison,
                trad_comparison,
            ) = create_triage_tab(fixture_names)

            # Tab 2: Schema Configuration
            with gr.TabItem(TAB_SCHEMA):
                gr.Markdown("## Dynamic Schema Configuration")
                gr.Markdown("Modify GLiNER2 labels at runtime.")

                with gr.Row():
                    schema_table = gr.DataFrame(
                        headers=["Label Name", "Description", "Active"],
                        datatype=["str", "str", "bool"],
                        value=[[label, "", True] for label in DEFAULT_ENTITY_LABELS],
                        label="Entity Labels",
                        interactive=True,
                        wrap=True,
                    )

                with gr.Row():
                    save_schema_btn = gr.Button("Save Configuration", variant="primary")
                    reset_schema_btn = gr.Button("Reset to Defaults")

            # Tab 3: Redacted Summary
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

        # Event Wiring
        case_selector.change(
            fn=lambda c: on_case_select(c, fixtures),
            inputs=[case_selector],
            outputs=[raw_input],
        )

        run_btn.click(
            fn=lambda t, s: run_analysis_ui(t, s, orchestrator),
            inputs=[raw_input, schema_table],
            outputs=[
                entity_display,
                incident_card,
                severity_indicator,
                team_indicator,
                redacted_text,
                similar_cases,
                evidence_timeline,
                routing_logic,
                final_prompt_output,
                validation_status,
                gliner_comparison,
                trad_comparison,
            ],
        )

        save_schema_btn.click(
            fn=lambda: gr.Info("Configuration saved!"),
            inputs=[],
            outputs=[],
        )

        reset_schema_btn.click(
            fn=lambda: [[label, "", True] for label in DEFAULT_ENTITY_LABELS],
            inputs=[],
            outputs=[schema_table],
        )

        manual_edit_toggle.change(
            fn=lambda x: gr.update(interactive=x),
            inputs=[manual_edit_toggle],
            outputs=[redacted_text],
        )

    return demo
