# Design Spec: Action-Oriented Triage Summary (Logic-First)

## Overview

This spec details the implementation of a professional "Triage Summary" for the MTH058 Ops Console. It replaces redundant UI components with a single, clear Markdown summary and functional override controls for GLiNER2 predictions.

## Objectives

- **Visual Hierarchy**: Use simple Markdown with bolding and emojis (🔴, ✅) to display incident status.
- **Manual Intervention**: Allow analysts to override GLiNER2-extracted `Severity`, `Team`, `Impact`, and `Safety Status` directly in the UI.
- **Safety Transparency**: Clearly display "PII SAFETY STATUS" (Safe vs. Unsafe Leak) as a core part of the triage decision.
- **Clutter Reduction**: Move raw analytical data into a collapsible "Developer View" to reduce cognitive load.

## Component Design

### 1. Unified Triage Summary (Markdown)

A single `gr.Markdown` component that dynamically renders the incident's state using simple text.

- **Content**:
  - `### INCIDENT SEVERITY: **{severity}** {severity_emoji}`
  - `### ASSIGNED TEAM: **{team}**`
  - `**Impact Summary:** {impact}`
  - `**PII SAFETY STATUS:** {safety_status_emoji} **{safety_label}**`
- **Initial State**: `### Awaiting analysis...`

### 2. Manual Override & Controls

A set of controls hidden by default to maintain a clean UI.

- **Edit Toggle**: A `gr.Button` ("Edit Predictions") that toggles the visibility of the `gr.Group` below.
- **Override Group**: A `gr.Group` containing:
  - **Severity Dropdown**: `gr.Dropdown` for manual severity correction.
  - **Team Dropdown**: `gr.Dropdown` for manual team assignment correction.
  - **Impact Textbox**: `gr.Textbox` for manual impact summary correction.
  - **Safety Status Checkbox**: `gr.Checkbox` for manual safety status override (Safe/Unsafe).
- **Data Flow**: Any change in the dropdowns or controls triggers a `change` event that re-renders the `Triage Summary` Markdown and updates the internal `Incident` state used by the "Redacted Summary" tab. These changes **do not** re-trigger the GLiNER2 analysis pipeline.

### 3. Developer View (Raw JSON)

- The existing `gr.JSON` ("Incident Card") is moved into a `gr.Accordion` labeled "Show Raw Analytical Data" at the bottom of the column.

## Technical Implementation

### File: `src/mth058/ui/interface.py`

- Replace `incident_card`, `severity_indicator`, and `team_indicator` in `create_triage_tab`.
- Implement `format_triage_summary_markdown(severity, team, impact, is_safe, incident_id)` to generate the Markdown string.
- Update `analyze_incident` to return values for the new override controls and the Markdown summary simultaneously.
- Add event listeners for the `Edit` button and all override controls.

## Data Flow & State Management

1. **Initial Analysis**:
   - `analyze_incident` callback computes values using GLiNER2 and generates a persistent `incident_id`.
   - Updates the `Triage Summary` Markdown and sets initial values for the override controls.
2. **Manual Update**:
   - Analyst changes a value in an override control.
   - The control's `change` event triggers an update to the `Triage Summary` Markdown to reflect the manual decision.
3. **Integration**:
   - The "Redacted Summary" tab pulls its values directly from the override controls to ensure the final output reflects any manual corrections.

## Testing Strategy

1. **Visual Verification**: Confirm that the Markdown summary correctly updates its text and emojis based on extraction and overrides.
2. **Interaction Verification**: Confirm that changing the "Severity" dropdown updates the Markdown summary instantly.
3. **End-to-End**: Ensure that a manually overridden severity is correctly reflected in the "Redacted Summary" prompt on the final tab.
