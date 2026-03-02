---
description: "Full frontend redesign pipeline — UX audit, layout design, implementation, React performance optimization, UI polish, and visual HTML audit report"
argument-hint: "<target path or description> [--framework react|vue|svelte] [--skip-performance] [--strict-mode]"
---

# Frontend Redesign Pipeline

## CRITICAL BEHAVIORAL RULES

You MUST follow these rules exactly. Violating any of them is a failure.

1. **Execute phases in order.** Do NOT skip ahead, reorder, or merge phases.
2. **Write output files.** Each phase MUST produce its output file in `.frontend-redesign/` before the next phase begins. Read from prior phase files -- do NOT rely on context window memory.
3. **Stop at checkpoints.** When you reach a `PHASE CHECKPOINT`, you MUST stop and wait for explicit user approval before continuing. Use the AskUserQuestion tool with clear options.
4. **Halt on failure.** If any step fails (agent error, missing files, access issues), STOP immediately. Present the error and ask the user how to proceed. Do NOT silently continue.
5. **Never enter plan mode autonomously.** Do NOT use EnterPlanMode. This command IS the plan -- execute it.
6. **Phase 6 runs 3 agents in parallel.** Fire all three agents in a single response using multiple Task tool calls.
7. **HTML report is mandatory.** Phase 6 MUST produce `.frontend-redesign/report.html` -- a self-contained visual dashboard.

## Pre-flight Checks

### 1. Check for existing session

Check if `.frontend-redesign/state.json` exists:

- If it exists and `status` is `"in_progress"`: Read it, display the current phase, and ask:
  ```
  Found an in-progress frontend redesign session:
  Target: [target from state]
  Current phase: [phase from state]

  1. Resume from where we left off
  2. Start fresh (archives existing session)
  ```
- If it exists and `status` is `"complete"`: Ask whether to archive and start fresh.

### 2. Initialize state

Create `.frontend-redesign/` directory and `state.json`:

```json
{
  "target": "$ARGUMENTS",
  "status": "in_progress",
  "flags": {
    "framework": null,
    "skip_performance": false,
    "strict_mode": false
  },
  "current_phase": 1,
  "completed_phases": [],
  "files_created": [],
  "started_at": "ISO_TIMESTAMP",
  "last_updated": "ISO_TIMESTAMP"
}
```

Parse `$ARGUMENTS` for `--framework`, `--skip-performance`, and `--strict-mode` flags.

### 3. Discover frontend files

Scan for frontend files:

```bash
find src -type f \( -name "*.tsx" -o -name "*.jsx" -o -name "*.vue" -o -name "*.svelte" -o -name "*.css" -o -name "*.scss" \) | head -80
```

Or use the path from `$ARGUMENTS` if provided. If no frontend files found, STOP and say so.

### 4. Detect framework

If `--framework` not specified, auto-detect from:
- `package.json` dependencies (react, vue, svelte)
- File extensions (.tsx/.jsx → React, .vue → Vue, .svelte → Svelte)

### 5. Sample key files

Read a representative cross-section:
- Entry layout files (App.tsx, Layout.tsx, _app.tsx, root.tsx)
- 3-5 core components
- Primary stylesheets (globals.css, tailwind.config)
- Design token files (tokens.ts, theme.ts, variables.css)

**Output file:** `.frontend-redesign/00-scope.md`

```markdown
# Redesign Scope

## Target
[Description of what is being redesigned]

## Framework
[Detected or specified framework]

## Frontend Files
[List of component, page, and stylesheet files]

## Key Files Sampled
[List of files read for pattern detection]

## Flags
- Framework: [name]
- Skip Performance: [yes/no]
- Strict Mode: [yes/no]

## Redesign Phases
1. UX Audit & User Flow Design
2. Layout Composition & Grid System
3. Implement Designs
4. React Performance Optimization
5. UI Polish & Micro-interactions
6. Final Design Audit (HTML Report)
```

---

## Phase 1: UX Audit & User Flow Design

