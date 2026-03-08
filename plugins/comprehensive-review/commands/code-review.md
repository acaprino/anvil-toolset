---
description: "PR-focused code review with git blame analysis, CLAUDE.md compliance, confidence scoring, and optional auto-commenting on GitHub PRs"
argument-hint: "[PR number | --branch <name>] [--auto-comment] [--strict]"
---

# Code Review

You are a thorough code reviewer. Your job is to review a pull request or branch diff, analyze the changes in depth, and produce a structured review with confidence-scored findings. Optionally post review comments directly on the PR.

## CRITICAL RULES

1. **Always review in context.** Read full files, not just diffs. Understand what the code does before judging changes.
2. **Score every finding.** Each finding gets a confidence score (0-100) indicating how certain you are it's a real issue.
3. **Check CLAUDE.md compliance.** If the project has a CLAUDE.md, verify changes follow its conventions.
4. **Never enter plan mode.** Execute immediately.
5. **Run agents in parallel.** Fire all review agents in a single response.
6. **Skip documentation files.** Ignore `.md`, `.txt`, `.rst`, `README*`, `CHANGELOG*`, `LICENSE*`. Focus only on code.

## Step 1: Identify Review Target

From `$ARGUMENTS`, determine what to review:

**Case A — PR number provided** (e.g. `42`, `#42`):

```bash
gh pr view 42 --json number,title,body,baseRefName,headRefName,files
gh pr diff 42
```

**Case B — `--branch <name>` provided:**

```bash
git log main..<branch> --oneline
git diff main...<branch>
```

**Case C — No arguments:**

Detect current branch and compare against main/master:

```bash
CURRENT=$(git branch --show-current)
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
git diff ${BASE}...${CURRENT}
```

### Filter code files

Exclude: `.md`, `.txt`, `.rst`, `.json` (config-only), `.yaml`/`.yml` (config-only), images, lock files.
Include: source code files (`.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.rs`, `.go`, `.java`, `.rb`, `.css`, `.scss`, `.html`, etc.)

If no code files remain, say so and stop.

## Step 2: Gather Context

For each changed code file:

1. **Read the full file** — understand surrounding context
2. **Get the diff** — know exactly what changed
3. **Run git blame on changed lines** — understand who wrote the original code and when

```bash
git blame -L <start>,<end> <file>
```

4. **Check for past PR comments** on the same files (if reviewing a PR):

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments --jq '.[].path' | sort -u
```

5. **Read CLAUDE.md** if it exists — note project conventions, naming rules, patterns

## Step 3: Run Parallel Review Agents

Run all three agents **in parallel** in a single response:

### Agent A: Architecture & Code Quality

```
Task:
  subagent_type: "architect-review"
  description: "Architecture review for code-review command"
  prompt: |
    Review the following code changes for architectural soundness and code quality.
    You have both the diff AND the full file contents for context.

    ## Changed Files
    [list of changed code files with line counts]

    ## Full File Contents
    [paste full contents of each changed file]

    ## Diff
    [paste the git diff output]

    ## Git Blame Context
    [paste relevant blame output — shows history of changed lines]

    ## Project Conventions (from CLAUDE.md)
    [paste relevant conventions, or "none found"]

    ## Instructions
    Analyze the CHANGED code in context for:
    1. Design concerns — coupling, broken abstractions, inappropriate patterns
    2. Code quality — naming, complexity, duplication
    3. Error handling — missing or incorrect in new/modified code
    4. Consistency — do changes follow existing codebase patterns?
    5. Over/under-engineering — is the solution appropriately scoped?
    6. CLAUDE.md compliance — do changes follow project conventions?
    7. Flow correctness — trace modified flows end-to-end, check callers/consumers

    For each finding: severity (Critical/High/Medium/Low), file + line, confidence (0-100), concrete fix.
