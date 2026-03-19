# Local Incident Intake & PII-Safe Triage Copilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a local-first incident triage system using GLiNER2 and Gradio Blocks with extraction, classification, redaction, and baseline comparison.

**Architecture:** Modular Service-Oriented (Approach 2) with services for extraction, classification, redaction, and similarity, coordinated by an Orchestrator.

**Tech Stack:** Python 3.13, GLiNER2, Gradio, Pydantic, importlib.resources.

---

## File Structure

- `src/mth058/models.py`: Pydantic data models (`Entity`, `Incident`, `IncidentCard`).
- `src/mth058/services/extractor.py`: `ExtractorService` using GLiNER2 (with chunking).
- `src/mth058/services/classifier.py`: `ClassifierService` using GLiNER2.
- `src/mth058/services/redactor.py`: `RedactorService` for PII masking.
- `src/mth058/services/similarity.py`: `SimilarityService` for finding related fixtures.
- `src/mth058/services/orchestrator.py`: `Orchestrator` to coordinate services.
- `src/mth058/data/fixtures.py`: Logic to load fixtures using `importlib.resources`.
- `src/mth058/data/sample_incident.json`: Synthetic incident fixtures.
- `src/mth058/ui/app.py`: Gradio Blocks UI layout and event wiring.
- `src/mth058/ui/theme.py`: Custom CSS and layout constants.
- `src/mth058/main.py`: Entry point to launch the Gradio app.

---

### Task 1: Data Models and Fixtures

**Files:**

- Create: `src/mth058/models.py`
- Create: `src/mth058/data/fixtures.py`
- Create: `src/mth058/data/sample_incident.json`
- Test: `tests/test_data.py`

**Tasks:**

- [ ] Step 1: Write failing test for fixture loading
- [ ] Step 2: Define Pydantic models in `models.py`
- [ ] Step 3: Implement fixture loading logic in `fixtures.py` using `importlib.resources`
- [ ] Step 4: Run test: `uv run pytest tests/test_data.py`
- [ ] Step 5: Commit

### Task 2: Extractor and Classifier Services (GLiNER2)

**Files:**

- Create: `src/mth058/services/extractor.py`
- Create: `src/mth058/services/classifier.py`
- Test: `tests/test_services.py`

**Tasks:**

- [ ] Step 1: Write failing test for extraction
- [ ] Step 2: Implement `ExtractorService` with GLiNER2 and chunking
- [ ] Step 3: Write failing test for classification
- [ ] Step 4: Implement `ClassifierService`
- [ ] Step 5: Run tests: `uv run pytest tests/test_services.py`
- [ ] Step 6: Commit

### Task 3: Redactor and Similarity Services

**Files:**

- Create: `src/mth058/services/redactor.py`
- Create: `src/mth058/services/similarity.py`
- Test: `tests/test_triage_logic.py`

**Tasks:**

- [ ] Step 1: Write failing test for PII redaction
- [ ] Step 2: Implement `RedactorService` with manual verification mode
- [ ] Step 3: Implement `SimilarityService` using label overlap
- [ ] Step 4: Run tests: `uv run pytest tests/test_triage_logic.py`
- [ ] Step 5: Commit

### Task 4: Orchestrator and Validation

**Files:**

- Create: `src/mth058/services/orchestrator.py`
- Test: `tests/test_orchestrator.py`

**Tasks:**

- [ ] Step 1: Write failing test for orchestrator coordination
- [ ] Step 2: Implement `Orchestrator` with input validation and PII check
- [ ] Step 3: Run tests: `uv run pytest tests/test_orchestrator.py`
- [ ] Step 4: Commit

### Task 5: UI Layout (Gradio Blocks)

**Files:**

- Create: `src/mth058/ui/app.py`
- Create: `src/mth058/ui/theme.py`
- Create: `src/mth058/main.py`

**Tasks:**

- [ ] Step 1: Define UI layout with Tabs, Rows, and Columns
- [ ] Step 2: Implement Baseline Comparison accordion
- [ ] Step 3: Implement Schema Configuration tab
- [ ] Step 4: Implement Redacted Summary tab
- [ ] Step 5: Commit UI structure

### Task 6: Event Wiring and Integration

**Files:**

- Modify: `src/mth058/ui/app.py`
- Modify: `src/mth058/main.py`

**Tasks:**

- [ ] Step 1: Wire "Run Analysis" button to Orchestrator
- [ ] Step 2: Implement Case Selector dropdown logic
- [ ] Step 3: Implement live schema update logic
- [ ] Step 4: Add loading indicators and error handling
- [ ] Step 5: Verify with `prek run --all-files`
- [ ] Step 6: Final commit
