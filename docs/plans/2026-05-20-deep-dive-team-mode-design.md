# Deep-Dive Team Mode — Design

**Date:** 2026-05-20
**Status:** Approved (brainstorming complete, ready for implementation plan)
**Author:** Alfio Caprino (with Claude Opus 4.7)

## Goal

Add an opt-in multi-agent team variant of `/deep-dive-analysis` that partitions large or monorepo codebases by directory/workspace/language, runs N parallel deep-dive instances per partition, then synthesizes a consolidated `.deep-dive/01..07.md` plus a new global interconnection map at `.deep-dive/08-interconnect-map.md`.

The classic `/deep-dive-analysis` command stays untouched for small projects and for users who do not want team-mode overhead.

## Constraints and non-goals

**In scope:**
- New command `/agent-teams:team-deep-dive`
- Four new agents under `plugins/deep-dive-analysis/agents/`
- Reuse the existing `senior-review:semantic-interconnect-mapper` agent unchanged
- Backward-compatible output layout so `/agent-teams:team-review`, `/codebase-mapper:map-codebase`, `/project-setup:create-claude-md`, and `/project-setup:maintain-claude-md` pick up team-mode output automatically

**Out of scope (post-launch, separate work):**
- Modifying `team-review` Phase 1b to reuse `.deep-dive/08-interconnect-map.md` when present
- Modifying `codebase-mapper:codebase-explorer` to leverage existing `.deep-dive/`
- Sharing prompt fragments between classic and team-mode workers (they are prompts, not runtime code; light duplication is acceptable)
- Implementing `--phase N` override in team mode

## Architectural decisions

These were locked through brainstorming Q&A:

| Decision                             | Choice                                                                                         |
|--------------------------------------|------------------------------------------------------------------------------------------------|
| Plugin home                          | New command in `agent-teams/`. Classic command untouched.                                       |
| Partitioning trigger                 | Auto-suggest at scope checkpoint, user confirms (Accept / Modify / Manual / Cancel)             |
| Per-partition agent count            | 3 workers per partition mirroring the classic 3-agent flow                                      |
| Synthesis architecture               | Synthesizer agent (mechanical merge + final report) followed by separate interconnect-mapper run|
| Partition cap                        | None. User is responsible for scope at the checkpoint.                                          |
| Cross-partition awareness            | Wave 2 workers can read all partitions' Wave 1 outputs (structures + interfaces) read-only      |

## Pipeline architecture

Four sequential phases, with maximum parallelism inside Phase 1.

```
Phase 0: Pre-flight + Partition Detection                       (main context)
  - Parse flags, init .deep-dive/state.json (mode: team)
  - Scan target via heuristic chain (workspaces -> conventions -> layer -> language -> fallback)
  - Propose partitioning at scope checkpoint
  - User chooses Accept / Modify / Manual / Cancel
  - Lock partition list in state.json
        |
        v
Phase 1: Partition Workers                                       (parallel, 3N agents)
  Per partition P_i, spawn 3 teammates:
    P_i.A (partition-structure-worker)  -> partitions/<P_i>/01-structure.md, 02-interfaces.md
    P_i.B (partition-behavior-worker)   -> partitions/<P_i>/03-flows.md, 04-semantics.md
    P_i.C (partition-quality-worker)    -> partitions/<P_i>/05-risks.md, 06-documentation.md

  Task dependencies (declared via addBlockedBy):
    Each P_i.B and P_i.C is blocked by ALL P_j.A (j=1..N), not only its own P_i.A.
    This creates a global barrier so Wave 2 workers can read every partition's
    01-structure.md and 02-interfaces.md (needed for cross-partition citations).

  Effective execution:
    Wave 1 (parallel): all P_i.A
    Global barrier: wait until every P_j.A completes
    Wave 2 (parallel): all P_i.B and all P_i.C
        |
        v
Phase 2: Synthesis                                               (sequential, 1 agent)
  deep-dive-synthesizer reads .deep-dive/partitions/*/ and writes:
    .deep-dive/01-structure.md       (unified inventory + cross-partition deps annotated)
    .deep-dive/02-interfaces.md      (per-partition + "Cross-partition exports" section)
    .deep-dive/03-flows.md           (per-partition + "Cross-partition flows" section)
    .deep-dive/04-semantics.md       (per-partition + "Cross-partition ADR" section)
    .deep-dive/05-risks.md           (concatenated, sorted by global severity)
    .deep-dive/06-documentation.md   (concatenated)
    .deep-dive/07-final-report.md    (team-mode template with Partition Map and Topology)
        |
        v
Phase 3: Interconnect Map                                        (sequential, 1 agent)
  senior-review:semantic-interconnect-mapper reads .deep-dive/01..07.md (the consolidated set)
  and writes .deep-dive/08-interconnect-map.md
  with Call Graph cross-partition (2-3 hop), Contracts (formal/structural/implicit),
  Invariants, Domain Rules, Assumptions, Integration Hot-Spots, Change Impact Radius.
```

