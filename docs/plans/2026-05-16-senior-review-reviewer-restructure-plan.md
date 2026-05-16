# Senior-Review Reviewers — Restructure Plan

**Date:** 2026-05-16
**Design doc:** [`2026-05-16-senior-review-reviewer-restructure-design.md`](2026-05-16-senior-review-reviewer-restructure-design.md)
**Status:** Ready to apply.

## Approach: unify the 5 gaps into one section

Instead of 5 separate edits per reviewer × 9 reviewers = 45 small edits, collapse the cross-cutting additions into a single `## Pipeline Conventions` section inserted **immediately before** the existing `## Output Persistence` section (added in the previous turn).

This keeps the agent body coherent: pipeline-related rules live next to each other at the bottom, leaving the dimension-specific analysis methodology untouched at the top.

## The `Pipeline Conventions` template

Two variants depending on the reviewer.

### Variant A: standard (8 reviewers)

Applied to: `security-auditor`, `code-auditor`, `ui-race-auditor`, `chicken-egg-detector`, `distributed-flow-auditor`, `cleanup-auditor`, `react-performance-optimizer`, `platform-reviewer`.

```markdown
## Pipeline Conventions

When invoked as part of a multi-reviewer pipeline (e.g., `/agent-teams:team-review` Phase 2), follow these conventions in addition to the dimension-specific rules above.

**Scope budget.** If after ~15 file reads you have not surfaced a finding in your dimension, the scope is too broad or your dimension is not relevant to this target. Stop, output a "no findings -- scope appears off-topic for this dimension" report, and return. Do not invent findings to fill space.

**No-findings protocol.** If your dimension genuinely has no findings on this target, output a one-line report stating so plus a list of what you examined. Reporting "examined X, Y, Z -- no issues" is a valid, useful result.

**Cross-reviewer notes.** If during analysis you spot an issue clearly belonging to another reviewer's dimension, list it in a `## Cross-Reviewer Notes` section at the end of your output with `file:line` and a one-line description. Phase 3 consolidation routes these to the appropriate reviewer.

**Interconnect anchor citation.** When a finding maps to a contract, invariant, or assumption documented in `.team-review/02-interconnect.md`, cite the map anchor (e.g., "Map anchor: ## Contracts -> Order-fulfillment idempotency"). Findings that cite map anchors are tracked as a quality metric.
```

### Variant B: logic-integrity-auditor only

The interconnect anchor citation is already mandated in this agent's body in a stricter form (every finding must cite an anchor). Omit that paragraph to avoid contradiction.

```markdown
## Pipeline Conventions

When invoked as part of a multi-reviewer pipeline (e.g., `/agent-teams:team-review` Phase 2), follow these conventions in addition to the dimension-specific rules above.

**Scope budget.** If after ~15 file reads you have not surfaced a finding in your dimension, the scope is too broad or your dimension is not relevant to this target. Stop, output a "no findings -- scope appears off-topic for this dimension" report, and return. Do not invent findings to fill space.

**No-findings protocol.** If your dimension genuinely has no findings on this target, output a one-line report stating so plus a list of what you examined. Reporting "examined X, Y, Z -- no issues" is a valid, useful result.

**Cross-reviewer notes.** If during analysis you spot an issue clearly belonging to another reviewer's dimension, list it in a `## Cross-Reviewer Notes` section at the end of your output with `file:line` and a one-line description. Phase 3 consolidation routes these to the appropriate reviewer.
```

## Tools allowlist hygiene (Gap 5)

Seven reviewers currently omit `tools:` from frontmatter, which means they inherit all tools. Add explicit `tools: Read, Write, Glob, Grep, Bash` to match the security posture of the three reviewers we standardized in the previous turn (cleanup-auditor, platform-reviewer, team-reviewer).

Affected:

- `security-auditor.md`
- `code-auditor.md`
- `logic-integrity-auditor.md`
- `ui-race-auditor.md`
- `chicken-egg-detector.md`
- `distributed-flow-auditor.md`
- `react-performance-optimizer.md`

The other 2 reviewers in scope (`cleanup-auditor`, `platform-reviewer`) already have explicit tools and need no frontmatter change.

## team-reviewer note

`team-reviewer.md` lives in the `agent-teams` plugin and already received `Scope Budget` + `Cross-Reviewer Notes` in the previous commit. The remaining two gaps (No-Findings Protocol, Interconnect Anchor Citation) are partially covered by existing Behavioral Traits and the lead's deduplication step, so we accept the small inconsistency rather than re-bumping `agent-teams` in this commit.

## Insertion point

In every reviewer, the previous turn appended `## Output Persistence` as the last section. Replace the literal string `## Output Persistence` with the `Pipeline Conventions` block + a blank line + `## Output Persistence`. Single Edit per file.

## Version bumps

| Plugin | Before | After | Reason |
|---|---|---|---|
| `senior-review` | 5.6.1 | 5.7.0 | Minor: 7 reviewer agents touched (Pipeline Conventions + tools allowlist) |
| `react-development` | 1.9.3 | 1.9.4 | Patch: react-performance-optimizer touched |
| `platform-engineering` | 1.2.1 | 1.2.2 | Patch: platform-reviewer touched |
| Marketplace `metadata.version` | 6.8.3 | 6.8.4 | Patch: three plugins bumped |

## Validation

- Read each file end-to-end after the edit to confirm the new section sits cleanly between the existing body and the Output Persistence section.
- Validate `marketplace.json` JSON.
- `grep` for `## Pipeline Conventions` across the 9 affected files should return 9 hits.
- `grep` for `tools:` in the 7 affected reviewers should return the new allowlist.

## Commit message

```
Restructure 9 reviewer agents with Pipeline Conventions (senior-review v5.7.0)

Applies the design from
docs/plans/2026-05-16-senior-review-reviewer-restructure-design.md
to the 9 reviewers used by /agent-teams:team-review Phase 2 (excluding
team-reviewer which already received the scope/cross-reviewer rules
in the previous commit).

Each reviewer gains a "Pipeline Conventions" section grouping four
cross-cutting rules: scope budget (stop after ~15 file reads if no
finding), no-findings protocol (honest empty reports), cross-reviewer
notes (route off-dimension observations), and interconnect anchor
citation (cite map anchors when applicable). The logic-integrity-auditor
variant omits the interconnect anchor paragraph since its body already
mandates anchor citation in a stricter form.

Tools allowlist hygiene: seven reviewers without explicit tools
frontmatter get an explicit "Read, Write, Glob, Grep, Bash" allowlist,
matching the three reviewers already standardized in the previous turn.

Plan: docs/plans/2026-05-16-senior-review-reviewer-restructure-plan.md
Reference: docs/references/agent-teams-best-practices.md
```
