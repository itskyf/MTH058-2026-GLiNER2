# AGENTS.md

## Overview

In 1-2 days, build a real workflow app, not a model wrapper. It must make users say "wow" by showing why GLiNER2 is better here than LLM-only extraction or traditional NER.

## Development Commands

- Run command in venv: `uv run <command>`
- Code Quality: `prek run --all-files`

## Skill usage

TODO

## Code Style Principles

- Use top-level imports.
- Use Google-style docstrings.
- Use comments strictly to explain non-obvious logic or provide context.
- Keep logging minimal and clear.
- Use modern Python typing (dict[str, int], X | None) and avoid Any.
- Use structured types (e.g., NamedTuple, dataclasses, TypedDict, Pydantic) instead of raw dictionaries for complex data to prevent hardcoded keys and enable IDE refactoring.
