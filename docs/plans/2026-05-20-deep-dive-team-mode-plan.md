# Deep-Dive Team Mode Implementation Plan

> **For agentic workers:** Use subagent-driven execution (if subagents available) or ai-tooling:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `/agent-teams:team-deep-dive`, a multi-agent variant of `/deep-dive-analysis` that partitions monorepos/large codebases by workspace/directory/language, runs 3 deep-dive workers per partition across 2 waves, then synthesizes consolidated `.deep-dive/01..07.md` plus a new global `.deep-dive/08-interconnect-map.md`.

**Architecture:** 4-phase pipeline. Phase 0 partition detection (main context). Phase 1 spawns `3N` workers in 2 waves with a global barrier between waves (so Wave 2 can read all partitions' Wave 1 outputs for cross-partition citations). Phase 2 synthesizer consolidates per-partition outputs into a backward-compatible `.deep-dive/01..07.md`. Phase 3 reuses `senior-review:semantic-interconnect-mapper` unchanged on the consolidated set to produce `.deep-dive/08-interconnect-map.md`.

**Tech Stack:** Claude Code marketplace plugins (markdown only — no runtime code). YAML frontmatter + body for agents/commands. Validation via `marketplace-ops:marketplace-health`, `marketplace-ops:skills-validate`, and grep checks. No automated tests; manual smoke tests on three representative repos.

**Spec source of truth:** `docs/plans/2026-05-20-deep-dive-team-mode-design.md` (committed as `e9a9ae2`). Read it once before starting — every decision below traces back to a numbered section in that doc.

---

## File Structure

Five new files, two modified files. File responsibilities:

| Path                                                                            | Status   | Responsibility                                                                          |
|---------------------------------------------------------------------------------|----------|-----------------------------------------------------------------------------------------|
| `plugins/deep-dive-analysis/agents/partition-structure-worker.md`              | NEW      | Runs classic Phase 1 + Phase 2 for one partition                                        |
| `plugins/deep-dive-analysis/agents/partition-behavior-worker.md`               | NEW      | Runs classic Phase 3 + Phase 4 for one partition                                        |
| `plugins/deep-dive-analysis/agents/partition-quality-worker.md`                | NEW      | Runs classic Phase 5 + Phase 6 for one partition                                        |
| `plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md`                   | NEW      | Consolidates per-partition outputs + writes Phase 7 (final report)                      |
| `plugins/agent-teams/commands/team-deep-dive.md`                               | NEW      | The orchestrator command (pre-flight, partition detect, spawn, synth, interconnect)     |
| `.claude-plugin/marketplace.json`                                              | MODIFY   | Add `agents` array to deep-dive-analysis (4 new files); append command path to agent-teams; bump versions |
| `plugins/deep-dive-analysis/skills/deep-dive-analysis/SKILL.md`                | MODIFY   | Add `## Team Mode Integration` section explaining when to use classic vs team           |
| `plugins/deep-dive-analysis/commands/deep-dive-analysis.md`                    | UNCHANGED| Classic command stays intact                                                            |
| `plugins/senior-review/agents/semantic-interconnect-mapper.md`                 | UNCHANGED| Reused as-is                                                                            |

**Convention check:** all new agent files use kebab-case naming matching the `name:` frontmatter field, follow the local frontmatter style (multiline `description:`, `tools:`, `model: opus`, `color:`), and avoid emojis and the dash-aside construct per `CLAUDE.md`.

---

## Task 1: Create partition-structure-worker agent

**Files:**
- Create: `plugins/deep-dive-analysis/agents/partition-structure-worker.md`

- [ ] **Step 1: Create the file with the exact content below**

```markdown
---
name: partition-structure-worker
description: >
  Spawned by /agent-teams:team-deep-dive Phase 1 Wave 1 to execute Phase 1 (Structure Extraction) and Phase 2 (Interface Analysis) of deep-dive analysis on a single partition of a multi-partition codebase. Writes ownership-restricted output to .deep-dive/partitions/<name>/01-structure.md and 02-interfaces.md.
  TRIGGER WHEN: spawned by the /agent-teams:team-deep-dive command during Phase 1 Wave 1 to handle one partition's structural extraction.
  DO NOT TRIGGER WHEN: invoked outside the team-deep-dive pipeline -- the classic /deep-dive-analysis command runs structure extraction inline without an agent.
tools: Read, Glob, Grep, Bash, Write
model: opus
color: cyan
---

# Partition Structure Worker

You execute Phase 1 (Structure Extraction) and Phase 2 (Interface Analysis) of deep-dive analysis on ONE partition assigned to you. You write exactly two files: `01-structure.md` and `02-interfaces.md` under your owned partition directory.

## INPUTS

The spawn prompt gives you:
- `partition_name`: kebab-case identifier (e.g. `api`, `frontend`, `packages-shared`)
- `partition_path`: absolute or repo-relative path to the partition root
- `active_flags`: object with `critical`, `comments`, `depth` (you only use `depth` -- if `lite`, your output is identical to full because Phase 1+2 always run)

## OWNERSHIP CONTRACT

- You write ONLY:
  - `.deep-dive/partitions/<partition_name>/01-structure.md`
  - `.deep-dive/partitions/<partition_name>/02-interfaces.md`
- You DO NOT touch any other file under `.deep-dive/`.
- You DO NOT update `.deep-dive/state.json` — that is the orchestrator's job.

## FORBIDDEN FILES

NEVER read or include contents from:
- `.env`, `.env.*` — environment variables with secrets
- `credentials.*`, `secrets.*`, `*secret*`, `*credential*`
- `*.pem`, `*.key`, `*.p12`, `*.pfx` — certificates and private keys
- `id_rsa*`, `id_ed25519*` — SSH keys
- `.npmrc`, `.pypirc`, `.netrc` — auth tokens
- Any file that appears to contain API keys, passwords, or tokens

If encountered: note file existence only (`".env present — contains environment config"`). NEVER quote contents.

## TOOL USAGE

Use the language-aware scripts in `${CLAUDE_PLUGIN_ROOT}/skills/deep-dive-analysis/scripts/` whenever the target language is supported (Python, Java, JavaScript, TypeScript, SQL, PL/SQL, Rust):

- **Structure extraction:** `ast_parser.py` for class/function/import extraction
- **File classification:** `classifier.py` for language detection and counting

Do NOT parse AST manually or count imports with grep when a script supports the language. Read the partition root directly (not the whole repo) and pass `--target $partition_path` to scripts.

For unsupported languages, fall back to `Read` and `Grep` directly.

## PHASE 1: Structure Extraction

Scan all files under `partition_path` and build a structural map.

For each file in the partition, extract:
- Module/file name and path (relative to partition root)
- Language and framework
- Imports and dependencies (mark imports as `internal` if they resolve within the partition, `cross-partition` if they reference a sibling partition, `external` otherwise)
- Exported symbols (functions, classes, constants)
- File size and complexity indicators (line count, function count)

**Output file:** `.deep-dive/partitions/<partition_name>/01-structure.md`

```markdown
# Partition: <partition_name> — Structure Extraction

## File Inventory
| File | Language | Lines | Functions | Classes | Imports (internal / cross / external) |
|------|----------|-------|-----------|---------|---------------------------------------|
| ... | ... | ... | ... | ... | ... |

## Dependency Graph
[Mermaid diagram of within-partition module dependencies.]

## Cross-Partition Outgoing References
[List of symbols/modules imported from OTHER partitions, format: `<other-partition>::<symbol>`. Use the partition list provided in the spawn prompt to disambiguate.]

## Entry Points (within this partition)
[Main files, API routes, CLI handlers, public API surface.]

## Key Observations
[Notable structural patterns or concerns scoped to this partition.]

## Where to Add New Code
- New feature module: `<path within partition>`
- New API endpoint: `<path within partition>`
- New utility: `<path within partition>`
- New tests: `<path within partition>`

## Naming Conventions Observed
- Files: <pattern>
- Functions: <pattern>
- Classes: <pattern>
```

## PHASE 2: Interface Analysis

For each module in the partition, document the public interface.

**Output file:** `.deep-dive/partitions/<partition_name>/02-interfaces.md`

```markdown
# Partition: <partition_name> — Interface Analysis

## Public APIs
[Organized by module. For each: signature, parameter types, return type.]

## Contracts
[Interface definitions, type shapes, schemas exported by this partition.]

## External Dependencies
[Third-party libraries used and how. Distinct from cross-partition refs.]

## Cross-Partition Inbound References
[Symbols exported by this partition that other partitions import. Populate via Grep across `.deep-dive/partitions/*/01-structure.md` if those files exist when you run; otherwise leave the section with "Pending cross-partition reconciliation in synthesis."]

## How to Add a New Module
1. Create file at `<path within partition>`
2. Follow interface pattern from `<example file>`
3. Register in `<registration point>`
4. Add tests at `<test path>`
```

## COMPLETION

When you finish writing both files, call `TaskUpdate` to mark your assigned task `completed`. Do not write a final summary or status report — the orchestrator handles synthesis.
```

- [ ] **Step 2: Verify frontmatter validity**

Run: `head -10 plugins/deep-dive-analysis/agents/partition-structure-worker.md`

Expected: YAML frontmatter block with `name`, `description` (multiline `>`), `tools`, `model`, `color`. No `---` mid-body.

- [ ] **Step 3: Grep for dash-aside violations**

Run: `grep -nE ' -- .* -- | — .* — ' plugins/deep-dive-analysis/agents/partition-structure-worker.md`

Expected: no matches (only single-connector em-dashes are allowed; bracketed asides are banned per CLAUDE.md).

- [ ] **Step 4: Commit**

```bash
git add plugins/deep-dive-analysis/agents/partition-structure-worker.md
git commit -m "Add partition-structure-worker agent for team-deep-dive Phase 1 Wave 1

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Create partition-behavior-worker agent

**Files:**
- Create: `plugins/deep-dive-analysis/agents/partition-behavior-worker.md`

- [ ] **Step 1: Create the file with the exact content below**

```markdown
---
name: partition-behavior-worker
description: >
  Spawned by /agent-teams:team-deep-dive Phase 1 Wave 2 to execute Phase 3 (Flow Tracing) and Phase 4 (Semantic Understanding) of deep-dive analysis on a single partition. Reads all partitions' Wave 1 outputs to cite cross-partition flows and contracts. Writes ownership-restricted output to .deep-dive/partitions/<name>/03-flows.md and 04-semantics.md.
  TRIGGER WHEN: spawned by the /agent-teams:team-deep-dive command during Phase 1 Wave 2 to handle one partition's behavioral and semantic analysis.
  DO NOT TRIGGER WHEN: invoked outside the team-deep-dive pipeline.
tools: Read, Glob, Grep, Bash, Write
model: opus
color: cyan
---

# Partition Behavior Worker

You execute Phase 3 (Flow Tracing) and Phase 4 (Semantic Understanding) of deep-dive analysis on ONE partition. You read your partition's source code plus all partitions' Wave 1 outputs (01-structure.md and 02-interfaces.md across `.deep-dive/partitions/*/`) so your flows and ADRs can cite cross-partition boundaries.

## INPUTS

The spawn prompt gives you:
- `partition_name`, `partition_path`, `active_flags` (you respect `critical`)
- Implicit: all `.deep-dive/partitions/*/01-structure.md` and `02-interfaces.md` already exist (Wave 1 barrier has closed)

## OWNERSHIP CONTRACT

You write ONLY:
- `.deep-dive/partitions/<partition_name>/03-flows.md`
- `.deep-dive/partitions/<partition_name>/04-semantics.md`

You read freely from:
- `partition_path` (source code in your partition)
- `.deep-dive/partitions/*/01-structure.md` and `02-interfaces.md` (all partitions)

You DO NOT touch any other file. You DO NOT update `.deep-dive/state.json`.

## FORBIDDEN FILES

(Same list as `partition-structure-worker`: `.env`, credentials, keys, tokens. Note presence only, never quote contents.)

## CROSS-PARTITION CITATION CONTRACT

When you encounter an outgoing call/import in your partition that resolves to another partition, cite it as `<other-partition>::<symbol>` instead of `external`. Use the cross-partition imports already documented in `01-structure.md` to disambiguate.

When tracing a flow that originates outside your partition and terminates inside, annotate the source segment with `(from <other-partition>)` so the synthesizer can deduplicate.

## PHASE 3: Flow Tracing

Trace critical execution paths through the partition:
- Request lifecycle (entry -> processing -> response)
- Data transformation pipeline (input -> validation -> processing -> output)
- Error propagation paths
- State mutation flows

If `active_flags.critical` is `true`, prioritize:
- Authentication / authorization flows
- Payment / transaction flows
- Data persistence flows

**Output file:** `.deep-dive/partitions/<partition_name>/03-flows.md`

```markdown
# Partition: <partition_name> — Flow Tracing

## Critical Paths
[Step-by-step flow descriptions with file:line references. Mark cross-partition steps with `(from <other-partition>)` or `(to <other-partition>)`.]

## Data Flow
[How data transforms through the partition. Use cross-partition arrows where applicable.]

## Error Handling Paths
[Where errors originate and propagate. Note when errors cross partition boundaries.]

## Side Effects
[Functions with side effects and their blast radius. Mark cross-partition side effects explicitly.]

## Process Diagrams

For each significant process within or touching this partition, generate a Mermaid flowchart. Categorize each diagram as Technical / Functional / End-to-End.

### Technical Processes
[Mermaid flowcharts -- max 5 most critical.]

### Functional Processes
[Mermaid flowcharts -- max 5.]

### End-to-End Processes
[Mermaid flowcharts -- max 5. End-to-end flows that span multiple partitions are valuable here; annotate partition boundaries with subgraph fences.]

Diagram guidelines:
- Use `flowchart TD` for linear processes, `flowchart LR` for pipelines
- Include decision nodes (`{condition}`) for branching
- Label edges with conditions, data passed, or HTTP methods
- Reference source as comments: `%% src/auth/login.py::handle_request`
- Mark error/failure paths with dotted lines: `-->|error|`
- Keep each diagram under 30 nodes
- For cross-partition flows, use Mermaid `subgraph <partition>` to fence partitions visually
```

## PHASE 4: Semantic Understanding

Document the WHY behind the code:
- Business purpose of each module in the partition
- Design decisions and trade-offs (inferred from code patterns)
- Historical context (from git blame and commit messages within the partition)
- Assumptions embedded in the code
- Implicit contracts not documented anywhere
- Architecture Decision Records (ADRs) — document rejected alternatives and WHY

**Output file:** `.deep-dive/partitions/<partition_name>/04-semantics.md`

```markdown
# Partition: <partition_name> — Semantic Understanding

## Module Purposes
[WHY each module in this partition exists.]

## Design Decisions
[Inferred decisions and their trade-offs, scoped to this partition.]

## Architecture Decision Records
[Each ADR:]
- **Decision:** [What was chosen]
- **Context:** [What problem it solves]
- **Alternatives rejected:** [What was NOT chosen and WHY]
- **Consequences:** [Trade-offs accepted]

ADRs that depend on cross-partition behavior (e.g. "API never calls DB directly, talks to worker via queue") belong here ONLY if the partition is one of the actors. The synthesizer will lift them to a global section.

## Embedded Assumptions
[Assumptions the code makes that aren't documented. Mark cross-partition assumptions explicitly.]

## Hidden Contracts
[Implicit agreements between modules. Mark cross-partition contracts as `<this-partition> ↔ <other-partition>`.]

## Conventions Observed
- Error handling: <pattern>
- Logging: <pattern>
- Configuration: <pattern>
```

## COMPLETION

When you finish writing both files, call `TaskUpdate` to mark your task `completed`.
```

- [ ] **Step 2: Verify frontmatter validity**

Run: `head -10 plugins/deep-dive-analysis/agents/partition-behavior-worker.md`

Expected: same as Task 1 verification.

- [ ] **Step 3: Grep for dash-aside violations**

Run: `grep -nE ' -- .* -- | — .* — ' plugins/deep-dive-analysis/agents/partition-behavior-worker.md`

Expected: no matches.

- [ ] **Step 4: Commit**

```bash
git add plugins/deep-dive-analysis/agents/partition-behavior-worker.md
git commit -m "Add partition-behavior-worker agent for team-deep-dive Phase 1 Wave 2

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Create partition-quality-worker agent

**Files:**
- Create: `plugins/deep-dive-analysis/agents/partition-quality-worker.md`

- [ ] **Step 1: Create the file with the exact content below**

```markdown
---
name: partition-quality-worker
description: >
  Spawned by /agent-teams:team-deep-dive Phase 1 Wave 2 to execute Phase 5 (Pattern & Risk Detection) and Phase 6 (Documentation Health) of deep-dive analysis on a single partition. Writes ownership-restricted output to .deep-dive/partitions/<name>/05-risks.md and 06-documentation.md.
  TRIGGER WHEN: spawned by the /agent-teams:team-deep-dive command during Phase 1 Wave 2 to handle one partition's risk and documentation audit.
  DO NOT TRIGGER WHEN: invoked outside the team-deep-dive pipeline.
tools: Read, Glob, Grep, Bash, Write
model: opus
color: cyan
---

# Partition Quality Worker

You execute Phase 5 (Pattern & Risk Detection) and Phase 6 (Documentation Health) of deep-dive analysis on ONE partition. You read your partition's source plus all partitions' Wave 1 outputs.

## INPUTS

The spawn prompt gives you:
- `partition_name`, `partition_path`, `active_flags` (you respect `comments`)
- Implicit: all `.deep-dive/partitions/*/01-structure.md` and `02-interfaces.md` already exist

## OWNERSHIP CONTRACT

You write ONLY:
- `.deep-dive/partitions/<partition_name>/05-risks.md`
- `.deep-dive/partitions/<partition_name>/06-documentation.md`

You read freely from `partition_path` and `.deep-dive/partitions/*/01-structure.md` + `02-interfaces.md`.

You DO NOT touch any other file. You DO NOT update `.deep-dive/state.json`.

## FORBIDDEN FILES

(Same list as `partition-structure-worker`.)

## TOOL USAGE

Use:
- `usage_finder.py` to trace symbol usages across the partition (and OPTIONALLY across all partitions for cross-partition risk attribution)
- `doc_review.py` for link validation and marker checks in `06-documentation.md` work
- `rewrite_comments.py` for comment quality analysis if `active_flags.comments` is true

Do NOT use raw bash to do these jobs.

## PHASE 5: Pattern & Risk Detection

Scan the partition for:
- **Anti-patterns:** God objects, spaghetti code, shotgun surgery, feature envy
- **Red flags:** Swallowed exceptions, hardcoded credentials (note presence only, never quote), race conditions, N+1 queries
- **Technical debt:** TODO/FIXME comments, deprecated APIs, outdated patterns
- **Failure modes:** What breaks under load, edge cases, missing error handling

**Output file:** `.deep-dive/partitions/<partition_name>/05-risks.md`

```markdown
# Partition: <partition_name> — Pattern & Risk Detection

## Anti-Patterns Found
[Organized by severity (Critical / High / Medium / Low). Each row: pattern, file:line, brief evidence, severity rationale.]

## Red Flags
[Security, reliability, performance risks. Same row schema.]

## Technical Debt Inventory
[TODO/FIXME items, deprecated usage, modernization opportunities. Each row cites file:line.]

## Failure Mode Analysis
[What could break and under what conditions. Pair each failure mode with the trigger and the user-visible impact.]

## Cross-Partition Risk Attribution
[Risks that depend on or impact other partitions (e.g. "this partition swallows errors that originate in <other-partition>"). Use `<other-partition>::<symbol>` notation.]
```

## PHASE 6: Documentation Health

Evaluate existing documentation in the partition against code reality:
- **Accuracy:** Do docs match the actual code?
- **Completeness:** What's documented vs what should be?
- **Freshness:** When were docs last updated vs code?
- **Broken links:** References to files/functions that don't exist
- **Comment quality:** If `active_flags.comments` is true, run `rewrite_comments.py` and include its findings

**Output file:** `.deep-dive/partitions/<partition_name>/06-documentation.md`

```markdown
# Partition: <partition_name> — Documentation Health

## Documentation vs Code Accuracy
[Mismatches between docs and reality. Each row: doc location, code location, discrepancy description.]

## Coverage Gaps
[Undocumented public APIs, missing architecture docs. Tie each gap to a public symbol from `02-interfaces.md`.]

## Broken References
[Dead links, non-existent file paths in docs.]

## Comment Quality [if active_flags.comments]
[Comment audit results from `rewrite_comments.py` with improvement suggestions. Skip section entirely if flag is false.]
```

## COMPLETION

When done, call `TaskUpdate` to mark your task `completed`.
```

- [ ] **Step 2: Verify frontmatter validity**

Run: `head -10 plugins/deep-dive-analysis/agents/partition-quality-worker.md`

Expected: well-formed YAML frontmatter.

- [ ] **Step 3: Grep for dash-aside violations**

Run: `grep -nE ' -- .* -- | — .* — ' plugins/deep-dive-analysis/agents/partition-quality-worker.md`

Expected: no matches.

- [ ] **Step 4: Commit**

```bash
git add plugins/deep-dive-analysis/agents/partition-quality-worker.md
git commit -m "Add partition-quality-worker agent for team-deep-dive Phase 1 Wave 2

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Create deep-dive-synthesizer agent

**Files:**
- Create: `plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md`

- [ ] **Step 1: Create the file with the exact content below**

```markdown
---
name: deep-dive-synthesizer
description: >
  Spawned by /agent-teams:team-deep-dive Phase 2 to consolidate per-partition deep-dive outputs into the standard .deep-dive/01..07.md layout. Reads .deep-dive/partitions/*/01..06.md and produces unified files with cross-partition sections plus a team-mode final report (07-final-report.md). Backward-compatible with team-review and codebase-mapper pickup logic.
  TRIGGER WHEN: spawned by the /agent-teams:team-deep-dive command during Phase 2 to consolidate partition outputs.
  DO NOT TRIGGER WHEN: invoked outside the team-deep-dive pipeline -- the classic /deep-dive-analysis writes phase files directly.
tools: Read, Glob, Grep, Write
model: opus
color: purple
---

# Deep-Dive Synthesizer

You consolidate the partition outputs produced by the three partition-worker types into a backward-compatible `.deep-dive/01..07.md` set. Downstream consumers (`team-review`, `codebase-mapper`, `project-setup:create-claude-md`) cannot distinguish your output from a classic single-agent deep-dive — that compatibility is your hard requirement.

## INPUTS

The spawn prompt gives you:
- `partitions`: list of `{name, path, status}` from `.deep-dive/state.json` (status is `done` or `failed`)
- `active_flags`: object with `critical`, `comments`, `depth`

You read freely from:
- `.deep-dive/partitions/*/01-structure.md` through `06-documentation.md`
- `.deep-dive/state.json` (read-only — do not write)

## OWNERSHIP CONTRACT

You write ONLY:
- `.deep-dive/01-structure.md`
- `.deep-dive/02-interfaces.md`
- `.deep-dive/03-flows.md`
- `.deep-dive/04-semantics.md`
- `.deep-dive/05-risks.md`
- `.deep-dive/06-documentation.md`
- `.deep-dive/07-final-report.md`

If `active_flags.depth == "lite"`, skip `03`, `04`, `06` (they will not exist in partition outputs either).

You DO NOT write `08-interconnect-map.md` — that is the next agent's job.

## FAILURE HANDLING

For any partition with `status: "failed"` in `partitions`, add a callout in EVERY consolidated file you produce:

```
> ⚠ Missing partitions: <comma-separated names>. Sections below are partial.
```

The `07-final-report.md` opens with an explicit `## Partial Completeness Warning` section listing the failed partitions.

## CONSOLIDATION RULES

You do NOT re-analyze the code. You consolidate text. Your only source material is the partition output files. Inferring cross-partition structure beyond what those files document is OK; inferring new findings from source code is NOT.

Run each rule below in order. Output one file per rule.

### Rule 01-structure.md: unified inventory

```markdown
# Deep Dive — Structure Extraction

## Partition Map
| Partition | Path | Language | Files | Status |
|-----------|------|----------|-------|--------|
| <name> | <path> | <lang> | <count> | done / failed |

## File Inventory
[Concatenate all `## File Inventory` tables from `partitions/*/01-structure.md`. Prefix each row with the partition name as the first column. Sort by partition name, then by file path.]

## Dependency Graph (cross-partition view)
[Mermaid `flowchart LR` with one `subgraph <partition>` per partition. Inside each subgraph: the partition-local modules. Across subgraphs: edges drawn from each partition's `## Cross-Partition Outgoing References` section in `01-structure.md`. Annotate cross edges with `(cross:<from>-><to>)`.]

## Global Entry Points
[Union of all partitions' `## Entry Points` sections. Prefix each entry with the partition name.]

## Cross-Partition Reference Summary
[Table of cross-partition edges discovered. Columns: From Partition | To Partition | Symbol | Caller File | Direction.]

## Where to Add New Code
[Concatenate per partition. Add a "## Cross-partition concerns" subsection at the end with global guidance like "shared utilities belong in <shared-partition>; do not duplicate in other partitions".]

## Naming Conventions (per partition)
[Concatenate per partition. Add a "## Cross-partition style conflicts" subsection listing any case where two partitions use incompatible conventions.]
```

### Rule 02-interfaces.md: per-partition + cross-exports

```markdown
# Deep Dive — Interface Analysis

## Public APIs (by partition)
[Concatenate per partition. Use `### Partition: <name>` headings.]

## Cross-Partition Exports
[Reconcile each partition's `## Cross-Partition Outgoing References` (from 01-structure.md) against the actual exporters (sibling partitions' `02-interfaces.md`). Produce a table: Exporting Partition | Symbol | Consumers (list of partitions). This is the section that lets downstream reviewers see contract surfaces at a glance.]

## Contracts (by partition)
[Concatenate per partition. Pull from each partition's `## Contracts` section.]

## External Dependencies
[Concatenate. Deduplicate by package name; if two partitions use different versions, note the divergence explicitly.]

## How to Add a New Module (per partition)
[Concatenate.]
```

### Rule 03-flows.md: per-partition + cross-flows

Skip this file if `active_flags.depth == "lite"`.

```markdown
# Deep Dive — Flow Tracing

## Critical Paths (by partition)
[Concatenate.]

## Cross-Partition Flows
[Walk each partition's flows looking for `(from <other>)` or `(to <other>)` annotations. Deduplicate: a flow A->B->C reported by both A and C becomes ONE entry here, anchored by the flow's earliest step. List flows with full end-to-end traces, citing the originating step in the partition that owns it.]

## Data Flow (consolidated)
[Concatenate per partition. Add a "## Inter-partition data movements" subsection summarizing queue messages, shared DB tables, HTTP calls between partitions.]

## Error Handling Paths
[Concatenate. Highlight cross-partition error propagation.]

## Side Effects
[Concatenate. Cross-partition side effects get their own subsection.]

## Process Diagrams
[Concatenate. Re-render any E2E diagram that crosses partitions with explicit `subgraph` fences if the source diagram lacked them.]
```

### Rule 04-semantics.md: per-partition + global ADRs

Skip this file if `active_flags.depth == "lite"`.

```markdown
# Deep Dive — Semantic Understanding

## Module Purposes (by partition)
[Concatenate.]

## Design Decisions (by partition)
[Concatenate.]

## Architecture Decision Records (per partition)
[Concatenate.]

## Cross-Partition ADR
[Promote any ADR that involves multiple partitions (e.g. "API talks to worker only via queue") here. Re-write to remove the partition-local framing and present as a global rule. Cite original ADR locations.]

## Embedded Assumptions (consolidated)
[Concatenate. Cross-partition assumptions get their own subsection.]

## Hidden Contracts (cross-partition)
[Pull every entry from partitions' `## Hidden Contracts` that uses `<this> ↔ <other>` notation. List them here as the canonical cross-partition contract registry.]

## Conventions Observed
[Concatenate. Note any conflicts (Partition A uses Logger X, Partition B uses Logger Y, etc.).]
```

### Rule 05-risks.md: severity-sorted consolidated

```markdown
# Deep Dive — Pattern & Risk Detection

## Anti-Patterns Found (by severity)
[Concatenate all partitions' anti-pattern tables. Re-sort the union by severity globally (Critical first). Each row: partition | pattern | file:line | severity | rationale.]

## Red Flags (by severity)
[Same treatment.]

## Technical Debt Inventory (by partition)
[Concatenate, no global re-sort — debt is partition-local.]

## Failure Mode Analysis
[Concatenate.]

## Cross-Partition Risk Attribution
[Pull every `## Cross-Partition Risk Attribution` entry from partitions. Deduplicate.]
```

### Rule 06-documentation.md: aggregated gaps

Skip this file if `active_flags.depth == "lite"`.

```markdown
# Deep Dive — Documentation Health

## Documentation vs Code Accuracy (by partition)
[Concatenate.]

## Coverage Gaps (priority-sorted)
[Union of all partitions' gaps. Sort by: public-API gaps first (cite the symbol from cross-partition exports if applicable), then internal coverage gaps.]

## Broken References (by partition)
[Concatenate.]

## Comment Quality [if active_flags.comments]
[Concatenate.]
```

### Rule 07-final-report.md: team-mode executive summary

Template:

```markdown
# Deep Dive Analysis Report (Team Mode)

## Target
[From state.json target]

## [if any partition failed] Partial Completeness Warning
[List failed partitions and which sections are incomplete.]

## Executive Summary
[2-3 sentences on overall codebase health, derived from consolidated 05-risks.md and 06-documentation.md.]

## Project at a Glance
[2-3 paragraph narrative explaining what this project does, who it's for, and how it works -- aggregated from 04-semantics.md if present, otherwise from 01-structure.md observations.]

## Partition Map
[Same table as 01-structure.md `## Partition Map`.]

## Cross-Partition Topology
[Same Mermaid diagram as 01-structure.md `## Dependency Graph (cross-partition view)`.]

## Architecture Overview
[Synthesized from consolidated 01-structure.md and 02-interfaces.md.]

## Technology Decisions
[Aggregated tech choices across partitions, useful for presentations.]

## Critical Paths (cross-partition)
[Pull from 03-flows.md `## Cross-Partition Flows` if present; otherwise list per-partition critical paths.]

## Key Process Diagrams
[Include 3-5 most important Mermaid flowcharts. Prioritize cross-partition E2E diagrams over partition-local Technical ones. Reference 03-flows.md for the complete set.]

## Design Insights
[Pull from 04-semantics.md `## Cross-Partition ADR` if present.]

## Per-Partition Health Scorecard
| Partition | Anti-Patterns (C/H/M/L) | Red Flags (C/H/M/L) | Doc Gaps | Tech Debt | Overall |
|-----------|--------------------------|----------------------|----------|-----------|---------|
| <name> | x/x/x/x | x/x/x/x | x | x | <Healthy / At Risk / Critical> |

## Risk Assessment (global)
[Same global severity matrix as classic Phase 7, but include `## Cross-Partition Risks` row pulled from 05-risks.md.]

## Documentation vs Reality
[Aggregated mismatches.]

## Top Priority Actions
[Derived from 05-risks.md Critical+High, cross-referenced with cross-partition impact when applicable.]

## Detailed Findings
[Cross-references to the consolidated phase files.]

## Quick Reference: Which File to Consult
| Your Task | Start With | Also Check |
|-----------|-----------|------------|
| Onboarding / understanding the project | 07-final-report, 01-structure | 04-semantics |
| Writing new feature | 01-structure (Where to Add), 02-interfaces | 04-semantics |
| Fixing a bug | 03-flows, 05-risks | 01-structure |
| Refactoring | 01-structure, 04-semantics, 05-risks | 03-flows |
| Code review | 02-interfaces, 05-risks, 08-interconnect-map | 06-documentation |
| Updating documentation | 06-documentation, 04-semantics | 02-interfaces |
| Cross-partition design decisions | 04-semantics (Cross-Partition ADR), 01-structure | 02-interfaces (Cross-Partition Exports) |

## Analysis Metadata
- Mode: team
- Target: [path]
- Partitions: [count] ([list])
- Phases completed: [list]
- Date: [timestamp]
```

## COMPLETION

When you finish writing all output files (respecting `--depth=lite` skips), call `TaskUpdate` to mark your task `completed`.
```

- [ ] **Step 2: Verify frontmatter validity**

Run: `head -10 plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md`

Expected: well-formed YAML frontmatter with `color: purple` (distinct from worker `cyan`).

- [ ] **Step 3: Grep for dash-aside violations**

Run: `grep -nE ' -- .* -- | — .* — ' plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md`

Expected: no matches.

- [ ] **Step 4: Commit**

```bash
git add plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md
git commit -m "Add deep-dive-synthesizer agent for team-deep-dive Phase 2 consolidation

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Create team-deep-dive command

**Files:**
- Create: `plugins/agent-teams/commands/team-deep-dive.md`

The orchestrator command. Long file; written in one task because all 4 phases reference each other.

- [ ] **Step 1: Create the file with the exact content below**

```markdown
---
description: >
  Multi-agent variant of /deep-dive-analysis for large or partitioned codebases. Auto-detects partitions (workspaces / dirs / language clusters), spawns 3 deep-dive workers per partition across 2 waves, synthesizes consolidated .deep-dive/01..07.md plus a global .deep-dive/08-interconnect-map.md.
  TRIGGER WHEN: the user wants deep-dive analysis on a monorepo or wants a cross-partition interconnection map produced as part of the same flow.
  DO NOT TRIGGER WHEN: the project is a single small directory (use /deep-dive-analysis) or the user wants a documentation-only audit (use /deep-dive-analysis --docs-only).
argument-hint: "<target> [--critical] [--comments] [--depth=lite|full] [--partition <path>] [--partition-name <name>] [--skip-interconnect] [--skip-synthesis] [--yes]"
---

# Team Deep-Dive

Orchestrate a partitioned multi-agent deep-dive plus global interconnect map.

## CRITICAL RULES

1. **Execute phases in order.** No skipping unless `--skip-synthesis` or `--skip-interconnect` is set.
2. **Spawn agents with file ownership.** Every spawn prompt enumerates the owned output files.
3. **Wait for the global Wave 1 barrier** before spawning Wave 2 workers.
4. **Never enter plan mode.** Execute immediately.
5. **Resume-safe.** Re-spawn only missing workers on resume.

## Skills to Load

Before starting, invoke these skills:
- `agent-teams:task-coordination-strategies` — task dependencies, addBlockedBy semantics
- `agent-teams:team-communication-protocols` — spawn prompt anatomy, shutdown
- `agent-teams:parallel-feature-development` — file ownership patterns

## Pre-flight Checks

1. Verify `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set
2. Parse `$ARGUMENTS`:
   - `<target>`: directory to analyze (default: cwd)
   - `--critical`: prioritize auth/payment/persistence in Phase 3-4
   - `--comments`: activate comment audit in Phase 6
   - `--depth=lite|full`: lite skips Phase 3-4 (workers B not spawned, synthesizer skips 03/04/06)
   - `--partition <path>`: manual partition (repeatable; overrides auto-detect)
   - `--partition-name <name>`: symbolic name for the N-th manual partition (1-indexed; optional)
   - `--skip-interconnect`: skip Phase 3
   - `--skip-synthesis`: skip Phase 2 AND Phase 3
   - `--yes`: auto-accept partition checkpoint
   - REJECT with explicit error if `--phase N` or `--docs-only` are passed (suggest classic `/deep-dive-analysis`)
3. Check `.deep-dive/state.json`:
   - If `mode == "team"` and `status == "in_progress"`: prompt to resume or archive
   - If `mode == "classic"`: refuse to start; instruct user to archive first
   - If `status == "complete"`: prompt to archive

## Phase 0: Pre-flight + Partition Detection

### Initialize state

Create `.deep-dive/` and `.deep-dive/state.json`:

```json
{
  "target": "$ARGUMENTS_TARGET",
  "mode": "team",
  "status": "in_progress",
  "flags": {
    "critical": false,
    "comments": false,
    "depth": "full"
  },
  "partitions": [],
  "phases": {
    "phase_0_detection": "pending",
    "phase_1_partition_workers": "pending",
    "phase_2_synthesis": "pending",
    "phase_3_interconnect": "pending"
  },
  "agents_spawned": [],
  "files_created": [],
  "started_at": "<ISO_TIMESTAMP>",
  "completed_at": null
}
```

### Run partition detection algorithm

If `--partition` was provided one or more times, skip auto-detect: use the manual list directly. Apply `--partition-name` mappings if provided; otherwise derive names from path basename.

Otherwise, run the detection chain (first rule that matches wins):

1. **Explicit workspace manifests** (in order):
   - `pnpm-workspace.yaml` -> `packages` field paths
   - `package.json` with `workspaces` field
   - `lerna.json` `packages`
   - `nx.json` + `apps/` + `libs/`
   - `turbo.json` + `apps/` + `packages/`
   - `Cargo.toml` `[workspace] members`
   - `pyproject.toml` `[tool.uv.workspace] members` or equivalent
2. **Convention-based monorepo:**
   - `apps/`, `packages/`, or `services/` at root with >1 subdirectory
   - `src/` with sub-dirs each having their own `package.json` / `pyproject.toml`
3. **Layer split:**
   - `src/{backend,frontend}`, `src/{api,web}`, `src/{server,client}`, or root-level `backend/` + `frontend/`
4. **Language split:**
   - Use `${CLAUDE_PLUGIN_ROOT}/skills/deep-dive-analysis/scripts/classifier.py` to count files per language
   - If ≥2 languages with ≥20 files each: partition per language (`*.py` -> "python", `*.ts/*.tsx` -> "typescript")
5. **Fallback:** single partition wrapping the entire target, name = `root`

**Always excluded paths:** `node_modules/`, `dist/`, `build/`, `.next/`, `target/`, `vendor/`, `__pycache__/`, `.venv/`.

**Partition naming rules:**
1. From workspace path -> basename
2. On collision -> slug-ified path
3. From language fallback -> language name
4. From single-partition fallback -> `root`

Normalize names: lowercase, separators -> hyphen, strip accents, allowed chars `[a-z0-9-]`.

For each partition, compute `file_count` and `loc_estimate` (use `classifier.py` + `wc -l` or `cloc` if available).

### Checkpoint

Present to the user:

```
Deep-dive team-mode scope:
Target: <target>

Detected partitioning strategy: <strategy name>

Proposed partitions (<N>):
  P1: <path>          (<language>, <file-count> files, ~<loc>k LOC)
  ...

Spawn plan: <N> partitions × 3 agents = <3N> workers + 1 synthesizer + 1 interconnect-mapper = <3N+2> agents total.

Note: token cost scales linearly with file count × agents. Consider `--depth=lite` for monorepos with many partitions.

Options:
  [A] Accept and start
  [M] Modify partition list (rename, regroup, exclude one)
  [m] Manual: provide partition paths
  [c] Cancel
```

If `--yes`, auto-select `[A]`.

If `[M]`, prompt for changes:
- `rename <old> <new>`
- `exclude <name>`
- `merge <name1> <name2> [<merged-name>]`
- `done` to finalize

If `[m]`, prompt for paths and optional names.

If `[c]`, set state to `cancelled` and exit.

Finalize `partitions` array in `state.json` with `{name, path, language_primary, file_count, loc_estimate, status: "pending"}` for each. Mark `phase_0_detection: "complete"`.

## Phase 1: Partition Workers (2 waves)

### Wave 1: Structure workers (parallel)

For each partition `P_i` in `state.json`:

1. Create directory `.deep-dive/partitions/<P_i.name>/`
2. Spawn `deep-dive-analysis:partition-structure-worker`:
   - `subagent_type`: `deep-dive-analysis:partition-structure-worker`
   - Task title: `"P<i>.A — Structure+Interfaces for partition <P_i.name>"`
   - Task prompt:

```
You are partition-structure-worker on partition "<P_i.name>".

Identity: P<i>.A
Owned files:
  - .deep-dive/partitions/<P_i.name>/01-structure.md
  - .deep-dive/partitions/<P_i.name>/02-interfaces.md
DO NOT touch any other file under .deep-dive/.

Target path for this partition: <P_i.path>
Active flags: --critical=<bool> --comments=<bool> --depth=<lite|full>

Sibling partitions (for cross-partition citation lookup if needed):
  <list each P_j.name -> P_j.path>

Required reads before writing:
  - <P_i.path>: all source files within scope
  - ${CLAUDE_PLUGIN_ROOT}/skills/deep-dive-analysis/SKILL.md
  - Scripts at ${CLAUDE_PLUGIN_ROOT}/skills/deep-dive-analysis/scripts/

Completion: when done, call TaskUpdate to mark your task completed.
```

3. Record spawn in `agents_spawned[]` with `{name: "P<i>.A", type: "partition-structure-worker", partition: "<P_i.name>", task_id: "..."}`.

After spawning all `P_i.A`: monitor via `TaskList`. Wait until every `P_i.A` task is `completed` OR `failed`.

For each partition: if `P_i.A` failed, mark `partitions[i].status = "failed"`. If completed, mark `partitions[i].status = "structure_done"`.

Mark `phase_1_partition_workers: "wave1_done"`.

### Wave 2: Behavior + Quality workers (parallel)

Skip workers B if `--depth=lite`.

For each partition `P_i` where `partitions[i].status == "structure_done"`:

1. If `--depth != lite`: spawn `deep-dive-analysis:partition-behavior-worker`:
   - Task title: `"P<i>.B — Flows+Semantics for partition <P_i.name>"`
   - Task prompt:

```
You are partition-behavior-worker on partition "<P_i.name>".

Identity: P<i>.B
Owned files:
  - .deep-dive/partitions/<P_i.name>/03-flows.md
  - .deep-dive/partitions/<P_i.name>/04-semantics.md
DO NOT touch any other file under .deep-dive/.

Target path for this partition: <P_i.path>
Active flags: --critical=<bool> --comments=<bool> --depth=<lite|full>

Sibling partitions: <list>

Required reads before writing:
  - <P_i.path>: source files
  - .deep-dive/partitions/*/01-structure.md (ALL partitions, already written by Wave 1)
  - .deep-dive/partitions/*/02-interfaces.md (ALL partitions)

Cross-partition citations: when you find an outgoing call/import that leaves
your partition, cite it as <other-partition>::<symbol>.

Completion: TaskUpdate to mark completed.
```

2. Spawn `deep-dive-analysis:partition-quality-worker`:
   - Task title: `"P<i>.C — Risks+Docs for partition <P_i.name>"`
   - Task prompt: same template as B, but with `partition-quality-worker` type, owned files `05-risks.md` and `06-documentation.md`.

Record both spawns in `agents_spawned[]`.

Monitor `TaskList`. For each partition, when both `P_i.B` (or only `P_i.C` in lite mode) and `P_i.C` complete:
- Mark `partitions[i].status = "done"`

When all partitions reach `done` or `failed`: mark `phase_1_partition_workers: "complete"` (or `"failed"` if EVERY partition is failed).

## Phase 2: Synthesis

Skip if `--skip-synthesis`.

Spawn a single `deep-dive-analysis:deep-dive-synthesizer`:
- Task prompt:

```
You are deep-dive-synthesizer.

Identity: SYNTH
Owned files: .deep-dive/01-structure.md through 07-final-report.md (skip 03, 04, 06 if depth=lite).
DO NOT touch .deep-dive/08-interconnect-map.md or any partition file.

Active flags: <flags from state.json>

Partitions to consolidate:
  <for each partition: {name, path, status, language_primary}>

For any partition with status=failed, add a "⚠ Missing partitions" callout in every consolidated file. The 07-final-report.md opens with a "Partial Completeness Warning" section.

Read .deep-dive/partitions/*/ and apply the consolidation rules in your agent definition.

Completion: TaskUpdate to mark completed.
```

Monitor. On completion: mark `phase_2_synthesis: "complete"`. On failure: mark `phase_2_synthesis: "failed"` and `phase_3_interconnect: "skipped_due_to_phase_2_failure"`, then jump to Phase 4.

## Phase 3: Interconnect Map

Skip if `--skip-interconnect` or `--skip-synthesis` or Phase 2 failed.

Spawn a single `senior-review:semantic-interconnect-mapper`:
- Task prompt:

```
Build the interconnect map for this codebase using the team-deep-dive consolidated output as primary context.

Primary context source: `.deep-dive/01-07.md` (consolidated from partition outputs by the synthesizer).
Target files: the entire codebase (union of partitions; see `.deep-dive/01-structure.md ## Partition Map`).
Output path: `.deep-dive/08-interconnect-map.md`

Produce the full structured map following your agent definition: Call Graph (2-3 hop for public entry points, with cross-partition edges marked), Contracts (formal / structural / implicit), Invariants, Domain Rules, Assumptions (verified / documented / unverified), Integration Hot-Spots, Change Impact Radius, Reviewer Hints.

Every claim must cite file:line. No recommendations, no fixes. Empty sections are acceptable if nothing applies.
```

Monitor. On completion: mark `phase_3_interconnect: "complete"`. On failure: mark `phase_3_interconnect: "failed"` and continue to Phase 4 (failure is non-blocking).

## Phase 4: Completion & Next Steps Menu

1. Update `state.json`: `status: "complete"`, `completed_at: <ISO_TIMESTAMP>`.
2. Send `shutdown_request` to all remaining teammates.
3. Call `TeamDelete` to remove team resources.
4. Present summary:

```
Deep dive (team mode) complete for: <target>

Partitions: <N> (<list of names + status>)

Output Files:
  Per-partition reports:    .deep-dive/partitions/*/01..06.md
  Consolidated reports:     .deep-dive/01-structure.md .. 07-final-report.md
  Interconnect map:         .deep-dive/08-interconnect-map.md (if Phase 3 ran)

Summary:
  - Files analyzed:  <count>
  - Anti-patterns:   <count>  |  Red flags: <count>  |  Tech debt: <count>
  - Documentation gaps: <count>
  - Cross-partition flows: <count>
```

5. Show Next Steps Menu:

```
What would you like to do next?

1. Start fixing — execute the action plan
2. Apply quick fixes
3. Deep dive further — re-run a single partition
4. Generate documentation
   4a. CLAUDE.md (suggests /project-setup:create-claude-md or maintain-claude-md)
   4b. Codebase map (suggests /codebase-mapper:map-codebase)
   4c. API / interface docs (suggests /codebase-mapper:docs-create)
5. Run code review — launch /agent-teams:team-review (will reuse this .deep-dive/ + 08-interconnect-map.md)
6. Export report
7. Nothing for now
```

Wait for user choice before proceeding.

## Resume Logic

On pre-flight detection of `mode == "team"` and `status == "in_progress"`:

- If `phases.phase_0_detection != "complete"`: archive and restart from zero
- If `phases.phase_1_partition_workers == "pending"`: re-run Phase 1 Wave 1
- If `phases.phase_1_partition_workers == "wave1_done"`: skip Wave 1, re-run Wave 2 for every partition with `status == "structure_done"` (no `B` and `C` outputs yet)
- If `phases.phase_1_partition_workers == "complete"` and `phase_2_synthesis != "complete"`: re-run Phase 2
- If `phases.phase_2_synthesis == "complete"` and `phase_3_interconnect != "complete"`: re-run Phase 3
- If `phases.phase_3_interconnect == "complete"`: present Phase 4 menu directly

## Quick Examples

- `/agent-teams:team-deep-dive .` — auto-detect, full depth
- `/agent-teams:team-deep-dive . --depth=lite` — lite mode (2N+2 agents)
- `/agent-teams:team-deep-dive . --critical` — prioritize security paths in Phase 3-4
- `/agent-teams:team-deep-dive . --partition packages/api --partition packages/web --yes` — manual partitions, auto-accept
- `/agent-teams:team-deep-dive . --skip-interconnect` — stop at Phase 2
- `/agent-teams:team-deep-dive . --skip-synthesis` — only per-partition reports (no consolidation)
```

- [ ] **Step 2: Verify frontmatter validity**

Run: `head -10 plugins/agent-teams/commands/team-deep-dive.md`

Expected: command frontmatter with `description:` (multiline `>`) and `argument-hint:`. No `name:` or `tools:` (commands don't have those — they're for skills/agents).

- [ ] **Step 3: Grep for dash-aside violations and stale tool names**

Run: `grep -nE ' -- .* -- | — .* — ' plugins/agent-teams/commands/team-deep-dive.md`

Expected: no matches.

Run: `grep -nE 'Teammate|spawnTeam|Task tool to spawn' plugins/agent-teams/commands/team-deep-dive.md`

Expected: no matches (modern agent-teams uses `TeamCreate`, `Agent`, `TaskUpdate`).

- [ ] **Step 4: Commit**

```bash
git add plugins/agent-teams/commands/team-deep-dive.md
git commit -m "Add /agent-teams:team-deep-dive command for partitioned deep-dive

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Update marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

This task: bump versions and register all 5 new files. Read the file first to confirm exact current state (versions may have moved since spec was written if other work landed).

- [ ] **Step 1: Read the current file**

Run: `grep -n '"version"' .claude-plugin/marketplace.json | head -5`

Expected lines (or higher if other work landed):
```
9:    "version": "6.20.0"          ← metadata.version
41:      "version": "1.10.0",       ← deep-dive-analysis
1399:    "version": "2.12.0",       ← agent-teams
```

If different, use the observed current version as the FROM number for the bumps below.

- [ ] **Step 2: Modify the deep-dive-analysis entry**

Locate the deep-dive-analysis plugin block (around line 38). Apply these changes:

**A. Bump `"version": "1.10.0"` -> `"version": "1.11.0"`** (minor: adds 4 agents)

**B. Add an `"agents"` array BEFORE `"skills"`. The block currently looks like:**

```json
      "category": "review",
      "strict": false,
      "skills": [
        "./skills/deep-dive-analysis"
      ],
      "commands": [
        "./commands/deep-dive-analysis.md"
      ]
    },
```

**Change to:**

```json
      "category": "review",
      "strict": false,
      "agents": [
        "./agents/partition-structure-worker.md",
        "./agents/partition-behavior-worker.md",
        "./agents/partition-quality-worker.md",
        "./agents/deep-dive-synthesizer.md"
      ],
      "skills": [
        "./skills/deep-dive-analysis"
      ],
      "commands": [
        "./commands/deep-dive-analysis.md"
      ]
    },
```

- [ ] **Step 3: Modify the agent-teams entry**

Locate the agent-teams plugin block (around line 1396). Apply these changes:

**A. Bump `"version": "2.12.0"` -> `"version": "2.13.0"`** (minor: adds 1 command)

**B. Append `"./commands/team-deep-dive.md"` to the existing `"commands"` array. The current last entry is `"./commands/team-codebase-map.md"`. After change:**

```json
      "commands": [
        "./commands/team-spawn.md",
        "./commands/team-review.md",
        "./commands/team-debug.md",
        "./commands/team-feature.md",
        "./commands/team-delegate.md",
        "./commands/team-status.md",
        "./commands/team-shutdown.md",
        "./commands/team-research.md",
        "./commands/team-design.md",
        "./commands/team-codebase-map.md",
        "./commands/team-deep-dive.md"
      ]
```

- [ ] **Step 4: Bump metadata.version**

Locate `"version"` near line 9 (inside the top-level `metadata` block).

Bump `"version": "6.20.0"` -> `"version": "6.21.0"` (minor: two plugins bumped + new feature).

- [ ] **Step 5: Validate JSON**

Run: `python -m json.tool .claude-plugin/marketplace.json > /dev/null && echo OK`

Expected: `OK`

- [ ] **Step 6: Verify referenced files exist**

Run:
```bash
for f in plugins/deep-dive-analysis/agents/partition-structure-worker.md \
         plugins/deep-dive-analysis/agents/partition-behavior-worker.md \
         plugins/deep-dive-analysis/agents/partition-quality-worker.md \
         plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md \
         plugins/agent-teams/commands/team-deep-dive.md; do
  test -f "$f" && echo "OK: $f" || echo "MISSING: $f"
done
```

Expected: all five `OK` lines.

- [ ] **Step 7: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "Register team-deep-dive agents and command in marketplace

Bumps deep-dive-analysis to 1.11.0 (adds 4 agents) and agent-teams to
2.13.0 (adds 1 command). metadata.version bumped to 6.21.0.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Update deep-dive-analysis SKILL.md with Team Mode Integration

**Files:**
- Modify: `plugins/deep-dive-analysis/skills/deep-dive-analysis/SKILL.md`

- [ ] **Step 1: Read the existing SKILL.md to find the insertion point**

Run: `grep -n '^##' plugins/deep-dive-analysis/skills/deep-dive-analysis/SKILL.md`

This lists all top-level sections. Find the last section that makes sense to precede a new "Team Mode Integration" section. Typical good locations:
- After a `## Integration` or `## Downstream Consumers` section if one exists
- Otherwise, immediately before the final `## References` / `## See also` / `## Quick Examples` section

If no obvious anchor exists, append the section at the end of the file.

- [ ] **Step 2: Add the section at the chosen location**

Insert this content (using `Edit` tool with the line preceding the chosen insertion point as `old_string` context):

```markdown

## Team Mode Integration

The classic `/deep-dive-analysis` command runs three subagents in two waves on a single target. For monorepos, multi-language repos, or large codebases where a single deep-dive's context window grows uncomfortable, switch to the team variant:

```
/agent-teams:team-deep-dive <target>
```

The team command:
1. Auto-detects partitions (workspaces, top-level dirs, or language clusters) and asks you to confirm at a checkpoint.
2. Spawns three deep-dive workers per partition in two waves (Wave 1 = Structure; Wave 2 = Behavior + Quality). Wave 2 workers read every partition's Wave 1 output, so cross-partition contracts and flows can be cited directly.
3. Synthesizes a backward-compatible `.deep-dive/01..07.md` set that any downstream consumer (`/agent-teams:team-review`, `/codebase-mapper:map-codebase`, `/project-setup:create-claude-md`) can pick up without changes.
4. Adds `.deep-dive/08-interconnect-map.md` produced by `senior-review:semantic-interconnect-mapper` on top of the consolidated set, giving a global Call Graph, Contracts, Invariants, and Integration Hot-Spots view.

### Choosing between classic and team

| Repo profile                                        | Use classic        | Use team           |
|-----------------------------------------------------|--------------------|--------------------|
| Single package, < 200 files, one language           | ✓                  |                    |
| Monorepo (pnpm/npm/yarn/lerna/nx/turbo workspaces)  |                    | ✓                  |
| Multi-language (Python + TS, etc.) at top level     |                    | ✓                  |
| You want a global interconnection map produced in the same run |        | ✓                  |
| You want to control phases via `--phase N` or `--docs-only` | ✓     |                    |

### Output layout (team mode)

```
.deep-dive/
├── state.json
├── partitions/
│   └── <name>/{01..06}.md          ← per-partition reports
├── 01-structure.md .. 07-final-report.md   ← consolidated (compat with classic)
└── 08-interconnect-map.md          ← new, global cross-partition map
```

See `docs/plans/2026-05-20-deep-dive-team-mode-design.md` for the full architecture.
```

- [ ] **Step 3: Verify dash-aside compliance**

Run: `grep -nE ' -- .* -- | — .* — ' plugins/deep-dive-analysis/skills/deep-dive-analysis/SKILL.md`

Expected: no bracketed-aside matches (single-connector dashes in tables are fine).

- [ ] **Step 4: Commit**

```bash
git add plugins/deep-dive-analysis/skills/deep-dive-analysis/SKILL.md
git commit -m "Document team-deep-dive integration in deep-dive-analysis SKILL.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Validation pass

**Files:**
- Read-only validation across all modified files

- [ ] **Step 1: Run marketplace structural validation**

Invoke the `marketplace-ops:marketplace-health` skill:

```
/marketplace-ops:marketplace-health
```

Expected: no errors, no missing-file warnings. New entries should appear in the inventory.

- [ ] **Step 2: Run skill/agent quality validation on new agents**

Invoke `marketplace-ops:skills-validate` targeting the 4 new agent files:

```
/marketplace-ops:skills-validate plugins/deep-dive-analysis/agents/partition-structure-worker.md \
                                  plugins/deep-dive-analysis/agents/partition-behavior-worker.md \
                                  plugins/deep-dive-analysis/agents/partition-quality-worker.md \
                                  plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md
```

Expected: pass on frontmatter completeness, activation pattern presence, token budget, no forbidden content.

If any agent fails: iterate on its frontmatter (description must have both TRIGGER WHEN and DO NOT TRIGGER WHEN; tools list must match capabilities the body actually uses; model must be `opus`; color is one of the allowed values).

- [ ] **Step 3: Stale tool name grep across all new/modified files**

Run:
```bash
grep -nE 'Teammate|spawnTeam|Task tool to spawn|`Teammate` cleanup' \
  plugins/agent-teams/commands/team-deep-dive.md \
  plugins/deep-dive-analysis/agents/partition-structure-worker.md \
  plugins/deep-dive-analysis/agents/partition-behavior-worker.md \
  plugins/deep-dive-analysis/agents/partition-quality-worker.md \
  plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md \
  plugins/deep-dive-analysis/skills/deep-dive-analysis/SKILL.md
```

Expected: no matches. (Modern agent-teams API uses `TeamCreate`, `TeamDelete`, `Agent`, `TaskUpdate`, `TaskList`.)

- [ ] **Step 4: Dash-aside construct grep across all new files**

Run:
```bash
grep -nE ' -- [a-zA-Z][^-]+ -- | — [a-zA-Z][^—]+ — | - [a-zA-Z][^-]+ - ' \
  plugins/agent-teams/commands/team-deep-dive.md \
  plugins/deep-dive-analysis/agents/partition-*.md \
  plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md
```

Expected: no bracketed-aside matches. Single-connector em-dashes used as section separators or in tables are fine.

If matches found: rewrite the offending sentences into separate sentences, parentheses, or colons per the CLAUDE.md rule.

- [ ] **Step 5: Document the team-mode smoke test plan (no execution required at this point — record the plan for future verification)**

Append to `docs/plans/2026-05-20-deep-dive-team-mode-plan.md` under a new `## Smoke Test Plan (manual, post-merge)` section, the three smoke test scenarios from the design doc (section "Testing strategy", Level 3). The engineer should NOT execute the smoke tests as part of this task — actual end-to-end testing requires real target repos and runtime resources. The plan records WHAT to test post-merge.

Write this block at the end of this plan file (or in a separate `docs/plans/2026-05-20-deep-dive-team-mode-smoke-tests.md` if preferred):

```markdown
## Smoke Test Plan (manual, post-merge)

### Scenario 1: pnpm monorepo with 3 packages
- Target: a repo with `pnpm-workspace.yaml` listing 3 packages
- Command: `/agent-teams:team-deep-dive .`
- Verify: auto-detect proposes 3 partitions from workspaces; user accepts; full pipeline runs to completion
- Inspect: `.deep-dive/partitions/*/` has 6 files each; `.deep-dive/01..08.md` exist; `08-interconnect-map.md` Call Graph contains cross-partition edges

### Scenario 2: flat single-language Python repo
- Target: a small Python project without workspaces
- Command: `/agent-teams:team-deep-dive src/`
- Verify: auto-detect falls back to 1 partition (`root`); 3 workers + synth + interconnect run
- Inspect: `08-interconnect-map.md` content matches expectations from current `/agent-teams:team-review` Phase 1b output style

### Scenario 3: layer-split repo with lite depth
- Target: a repo with `src/backend/` (Python) and `src/frontend/` (TS)
- Command: `/agent-teams:team-deep-dive src/ --depth=lite`
- Verify: auto-detect proposes 2 partitions; lite mode skips workers B
- Inspect: only `01-structure.md`, `02-interfaces.md`, `05-risks.md`, `07-final-report.md`, `08-interconnect-map.md` exist in `.deep-dive/`; agent count = 2*2 + 2 = 6

### Scenario 4: resume from interrupt
- Run scenario 1, but Ctrl+C during Wave 2
- Re-run the same command
- Verify: pre-flight detects in-progress session and offers resume; only missing Wave 2 workers are re-spawned; Phase 2 and Phase 3 run after resumed Wave 2 completes

### Scenario 5: downstream pickup
- After scenario 1 completes, run `/agent-teams:team-review .` on the same target
- Verify: team-review Phase 1a finds existing `.deep-dive/` and does not regenerate
- Verify: team-review writes to `.team-review/` without conflict
```

- [ ] **Step 6: Commit the smoke test plan**

```bash
git add docs/plans/2026-05-20-deep-dive-team-mode-plan.md
git commit -m "Document team-deep-dive smoke test plan for post-merge verification

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 7: Push to remote**

After confirming all 8 commits look correct (`git log --oneline -10`):

```bash
git push origin master
```

Expected: push succeeds; new commits visible on `acaprino/claude-code-daodan`.

---

## Self-Review Checklist (run after writing the plan, before handing off)

These are NOT execution steps. They are the plan author's checks against the spec.

**1. Spec coverage — every section in the design doc is implemented:**

| Spec section                                                  | Plan task           |
|---------------------------------------------------------------|---------------------|
| Pipeline architecture (Phase 0-3)                             | Task 5              |
| Partition detection algorithm                                 | Task 5 (Phase 0)    |
| Agent roster: partition-structure-worker                      | Task 1              |
| Agent roster: partition-behavior-worker                       | Task 2              |
| Agent roster: partition-quality-worker                        | Task 3              |
| Agent roster: deep-dive-synthesizer                           | Task 4              |
| Reuse of semantic-interconnect-mapper                         | Task 5 (Phase 3)    |
| Spawn prompt template                                         | Task 5              |
| Output layout (`.deep-dive/partitions/...` + consolidated)    | Tasks 1-5           |
| state.json schema                                             | Task 5 (Phase 0)    |
| Resume semantics                                              | Task 5 (Resume Logic) |
| Failure handling                                              | Tasks 4, 5          |
| CLI flag mapping                                              | Task 5 (Pre-flight) |
| Integration with team-review / codebase-mapper / project-setup| Implicit (no changes needed; documented in Task 7 SKILL.md) |
| Marketplace registration                                      | Task 6              |
| Testing strategy                                              | Task 8 (smoke test plan only; no execution in this PR) |

**2. Placeholder scan — verified no occurrence of `TBD`, `TODO`, `???`, "fill in later", "similar to Task N" in this plan.**

**3. Type consistency — verified:**
   - Agent file names match `name:` frontmatter in all 4 new agents
   - Agent identifiers in spawn prompts (`P<i>.A`, `P<i>.B`, `P<i>.C`, `SYNTH`) are used consistently across Task 5
   - Output paths are identical across the agent definitions (Tasks 1-4) and the spawn prompts (Task 5)
   - State.json field names (`partitions[].status`, `phases.phase_*`) are identical between Phase 0 init (Task 5) and Resume Logic (Task 5)
   - Marketplace.json version numbers (`1.10.0 -> 1.11.0`, `2.12.0 -> 2.13.0`, `6.20.0 -> 6.21.0`) match across the task description and the verification step
