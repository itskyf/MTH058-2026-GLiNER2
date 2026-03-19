# Plan

## Project Objective

Implement a local-first "Local Incident Intake & PII-Safe Triage Copilot" demo using Python, Gradio Blocks, and GLiNER2. Emphasize why GLiNER2 outperforms LLM-only or traditional NER workflows.

## Tech Stack

- Python backend
- Gradio Blocks (no Interface, no React/Next.js)
- [GLiNER2](https://huggingface.co/fastino/gliner2-large-v1) for extraction and classification

## Core Capabilities

- Multi-section input parsing for chat threads, ticket text, and system logs.
- Zero-shot entity extraction for incident-specific labels.
- Classification for severity, owning team, and customer impact.
- Structured extraction generating a complete incident card.
- PII redaction that masks sensitive data while keeping operational entities intact.
- Routing suggestions and similar-incident filter chips.
- Live schema mutation allowing users to add new labels at runtime without retraining.
- Baseline comparison against regex or traditional NER.
- Hybrid mode generating an LLM-ready prompt from redacted structured outputs.

## UI Layout

- Build a single-screen ops console using Tabs, Rows, Columns, and Accordions.
- Left panel: Case selector and editable raw text sections.
- Center panel: Extracted entities, classifications, incident card, and timeline evidence.
- Right panel: Redacted text, routing logic, filter chips, schema editor, and export actions.
- Styling: Add minified custom CSS for a polished demo look.
- Interaction: Ensure source spans map clearly to extracted values.

## Architecture and Data

- Keep all operations local and privacy-first.
- Maintain a clean directory structure separating app logic, UI, and data fixtures.
- Define domains, labels, and structured fields using Pydantic or dataclasses.
- Keep fixtures out of the main logic files. Use importlib.resources.files() to load data safely; strictly avoid pathlib.Path(file) or hard-coded paths.
- Include diverse synthetic fixtures like payment rollback, duplicate charges, login outage, Kafka backlog, mobile crash, tenant outage, provider timeout, and PII leaks.

## Execution Steps

- Initialize the project and configure dependencies via uv.
- Define data schemas and load external fixtures.
- Implement GLiNER2 pipelines for extraction, classification, and redaction.
- Implement baseline rules and routing logic.
- Construct and wire the Gradio UI.
- Verify functionality and code quality using prek.
- Add a README.md with setup instructions and a short demo script.
