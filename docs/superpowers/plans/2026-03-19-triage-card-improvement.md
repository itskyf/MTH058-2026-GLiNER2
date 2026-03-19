# Action-Oriented Triage Summary Implementation Plan (Logic-First)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the redundant JSON and label components in the Triage tab with a single, clear Markdown summary and functional override controls for GLiNER2 predictions.

**Architecture:**

1. **UI Refactor**: Consolidate the "Extraction" column components into a unified `gr.Markdown` summary and a `gr.Group` for overrides.
2. **Markdown Formatter**: Implement a function to generate the triage summary Markdown string.
3. **State Management**: Use `gr.State` to persist the `incident_id` across manual overrides.
4. **Event Wiring**: Connect override controls (dropdowns, textboxes) to update the Markdown summary instantly without re-running GLiNER2.
5. **Integration**: Ensure the "Redacted Summary" tab uses the state from these override controls.

**Tech Stack:** Python, Gradio, Polars.

---

## Task 1: Implement Markdown Formatter Utility

**Files:**

- Create: `src/mth058/ui/formatters.py`
- Test: `tests/test_formatters.py`

**Steps:**

- [ ] **Step 1: Write tests for Markdown formatter**

```python
from mth058.ui.formatters import format_triage_summary_markdown

def test_format_triage_summary_markdown_critical():
    md = format_triage_summary_markdown("Critical", "SRE", "Total outage", True, "INC-001")
    assert "### INCIDENT SEVERITY: **Critical** 🔴" in md
    assert "SRE" in md
    assert "Total outage" in md
    assert "PII SAFETY STATUS: ✅ **SAFE**" in md
    assert "INC-001" in md
```

- [ ] **Step 2: Implement `format_triage_summary_markdown`**

```python
def format_triage_summary_markdown(severity: str, team: str, impact: str, is_safe: bool, incident_id: str) -> str:
    severity_emojis = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🔵",
        "Unknown": "⚪"
    }
    sev_emoji = severity_emojis.get(severity, "⚪")
    safety_label = "SAFE" if is_safe else "UNSAFE LEAK"
    safety_emoji = "✅" if is_safe else "❌"

    return f"""
### INCIDENT SEVERITY: **{severity}** {sev_emoji}
**ID:** `{incident_id}`

### ASSIGNED TEAM: **{team}**

**Impact Summary:** {impact}

**PII SAFETY STATUS:** {safety_emoji} **{safety_label}**
"""
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_formatters.py`

- [ ] **Step 4: Commit**

```bash
git add src/mth058/ui/formatters.py tests/test_formatters.py
git commit -m "feat: add triage summary Markdown formatter"
```

---

### Task 2: Refactor `TriageUI` and `create_triage_tab`

**Files:**

- Modify: `src/mth058/ui/interface.py`

- [ ] **Step 1: Update `TriageUI` dataclass**

Add `incident_id_state`, `triage_summary_md`, `edit_btn`, `override_group`, `override_severity`, `override_team`, `override_impact`, and `override_safety`. Remove `severity_indicator` and `team_indicator`. Wrap `incident_card` and `entity_display` in an accordion.

- [ ] **Step 2: Implement UI changes in `create_triage_tab`**

```python
from mth058.ui.formatters import format_triage_summary_markdown

# Inside create_triage_tab:
incident_id_state = gr.State(value="INC-PENDING")

# ... in center column ...
with gr.Column(scale=1):
    gr.Markdown("### 2. Triage Decision")
    triage_summary_md = gr.Markdown(
        value="### Awaiting analysis...",
        label="Triage Summary"
    )

    edit_btn = gr.Button("Edit Predictions", size="sm")

    with gr.Group(visible=False) as override_group:
        override_severity = gr.Dropdown(choices=SEVERITY_LABELS, label="Manual Severity")
        override_team = gr.Dropdown(choices=TEAM_LABELS, label="Manual Team")
        override_impact = gr.Textbox(label="Manual Impact Summary", lines=2)
        override_safety = gr.Checkbox(label="PII Safety Status (Checked = Safe)", value=True)

    with gr.Accordion("Show Raw Analytical Data", open=False):
        entity_display = gr.HighlightedText(...) # Keep existing
        incident_card = gr.JSON(...) # Keep existing
```

- [ ] **Step 3: Commit**

```bash
git add src/mth058/ui/interface.py
git commit -m "refactor: update TriageUI structure with interactive summary"
```

---

### Task 3: Update `analyze_incident` Logic

**Files:**

- Modify: `src/mth058/ui/interface.py`

- [ ] **Step 1: Generate Incident ID and update return dictionary**

```python
import random
import string

# Inside analyze_incident:
incident_id = f"INC-2026-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

# Update return dict:
return {
    ui.incident_id_state: incident_id,
    ui.triage_summary_md: format_triage_summary_markdown(incident.severity, incident.team, incident.impact, incident.is_safe, incident_id),
    ui.override_severity: incident.severity,
    ui.override_team: incident.team,
    ui.override_impact: incident.impact,
    ui.override_safety: incident.is_safe,
    # ... other components ...
}
```

- [ ] **Step 2: Commit**

```bash
git add src/mth058/ui/interface.py
git commit -m "feat: update analysis callback to return triage summary data"
```

---

### Task 4: Wire Manual Override Events

**Files:**

- Modify: `src/mth058/ui/interface.py` (in `create_ui`)

- [ ] **Step 1: Add event listeners for toggles and overrides**

```python
# Toggle visibility
triage_ui.edit_btn.click(
    fn=lambda visible: gr.update(visible=not visible),
    inputs=[triage_ui.override_group],
    outputs=[triage_ui.override_group]
)

# Live update summary on override change
override_inputs = [
    triage_ui.override_severity,
    triage_ui.override_team,
    triage_ui.override_impact,
    triage_ui.override_safety,
    triage_ui.incident_id_state
]

for inp in override_inputs[:-1]: # exclude state for trigger
    inp.change(
        fn=format_triage_summary_markdown,
        inputs=override_inputs,
        outputs=[triage_ui.triage_summary_md]
    )
```

- [ ] **Step 2: Refine event wiring for Redacted tab**

Update the Redacted tab components to use `override_severity` and `override_team` values.

- [ ] **Step 3: Commit**

```bash
git add src/mth058/ui/interface.py
git commit -m "feat: wire interactive events for triage summary overrides"
```

---

### Task 5: Final Verification

- [ ] **Step 1: Run the app and verify visual layout**
- [ ] **Step 2: Verify manual overrides update the summary and final prompt**
- [ ] **Step 3: Run all existing tests**