**Total agents spawned:** `3N + 2` (where N = number of partitions).
**Total output files:** `6N` (per-partition reports) + `8` (consolidated + interconnect map) = `6N + 8`.

## Partition detection algorithm

Executed in Phase 0 by the main context (no agent). First rule that matches wins.

1. **Explicit workspace manifests**, in order:
   - `pnpm-workspace.yaml` -> `packages` field
   - `package.json` with `workspaces` field (npm/yarn)
   - `lerna.json` with `packages`
   - `nx.json` + `apps/` + `libs/`
   - `turbo.json` + `apps/` + `packages/`
   - `Cargo.toml` with `[workspace] members`
   - `pyproject.toml` with `[tool.uv.workspace] members` or equivalent
2. **Convention-based monorepo:**
   - `apps/`, `packages/`, or `services/` at root with more than one subdirectory
   - `src/` with subdirectories that have their own `package.json` / `pyproject.toml`
3. **Layer split:**
   - `src/{backend,frontend}`, `src/{api,web}`, `src/{server,client}`, or `backend/` + `frontend/` at root
4. **Language split:**
   - Use `classifier.py` to count files per language
   - If 2 or more languages with at least 20 files each: partition per language
5. **Fallback:** single partition wrapping the entire target, named `root`.

**Excluded paths (always):** `node_modules/`, `dist/`, `build/`, `.next/`, `target/`, `vendor/`, `__pycache__/`, `.venv/`. Hard-coded.

**Partition naming rules:**
1. From workspace path -> basename (`packages/api` -> `api`)
2. On basename collision -> slug-ified full path (`packages-api`, `services-api`)
3. From language fallback -> language name (`python`, `typescript`)
4. From single-partition fallback -> `root`

Allowed characters: `[a-z0-9-]`. Normalize lowercase, separators -> hyphen, strip accents.

**Checkpoint prompt format:**

```
Deep-dive team-mode scope:
Target: <target path>

Detected partitioning strategy: <strategy name>

Proposed partitions (<N>):
  P1: <path>          (<language>, <file-count> files, ~<loc>k LOC)
  ...

Spawn plan: <N> partitions × 3 agents = <3N> workers + 1 synthesizer + 1 interconnect-mapper = <3N+2> agents total.

Options:
  [A] Accept and start
  [M] Modify partition list (rename, regroup, exclude one)
  [m] Manual: provide your own partition paths
  [c] Cancel
```

## Agent roster

Four new agents in `plugins/deep-dive-analysis/agents/`, plus one reused from `senior-review`.

### `deep-dive-analysis:partition-structure-worker` (new)

- **Coverage:** Phase 1 (Structure) + Phase 2 (Interfaces) for one partition
- **File ownership:** only `.deep-dive/partitions/<name>/01-structure.md` and `02-interfaces.md`
- **Reads:** the partition path + scripts in `${CLAUDE_PLUGIN_ROOT}/skills/deep-dive-analysis/scripts/`
- **Tools:** `Read, Glob, Grep, Bash, Write`
- **Color:** `cyan`
- **Body:** condensed from Phase 1 + 2 sections of the classic command, parameterized on partition path

### `deep-dive-analysis:partition-behavior-worker` (new)

- **Coverage:** Phase 3 (Flows) + Phase 4 (Semantics)
- **File ownership:** only `.deep-dive/partitions/<name>/03-flows.md` and `04-semantics.md`
- **Reads:** own partition + all `.deep-dive/partitions/*/01-structure.md` and `02-interfaces.md`
- **Cross-partition citation contract:** when an outgoing call/import leaves the partition, cite it as `<other-partition>::<symbol>` instead of `external`
- **Tools:** `Read, Glob, Grep, Bash, Write`
- **Color:** `cyan`

### `deep-dive-analysis:partition-quality-worker` (new)

- **Coverage:** Phase 5 (Risks) + Phase 6 (Documentation)
- **File ownership:** only `.deep-dive/partitions/<name>/05-risks.md` and `06-documentation.md`
- **Reads:** own partition + all `.deep-dive/partitions/*/01-structure.md` and `02-interfaces.md`
- **Tools:** `Read, Glob, Grep, Bash, Write` (Bash for `usage_finder.py`, `doc_review.py`, `rewrite_comments.py`)
- **Color:** `cyan`