```
Task:
  subagent_type: "ui-ux-designer"
  description: "UX audit and user flow redesign"
  prompt: |
    Perform a comprehensive UX audit of this frontend application and design improved user flows.

    ## Scope
    [Insert contents of .frontend-redesign/00-scope.md]

    ## Sampled File Contents
    [Paste contents of key layout and component files]

    ## Instructions
    Audit and redesign:
    1. **Current UX assessment**: Evaluate existing patterns, identify pain points
    2. **Component responsibility audit**: God components, missing abstractions, prop explosion
    3. **User flow analysis**: Navigation paths, dead ends, missing feedback
    4. **Information hierarchy**: Visual hierarchy consistency, primary/secondary/tertiary actions
    5. **State handling**: Empty states, loading states, error states — are all three handled?
    6. **Accessibility**: Semantic HTML, ARIA, keyboard navigation, focus management, contrast
    7. **Design system adherence**: Colors, spacing, typography from tokens or scattered values?

    For each finding:
    - Current state (what's wrong)
    - Redesigned state (what it should be)
    - Priority: Critical/High/Medium/Low
    - Specific implementation guidance

    Organize findings as: issues to fix, patterns to establish, components to refactor.

    Write your findings as a structured markdown document.
```

**Output file:** `.frontend-redesign/01-ux-audit.md`

```markdown
# Phase 1: UX Audit & User Flow Design

## Current State Assessment
[Overall UX health]

## Critical UX Issues
[Must-fix problems]

## User Flow Redesign
[Improved navigation and interaction patterns]

## Component Refactoring Plan
[Components that need restructuring]

## Design System Recommendations
[Token system, component library suggestions]

## Accessibility Gaps
[A11y issues and fixes]

## Key Findings for Phase 2 Context
[Layout and spacing issues that inform the layout phase]
```

Update `state.json`: set `current_phase` to 2, add phase 1 to `completed_phases`.

---

## Phase 2: Layout Composition & Grid System

Read `.frontend-redesign/01-ux-audit.md` for context.

```
Task:
  subagent_type: "ui-layout-designer"
  description: "Layout system design and grid composition"
  prompt: |
    Design a comprehensive layout system and grid composition for this frontend redesign.

    ## Scope
    [Insert contents of .frontend-redesign/00-scope.md]

    ## UX Audit Context
    [Insert contents of .frontend-redesign/01-ux-audit.md — especially layout/spacing findings]

    ## Sampled File Contents
    [Paste contents of layout and stylesheet files]

    ## Instructions
    Design and specify:
    1. **Grid system**: Define the layout grid (CSS Grid/Flexbox), column structure, gutters
    2. **Spacing scale**: Design a consistent spacing system (4px/8px base) with named tokens
    3. **Responsive strategy**: Breakpoints, mobile-first vs desktop-first, layout shifts
    4. **Typography scale**: Font sizes, line heights, letter spacing as tokens
    5. **Container strategy**: Max-widths, centering, content containers
    6. **Page templates**: Common page layouts (sidebar+content, full-width, split)
    7. **Component sizing**: Consistent sizing system for buttons, inputs, cards

    For each specification, provide:
    - Design token values (CSS custom properties)
    - Example CSS code
    - Migration notes from current patterns

    Write your specifications as a structured markdown document.
```

**Output file:** `.frontend-redesign/02-layout-spec.md`

Update `state.json`: set `current_phase` to "checkpoint-1", add phase 2 to `completed_phases`.

---

## PHASE CHECKPOINT 1 -- User Approval Required

Display a summary of the UX audit and layout specifications:

```
Phases 1-2 complete: UX audit and layout system designed.

UX Audit:
- Critical issues: [count]
- Components to refactor: [count]
- Accessibility gaps: [count]

Layout System:
- Grid: [type]
- Spacing scale: [base unit]
- Breakpoints: [count]

Please review:
- .frontend-redesign/01-ux-audit.md
- .frontend-redesign/02-layout-spec.md

1. Continue -- implement the designs
2. Revise -- adjust UX or layout decisions before implementing
3. Pause -- save progress and stop here
```

Do NOT proceed to Phase 3 until the user approves.

---

## Phase 3: Implement Designs

Read `.frontend-redesign/01-ux-audit.md` and `.frontend-redesign/02-layout-spec.md` for the approved designs.

Use the frontend-design skill process to implement:

### Step 3A: Design tokens & foundation

- Create or update design token files (CSS custom properties or theme config)
- Implement spacing scale, typography scale, color tokens
- Set up layout grid utilities

### Step 3B: Component refactoring

Working through the UX audit's component refactoring plan:
- Refactor god components into focused components
- Implement missing abstractions
- Add proper state handling (empty, loading, error)
- Fix accessibility issues (semantic HTML, ARIA, keyboard nav)

