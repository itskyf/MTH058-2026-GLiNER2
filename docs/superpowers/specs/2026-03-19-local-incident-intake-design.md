# Local Incident Intake & PII-Safe Triage Copilot Design

## 1. Overview

A local-first incident triage system using GLiNER2 and Gradio Blocks. It extracts entities, classifies severity/teams, and redacts PII for safe LLM interaction.

## 2. Architecture

The system uses a **Modular Service-Oriented (Approach 2)** architecture.

### 2.1 Services

- **ExtractorService**: Uses GLiNER2 for zero-shot entity extraction with a **chunking strategy** for large logs.
- **ClassifierService**: Uses GLiNER2 for classification (severity, team).
- **RedactorService**: Masks PII based on extracted offsets. Includes a **manual verification mode**.
- **SimilarityService**: Calculates similarity to existing fixtures based on **label overlap** and metadata.
- **Orchestrator**: Coordinates services, manages `IncidentContext`, and performs **input validation**.

### 2.2 Data Models (Pydantic)

- `Entity`: label, text, start, end, score.
- `Incident`: raw_text, sections (chat, logs, etc.), entities, severity, team, impact.
- `IncidentCard`: title, summary, key_entities, status.

## 3. UI Layout (Gradio Blocks)

A single-screen ops console with three main tabs:

### 3.1 Incident Triage Tab

- **Header:** Case Selector (Simple Dropdown), Run Analysis (Button), **Loading Indicator**.
- **Main Area (3 Columns):**
  - **Left (Input):** Raw Text (Textarea), Evidence Timeline (Markdown).
  - **Center (Extraction):** Entity Display (AnnotatedText), Incident Card (JSON/Table), Severity/Team (Status Indicators).
  - **Right (Triage/Output):** Redacted Text (Textarea with **Manual Edit Toggle**), Routing Logic (Markdown/JSON), Similar Cases (Chips).
  - **Bottom Drawer/Section (Optional):** Baseline Comparison (Toggle to compare GLiNER2 zero-shot outputs vs. Traditional NER like spaCy to highlight the "wow" factor).

### 3.2 Schema Configuration Tab

- Dynamic table for modifying GLiNER2 labels (Name + Description) at runtime.
- **Dynamic Schema Configuration** (Zero-shot parameter update, no retraining).
- Save/Reset buttons.

### 3.3 Redacted Summary Tab

- "Hybrid Mode" output: Generic JSON/ChatML prompt with redacted structured outputs for LLM-ready usage.
- **Validation Check:** Ensures no known PII labels remain in the final prompt.

## 4. Data Strategy & Fixtures

- **Fixtures:** Synthetic JSON files for various incident types (payments, infrastructure, security, etc.).
- **Storage:** `src/mth058/data/` directory, loaded via `importlib.resources`.
- **GLiNER2 Pipeline:** `fastino/gliner2-large-v1` for both extraction and classification.
- **Error Handling:** Graceful fallback if model loading fails or OOM occurs.

## 5. Security & Privacy

- **Local-First:** All processing (GLiNER2, Redaction) happens on-device.
- **PII-Safe:** Sensitive data (PERSON, EMAIL, PHONE) is redacted. **Manual override** allowed for edge cases.

## 6. Implementation Plan

- Step 1: Define Pydantic models and load fixtures.
- Step 2: Implement `ExtractorService` (with chunking) and `ClassifierService` using GLiNER2.
- Step 3: Implement `RedactorService`, `SimilarityService`, and routing logic.
- Step 4: Build Gradio UI with Tabs, Rows, and Columns. Add **error handling** and **loading states**.
- Step 5: Wire events, implement **input validation**, and test with diverse fixtures.
- Step 6: Verify with `prek` (pre-commit alternative, mentioned in `AGENTS.md`).