### `deep-dive-analysis:deep-dive-synthesizer` (new)

- **Coverage:** consolidate Phase 1-6 across partitions + write Phase 7 (final report)
- **File ownership:** only `.deep-dive/01-structure.md` through `07-final-report.md`
- **Reads:** all of `.deep-dive/partitions/*/`
- **Tools:** `Read, Glob, Grep, Write` (no Bash; pure text synthesis)
- **Color:** `purple`
- **Per-file synthesis logic:**
  - `01-structure.md`: unified file inventory; dependency graph with cross-partition edges annotated `(cross:P_i->P_j)`; global entry points list
  - `02-interfaces.md`: per-partition API tables + `## Cross-partition exports` section listing symbols actually imported by other partitions
  - `03-flows.md`: per-partition flows + `## Cross-partition flows` section marking partitions involved
  - `04-semantics.md`: per-partition ADR + `## Cross-partition ADR` section with global architecture decisions ("API talks to worker only via queue", "Frontend never calls DB directly")
  - `05-risks.md`: all risks concatenated, sorted by severity globally, annotated with originating partition
  - `06-documentation.md`: aggregated doc gaps with per-partition priority
  - `07-final-report.md`: team-mode template adding `## Partition Map`, `## Cross-Partition Topology`, `## Per-Partition Health Scorecard` to the classic template

### `senior-review:semantic-interconnect-mapper` (reused, unchanged)

- **Invocation in Phase 3:** primary context source = `.deep-dive/01-07.md` (consolidated); output path = `.deep-dive/08-interconnect-map.md`; target files = entire target (union of partitions)
- No modifications to the agent definition

## Spawn prompt template (partition workers)

```
You are <Type> on partition "<name>".

Identity: P_<index>.<A|B|C>
Owned files:
  - .deep-dive/partitions/<name>/<file1>
  - .deep-dive/partitions/<name>/<file2>
DO NOT touch any other file under .deep-dive/.

Target path for this partition: <path>
Active flags from main command: --critical=<bool> --comments=<bool> --depth=<lite|full>

Required reads before writing:
  - <partition path>: all source files within scope
  - ${CLAUDE_PLUGIN_ROOT}/skills/deep-dive-analysis/SKILL.md
  - [Wave 2 only] .deep-dive/partitions/*/01-structure.md and 02-interfaces.md

Cross-partition citations: when you find an outgoing call/import that leaves
your partition, cite it as <other-partition>::<symbol> using the structures
available in .deep-dive/partitions/*/01-structure.md.

Completion: when done, call TaskUpdate to mark your task completed.
```

## Filesystem layout

```
.deep-dive/
├── state.json
├── partitions/
│   ├── <partition-1>/
│   │   ├── 01-structure.md
│   │   ├── 02-interfaces.md
│   │   ├── 03-flows.md
│   │   ├── 04-semantics.md
│   │   ├── 05-risks.md
│   │   └── 06-documentation.md
│   └── <partition-2>/
│       └── ...
├── 01-structure.md          ← consolidated (backward-compat with classic)
├── 02-interfaces.md
├── 03-flows.md
├── 04-semantics.md
├── 05-risks.md
├── 06-documentation.md
├── 07-final-report.md
└── 08-interconnect-map.md   ← new, from semantic-interconnect-mapper
```

Compatibility guarantee: `.deep-dive/01..07.md` is indistinguishable to downstream consumers from classic-mode output. `team-review` and `codebase-mapper` need zero changes.

## State management

### state.json schema (team mode)

```json
{
  "target": "<original target path>",
  "mode": "team",
  "status": "in_progress | complete | failed",
  "flags": {
    "critical": false,
    "comments": false,
    "depth": "full"
  },
  "partitions": [
    {
      "name": "api",
      "path": "packages/api",
      "language_primary": "python",
      "file_count": 142,
      "loc_estimate": 12000,
      "status": "pending | structure_done | done | failed"
    }
  ],
  "phases": {
    "phase_0_detection": "pending | complete",
    "phase_1_partition_workers": "pending | wave1_done | complete | failed",
    "phase_2_synthesis": "pending | complete | failed",
    "phase_3_interconnect": "pending | complete | failed"
  },
  "agents_spawned": [
    {"name": "P1.A", "type": "partition-structure-worker", "partition": "api", "task_id": "..."}
  ],
  "files_created": [],
  "started_at": "ISO_TIMESTAMP",
  "completed_at": "ISO_TIMESTAMP | null"
}
```

### Resume semantics

