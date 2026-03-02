---
description: "Full design, layout, and CSS audit of the entire frontend — UX patterns, component hierarchy, spacing system, typography, accessibility, and visual consistency — outputs an actionable markdown report"
argument-hint: "[src-path] [--framework react|vue|svelte] [--strict-mode]"
---

# Full Frontend Design & CSS Review

You are a senior frontend design auditor. Perform a **comprehensive design, layout, and CSS review** of the entire frontend codebase — not just recent changes. Evaluate UX patterns, visual consistency, accessibility, layout system, typography, and CSS architecture.

## CRITICAL RULES

1. **Scan the whole frontend.** Use `src/`, `app/`, `components/`, `pages/`, `styles/` — or the path from `$ARGUMENTS` if provided.
2. **Design + CSS only.** Ignore backend files, API routes, build config. Focus on components, stylesheets, layout files.
3. **Run all agents in parallel.** Fire all in a single response.
4. **Write markdown report.** Output is `.design-review/report.md` — an actionable checklist with scores, findings, and fix instructions.
5. **Never enter plan mode.** Execute immediately.

## Step 1: Discover Frontend Files

```bash
find src -type f \( -name "*.tsx" -o -name "*.jsx" -o -name "*.vue" -o -name "*.svelte" -o -name "*.css" -o -name "*.scss" -o -name "*.sass" \) | head -80
```

Or use the path from `$ARGUMENTS` if provided. List what you find — components, pages, and stylesheet files.

If no frontend files are found, stop and say so.

## Step 2: Sample Key Files

Read a representative cross-section:
- Entry layout files (e.g., `App.tsx`, `Layout.tsx`, `_app.tsx`, `root.tsx`)
- 3-5 core components
- Primary stylesheet(s) or `globals.css` / `tailwind.config`
- Design token files (`tokens.ts`, `theme.ts`, `variables.css`)

This gives you the design language and patterns to evaluate against.

## Step 3: Run Parallel Review Agents

Fire all three agents **in parallel** in a single response:

### Agent A: UX Patterns & Component Architecture

