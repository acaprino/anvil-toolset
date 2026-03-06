---
description: "Review code changes — uncommitted changes, staged changes, or recent commits — using focused architecture, security, and pattern analysis agents in parallel"
argument-hint: "[--last-commits N] [--security-focus] [--strict-mode]"
---

# Review Recent Changes

You are a focused code reviewer. Your job is to review **code changes** — uncommitted edits, staged files, or recent commits. This is NOT a full project review. You look only at what changed, not at documentation.

## CRITICAL RULES

1. **Detect change source automatically.** Check for uncommitted changes first. If none, fall back to recent commits. Always confirm the scope with the user before running agents.
2. **Skip documentation files.** Ignore `.md`, `.txt`, `.rst`, `README*`, `CHANGELOG*`, `LICENSE*`. Focus only on code.
3. **Run agents in parallel.** Fire all review agents in a single response using multiple Task tool calls.
4. **Never enter plan mode.** Execute immediately.
5. **Output a single concise report.** No intermediate files needed — deliver findings directly in the conversation.
6. **Read surrounding context.** For each changed file, read the full file (not just the diff) so agents understand the code in context.

## Critical Analysis Directive

These agents are configured for critical analysis. The goal is to find problems, not validate code. Do not soften findings or lead with positive framing.

## Step 1: Detect Changes

Run these commands to identify what to review:

```bash
git diff --name-only          # unstaged changes
git diff --cached --name-only # staged changes
```

### Decision tree

**Case A — Uncommitted changes exist** (unstaged and/or staged):

Use `git diff` (unstaged) and `git diff --cached` (staged) as the review target. The diff source is "uncommitted changes".

**Case B — No uncommitted changes, `--last-commits N` flag provided:**

Use `git diff HEAD~N..HEAD` as the review target. The diff source is "last N commits".

**Case C — No uncommitted changes, no flag:**

Check recent commits:

```bash
git log --oneline -5
```

Default to reviewing the last commit (`HEAD~1..HEAD`). The diff source is "last commit".

### Filter code files

From the detected changes, filter out non-code files:
- Exclude: `.md`, `.txt`, `.rst`, `.json` (config-only), `.yaml`/`.yml` (config-only), images, lock files
- Include: source code files (`.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.rs`, `.go`, `.java`, `.rb`, `.css`, `.scss`, `.html`, etc.)

If no code files remain (only docs/config), say so and stop.

## Step 2: Confirm Scope with User

**Always** present what you found and ask for confirmation before running agents:

```
Found [change source]:

Code files to review:
- [file1] (+X/-Y lines)
- [file2] (+X/-Y lines)
- ...

Total: [N] code files, [M] lines changed

1. Review these changes
2. Review last N commits instead — specify how many
3. Review specific files only — I'll tell you which
4. Cancel
```

Use AskUserQuestion with these options. Do NOT proceed until the user confirms.

## Step 3: Gather Context

For each changed code file:

1. **Read the full file** (not just the diff) to understand the surrounding context
2. **Get the diff** for that file to know exactly what changed

This allows agents to evaluate changes against the existing codebase patterns, not in isolation.

```bash
git diff [source] -- <code files only>
```

If the total diff is very large (>500 lines), prioritize:
1. New files (highest priority — no prior review)
2. Files with the most changes
3. Files touching security-sensitive areas (auth, input handling, crypto)

## Step 4: Run Parallel Review Agents

Run all three agents **in parallel** in a single response:

### Agent A: Architecture & Code Quality

```
Task:
  subagent_type: "architect-review"
  description: "Architecture and code quality review of recent changes"
  prompt: |
    Review the following code changes for architectural soundness and code quality.
    You have both the diff AND the full file contents for context.
    Skip documentation files. Focus only on code.

    ## Change Source
    [uncommitted changes / last N commits / specific commit range]

    ## Changed Files
    [list of changed code files with line counts]

    ## Full File Contents
    [paste full contents of each changed file — this is context, not the review target]

    ## Diff (this is what you're reviewing)
    [paste the git diff output]

    ## Instructions
    Analyze the CHANGED code (diff) in context of the full files for:
    1. **Design concerns**: Are the changes architecturally sound? Inappropriate coupling or broken abstractions?
    2. **Code quality**: Naming, function length, complexity, duplication
    3. **Error handling**: Missing or incorrect error handling in new/modified code
    4. **Consistency**: Do the changes follow the patterns already in the codebase? Check the full file for established patterns.
    5. **Over-engineering or under-engineering**: Is the solution appropriately scoped?
    6. **Integration**: Do the changes integrate well with the existing code? Any broken contracts?
    7. **Flow correctness**: Trace modified flows end-to-end. Does every step connect? Could this change break callers, importers, or downstream consumers of modified functions/state/events?

    For each finding: severity (Critical/High/Medium/Low), file + line, and a concrete fix recommendation.
    Do not soften findings. Findings are your priority.

    Keep the response focused and concise — this is a targeted review, not a full audit.
```