Pre-flight checks `.deep-dive/state.json`:

- `mode == "team"` and `status == "in_progress"`: offer resume by phase
  - Phase 0 incomplete -> discard, restart from zero
  - Phase 1 incomplete with `wave1_done`: re-spawn only Wave 2 workers (B and C) for partitions where `status == "structure_done"`
  - Phase 1 incomplete with Wave 2 in flight: re-spawn only B and C for partitions with `status != "done"`
  - Phase 2 incomplete: re-spawn synthesizer; partition files are ready
  - Phase 3 incomplete: re-spawn interconnect-mapper; consolidated set is ready
- `mode == "classic"`: refuse to start, ask user to archive the classic session first

### Failure handling

- **Partition worker failure:** that partition marked `failed`. Other partitions continue. Synthesizer runs anyway, receives the failed list, writes `⚠ Missing partitions: <list>` callout in each consolidated file. `07-final-report.md` opens with an explicit partial-completeness warning.
- **Synthesizer failure:** stop. Mark `phase_2_synthesis: "failed"` and `phase_3_interconnect: "skipped_due_to_phase_2_failure"`. User sees per-partition files; can resume.
- **Interconnect-mapper failure:** deep-dive considered complete (files 01-07 exist). `08-interconnect-map.md` marked `failed` in state.json; warning shown, not blocking error.

### Idempotency

All workers write via `Write` on their owned files. Re-spawning a worker on its target produces a deterministic overwrite. No append, no cumulative state.

## CLI flags

### Propagated from classic command

| Flag             | Type   | Default | Behavior in team mode                                                                  |
|------------------|--------|---------|----------------------------------------------------------------------------------------|
| `--critical`     | bool   | false   | Propagated to every worker B (priority on auth/payment/persistence in Phase 3-4)        |
| `--comments`     | bool   | false   | Propagated to every worker C (Phase 6 activates comment audit)                          |
| `--depth=lite\|full` | enum   | full    | `lite` skips Phase 3-4: worker B not spawned. Workers A and C run as usual.             |

### Team-mode-specific

| Flag                   | Type   | Default | Behavior                                                                              |
|------------------------|--------|---------|---------------------------------------------------------------------------------------|
| `--partition <path>`   | repeat | none    | Manual mode: forces partition list. Can be repeated.                                  |
| `--partition-name <n>` | repeat | none    | Used with `--partition`: symbolic name for the N-th partition (1-indexed)             |
| `--skip-interconnect`  | bool   | false   | Skip Phase 3. Output ends at `.deep-dive/07-final-report.md`.                          |
| `--skip-synthesis`     | bool   | false   | Skip Phase 2 AND Phase 3 (interconnect-mapper depends on consolidated files). Output: per-partition files only. |
| `--yes`                | bool   | false   | Auto-accept partition checkpoint (for scripting)                                      |

### Unsupported flags (return error with suggestion)

- `--phase N`: distributed phases cannot be skipped individually. Suggest classic `/deep-dive-analysis --phase N`.
- `--docs-only`: same. Suggest classic `/deep-dive-analysis --docs-only`.

### `--depth=lite` precise semantics

- Worker A spawned: yes
- Worker B spawned: no
- Worker C spawned: yes
- Synthesizer writes: `01-structure.md`, `02-interfaces.md`, `05-risks.md`, `07-final-report.md` (condensed). Skips 03, 04, 06.
- Interconnect-mapper runs normally on available files.
- Agent count `lite`: `2N + 2` instead of `3N + 2`.

## Integration with existing pipelines

### `/agent-teams:team-review`

Already compatible, zero modifications needed:
- Phase 1a picks up `.deep-dive/01-07.md` regardless of source mode
- Phase 1b spawns its own `semantic-interconnect-mapper` writing to `.team-review/interconnect.md`; no conflict with our `.deep-dive/08-interconnect-map.md`

Post-launch optimization (out of scope for v1): teach team-review to reuse `.deep-dive/08-interconnect-map.md` when present and recent.

### `/codebase-mapper:map-codebase`

Already compatible, zero modifications needed.

Post-launch optimization (out of scope for v1): teach `codebase-explorer` to use `.deep-dive/01-07.md` as a hint when present.

### `/project-setup:create-claude-md` and `/project-setup:maintain-claude-md`

Already compatible: both auto-detect `.deep-dive/` and use it as ground truth.

### Completion menu re-entry

Team mode replicates the classic Next Steps Menu with one extra option:

```
What would you like to do next?

1. Start fixing
2. Apply quick fixes
3. Deep dive further
4. Generate documentation
5. Run code review - launch /agent-teams:team-review (reuses this .deep-dive/ + 08-interconnect-map.md)
6. Export report
7. Nothing for now
```

