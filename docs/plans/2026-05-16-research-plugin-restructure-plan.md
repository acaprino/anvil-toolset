# Research Plugin — Restructure Plan

**Date:** 2026-05-16
**Design doc:** [`2026-05-16-research-plugin-restructure-design.md`](2026-05-16-research-plugin-restructure-design.md)
**Status:** Ready to apply.

## Diagnosis result

The design doc's H1 hypothesis is **confirmed by Anthropic documentation**:

> "Subagents cannot spawn other subagents. This prevents infinite nesting while still gathering necessary context."
> — [Create custom subagents (Claude Code Docs)](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

> "For multiagent coordination, the coordinator can only delegate to one level of agents; depth > 1 is ignored."

This is a **harness-level restriction**, not a system-prompt issue. When `deep-researcher` is itself spawned as a sub-agent (as happened in the previous turn), the `Agent` tool is not exposed at that level even though the frontmatter declares `tools: Agent, Read`. Fix 1 (explicit tool-call template) cannot help, because the tool is genuinely absent.

H2 (self-restriction) is a contributing factor: the agent's body could have detected the absent tool and switched to a fallback, but its body has no fallback path defined.

H3 (frontmatter-runtime mismatch) is **invalidated**: the runtime behavior matches the documented restriction.

## Selected fixes

| Fix | Apply | Rationale |
|---|---|---|
| Fix 1 (explicit Agent tool template) | NO | Tool is genuinely absent in nested case. Adding template does not unblock. |
| Fix 2 (WebSearch + WebFetch fallback / Direct mode) | YES | Only mechanism that lets the agent produce work in the nested case. |
| Fix 3 (structured failure response) | YES (light version) | For the case where Direct mode also runs out of budget; preserve diagnosability. |
| Fix 4 (quick-searcher metadata block) | YES | Cheap; helps orchestrator-mode synthesis distinguish complete vs partial sub-agent runs. |

## Edits

### `plugins/research/agents/deep-researcher.md`

**Frontmatter (line 7):**

```yaml
tools: Agent, Read
```

becomes

```yaml
tools: Agent, Read, WebSearch, WebFetch
```

**Body restructure** — replace lines 14-18 (current intro paragraph) and the "WORKFLOW" section (lines 38-89) with the dual-mode design. Key new structure:

1. Add new `# OPERATING MODES` section at the top of the body, after `# ROLE`, defining:

   ```
   # OPERATING MODES

   You operate in one of two modes, detected at the start of every invocation.

   ## Mode A: Orchestrator (preferred)

   You were invoked at the top level of the session (by the user or by a slash
   command). The `Agent` tool is in your toolset. Spawn parallel
   `research:quick-searcher` sub-agents, one per activated angle, then synthesize.

   ## Mode B: Direct (fallback)

   You were invoked as a sub-agent of another agent. Per Claude Agent SDK
   restrictions, sub-agents cannot spawn further sub-agents, so the `Agent` tool
   is not available at this level. Execute the activated angles yourself using
   `WebSearch` and `WebFetch`, with the same per-angle budget that would have
   gone to each sub-agent.

   ## Detection

   At the start of every invocation, check whether `Agent` is in your visible
   toolset. If yes, Mode A. If no, Mode B. State which mode you are operating in
   as the first line of your final report.
   ```

2. Rename `# WORKFLOW` to `# WORKFLOW (Mode A: Orchestrator)` and keep its content largely as-is, except:
   - **Phase 2** is rewritten to include the explicit Agent-tool call template (see Design Fix 1; useful even if not strictly required, as a quality-of-life clarification):

     ```
     ## Phase 2: Spawn sub-agents in parallel (Mode A only)

     Use the `Agent` tool with `subagent_type: "research:quick-searcher"`.
     Launch all activated angles in a single message with multiple Agent tool
     calls so they run concurrently. Each spawn prompt follows the template
     below.
     ```

3. Add `# WORKFLOW (Mode B: Direct)` as a parallel section:

   ```
   # WORKFLOW (Mode B: Direct)

   ## Phase 1: Classify (same as Mode A)

   ## Phase 2: Execute angles yourself

   For each activated angle, run the angle yourself:
   - Budget per angle: 5 WebSearch + 3 WebFetch + 1 round (same as a
     quick-searcher sub-agent would have)
   - Hard cap on total: do not exceed the per-angle budget × number of angles.
     If you find yourself wanting a second round, stop and accept partial findings.
   - Capture results in the same `## Findings for angle [X]` format that
     quick-searcher would have produced, so Phase 3 synthesis is identical
     across modes.

   Run all angles serially in Mode B (the harness does not let you parallelize
   web calls across distinct angle contexts the way sub-agents would).

   ## Phase 3: Synthesize (same as Mode A)
   ```

4. Add `# FAILURE RESPONSE` section near the bottom:

   ```
   # FAILURE RESPONSE

   If you cannot complete the research in either mode, return exactly:

   ## Research failed
   - Mode attempted: A | B
   - Reason: <one line>
   - Tools available: <list>
   - Recommended fallback: invoke `research:quick-searcher` directly from the
     calling agent, or use `WebSearch` inline.

   Do not return a long apology. The caller needs a structured signal to
   decide whether to retry or escalate.
   ```

5. Update the `# OUTPUT TEMPLATE` section to require the first line of the
   final report to be `**Operating mode**: A | B`. This lets the caller see
   immediately whether sub-agent parallelism was achieved or whether the
   results came from a serial Direct-mode pass.

### `plugins/research/agents/quick-searcher.md`

**No frontmatter changes.**

**Body change** — extend the sub-unit-mode output format (lines 50-63) to include a metadata block:

```
## Sub-unit metadata
- Budget assigned: <as received>
- Budget used: ~N WebSearch + M WebFetch
- Exit reason: completed | budget-exhausted | target-not-found
```

This is non-load-bearing but makes orchestrator-mode synthesis more honest about partial coverage.

## Version bumps

| Plugin | Before | After | Reason |
|---|---|---|---|
| `research` | 2.6.1 | 2.7.0 | Minor: new fallback mode + new tools in deep-researcher |
| Marketplace `metadata.version` | 6.8.1 | 6.8.2 | Patch: one plugin bumped, no global API change |

## Validation

Markdown-only repo, no automated tests. Validation steps after applying:

1. Visually verify the rewritten `deep-researcher.md` reads cleanly and each phase still references the same `OUTPUT TEMPLATE` / `BUDGETS` / `ANTI-LOOP` sections.
2. Re-run the original failing scenario: spawn `research:deep-researcher` as a sub-agent and ask it for a multi-angle research task. Confirm it now detects Mode B, runs Direct mode, and returns a structured report.
3. Run the same scenario as a top-level invocation (e.g., via `/research:deep-researcher` if available, or by typing the agent's trigger phrase in a fresh session). Confirm it runs Mode A and spawns quick-searcher sub-agents.

## Risks (recap from design + new)

- **Direct mode token usage:** each top-level deep-researcher invocation that ends up in Mode B costs roughly the same as the equivalent quick-searcher × N angles, plus deep-researcher's own classification and synthesis. This is more than a pure orchestrator role but cheaper than a single mega-search. Acceptable.
- **Mode confusion:** if a caller does not check the operating-mode line in the output, they may assume parallelism that didn't happen. Mitigation: the output template requires Mode A | B as line 1.
- **`research:web-search-techniques` skill load:** the skill was originally loaded by quick-searcher (which has the web tools); now deep-researcher also has them. The skill must be loaded by deep-researcher too when operating in Mode B. Add to the `# OPERATING MODES` section: "In Mode B, also load `research:web-search-techniques` for query technique guidance."

## Estimated total diff

- `deep-researcher.md`: ~80 lines added, ~10 lines moved/renamed.
- `quick-searcher.md`: ~7 lines added.
- `marketplace.json`: 2 version bumps.

## Commit message

```
Add Direct mode fallback to research:deep-researcher (v2.7.0)

Anthropic Agent SDK restricts sub-agents from spawning further
sub-agents, so deep-researcher cannot call quick-searcher when it is
itself spawned as a sub-agent. Without a fallback, it bails with a
free-form apology — exactly what happened during the
agent-teams-best-practices research turn that exposed this.

Adds dual-mode operation:
- Mode A (Orchestrator): top-level invocation, spawns quick-searcher
  sub-agents in parallel (unchanged behavior).
- Mode B (Direct): nested invocation, executes the activated angles
  itself via WebSearch+WebFetch with the same per-angle budget.

Detection is by checking for the Agent tool in the visible toolset.
The output template now leads with the operating mode so callers can
see immediately whether parallelism was achieved.

Tools allowlist: WebSearch and WebFetch added.

quick-searcher gains a non-load-bearing sub-unit-metadata block so
orchestrator-mode synthesis can distinguish complete vs partial
sub-agent runs.

Plan: docs/plans/2026-05-16-research-plugin-restructure-plan.md
Reference: docs/references/agent-teams-best-practices.md
```
