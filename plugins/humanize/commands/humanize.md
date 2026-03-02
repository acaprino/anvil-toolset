---
description: "Rewrite source code to be more readable and human-friendly — improves naming, removes AI boilerplate, adds clarity comments — without changing behavior"
argument-hint: "<file or directory> [--dry-run] [--strict]"
---

# Humanize Code

Use the `humanize` agent to rewrite source code for readability without changing behavior.

## CRITICAL RULES

1. **Run tests before and after.** Establish a baseline, then verify no regressions.
2. **If `--dry-run`, preview only.** Show proposed changes without modifying files.
3. **Revert on test failure.** If any test fails after a change, undo it immediately.
4. **Never enter plan mode.** Execute immediately.

## Step 1: Identify Target

From `$ARGUMENTS`, determine files to humanize:
- If a file path: humanize that file
- If a directory: humanize all source files in it
- Filter out test files (unless they reference renamed symbols)

List the files to be humanized and their language.

## Step 2: Establish Test Baseline

Run the project's test suite:
```bash
pytest -v 2>/dev/null || npm test 2>/dev/null || cargo test 2>/dev/null
```

Record passing/failing tests. If no tests exist, warn the user:

```
No tests found. Humanization changes can't be automatically validated.

1. Proceed anyway — I'll be extra careful
2. Cancel — set up tests first
```

## Step 3: Preview Changes (always for --dry-run, ask otherwise)

If `--dry-run` flag is set, or if the target is a directory with >3 files, show a preview first:

For each file, analyze and propose:
- Variable/function renames (vague → domain-meaningful)
- Boilerplate comments to remove (paraphrase comments, empty docstrings)
- Why-comments to add (non-obvious business logic)
- Minor structural improvements (guard clauses, early returns)

Present the preview:

```
Humanization preview for: [target]

[file1]:
- Rename `data` → `user_profile` (line 23)
- Rename `proc` → `process_payment` (line 45)
- Remove boilerplate docstring (line 12-15)
- Add comment explaining retry logic (line 67)

[file2]:
- ...

Total changes: [count] across [file count] files

1. Apply all changes
2. Apply to specific files only
3. Cancel
```

If `--dry-run`, stop after the preview.

## Step 4: Apply Changes

Use the `humanize` agent:

```
Task:
  subagent_type: "humanize"
  description: "Humanize [target] for readability"
  prompt: |
    Improve the readability and human-friendliness of this code.
    Do NOT change behavior — only improve naming, comments, and clarity.

    ## Files to Humanize
    [list of files]

    ## Approved Changes
    [from preview, if applicable]

    ## Instructions
    For each file:
    1. Rename vague variables and parameters to domain-meaningful names
    2. Remove paraphrase comments and empty boilerplate docstrings
    3. Add brief why-comments for non-obvious business logic
    4. Use guard clauses / early returns where it improves readability

    Do NOT:
    - Change any behavior or logic
    - Reorder code or extract functions (unless --strict)
    - Remove error handling, validations, or imports
    - Modify test files (except renaming symbols renamed in source)
    - Add type annotations to unchanged code
```

## Step 5: Validate & Report

After changes:

```bash
pytest -v 2>/dev/null || npm test 2>/dev/null || cargo test 2>/dev/null
```

If any test fails: revert the last file's changes and report which file caused the failure.

Present summary:

```
Humanization complete for: [target]

Files modified: [count]
Changes made:
- Renames: [count]
- Comments removed: [count]
- Comments added: [count]
- Guard clauses: [count]

Tests: [all passing / X failures — reverted problematic changes]

Review the changes with: git diff
```

If `--strict` flag is set, also flag any remaining readability concerns that weren't auto-fixable.

## What It Does

- Renames vague variables and parameters to domain-meaningful names
- Removes paraphrase comments and empty boilerplate docstrings
- Adds brief why-comments for non-obvious business logic

## What It Does NOT Do

- Does not reorder code, extract functions, or change control flow (unless `--strict`)
- Does not remove error handling, validations, or imports
- Does not modify test files (unless renaming symbols renamed in source)

For deeper restructuring, use `/python-full-refactor` for metrics-driven refactoring.

Humanize the following:

$ARGUMENTS
