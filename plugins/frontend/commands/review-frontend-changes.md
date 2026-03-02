---
description: "Review frontend code changes made in the current Claude Code session — React, performance, UX, CSS — and output an actionable markdown report"
argument-hint: "[--strict-mode] [--framework react|vue|svelte]"
---

# Review Recent Frontend Changes

You are a frontend code reviewer. Review the **frontend code changes made in the current session** and produce an actionable markdown report. Focus on React/JS/TS/CSS — not backend code, not documentation.

## CRITICAL RULES

1. **Diff first.** Start from `git diff HEAD` — this is ground truth of what changed. If no uncommitted changes, fall back to last commit and confirm scope with user.
2. **Frontend files only.** Include: `.js`, `.jsx`, `.ts`, `.tsx`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.svelte`, `.html` (template changes). Skip `.md`, backend files, config-only changes.
3. **Run review agents in parallel.** Fire all agents in a single response.
4. **Write markdown report.** Output is `.frontend-review/report.md` — an actionable checklist with scores, findings, and fix instructions.
5. **Never enter plan mode.** Execute immediately.

## Step 1: Identify Changed Frontend Files

```bash
git diff HEAD --name-only
git diff --name-only
git diff --cached --name-only
```

Filter to frontend extensions only: `.js`, `.jsx`, `.ts`, `.tsx`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.svelte`, `.html`.

If no frontend files changed, say so and stop.

List the files you'll review.

## Step 2: Get Diff Content

```bash
git diff HEAD -- <frontend files only>
```

If diff is large (>400 lines), prioritize new files and heavily changed ones.

## Step 3: Run Parallel Frontend Review Agents

Fire all three agents **in parallel** in a single response:

### Agent A: React & Performance

```
Task:
  subagent_type: "react-performance-optimizer"
  description: "React and performance review of recent frontend changes"
  prompt: |
    Review the following frontend code changes for React quality and performance issues.

    ## Changed Files
    [list of changed frontend files]

    ## Diff
    [paste the git diff output]

    ## Instructions
    Analyze for:
    1. **React patterns**: Incorrect hook usage, missing deps, stale closures, unnecessary re-renders
    2. **Performance**: Missing memoization (useMemo/useCallback/memo), expensive computations in render, N+1 effect chains
    3. **Bundle impact**: Heavy imports, missing lazy loading, large inline assets
    4. **State management**: Prop drilling, redundant state, state duplication across components
    5. **React 19 opportunities**: Can React Compiler handle this? Server Component candidates?
    6. **Accessibility basics**: Missing ARIA roles, keyboard handlers, focus management

    For each finding: severity (Critical/High/Medium/Low), file + line, specific fix.
    Also note what was done well.

    Return structured JSON at the end:
    ```json
    {
      "findings": [
        { "severity": "High", "category": "Performance", "file": "...", "line": 42, "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "performance": 7, "code_quality": 8, "overall": 7 }
    }
    ```
```

### Agent B: UX & Component Design

```
Task:
  subagent_type: "ui-ux-designer"
  description: "UX and component design review of recent frontend changes"
  prompt: |
    Review the following frontend code changes for UX and component design quality.

    ## Changed Files
    [list of changed frontend files]

    ## Diff
    [paste the git diff output]

    ## Instructions
    Analyze for:
    1. **Component design**: Is component responsibility well-defined? Are props sensible?
    2. **UX patterns**: Are interactions intuitive? Loading/error/empty states handled?
    3. **Accessibility**: ARIA attributes, semantic HTML, keyboard navigation, color contrast indicators
    4. **Design system consistency**: Are spacing, color, and typography tokens used correctly vs hardcoded values?
    5. **Responsive design**: Are breakpoints and fluid layouts considered?
    6. **User feedback**: Are async operations communicated (loading spinners, toasts, error messages)?

    For each finding: severity (Critical/High/Medium/Low), file + line, specific fix.
    Also note what was done well.

    Return structured JSON at the end:
    ```json
    {
      "findings": [
        { "severity": "Medium", "category": "Accessibility", "file": "...", "line": 15, "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "ux": 7, "accessibility": 6, "overall": 7 }
    }
    ```
```

### Agent C: CSS & Visual Polish

```
Task:
  subagent_type: "ui-polisher"
  description: "CSS and visual polish review of recent frontend changes"
  prompt: |
    Review the following frontend code changes for CSS quality and visual polish.

    ## Changed Files
    [list of changed frontend files]

    ## Diff
    [paste the git diff output]

    ## Instructions
    Analyze for:
    1. **CSS quality**: Specificity conflicts, redundant rules, missing resets, hardcoded px vs rem/em
    2. **Modern CSS**: Opportunities for CSS variables, container queries, logical properties, grid/flexbox improvements
    3. **Animation & transitions**: Missing or janky transitions, GPU-accelerated properties, reduced-motion support
    4. **Visual consistency**: Inconsistent shadows, border-radius, spacing values vs design tokens
    5. **Dark mode support**: Are colors and images adapted for dark mode if the project uses it?
    6. **Paint performance**: Avoid layout-triggering properties in animations, will-change abuse

    For each finding: severity (Critical/High/Medium/Low), file + line, specific fix.
    Also note what was done well.

    Return structured JSON at the end:
    ```json
    {
      "findings": [
        { "severity": "Low", "category": "CSS Quality", "file": "...", "line": 8, "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "css_quality": 8, "visual_polish": 7, "overall": 8 }
    }
    ```
```

## Step 4: Generate Markdown Report

After all agents complete, create `.frontend-review/` directory and write `report.md`.

Merge and deduplicate overlapping findings from the three agents. Order by severity, then file name.

**Output file:** `.frontend-review/report.md`

```markdown
# Frontend Review — [date]

## Scores

| Category | Score |
|----------|-------|
| Performance | X/10 |
| UX Quality | X/10 |
| CSS Quality | X/10 |
| Accessibility | X/10 |
| **Overall** | **X/10** |

Critical: X | High: X | Medium: X | Low: X

## Changed Files

- `file1.tsx` (+X/-Y)
- `file2.css` (+X/-Y)

---

## Critical & High Issues

### `ComponentName.tsx:42` — [issue title]
- **Severity**: Critical
- **Category**: Performance
- **Issue**: [description of what's wrong]
- **Fix**: [concrete fix instruction with code if helpful]
- [ ] Fixed

### `OtherFile.tsx:15` — [issue title]
- **Severity**: High
- **Category**: Accessibility
- **Issue**: [description]
- **Fix**: [fix instruction]
- [ ] Fixed

---

## Medium & Low Issues

### `file.tsx:30` — [issue title]
- **Severity**: Medium
- **Category**: [React/UX/CSS]
- **Issue**: [description]
- **Fix**: [fix instruction]
- [ ] Fixed

---

## What's Working Well

- [positive observation from agents]
- [another positive]

---

## Action Plan

1. [ ] [highest priority fix — from critical findings]
2. [ ] [second priority]
3. [ ] [third priority]
4. [ ] [fourth priority]
5. [ ] [fifth priority]
```

**Print a short summary** in the conversation:

```
Frontend review complete.

Report: .frontend-review/report.md

Overall Score: X/10
Critical: X | High: X | Medium: X | Low: X

Top issues:
1. [highest severity finding summary]
2. [second]
3. [third]
```

If `--strict-mode` is passed and there are Critical findings, warn:
```
STRICT MODE: Critical issues found. Fix before committing.
```
