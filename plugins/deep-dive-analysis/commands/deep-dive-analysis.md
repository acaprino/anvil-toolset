---
description: "Systematic codebase analysis combining structure extraction with semantic understanding — documents WHAT, WHY, HOW, and CONSEQUENCES of code with phased output"
argument-hint: "<target path> [--critical] [--comments] [--docs-only] [--phase N]"
---

# Deep Dive Analysis

## CRITICAL RULES

1. **Execute phases in order.** Unless `--phase N` skips to a specific phase.
2. **Write output files.** Each phase produces a file in `.deep-dive/` for context passing.
3. **Stop at checkpoints.** Confirm scope before starting analysis and before applying changes.
4. **Never enter plan mode.** Execute immediately.
5. **Code is ground truth.** Document what the code actually does, not what you think it should do.

## Pre-flight

### 1. Check for existing session

Check if `.deep-dive/state.json` exists:
- If in progress: offer to resume or start fresh
- If complete: offer to archive and start fresh

### 2. Initialize state

Create `.deep-dive/` directory and `state.json`:

```json
{
  "target": "$ARGUMENTS",
  "status": "in_progress",
  "flags": {
    "critical": false,
    "comments": false,
    "docs_only": false,
    "phase": null
  },
  "current_phase": 1,
  "completed_phases": [],
  "files_created": [],
  "started_at": "ISO_TIMESTAMP"
}
```

Parse flags: `--critical` (prioritize high-risk code), `--comments` (comment quality mode), `--docs-only` (documentation health only, skip to Phase 6), `--phase N` (start at phase N).

### 3. Confirm scope

Scan the target and present:

```
Deep dive target: [path]
Files to analyze: [count] ([language breakdown])
Flags: [active flags]

Analysis phases:
1. Structure Extraction — file inventory, dependency graph
2. Interface Analysis — public APIs, contracts, exports
3. Flow Tracing — data flow, control flow, critical paths
4. Semantic Understanding — WHY code exists, design decisions
5. Pattern & Risk Detection — anti-patterns, red flags, tech debt
6. Documentation Health — existing docs accuracy, gaps
7. Final Report — consolidated findings

1. Proceed with full analysis
2. Analyze specific phase only (--phase N)
3. Quick scan (phases 1-2 only)
4. Cancel
```

---

## Phase 1: Structure Extraction

Scan all files in the target and build a structural map.

For each file, extract:
- Module/file name and path
- Language and framework
- Imports and dependencies
- Exported symbols (functions, classes, constants)
- File size and complexity indicators (line count, function count)

**Output file:** `.deep-dive/01-structure.md`

```markdown
# Phase 1: Structure Extraction

## File Inventory
| File | Language | Lines | Functions | Classes | Imports |
|------|----------|-------|-----------|---------|---------|
| ... | ... | ... | ... | ... | ... |

## Dependency Graph
[Mermaid diagram of module dependencies]

## Entry Points
[Main files, API routes, CLI handlers]

## Key Observations
[Notable structural patterns or concerns]
```

Update `state.json`: add phase 1 to `completed_phases`.

---

## Phase 2: Interface Analysis

For each module, document the public interface:

- Function signatures with parameter types and return types
- Class hierarchies and method signatures
- API endpoints with request/response shapes
- Configuration interfaces
- Event/signal contracts

**Output file:** `.deep-dive/02-interfaces.md`

```markdown
# Phase 2: Interface Analysis

## Public APIs
[Organized by module]

## Contracts
[Interface definitions, type shapes, schemas]

## External Dependencies
[Third-party libraries and how they're used]
```

---

## Phase 3: Flow Tracing

Trace critical execution paths through the codebase:

- Request lifecycle (entry → processing → response)
- Data transformation pipeline (input → validation → processing → output)
- Error propagation paths (where errors originate, how they're handled)
- State mutation flows (what changes state, side effects)

If `--critical` flag is set, prioritize:
- Authentication/authorization flows
- Payment/transaction flows
- Data persistence flows

**Output file:** `.deep-dive/03-flows.md`

```markdown
# Phase 3: Flow Tracing

## Critical Paths
[Step-by-step flow descriptions with file:line references]

## Data Flow
[How data transforms through the system]

## Error Handling Paths
[Where errors originate and how they propagate]

## Side Effects
[Functions with side effects and their blast radius]
```

---

## Phase 4: Semantic Understanding

This is the AI-powered phase — understand the **WHY** behind the code:

- Business purpose of each module
- Design decisions and trade-offs (inferred from code patterns)
- Historical context (from git blame and commit messages)
- Assumptions embedded in the code
- Implicit contracts not documented anywhere

**Output file:** `.deep-dive/04-semantics.md`

```markdown
# Phase 4: Semantic Understanding

## Module Purposes
[WHY each module exists, not just WHAT it does]

## Design Decisions
[Inferred decisions and their trade-offs]

## Embedded Assumptions
[Assumptions the code makes that aren't documented]

## Hidden Contracts
[Implicit agreements between modules]
```

---

## Phase 5: Pattern & Risk Detection

Scan for anti-patterns, red flags, and technical debt:

- **Anti-patterns**: God objects, spaghetti code, shotgun surgery, feature envy
- **Red flags**: Swallowed exceptions, hardcoded credentials, race conditions, N+1 queries
- **Technical debt**: TODO/FIXME comments, deprecated APIs, outdated patterns
- **Failure modes**: What breaks under load, edge cases, missing error handling

**Output file:** `.deep-dive/05-risks.md`

```markdown
# Phase 5: Pattern & Risk Detection

## Anti-Patterns Found
[Organized by severity]

## Red Flags
[Security, reliability, and performance risks]

## Technical Debt Inventory
[TODO/FIXME items, deprecated usage, modernization opportunities]

## Failure Mode Analysis
[What could break and under what conditions]
```

---

## Phase 6: Documentation Health

Evaluate existing documentation against the code reality:

- **Accuracy**: Do docs match the actual code?
- **Completeness**: What's documented vs what should be?
- **Freshness**: When were docs last updated vs code?
- **Broken links**: References to files/functions that don't exist
- **Comment quality**: Using antirez standards (if `--comments` flag)

If `--comments` flag is set, also analyze comment quality:
- Identify trivial/debt/backup comments
- Score comment usefulness
- Suggest rewrites following antirez standards

**Output file:** `.deep-dive/06-documentation.md`

```markdown
# Phase 6: Documentation Health

## Documentation vs Code Accuracy
[Mismatches between docs and reality]

## Coverage Gaps
[Undocumented public APIs, missing architecture docs]

## Broken References
[Dead links, non-existent file paths in docs]

## Comment Quality [if --comments]
[Comment audit with improvement suggestions]
```

---

## Phase 7: Final Report

Read all `.deep-dive/*.md` files (01 through 06) and generate the consolidated report.

**Output file:** `.deep-dive/07-final-report.md`

```markdown
# Deep Dive Analysis Report

## Target
[From scope]

## Executive Summary
[2-3 sentences on overall codebase health]

## Architecture Overview
[Mermaid diagram + narrative from Phases 1-2]

## Critical Paths
[Key findings from Phase 3]

## Design Insights
[Key findings from Phase 4]

## Risk Assessment
| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Anti-patterns | X | X | X | X |
| Security risks | X | X | X | X |
| Technical debt | X | X | X | X |
| Doc gaps | X | X | X | X |

## Top Priority Actions
1. [Most important fix/improvement]
2. [Second priority]
3. [Third priority]

## Detailed Findings
[Cross-references to phase files for full details]

## Analysis Metadata
- Target: [path]
- Files analyzed: [count]
- Phases completed: [list]
- Date: [timestamp]
```

Update `state.json`: set `status` to `"complete"`.

---

## Completion

```
Deep dive analysis complete for: $ARGUMENTS

Output Files:
- Structure: .deep-dive/01-structure.md
- Interfaces: .deep-dive/02-interfaces.md
- Flows: .deep-dive/03-flows.md
- Semantics: .deep-dive/04-semantics.md
- Risks: .deep-dive/05-risks.md
- Documentation: .deep-dive/06-documentation.md
- Final Report: .deep-dive/07-final-report.md

Summary:
- Files analyzed: [count]
- Anti-patterns: [count] | Red flags: [count] | Tech debt items: [count]
- Documentation gaps: [count]

Start with the final report: .deep-dive/07-final-report.md
```

## Quick Examples

- `/deep-dive-analysis src/` — Full 7-phase analysis
- `/deep-dive-analysis src/auth/ --critical` — Prioritize security-critical code
- `/deep-dive-analysis src/ --docs-only` — Documentation health check only
- `/deep-dive-analysis src/ --comments` — Include comment quality audit
- `/deep-dive-analysis src/ --phase 5` — Jump to pattern & risk detection