## Files to create / modify

### Create (5 new files)

1. `plugins/agent-teams/commands/team-deep-dive.md`
2. `plugins/deep-dive-analysis/agents/partition-structure-worker.md`
3. `plugins/deep-dive-analysis/agents/partition-behavior-worker.md`
4. `plugins/deep-dive-analysis/agents/partition-quality-worker.md`
5. `plugins/deep-dive-analysis/agents/deep-dive-synthesizer.md`

### Modify (2-3 existing files)

1. `.claude-plugin/marketplace.json`:
   - `deep-dive-analysis`: bump `version` (minor: new agents); add the 4 agent paths
   - `agent-teams`: bump `version` (minor: new command); add `commands/team-deep-dive.md`
   - `metadata.version`: bump patch
2. `plugins/deep-dive-analysis/skills/deep-dive-analysis/SKILL.md`: add a `## Team Mode Integration` section explaining when to choose classic vs team
3. `CLAUDE.md`: no change required (plugin count stays 43; deep-dive-analysis is a custom plugin, no sync table entry needed)

### Intentionally NOT modified

- `plugins/deep-dive-analysis/commands/deep-dive-analysis.md`: classic command stays intact
- `plugins/agent-teams/agents/*.md`: the 4 team agents (lead, implementer, reviewer, debugger) are not used here; we use dedicated agents in the deep-dive-analysis plugin
- `plugins/senior-review/agents/semantic-interconnect-mapper.md`: reused as-is

## Testing strategy

The marketplace has no automated tests. Verification is manual, scripted, and layered.

**Level 1 — Structural validation (deterministic):**
- Grep for stale tool names (`Teammate`, `Task tool to spawn`, `spawnTeam`)
- Grep for dash-aside construct in new files
- Grep for references to non-existent paths
- JSON validate `marketplace.json`
- Run `marketplace-ops:marketplace-health` skill

**Level 2 — Skill/agent quality validation (AI-driven):**
- Run `marketplace-ops:skills-validate` on the 4 new agents (frontmatter, activation, token budget)

**Level 3 — Smoke tests (manual, three representative cases):**
1. **pnpm monorepo** with 3 packages
   - `/agent-teams:team-deep-dive .`
   - Verify auto-detect proposes 3 partitions from workspaces
   - Accept, wait, verify filesystem layout and cross-partition citations in `08-interconnect-map.md`
2. **Flat single-language Python repo**
   - `/agent-teams:team-deep-dive src/`
   - Verify auto-detect falls back to 1 partition
   - Verify `08-interconnect-map.md` content roughly equivalent to current `team-review` Phase 1b output
3. **Layer split repo** (`src/backend` Python + `src/frontend` TS)
   - Verify 2 partitions proposed
   - Run with `--depth=lite`
   - Verify only `01`, `02`, `05`, `07`, `08` exist; agent count = `2*2 + 2 = 6`

**Level 4 — Downstream pickup validation:**
- After team-deep-dive on a real target, run `/agent-teams:team-review .`
- Verify team-review Phase 1a picks up existing `.deep-dive/` (no regeneration)
- Verify team-review writes to `.team-review/` (no path conflict)

**Level 5 — Resume test:**
- Start team-deep-dive, interrupt during Wave 2
- Re-launch: verify pre-flight detects in-progress session and offers resume
- Accept resume: verify only missing workers are re-spawned

## Open questions / risks

- **Cost transparency:** the checkpoint shows agent count but not estimated cost. Users on metered tiers should be aware. Mitigation: include a one-line note in the checkpoint ("Token cost scales roughly linearly with file count × agents; consider `--depth=lite` for monorepos > 10 partitions").
- **Cross-partition flow tracing fidelity:** Wave 2 workers see other partitions' structures but not their flows. A flow that traverses 3 partitions might be reported 3 times with different framing. Mitigation: the synthesizer's `## Cross-partition flows` section explicitly deduplicates; interconnect-mapper Call Graph also normalizes.
- **Partition naming collisions:** rare but possible (e.g., two `core` subdirectories). Algorithm covers it via slug-ified path, but the resulting names (`packages-core`, `services-core`) may be ugly. Acceptable trade-off.
- **`marketplace-ops:skills-validate` may flag the new agents:** if so, iterate on frontmatter before commit. This is normal.

## Approval status

All 6 design sections approved interactively. Ready for:
1. Spec self-review (this document)
2. User review of this document
3. Hand-off to `ai-tooling:writing-plans` for the implementation plan