### Step 3C: Layout implementation

Following the layout spec:
- Apply grid system to page templates
- Implement responsive breakpoints
- Apply consistent spacing tokens
- Fix typography scale

### Step 3D: User flow improvements

From the UX audit:
- Fix navigation dead ends
- Add missing feedback (loading indicators, success/error states)
- Improve information hierarchy

Log all changes to `.frontend-redesign/03-implementation-log.md`:

```markdown
# Phase 3: Implementation Log

## Design Tokens Created/Updated
[List of token files and values]

## Components Refactored
[List of components with changes made]

## Layout Changes
[Grid, spacing, responsive changes]

## User Flow Improvements
[Navigation, feedback, hierarchy changes]

## Files Modified
[Complete list of modified files]
```

Update `state.json`: set `current_phase` to 4, add phase 3 to `completed_phases`.

---

## Phase 4: React Performance Optimization

**Skip if:** `--skip-performance` flag is set. If skipped, proceed to Phase 5.

Read `.frontend-redesign/03-implementation-log.md` for context on what changed.

```
Task:
  subagent_type: "react-performance-optimizer"
  description: "React performance optimization after redesign"
  prompt: |
    Optimize the React performance of this frontend after a major redesign.

    ## Scope
    [Insert contents of .frontend-redesign/00-scope.md]

    ## Implementation Context
    [Insert summary of changes from .frontend-redesign/03-implementation-log.md]

    ## Instructions
    Analyze and optimize:
    1. **Re-render audit**: Identify components that re-render unnecessarily after the redesign
    2. **Memoization**: Add React.memo, useMemo, useCallback where needed
    3. **Code splitting**: Verify lazy loading is in place for new/refactored components
    4. **State management**: Check for unnecessary context re-renders from new token system
    5. **Bundle impact**: Did the redesign increase bundle size? Optimize if so
    6. **CSS performance**: New animations GPU-accelerated? Layout-triggering properties?
    7. **Hydration**: If SSR, check hydration mismatch risks from new components

    For each optimization:
    - What was the problem
    - What you changed
    - Expected performance impact

    Apply the optimizations directly to the code. Run tests to verify nothing breaks.

    Write your findings and changes as a structured markdown document.
```

**Output file:** `.frontend-redesign/04-performance.md`

Update `state.json`: set `current_phase` to 5, add phase 4 to `completed_phases`.

---

## Phase 5: UI Polish & Micro-interactions

Read `.frontend-redesign/03-implementation-log.md` and `.frontend-redesign/04-performance.md` (if exists) for context.

```
Task:
  subagent_type: "ui-polisher"
  description: "UI polish and micro-interactions for redesigned frontend"
  prompt: |
    Add visual polish and micro-interactions to this redesigned frontend.

    ## Scope
    [Insert contents of .frontend-redesign/00-scope.md]

    ## Implementation Context
    [Insert summary from .frontend-redesign/03-implementation-log.md]

    ## Performance Context
    [Insert summary from .frontend-redesign/04-performance.md if exists, noting any animation constraints]

    ## Instructions
    Polish and enhance:
    1. **Transitions**: Smooth page transitions, component mount/unmount animations
    2. **Hover & focus states**: Consistent interactive feedback on all clickable elements
    3. **Loading animations**: Skeleton screens, spinners, progress bars where needed
    4. **Micro-interactions**: Button press feedback, form validation animations, success states
    5. **Motion system**: Consistent easing curves, duration scale, spring parameters
    6. **Dark mode**: If supported, verify all new components adapt properly
    7. **Reduced motion**: Respect prefers-reduced-motion for all animations
    8. **Empty states**: Beautiful empty state illustrations/messages where needed
    9. **Error states**: Friendly error messages with recovery actions

    Apply changes directly. Use GPU-accelerated properties (transform, opacity) for animations.
    Run tests to verify nothing breaks.

    Write your changes as a structured markdown document.
```

**Output file:** `.frontend-redesign/05-polish-log.md`

Update `state.json`: set `current_phase` to "checkpoint-2", add phase 5 to `completed_phases`.

---

## PHASE CHECKPOINT 2 -- User Approval Required

