# Lint Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix linting errors in `formatters.py`, `interface.py`, and `test_formatters.py` as reported by `prek run --all-files`.

**Architecture:** Systematic file-by-file correction of docstrings, type annotations, and function call arguments.

**Tech Stack:** Python, Ruff, Prek

---

## Task 1: Fix `src/mth058/ui/formatters.py`

**Files:**

- Modify: `src/mth058/ui/formatters.py:27-39`

- [ ] **Step 1: Fix docstring blank line**
Insert a blank line after the summary:

```python
    """Formats the incident triage data into a styled HTML card using minijinja.

    Args:
```

- [ ] **Step 2: Verify locally**
Run: `uv run ruff check src/mth058/ui/formatters.py`
Expected: No error for D205.

### Task 2: Fix `src/mth058/ui/interface.py`

**Files:**

- Modify: `src/mth058/ui/interface.py` (multiple spots)

- [ ] **Step 1: Fix Boolean positional calls (FBT003)**
Update `format_triage_card_html` calls to use keywords for `is_safe`.
Example (line 131, 226, 304):

```python
is_safe=True
```

- [ ] **Step 2: Fix S311 and use UUID if appropriate**
Check line 214 and 216. If asked, use `uuid` or ensure `secrets` is not flagging.
Wait, if it's not flagging, I'll stick to `secrets` as it was already there, but if the user *asks* for `uuid`, I'll use it.
The user said: "check if it's UUID need and use the right module".
I'll replace `secrets` with `uuid` for a more standard ID.
- [ ] **Step 3: Verify locally**
Run: `uv run ruff check src/mth058/ui/interface.py`
Expected: No errors for FBT, S311, E501.

### Task 3: Fix `tests/test_formatters.py`

**Files:**

- Modify: `tests/test_formatters.py`

**Steps:**

- [ ] **Step 1: Add return types (ANN201)**
Update test functions to have `-> None`.
- [ ] **Step 2: Fix docstring blank line (D205)**
Insert a blank line after the summary.
- [ ] **Step 3: Fix Boolean positional calls (FBT003)**
Use `is_safe=` in `format_triage_card_html` calls.
- [ ] **Step 4: Verify locally**
Run: `uv run ruff check tests/test_formatters.py`

### Task 4: Final verification

- [ ] **Step 1: Run `prek` on all files**
Run: `uv run prek run --all-files`
- [ ] **Step 2: Fix any remaining errors**
- [ ] **Step 3: Commit**
