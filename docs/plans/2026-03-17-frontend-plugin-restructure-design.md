# Frontend Plugin: Reorganize to 2 Agents + Unified Skill

## Context

The frontend plugin currently has 4 agents with overlapping responsibilities and 6 skills. Three agents (ui-ux-designer, ui-polisher, css-master) are web-specific and should be merged into one `web-designer` agent. The fourth (ui-layout-designer) is platform-agnostic and stays separate. The `css-master` skill merges into a new unified `frontend` skill alongside the agent reference files. Component library skills (shadcn-ui, daisyui, radix-ui) remain separate since they are alternatives, not layers.

## Current State

```
agents/
  css-master.md               # CSS architecture, migration, modern features
  ui-layout-designer.md       # Universal layout/grid/spatial composition
  ui-polisher.md              # Animations, micro-interactions, polish
  ui-ux-designer.md           # Design systems, UX psychology, accessibility
  references/                 # Shared agent references
    flow-patterns.md
    layout-patterns.md
    ui-pattern-guide.md
    ux-patterns.md
skills/
  css-master/                 # CSS reference + architecture
    SKILL.md
    references/
      css-patterns.md
      argyle-cacadia-2025-deck.md  (upstream-synced from paulirish/dotfiles)
  frontend-design/            # Upstream-synced from anthropics/claude-code
  premium-web-consultant/     # Consulting workflow + templates
  shadcn-ui/                  # Component library
  daisyui/                    # Component library
  radix-ui/                   # Component library
```

## Target State

```
agents/
  web-designer.md             # Merged: CSS + polish + UX (web-specific)
  ui-layout-designer.md       # KEEP as-is (universal)
skills/
  frontend/                   # NEW unified web knowledge base
    SKILL.md
    references/
      css-patterns.md           # from css-master skill
      argyle-cacadia-2025-deck.md  # from css-master skill (upstream-synced)
      flow-patterns.md          # from agents/references/
      layout-patterns.md        # from agents/references/
      ui-pattern-guide.md       # from agents/references/
      ux-patterns.md            # from agents/references/
  frontend-design/            # KEEP (upstream-synced)
  premium-web-consultant/     # KEEP (consulting workflow)
  shadcn-ui/                  # KEEP (library-specific)
  daisyui/                    # KEEP (library-specific)
  radix-ui/                   # KEEP (library-specific)
```

## Design Decisions

### Why merge 3 agents into 1?

The current 4 agents have explicit `<agent_delegation>` sections that say "if X, STOP and recommend agent Y". This creates ping-pong between agents for common web tasks that span CSS + polish + UX. A single `web-designer` agent handles all web-specific concerns without delegation overhead.

### Why keep ui-layout-designer separate?

Layout/spatial composition applies to desktop apps, mobile apps, web apps, and any visual interface. It is not web-specific. Merging it into `web-designer` would reduce its applicability.

### Why keep component library skills separate?

shadcn-ui, daisyui, and radix-ui are alternatives to each other. A project uses one, not all three. Merging them loads irrelevant docs and dilutes trigger precision. They are distinct knowledge bases with specific trigger words.

### Why not keep css-master as a separate skill?

CSS is a core web concern. The css-master skill's references (css-patterns.md, argyle-cacadia-2025-deck.md) are web-specific knowledge that belongs in the unified frontend skill alongside UX and UI patterns.

**Note:** All paths in Steps 1-3 are relative to `plugins/frontend/`. Use `git mv` for all moves to preserve history.

## Implementation Steps

### Step 1: Create unified frontend skill directory and move references

- Create `plugins/frontend/skills/frontend/SKILL.md` (unified entry point with sections for CSS, UX patterns, UI patterns, flow patterns)
- `git mv` `skills/css-master/references/css-patterns.md` to `skills/frontend/references/`
- `git mv` `skills/css-master/references/argyle-cacadia-2025-deck.md` to `skills/frontend/references/`
- `git mv` `agents/references/flow-patterns.md` to `skills/frontend/references/`
- `git mv` `agents/references/layout-patterns.md` to `skills/frontend/references/`
- `git mv` `agents/references/ui-pattern-guide.md` to `skills/frontend/references/`
- `git mv` `agents/references/ux-patterns.md` to `skills/frontend/references/`
- Delete `skills/css-master/SKILL.md`
- Delete `skills/css-master/` directory
- Delete `agents/references/` directory

### Step 2: Create web-designer.md agent

Merge knowledge from ui-ux-designer + ui-polisher + css-master into a single agent:

