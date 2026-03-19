# Design Spec: Action-Oriented Triage Card (Interactive)

## Overview

Improve the incident triage UI in the MTH058 Ops Console by replacing redundant, overlapping components (JSON card, separate labels) with a single, professional "Triage Card" that supports manual overrides.

## Objectives

- Remove redundant information display in the "Extraction" column.
- Improve visual hierarchy and aesthetics using styled badges and color-coded borders.
- Allow analysts to manually override GLiNER2 predictions (Severity, Team) directly in the UI.

## Component Changes

### 1. Unified Triage Card

- **Implementation**: Use a combination of `gr.HTML` for the card display and `gr.Group` for structural containment.
- **Visuals**:
  - `border-left`: 10px wide, color-coded by severity (Critical: Red, High: Orange, Medium: Yellow, Low: Blue).
  - **Header**: "INCIDENT SEVERITY" badge (large) + Auto-generated incident ID.
  - **Body**: "ASSIGNED TEAM" badge + "EXTRACTED IMPACT" text area.
  - **Footer**: "PII SAFETY STATUS" badge (Green for Safe, Red for Unsafe Leak).
- **Interactivity**: Include "Edit" links/icons that toggle the visibility of manual override dropdowns.

### 2. Manual Override Controls

- **Severity Dropdown**: A `gr.Dropdown` initially hidden or placed below the card to manually correct severity.
- **Team Dropdown**: A `gr.Dropdown` initially hidden or placed below the card to manually correct team assignments.
- **Data Flow**: Any selection in these dropdowns will trigger a `change` event to update the `Triage Card` HTML preview and the internal `Incident` state.

### 3. Developer/Raw View

- Move the current `gr.JSON` (Incident Card) into a `gr.Accordion` labeled "Show Raw Analytical Data" at the bottom of the column to reduce cognitive load.

## Data Flow & State Management

1. **Analysis Run**:
   - `analyze_incident` callback computes severity/team using GLiNER2.
   - It updates the `Triage Card` HTML and the `Severity/Team` dropdown values.
2. **Manual Override**:
   - Analyst clicks "Edit" on the card.
   - The corresponding dropdown is revealed.
   - Any change to the dropdown triggers an update to the `Triage Card` HTML to reflect the new manual decision.
3. **Integration**:
   - The final "Redacted Summary" tab uses the *latest* selected values from the UI state (incorporating manual overrides) for its prompt generation.

## Technical Details

### File: `src/mth058/ui/interface.py`

- Modify `create_triage_tab` to replace `incident_card`, `severity_indicator`, and `team_indicator` with the new design.
- Define a helper function `format_triage_card_html(severity, team, impact, is_safe)` to generate the card's HTML fragment.

### File: `src/mth058/data/theme.css`

- Add CSS classes for:
  - `.triage-card`: Container with padding, background, and rounded corners.
  - `.triage-card-badge`: Base style for badges.
  - `.severity-critical`, `.severity-high`, etc.: Specific color tokens.
  - `.team-badge`: Styled badge for team assignment.

## Testing Strategy

1. **Visual Verification**: Use Gradio's live reload to verify the card's layout and border color changes based on extraction.
2. **Interaction Verification**: Confirm that changing the "Severity" dropdown updates the card badge and color-coding instantly.
3. **End-to-End**: Ensure that a manually overridden severity is correctly reflected in the "Redacted Summary" prompt on the final tab.
