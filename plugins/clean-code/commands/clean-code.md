---
description: >
  "Rewrite source code to be more readable and human-friendly -- improves naming, removes AI boilerplate, simplifies structure, adds clarity comments -- without changing behavior" argument-hint: "<file or directory> [--dry-run] [--strict] [--yes]".
  TRIGGER WHEN: the user requires assistance with tasks related to this domain.
  DO NOT TRIGGER WHEN: the task is outside the specific scope of this component.
---

# Clean Code

Use the `clean-code-agent` to rewrite source code for readability without changing behavior.

## CRITICAL RULES

1. **Run tests before and after.** Establish a baseline, then verify no regressions.
2. **If `--dry-run`, preview only.** Show proposed changes without modifying files.
3. **Revert on test failure.** If any test fails after a change, revert with `git restore <file>` immediately.
4. **Ask for confirmation** at Steps 2 and 3, unless `--yes` flag is provided.

## Step 1: Identify Target

From `$ARGUMENTS`, determine files to clean:
- If a file path: clean that file
- If a directory: clean all source files in it
- Filter out test files (unless they reference renamed symbols)

List the files to be cleaned and their language.

## Step 2: Establish Validation Baseline

Detect available validation tools by inspecting project files:

**Type checker** (detect first -- catches rename regressions tests may miss):
- `tsconfig.json` -> `tsc --noEmit`
- `pyproject.toml` with mypy/pyright config, or `mypy.ini`, `pyrightconfig.json` -> `mypy .` or `pyright`
- `Cargo.toml` -> `cargo check`
- `go.mod` -> `go vet ./...`

**Test runner:**
- `package.json` -> `npm test`
- `pyproject.toml`/`setup.py` -> `pytest`
- `Cargo.toml` -> `cargo test`
- `go.mod` -> `go test ./...`
- `Makefile` with test target -> `make test`

**Linter:**
- `ruff.toml` or `pyproject.toml` with ruff config -> `ruff check`
- `.eslintrc*` or `eslint.config.*` -> `eslint`
- `Cargo.toml` -> `cargo clippy`

Run all detected tools and capture both stdout and stderr. Record the baseline.

**Hard gate:** if NO tests AND NO type checker are found, do NOT proceed. Tell the user:

```
No tests or type checker found. Cannot validate that changes are safe.

1. Cancel -- set up tests or type checking first (recommended)
2. Proceed with --force -- I'll be careful but regressions may go undetected
```

If `--yes` flag is provided without `--force`, still block. Only `--force` bypasses this gate.

## Step 3: Preview Changes (always for --dry-run, ask otherwise)

If `--dry-run` flag is set, or if the target is a directory with >3 files, show a preview first.
If `--yes` flag is provided, apply all changes after showing the preview without asking.

For each file, analyze and propose:
- Variable/function renames (vague → domain-meaningful)
- Boilerplate comments to remove (paraphrase comments, empty docstrings)
- Why-comments to add (non-obvious business logic)
- Structural simplifications (flatten nesting, remove redundant abstractions, consolidate logic)

Present the preview:

```
Clean Code preview for: [target]

[file1]:
- Rename `data` → `user_profile` (line 23)
- Rename `proc` → `process_payment` (line 45)
- Remove boilerplate docstring (line 12-15)
- Flatten nested if/else chain (line 30-50)
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

Use the `clean-code-agent` agent:

```
Task:
  subagent_type: "clean-code-agent"
  description: "Clean [target] for readability"
  prompt: |
    Improve the readability and human-friendliness of this code.
    Do NOT change behavior -- only improve naming, comments, structure, and clarity.

    ## Files to Clean
    [list of files]

    ## Approved Changes
    [from preview, if applicable]

    ## Instructions
    For each file:
    1. Rename vague variables and parameters to domain-meaningful names
    2. Remove paraphrase comments and empty boilerplate docstrings
    3. Add brief why-comments for non-obvious business logic
    4. Simplify structure: flatten nesting with early returns, remove redundant
       wrappers, consolidate scattered logic, replace nested ternaries with
       switch/if-else, choose clarity over brevity

    Do NOT:
    - Change any behavior or logic
    - Reorder top-level code or extract functions (UNLESS --strict flag is present in $ARGUMENTS, in which case you may do so carefully)
    - Remove error handling, validations, or imports
    - Modify test files (except renaming symbols renamed in source)
    - Add type annotations to unchanged code
    - Over-simplify: keep abstractions that aid testing/extension
    - Combine too many concerns into one function
```

## Step 5: Validate & Report

After changes, re-run ALL validation tools detected in Step 2, in this order:

1. **Type checker** -- catches rename-induced type errors. If it fails on a file that passed in baseline, immediately `git restore <file>`.
2. **Tests** -- catches behavioral regressions. If any test that was passing in baseline now fails, immediately `git restore <file>`.
3. **Linter** -- catches syntax/style errors introduced by changes. If new errors appear, fix or revert.
4. **Non-code grep** -- for every renamed symbol, search `.json`, `.yaml`, `.yml`, `.toml`, `.env`, `.cfg`, `.ini`, `.xml`, `.html`, `.md` files for the OLD name. Report any matches as warnings -- these may be config references, serialization keys, or documentation that now refers to a stale name.

Present summary:

```
Clean Code complete for: [target]

Files modified: [count]
Changes made:
- Renames: [count]
- Comments removed: [count]
- Comments added: [count]
- Structural simplifications: [count]

Validation:
  Type check: [passed / N errors -- reverted] or [not available]
  Tests: [all passing / X failures -- reverted] or [not available]
  Linter: [passed / N new warnings] or [not available]

Stale references found in non-code files:
  - [config.json:12] -- still references old name `data`
  - [README.md:45] -- documents old function name `proc`

Review the changes with: git diff
```

If `--strict` flag is set, also flag any remaining readability concerns that weren't auto-fixable.

## What It Does

- Renames vague variables and parameters to domain-meaningful names
- Removes paraphrase comments and empty boilerplate docstrings
- Adds brief why-comments for non-obvious business logic
- Simplifies structure: flattens nesting, removes redundant abstractions, consolidates logic

## What It Does NOT Do

- Does not reorder top-level code, extract functions, or change APIs (unless `--strict`)
- Does not remove error handling, validations, or imports
- Does not modify test files (unless renaming symbols renamed in source)
- Does not over-simplify: keeps abstractions that aid testing or extension

For deeper restructuring, use `/python-refactor` for metrics-driven refactoring.

Clean the following:

$ARGUMENTS