- `name: web-designer`
- `description:` web-specific frontend expert covering CSS architecture, animations/polish, design systems, UX psychology, accessibility, and visual design. Use proactively for any web UI work.
- `model: opus`
- `tools: Read, Write, Edit, Bash, Glob, Grep`
- `color: purple`

Body structure (merged from all 3 agents):
- Core philosophy: combine css-master philosophy (native CSS first, specificity is architecture) + ui-polisher philosophy (animation is communication, restraint over excess) + ui-ux-designer philosophy (design tokens first, accessibility baked in)
- Core expertise: CSS architecture + modern CSS, animations + micro-interactions + motion narrative, design systems + UX psychology + accessibility
- Execution flow: context discovery, design execution, polish pass, handoff
- Technical patterns: CSS (from css-master), Motion/Framer Motion/GSAP (from ui-polisher), design token systems (from ui-ux-designer)
- Rules to enforce: merge all `<rules_to_enforce>` sections (animation constants, easing rules, CSS architecture rules, UX laws, production details)
- Modern browser APIs: View Transitions, @starting-style, scroll-driven animations (from ui-polisher)
- Quality checklist: merge all 3 checklists
- Tool directives: merge all 3
- Testing directives: merge all 3
- Agent delegation: only delegate to `ui-layout-designer` (for layout structure) and `react-performance-optimizer` (for React re-renders). Remove all cross-delegation between the 3 merged agents.

### Step 3: Delete old agent files

- Delete `agents/ui-polisher.md`
- Delete `agents/ui-ux-designer.md`
- Delete `agents/css-master.md`

### Step 4: Update marketplace.json

- Update agents array: `["./agents/web-designer.md", "./agents/ui-layout-designer.md"]`
- Update skills array: replace `"./skills/css-master"` with `"./skills/frontend"`, keep the other 5
- Keep commands array unchanged: `["./commands/review-design.md"]`
- Bump plugin version (3.4.0 -> 3.5.0)
- Bump metadata version

### Step 5: Update docs/plugins/frontend.md

- Reflect 2 agents + 6 skills structure
- Update agent descriptions and invocation examples
- Update skill listing (frontend replaces css-master)

### Step 6: Update CLAUDE.md

- Update plugin count if it changes (it doesn't -- still 33 plugins)
- Update upstream sync table: change `frontend (css-master)` row identifier to `frontend (frontend)`
- Update local file paths in the sync table: `plugins/frontend/skills/css-master/SKILL.md` -> `plugins/frontend/skills/frontend/SKILL.md` and `plugins/frontend/skills/css-master/references/argyle-cacadia-2025-deck.md` -> `plugins/frontend/skills/frontend/references/argyle-cacadia-2025-deck.md`
- Update the corresponding `gh api` sync commands section with the new local target paths

## Files to Create

- `plugins/frontend/agents/web-designer.md`
- `plugins/frontend/skills/frontend/SKILL.md`

## Files to Move (git mv)

- `skills/css-master/references/css-patterns.md` -> `skills/frontend/references/`
- `skills/css-master/references/argyle-cacadia-2025-deck.md` -> `skills/frontend/references/`
- `agents/references/flow-patterns.md` -> `skills/frontend/references/`
- `agents/references/layout-patterns.md` -> `skills/frontend/references/`
- `agents/references/ui-pattern-guide.md` -> `skills/frontend/references/`
- `agents/references/ux-patterns.md` -> `skills/frontend/references/`

## Files to Delete

- `agents/ui-polisher.md`
- `agents/ui-ux-designer.md`
- `agents/css-master.md`
- `skills/css-master/SKILL.md`
- `agents/references/` (directory, after moving contents)

## Files to Modify

- `.claude-plugin/marketplace.json`
- `docs/plugins/frontend.md`

## Upstream Sync Impact

- `css-master` skill references include `argyle-cacadia-2025-deck.md` synced from `paulirish/dotfiles`. Moving it to `skills/frontend/references/` means the CLAUDE.md upstream sync table needs updating (local path changes).
- `frontend-design` skill is untouched -- no upstream sync impact.

## Verification

1. `ls plugins/frontend/skills/frontend/references/` -- expect 6 files
2. `ls plugins/frontend/agents/` -- expect 2 files: web-designer.md, ui-layout-designer.md
3. `ls plugins/frontend/skills/` -- expect 6 dirs: frontend, frontend-design, premium-web-consultant, shadcn-ui, daisyui, radix-ui
4. `python -c "import json; json.load(open('.claude-plugin/marketplace.json'))"` -- valid JSON
5. No orphan references in old directories
6. SKILL.md links point to existing reference files