```
Task:
  subagent_type: "ui-ux-designer"
  description: "Full UX and component architecture design audit"
  prompt: |
    Perform a full UX and component architecture audit of this frontend codebase.

    ## Scope
    [list of key files sampled]

    ## File Contents
    [paste sampled component and layout file contents]

    ## Instructions
    Evaluate:
    1. **Component responsibility**: God components, missing abstractions, component prop explosion
    2. **UX patterns**: Consistency of interaction patterns (forms, modals, navigation, data loading)
    3. **Empty/loading/error states**: Are all three states handled everywhere they're needed?
    4. **Information hierarchy**: Is visual hierarchy consistent? Do primary/secondary/tertiary actions follow a system?
    5. **User flows**: Are there obvious dead ends, missing feedback, or confusing navigation?
    6. **Design system adherence**: Are colors, spacing, and typography from a token system, or are they scattered arbitrary values?
    7. **Accessibility audit**: Semantic HTML, ARIA roles, keyboard navigation, focus management, color contrast awareness

    For each finding: severity (Critical/High/Medium/Low), file, issue, specific fix recommendation.
    Note what's working well.

    Return structured JSON at the end:
    ```json
    {
      "findings": [
        { "severity": "High", "category": "Accessibility", "file": "...", "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "ux_consistency": 7, "accessibility": 5, "component_design": 8, "overall": 7 }
    }
    ```
```

### Agent B: Layout System & Spatial Design

```
Task:
  subagent_type: "ui-layout-designer"
  description: "Layout system, grid, and spatial design audit"
  prompt: |
    Audit the layout system, grid, spacing, and spatial design of this frontend codebase.

    ## Scope
    [list of key files sampled]

    ## File Contents
    [paste sampled layout and stylesheet file contents]

    ## Instructions
    Evaluate:
    1. **Layout system**: Is there a consistent grid/layout pattern (CSS Grid, Flexbox, utility classes)? Or ad-hoc layouts per component?
    2. **Spacing scale**: Is spacing derived from a consistent scale (4px/8px/rem)? Or arbitrary pixel values scattered everywhere?
    3. **Responsive strategy**: Are breakpoints consistent? Mobile-first vs desktop-first? Are there layout shifts on resize?
    4. **Typography system**: Font scale, line-height, letter-spacing — are they tokens or raw values?
    5. **Alignment & rhythm**: Do elements align to a clear baseline? Is vertical rhythm maintained?
    6. **Above-the-fold**: Is the critical viewport optimized? Is the most important content immediately visible?
    7. **Container strategy**: Max-widths, centering, content containers — are they consistent?

    For each finding: severity (Critical/High/Medium/Low), file, issue, specific fix.
    Note what's done well.

    Return structured JSON at the end:
    ```json
    {
      "findings": [
        { "severity": "Medium", "category": "Spacing", "file": "...", "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "layout_system": 7, "responsive": 8, "typography": 6, "overall": 7 }
    }
    ```
```

### Agent C: CSS Architecture & Visual Polish

```
Task:
  subagent_type: "ui-polisher"
  description: "CSS architecture and visual polish audit"
  prompt: |
    Audit the CSS architecture, code quality, and visual polish of this frontend codebase.

    ## Scope
    [list of key files sampled]

    ## File Contents
    [paste sampled stylesheet and component file contents]

    ## Instructions
    Evaluate:
    1. **CSS architecture**: Global styles pollution, specificity wars, selector depth, !important abuse
    2. **Modern CSS usage**: Are CSS custom properties used? Container queries? Logical properties? Or legacy patterns?
    3. **Animation quality**: Transitions feel smooth? GPU-accelerated properties? prefers-reduced-motion respected?
    4. **Visual consistency**: Border-radius, shadow elevation, color palette — are they consistent or scattered?
    5. **Dark mode**: Is dark mode supported? Are colors properly adapted or just inverted?
    6. **CSS performance**: Unnecessary repaints, layout-triggering animations, oversized background images
    7. **Dead CSS**: Unused selectors, legacy overrides, commented-out blocks
    8. **Component isolation**: Are styles scoped or do they leak? CSS Modules / Tailwind / CSS-in-JS used correctly?

    For each finding: severity (Critical/High/Medium/Low), file, issue, specific fix.
    Note what's done well.

    Return structured JSON at the end:
    ```json
    {
      "findings": [
        { "severity": "Low", "category": "CSS Architecture", "file": "...", "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "css_architecture": 8, "visual_polish": 7, "animations": 9, "overall": 8 }
    }
    ```
```

## Step 4: Generate Markdown Report

After all agents complete, create `.design-review/` directory and write `report.md`.

Merge and deduplicate overlapping findings from the three agents. Order by severity, then file name. Group findings by category (UX, Layout, CSS).

**Output file:** `.design-review/report.md`

```markdown
# Design & CSS Review — [date]

Full frontend audit · [N] components · [M] stylesheets

## Scores

| Category | Score |
|----------|-------|
| UX Quality | X/10 |
| Layout System | X/10 |
| CSS Architecture | X/10 |
| Accessibility | X/10 |
| Typography | X/10 |
| **Overall** | **X/10** |

Critical: X | High: X | Medium: X | Low: X

## Files Audited

- `Component.tsx`, `Layout.tsx`, `globals.css`, ...

---

## Critical & High Issues

### UX & Components

#### `Button.tsx` — [issue title]
- **Severity**: Critical
- **Issue**: [description]
- **Fix**: [concrete fix instruction]
- [ ] Fixed

### Layout & Spacing

#### `Layout.tsx` — [issue title]
- **Severity**: High
- **Issue**: [description]
- **Fix**: [fix instruction]
- [ ] Fixed

### CSS Architecture

#### `globals.css` — [issue title]
- **Severity**: High
- **Issue**: [description]
- **Fix**: [fix instruction]
- [ ] Fixed

---

## Medium & Low Issues

### UX & Components
[Same format as above]

### Layout & Spacing
[Same format]

### CSS Architecture
[Same format]

---

## What's Working Well

- [positive observation from agents]
- [another positive]

---

## Action Plan

1. [ ] [top priority fix — from critical findings]
2. [ ] [second priority]
3. [ ] [third priority]
4. [ ] [fourth priority]
5. [ ] [fifth priority]
```

**Print a short summary** in the conversation:

```
Design & CSS review complete.

Report: .design-review/report.md

Overall Score: X/10
UX: X/10 | Layout: X/10 | CSS: X/10 | Accessibility: X/10

Critical: X | High: X | Medium: X | Low: X

Top 3 issues:
1. [critical issue summary]
2. [high issue summary]
3. [high issue summary]
```

If `--strict-mode` is set and Critical findings exist:
```
⚠️  STRICT MODE: X critical design issues found. Recommend addressing before shipping.
```
