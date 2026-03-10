---
description: "Find and remove dead code -- auto-detects language: Knip for TypeScript/JavaScript, vulture + ruff for Python"
argument-hint: "[path] [--dry-run] [--dependencies-only] [--exports-only] [--production]"
---

# Cleanup Dead Code

Detect and remove unused code. Auto-detects the project language and dispatches to the appropriate skill.

## CRITICAL RULES

1. **Run tests before and after.** Establish a baseline, then verify no regressions.
2. **If `--dry-run`, report only.** Show findings without modifying files.
3. **Revert on test failure.** If any test fails after a change, undo it immediately.
4. **Never remove code that is used via side effects.** Check dynamic imports, decorators, and framework conventions.

## Step 1: Detect Language

```bash
# Check for TS/JS project
ls package.json 2>/dev/null

# Check for Python project
ls pyproject.toml setup.py setup.cfg 2>/dev/null
find . -maxdepth 3 -name "*.py" -print -quit 2>/dev/null
```

### Decision tree

**Knip mode** (TS/JS) - `package.json` exists:
- Proceed to Step 2A

**Python mode** - `*.py` files, `pyproject.toml`, or `setup.py` exist (no `package.json`):
- Proceed to Step 2B

**Both exist** - ask the user which to analyze, or run both sequentially.

## Step 2A: Knip Analysis (TypeScript/JavaScript)

Invoke the `knip` skill from `typescript-development`. Pass through any flags from `$ARGUMENTS` (`--dependencies-only`, `--exports-only`, `--production`, path).

Fallback if skill unavailable:
```bash
bunx knip 2>/dev/null || npx knip
```

Proceed to Step 3 with Knip findings.

## Step 2B: Python Analysis (vulture + ruff)

Invoke the `python-dead-code` skill from `python-development`. Pass through any path from `$ARGUMENTS`.

Fallback if skill unavailable:
```bash
uv run vulture [target] --min-confidence 80 2>/dev/null || vulture [target] --min-confidence 80
uv run ruff check [target] --select F401,F841 2>/dev/null || ruff check [target] --select F401,F841
```

Proceed to Step 3 with Python findings.

## Step 3: Present Findings

Categorize and display all findings by type (unused imports, variables, functions, classes, dependencies, exports, files). Include file:line locations.

If `--dry-run`, stop here.

## Step 4: Establish Test Baseline

```bash
# TS/JS
npm test 2>/dev/null || bun test 2>/dev/null || npx vitest run 2>/dev/null

# Python
pytest -v 2>/dev/null || python -m pytest -v 2>/dev/null
```

If no tests exist, warn and ask whether to proceed with manual verification or cancel.

## Step 5: Apply Cleanup

Apply changes in safest-first order:
- **TS/JS**: unused dependencies -> unused exports -> unused types -> unused files
- **Python**: unused imports -> unused variables -> unused functions/classes

For each change, verify no dynamic imports, side-effect usage, or framework conventions. Remove in small batches and validate.

## Step 6: Validate & Report

Re-run tests. If any fail, revert the last batch. Present a summary of what was removed and test status.

## What It Does

- **TypeScript/JavaScript (Knip)**: Finds unused dependencies, exports, files, and types. See the `knip` skill for details.
- **Python (vulture + ruff)**: Finds unused imports, variables, functions, classes, and unreachable code. See the `python-dead-code` skill for details.

## What It Does NOT Do

- Remove code used via side effects, dynamic imports, or reflection
- Modify framework-convention files (Next.js pages/, Django views, pytest fixtures)
- Remove dependencies used only in scripts
- Touch test files unless they reference removed symbols

$ARGUMENTS