### Agent B: Security Assessment

```
Task:
  subagent_type: "security-auditor"
  description: "Security review of recent changes"
  prompt: |
    Review the following code changes for security vulnerabilities.
    You have both the diff AND the full file contents for context.
    Skip documentation files. Focus only on code.

    ## Change Source
    [uncommitted changes / last N commits / specific commit range]

    ## Changed Files
    [list of changed code files]

    ## Full File Contents
    [paste full contents of each changed file — this is context]

    ## Diff (this is what you're reviewing)
    [paste the git diff output]

    ## Instructions
    Check the CHANGED code (diff) in context of the full files for:
    1. **Injection risks**: SQL, command, LDAP, XPath, XSS injection in new or modified code
    2. **Input validation**: Missing or insufficient validation of user-controlled input
    3. **Authentication/authorization**: Flawed logic, missing checks, privilege escalation
    4. **Secrets exposure**: Hardcoded credentials, tokens, keys, API secrets
    5. **Insecure defaults**: Debug mode, verbose errors, permissive CORS, missing security headers
    6. **Dependency risks**: New packages added — are they trustworthy and up to date?
    7. **Data exposure**: Sensitive data in logs, error messages, or API responses

    For each finding: severity, CWE if applicable, file + line, attack scenario, concrete fix.
    If no security issues found, explain what attack surfaces you examined and why they are safe.

    Keep the response concise — targeted review only.
```

### Agent C: Pattern Consistency & Scoring

```
Task:
  subagent_type: "pattern-quality-scorer"
  description: "Pattern consistency and quality scoring of recent changes"
  prompt: |
    Analyze the following code changes for pattern consistency and assign a quality score.
    You have both the diff AND the full file contents for context.

    ## Change Source
    [uncommitted changes / last N commits / specific commit range]

    ## Changed Files
    [list of changed code files]

    ## Full File Contents
    [paste full contents of each changed file — use these to identify dominant patterns]

    ## Diff (this is what you're reviewing)
    [paste the git diff output]

    ## Instructions

    ### Pattern Consistency
    For each changed file, use the FULL file to identify dominant patterns, then check if the DIFF follows them:
    - Error handling style (try/catch, Result types, error checks)
    - Async patterns (async/await vs callbacks vs promises)
    - Naming conventions (camelCase, snake_case, naming semantics)
    - Import conventions (grouping, ordering)
    - Null/optional handling (defensive checks, optional chaining)
    - Resource management (using, defer, finally, context managers)

    Key question: "Is there an established pattern in this file that the new code should follow but doesn't?"

    ### Anti-patterns introduced
    Flag: swallowed exceptions, tight coupling, mutable globals, TODO in critical paths,
    hardcoded magic numbers, duplicated logic, missing type safety.

    ### Mental Models (apply all six)
    - **Security Engineer**: Is all input treated as malicious?
    - **Performance Engineer**: Any O(n²) loops, N+1 queries, blocking I/O?
    - **Team Lead**: Will a junior dev understand this in 6 months?
    - **Systems Architect**: How does this fail? Blast radius?
    - **SRE**: What breaks at 3 AM?
    - **Pattern Detective**: What patterns exist, and did this change violate them?

    ### Quality Score for These Changes
    Score only the changed code (not the whole project):

    | Category        | Score |
    |-----------------|-------|
    | Code Quality    | X/10  |
    | Security        | X/10  |
    | Consistency     | X/10  |
    | **Overall**     | **X/10** |

    Default overall score to 5/10. Justify any score above 7 with specific evidence.
    Scoring guide: 9-10 excellent, 7-8 good, 5-6 adequate, 3-4 poor, 1-2 critical.
    Include 2-3 sentence rationale per score.
```

## Step 5: Consolidated Summary

After all three agents complete, synthesize their findings into a final summary directly in the conversation:

```
## Review Summary — [Change Source]

### Changed Files
[list with line counts]

### Overall Score: X/10

### Critical & High Issues
[merged list from all agents, deduplicated, ordered by severity]

### Medium & Low Issues
[merged list]

### Positive Observations (if any)
[only include if agents reported genuinely noteworthy positive patterns]

### Top 3 Recommended Actions
1. [highest priority fix]
2. [second priority]
3. [third priority]
```

If `--security-focus` is passed, give extra weight to security findings and recommend fixing all security issues before proceeding.

If `--strict-mode` is passed and there are Critical findings, append:

```
STRICT MODE: Critical issues found. Recommend fixing before committing.
```

Keep the entire output concise. This is a quick review, not a full audit report.