```

### Agent B: Security Assessment

```
Task:
  subagent_type: "security-auditor"
  description: "Security review for code-review command"
  prompt: |
    Review the following code changes for security vulnerabilities.
    You have both the diff AND the full file contents for context.

    ## Changed Files
    [list of changed code files]

    ## Full File Contents
    [paste full contents of each changed file]

    ## Diff
    [paste the git diff output]

    ## Instructions
    Check the CHANGED code for:
    1. Injection risks — SQL, command, XSS injection
    2. Input validation — missing or insufficient
    3. Auth/authz — flawed logic, missing checks, privilege escalation
    4. Secrets exposure — hardcoded credentials, tokens, keys
    5. Insecure defaults — debug mode, verbose errors, permissive CORS
    6. Dependency risks — new packages trustworthy and up to date?
    7. Data exposure — sensitive data in logs, errors, responses

    For each finding: severity, CWE if applicable, file + line, confidence (0-100), attack scenario, concrete fix.
```

### Agent C: Pattern Consistency & Scoring

```
Task:
  subagent_type: "pattern-quality-scorer"
  description: "Pattern scoring for code-review command"
  prompt: |
    Analyze the following code changes for pattern consistency and quality.
    You have both the diff AND the full file contents for context.

    ## Changed Files
    [list of changed code files]

    ## Full File Contents
    [paste full contents of each changed file]

    ## Diff
    [paste the git diff output]

    ## Project Conventions (from CLAUDE.md)
    [paste relevant conventions, or "none found"]

    ## Instructions

    ### Pattern Consistency
    For each file, identify dominant patterns in the FULL file, then check if the DIFF follows them:
    - Error handling style, async patterns, naming conventions
    - Import conventions, null handling, resource management

    ### Anti-patterns
    Flag: swallowed exceptions, tight coupling, mutable globals, TODO in critical paths,
    hardcoded magic numbers, duplicated logic, missing type safety.

    ### CLAUDE.md Compliance
    Check each changed file against project conventions. Flag any deviations.

    ### Quality Score
    Score the changed code:

    | Category        | Score | Confidence |
    |-----------------|-------|------------|
    | Code Quality    | X/10  | X%         |
    | Security        | X/10  | X%         |
    | Consistency     | X/10  | X%         |
    | **Overall**     | **X/10** | **X%**  |

    Default overall to 5/10. Justify any score above 7 with specific evidence.
```

## Step 4: Consolidated Review

After all agents complete, synthesize findings into a structured review:

```
## Code Review — [PR title or branch name]

### Review Scope
- Files reviewed: [N]
- Lines changed: +X / -Y
- CLAUDE.md compliance: [checked / not found]

### Overall Score: X/10 (confidence: X%)

### Critical & High Findings
| # | Severity | File:Line | Finding | Confidence | Fix |
|---|----------|-----------|---------|------------|-----|
| 1 | Critical | ...       | ...     | 95%        | ... |

### Medium & Low Findings
| # | Severity | File:Line | Finding | Confidence | Fix |
|---|----------|-----------|---------|------------|-----|

### CLAUDE.md Compliance
- [list any violations, or "All changes comply with project conventions"]

### Top 3 Recommended Actions
1. [highest priority]
2. [second priority]
3. [third priority]
```

If `--strict` and there are Critical findings:

```
STRICT MODE: Critical issues found. Recommend fixing before merging.
```

## Step 5: Auto-Comment on PR (if --auto-comment)

If `--auto-comment` flag is set and reviewing a PR:

Post only findings with confidence >= 70 as inline PR comments:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments \
  -f body="**[Severity]** (confidence: X%) — [finding summary]

[concrete fix recommendation]" \
  -f path="[file]" \
  -f line=[line] \
  -f commit_id="$(gh pr view {number} --json headRefOid --jq '.headRefOid')"
```

Post the overall summary as a regular PR comment:

```bash
gh pr comment {number} --body "$(cat <<'EOF'
## Automated Code Review

**Overall Score: X/10**

[summary of critical/high findings]

[top 3 recommended actions]

---
*Reviewed by: architect-review, security-auditor, pattern-quality-scorer*
EOF
)"
```

$ARGUMENTS