```
Phases 3-5 complete: Implementation, performance, and polish done.

Summary:
- Components refactored: [count]
- Layout changes: [count]
- Performance optimizations: [count]
- Polish additions: [count]

Please review:
- .frontend-redesign/03-implementation-log.md
- .frontend-redesign/04-performance.md
- .frontend-redesign/05-polish-log.md

1. Continue -- run the final design audit and generate HTML report
2. Adjust -- make changes before the audit
3. Pause -- save progress and stop here
```

Do NOT proceed to Phase 6 until the user approves.

---

## Phase 6: Final Design Audit & HTML Report

Read all `.frontend-redesign/*.md` files for full context.

Re-read the modified frontend files to assess the final state.

Run all three audit agents **in parallel** in a single response:

### Agent A: UX Patterns & Component Architecture

```
Task:
  subagent_type: "ui-ux-designer"
  description: "Final UX audit of redesigned frontend"
  prompt: |
    Perform a final UX audit of the redesigned frontend.

    ## Scope
    [List of key files after redesign]

    ## File Contents
    [Paste sampled component and layout file contents — the CURRENT state after all changes]

    ## Instructions
    Evaluate the redesigned frontend:
    1. Component responsibility — are god components resolved?
    2. UX patterns — consistent interaction patterns?
    3. Empty/loading/error states — all three handled everywhere?
    4. Information hierarchy — visual hierarchy consistent?
    5. User flows — dead ends fixed? Feedback present?
    6. Design system adherence — tokens used consistently?
    7. Accessibility — semantic HTML, ARIA, keyboard nav, contrast?

    For each finding: severity (Critical/High/Medium/Low), file, issue, specific fix.
    Note what's working well.

    Return structured JSON:
    ```json
    {
      "findings": [
        { "severity": "...", "category": "...", "file": "...", "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "ux_consistency": N, "accessibility": N, "component_design": N, "overall": N }
    }
    ```
```

### Agent B: Layout System & Spatial Design

```
Task:
  subagent_type: "ui-layout-designer"
  description: "Final layout audit of redesigned frontend"
  prompt: |
    Audit the layout system of the redesigned frontend.

    ## Scope
    [List of key files after redesign]

    ## File Contents
    [Paste sampled layout and stylesheet file contents — CURRENT state]

    ## Instructions
    Evaluate:
    1. Layout system — consistent grid/layout pattern?
    2. Spacing scale — derived from consistent scale?
    3. Responsive strategy — breakpoints consistent? No layout shifts?
    4. Typography system — font scale as tokens?
    5. Alignment & rhythm — baseline alignment, vertical rhythm?
    6. Container strategy — max-widths, centering consistent?

    For each finding: severity, file, issue, specific fix.
    Note what's done well.

    Return structured JSON:
    ```json
    {
      "findings": [
        { "severity": "...", "category": "...", "file": "...", "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "layout_system": N, "responsive": N, "typography": N, "overall": N }
    }
    ```
```

### Agent C: CSS Architecture & Visual Polish

```
Task:
  subagent_type: "ui-polisher"
  description: "Final CSS and polish audit of redesigned frontend"
  prompt: |
    Audit the CSS architecture and visual polish of the redesigned frontend.

    ## Scope
    [List of key files after redesign]

    ## File Contents
    [Paste sampled stylesheet and component file contents — CURRENT state]

    ## Instructions
    Evaluate:
    1. CSS architecture — global pollution, specificity, !important abuse?
    2. Modern CSS — custom properties, container queries, logical properties?
    3. Animation quality — smooth transitions, GPU-accelerated, reduced-motion respected?
    4. Visual consistency — border-radius, shadows, colors consistent?
    5. Dark mode — properly adapted?
    6. CSS performance — unnecessary repaints, layout-triggering animations?
    7. Dead CSS — unused selectors, legacy overrides?
    8. Component isolation — styles scoped properly?

    For each finding: severity, file, issue, specific fix.
    Note what's done well.

    Return structured JSON:
    ```json
    {
      "findings": [
        { "severity": "...", "category": "...", "file": "...", "issue": "...", "fix": "..." }
      ],
      "positives": ["..."],
      "score": { "css_architecture": N, "visual_polish": N, "animations": N, "overall": N }
    }
    ```
```

### Generate HTML Report

After all agents complete, create `.frontend-redesign/report.html` — a self-contained visual dashboard.

Use this exact HTML template and design system:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Frontend Redesign Audit — [date]</title>
  <style>
    :root {
      --c-bg: #0f1117;
      --c-surface: #1a1d27;
      --c-surface-2: #22263a;
      --c-border: #2a2d3a;
      --c-text: #e2e8f0;
      --c-muted: #8892a4;
      --c-critical: #ef4444;
      --c-high: #f97316;
      --c-medium: #eab308;
      --c-low: #3b82f6;
      --c-good: #22c55e;
      --c-accent: #8b5cf6;
      --c-ux: #06b6d4;
      --c-layout: #f59e0b;
      --c-css: #ec4899;
      --radius: 10px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: var(--c-bg);
      color: var(--c-text);
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 14px;
      line-height: 1.6;
      padding: 40px 28px;
      max-width: 1020px;
      margin: 0 auto;
    }

    header { margin-bottom: 36px; }
    header h1 { font-size: 26px; font-weight: 800; color: #fff; letter-spacing: -.02em; }
    .subtitle { color: var(--c-muted); margin-top: 6px; font-size: 13px; }
    .tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; }
    .tag {
      font-size: 11px; padding: 3px 9px; border-radius: 99px;
      border: 1px solid var(--c-border); background: var(--c-surface); color: var(--c-muted);
      font-family: monospace;
    }

    .legend { display: flex; gap: 20px; margin-bottom: 28px; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--c-muted); }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; }

    .scores {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 14px;
      margin-bottom: 36px;
    }
    .score-card {
      background: var(--c-surface);
      border: 1px solid var(--c-border);
      border-radius: var(--radius);
      padding: 22px 18px 18px;
      text-align: center;
      position: relative;
      overflow: hidden;
    }
    .score-card::before {
      content: '';
      position: absolute; top: 0; left: 0; right: 0;
      height: 3px;
    }
    .score-card.cat-ux::before     { background: var(--c-ux); }
    .score-card.cat-layout::before { background: var(--c-layout); }
    .score-card.cat-css::before    { background: var(--c-css); }
    .score-card.cat-overall::before { background: var(--c-accent); }
    .score-card .label { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--c-muted); margin-bottom: 10px; }
    .score-card .value { font-size: 42px; font-weight: 900; line-height: 1; }
    .score-card .sub  { font-size: 12px; color: var(--c-muted); margin-top: 4px; }
    .score-card .gauge { margin-top: 12px; height: 5px; border-radius: 99px; background: var(--c-border); overflow: hidden; }
    .score-card .gauge-fill { height: 100%; border-radius: 99px; }
    .score-good   .value, .score-good   .gauge-fill { color: var(--c-good);     background: var(--c-good); }
    .score-mid    .value, .score-mid    .gauge-fill { color: var(--c-medium);   background: var(--c-medium); }
    .score-bad    .value, .score-bad    .gauge-fill { color: var(--c-critical); background: var(--c-critical); }
    .cat-overall .value { color: #c4b5fd; }
    .cat-overall .gauge-fill { background: var(--c-accent); }

    .pillrow { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
    .pill {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 5px 14px; border-radius: 99px;
      font-size: 13px; font-weight: 600;
    }
    .pill.critical { background: rgba(239,68,68,.12); color: var(--c-critical); border: 1px solid rgba(239,68,68,.3); }
    .pill.high     { background: rgba(249,115,22,.12); color: var(--c-high);     border: 1px solid rgba(249,115,22,.3); }
    .pill.medium   { background: rgba(234,179,8,.12);  color: var(--c-medium);   border: 1px solid rgba(234,179,8,.3); }
    .pill.low      { background: rgba(59,130,246,.12); color: var(--c-low);      border: 1px solid rgba(59,130,246,.3); }

    .tabs { display: flex; gap: 2px; margin-bottom: 20px; border-bottom: 1px solid var(--c-border); }
    .tab {
      padding: 8px 16px; font-size: 13px; font-weight: 500; cursor: pointer;
      color: var(--c-muted); border-bottom: 2px solid transparent;
      background: none; border-top: none; border-left: none; border-right: none;
      margin-bottom: -1px; transition: color .15s;
    }
    .tab.active { color: #fff; border-bottom-color: var(--c-accent); }

    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .section { margin-bottom: 28px; }
    .section-title {
      font-size: 14px; font-weight: 600; color: var(--c-muted);
      text-transform: uppercase; letter-spacing: .06em;
      margin-bottom: 12px;
      display: flex; align-items: center; gap: 8px;
    }
    .section-title .cnt {
      font-size: 12px; font-weight: 500; color: var(--c-muted);
      background: var(--c-surface); border: 1px solid var(--c-border);
      border-radius: 99px; padding: 1px 8px;
    }

    .finding {
      background: var(--c-surface);
      border: 1px solid var(--c-border);
      border-left: 3px solid transparent;
      border-radius: var(--radius);
      padding: 14px 16px;
      margin-bottom: 10px;
    }
    .finding.critical { border-left-color: var(--c-critical); }
    .finding.high     { border-left-color: var(--c-high); }
    .finding.medium   { border-left-color: var(--c-medium); }
    .finding.low      { border-left-color: var(--c-low); }

    .finding-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
    .badge {
      font-size: 10px; font-weight: 700; padding: 2px 7px;
      border-radius: 4px; text-transform: uppercase; letter-spacing: .05em;
    }
    .badge.critical { background: rgba(239,68,68,.15); color: var(--c-critical); }
    .badge.high     { background: rgba(249,115,22,.15); color: var(--c-high); }
    .badge.medium   { background: rgba(234,179,8,.15);  color: var(--c-medium); }
    .badge.low      { background: rgba(59,130,246,.15); color: var(--c-low); }
    .badge.cat-ux     { background: rgba(6,182,212,.1);   color: #67e8f9; }
    .badge.cat-layout { background: rgba(245,158,11,.1);  color: #fcd34d; }
    .badge.cat-css    { background: rgba(236,72,153,.1);  color: #f9a8d4; }

    .file-ref { font-family: monospace; font-size: 11px; color: var(--c-muted); }
    .finding-text { color: var(--c-text); margin-bottom: 8px; }
    .fix-box {
      background: rgba(34,197,94,.07);
      border: 1px solid rgba(34,197,94,.18);
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 12px; color: #86efac;
    }
    .fix-box b { font-weight: 600; }

    .positives-box {
      background: rgba(34,197,94,.05);
      border: 1px solid rgba(34,197,94,.18);
      border-radius: var(--radius);
      padding: 20px;
      margin-bottom: 28px;
    }
    .positives-box h3 { color: var(--c-good); font-size: 14px; font-weight: 600; margin-bottom: 10px; }
    .positives-box ul { padding-left: 18px; }
    .positives-box li { color: #bbf7d0; margin-bottom: 4px; }

    .action-plan {
      background: var(--c-surface);
      border: 1px solid var(--c-border);
      border-radius: var(--radius);
      padding: 20px;
      margin-bottom: 36px;
    }
    .action-plan h3 { font-size: 15px; font-weight: 600; margin-bottom: 14px; }
    .action-item {
      display: flex; gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid var(--c-border);
    }
    .action-item:last-child { border-bottom: none; padding-bottom: 0; }
    .action-num {
      flex-shrink: 0;
      width: 24px; height: 24px; border-radius: 50%;
      background: var(--c-accent); color: #fff;
      font-size: 12px; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
    }
    .action-text { font-size: 13px; }

    /* REDESIGN-SPECIFIC: Before/After comparison */
    .comparison {
      background: var(--c-surface);
      border: 1px solid var(--c-border);
      border-radius: var(--radius);
      padding: 20px;
      margin-bottom: 28px;
    }
    .comparison h3 { font-size: 15px; font-weight: 600; margin-bottom: 14px; }
    .comparison-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .comparison-col h4 { font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: var(--c-muted); margin-bottom: 8px; }
    .comparison-col.before { border-right: 1px solid var(--c-border); padding-right: 16px; }
    .comparison-item { font-size: 13px; margin-bottom: 6px; }
    .comparison-item .old { color: var(--c-critical); text-decoration: line-through; }
    .comparison-item .new { color: var(--c-good); }

    footer {
      border-top: 1px solid var(--c-border);
      padding-top: 18px;
      font-size: 11px; color: var(--c-muted);
    }

    @media print {
      body { background: #fff; color: #111; }
      .finding, .score-card { border-color: #ccc; }
      .tab-content { display: block !important; }
      .tabs { display: none; }
    }
  </style>
  <script>
    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).classList.add('active');
      btn.classList.add('active');
    }
  </script>
</head>
<body>

<header>
  <h1>Frontend Redesign Audit</h1>
  <div class="subtitle">Full redesign pipeline audit · [DATE] · [N] components · [M] stylesheets</div>
  <div class="tag-row">
    <!-- one .tag per key scanned directory/file -->
  </div>
</header>

<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:var(--c-ux)"></div> UX & Components</div>
  <div class="legend-item"><div class="legend-dot" style="background:var(--c-layout)"></div> Layout & Spacing</div>
  <div class="legend-item"><div class="legend-dot" style="background:var(--c-css)"></div> CSS Architecture</div>
</div>

<!-- SCORES -->
<div class="scores">
  <!-- Populate: score-good for 8-10, score-mid for 5-7, score-bad for 1-4 -->
  <!-- Categories: UX Quality, Layout System, CSS Architecture, Accessibility, Typography, Overall -->
</div>

<!-- SEVERITY SUMMARY -->
<div class="pillrow">
  <span class="pill critical">● X Critical</span>
  <span class="pill high">● X High</span>
  <span class="pill medium">● X Medium</span>
  <span class="pill low">● X Low</span>
</div>

<!-- BEFORE/AFTER COMPARISON -->
<div class="comparison">
  <h3>Before vs After Redesign</h3>
  <div class="comparison-grid">
    <div class="comparison-col before">
      <h4>Before</h4>
      <!-- Key metrics/issues from Phase 1 audit -->
    </div>
    <div class="comparison-col">
      <h4>After</h4>
      <!-- Improvements from Phases 3-5 -->
    </div>
  </div>
</div>

<!-- TABBED FINDINGS -->
<div class="tabs">
  <button class="tab active" onclick="switchTab('tab-all', this)">All Findings</button>
  <button class="tab" onclick="switchTab('tab-ux', this)">UX & Components</button>
  <button class="tab" onclick="switchTab('tab-layout', this)">Layout & Spacing</button>
  <button class="tab" onclick="switchTab('tab-css', this)">CSS Architecture</button>
</div>

<div id="tab-all" class="tab-content active">
  <!-- All findings from all agents, organized by severity -->
</div>

<div id="tab-ux" class="tab-content">
  <!-- UX-only findings -->
</div>

<div id="tab-layout" class="tab-content">
  <!-- Layout-only findings -->
</div>

<div id="tab-css" class="tab-content">
  <!-- CSS-only findings -->
</div>

<!-- POSITIVES -->
<div class="positives-box">
  <h3>What's Working Well</h3>
  <ul>
    <!-- Positives from all agents -->
  </ul>
</div>

<!-- ACTION PLAN -->
<div class="action-plan">
  <h3>Remaining Action Items</h3>
  <!-- Top 5 remaining improvements from the audit -->
</div>

<footer>
  Generated by /frontend-redesign · workflows plugin · [TIMESTAMP]
</footer>

</body>
</html>
```

**Populate the report:**
- Score classes: `score-good` for 8-10, `score-mid` for 5-7, `score-bad` for 1-4
- Category badge classes: `cat-ux`, `cat-layout`, `cat-css`
- Comparison section: key before/after metrics from Phase 1 vs Phase 6 audits
- Tab sections: duplicate relevant findings into each tab
- Action plan: ordered list of top 5 remaining improvements

**Open the file:**

```bash
start .frontend-redesign/report.html     # Windows
open .frontend-redesign/report.html      # macOS
xdg-open .frontend-redesign/report.html  # Linux
```

Update `state.json`: set `status` to `"complete"`, `last_updated` to current timestamp.

---

## Completion

Print a short summary:

```
Frontend redesign pipeline complete for: $ARGUMENTS

## Output Files
- Scope: .frontend-redesign/00-scope.md
- UX Audit: .frontend-redesign/01-ux-audit.md
- Layout Spec: .frontend-redesign/02-layout-spec.md
- Implementation Log: .frontend-redesign/03-implementation-log.md
- Performance: .frontend-redesign/04-performance.md
- Polish Log: .frontend-redesign/05-polish-log.md
- HTML Report: .frontend-redesign/report.html

## Summary
Overall Score: X/10
UX: X/10 | Layout: X/10 | CSS: X/10 | Accessibility: X/10

Critical: X | High: X | Medium: X | Low: X

Top 3 remaining issues:
1. [issue summary]
2. [issue summary]
3. [issue summary]
```

If `--strict-mode` is set and Critical findings exist:
```
STRICT MODE: Critical design issues remain after redesign. Recommend addressing before shipping.
```
