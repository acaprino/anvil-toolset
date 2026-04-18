---
name: marketplace-audit
description: >
  Validate the integrity of any Claude Code plugin marketplace. Use PROACTIVELY before any commit that modifies plugin files or marketplace.json. Checks marketplace.json consistency, verifies all referenced files exist, validates frontmatter fields, detects orphaned plugins/skills/agents/commands, and reports naming convention violations.
  TRIGGER WHEN: before any commit that modifies plugin files or marketplace.json; when the user asks to verify marketplace.json integrity, find orphan files, or check naming conventions in a Claude Code plugin marketplace.
  DO NOT TRIGGER WHEN: the task is AI-powered content quality review (use marketplace-review) or scaffolding new plugins (use marketplace-scaffold-plugin / skills-creator).
---

# Marketplace Audit

Run a comprehensive structural validation of any Claude Code plugin marketplace. Works against any project that follows the standard `.claude-plugin/marketplace.json` + `plugins/<name>/` layout.

## Audit steps

### Step 1: Run the validation script

Execute the audit script to get a machine-readable report:

```bash
# Validate only
python "${CLAUDE_PLUGIN_ROOT}/skills/marketplace-audit/scripts/audit_marketplace.py"

# Validate and auto-fix color issues (invalid, missing, disharmonious)
python "${CLAUDE_PLUGIN_ROOT}/skills/marketplace-audit/scripts/audit_marketplace.py" --fix
```

The script resolves the target project root by walking up from the script location, or respects a `--project-root <path>` flag if invoking it from a different marketplace than where the plugin is installed.

### Step 2: Review findings

The script checks:

1. **File existence** -- every path in marketplace.json `agents` / `skills` / `commands` arrays resolves to a real file or directory
2. **Orphaned files** -- agent `.md` files, skill directories, or command `.md` files on disk not registered in any plugin
3. **Frontmatter validation**
   - Agents: must have `name`, `description`, `model`, `color`
   - Skills: must have `name`, `description`
   - Commands: must have `description`
4. **Color consistency and harmony**
   - All agents within a plugin should use the same color
   - Warn when a single color is overused across too many plugins (threshold configurable)
   - Report color distribution across all plugins
   - Valid colors: red, blue, green, yellow, purple, orange, pink, cyan
   - Use `--fix` to auto-correct invalid or missing colors
5. **Naming conventions**
   - All names are kebab-case
   - Agent filename matches frontmatter `name` field
   - Plugin directory name matches marketplace.json `name` field
   - Skill directory name matches frontmatter `name` field
   - Workflow command output directories match command filename (e.g., `feature-e2e.md` typically writes to `.feature-e2e/`)
   - No naming collisions between commands in different plugins
   - No em dash characters anywhere (use hyphen `-` or double hyphen `--`)
6. **Cross-reference consistency (project-specific, best-effort)**
   - If a git remote is configured, suggest that the marketplace `name` align with the repo name (warning only)
   - If a `CLAUDE.md` is present at the project root, suggest that its project header match the marketplace name (warning only)
   - These are advisory -- different marketplace maintainers have different conventions
7. **Marketplace.json schema**
   - Every plugin has: `name`, `source`, `description`, `version`, `author`, `license`, `keywords`, `category`, `strict`
   - No duplicate plugin names
   - Duplicate keywords across plugins (warning only -- may be intentional)
8. **Version sanity**
   - All versions are valid semver (`MAJOR.MINOR.PATCH`)
   - `metadata.version` is present at the root

### Step 3: Fix issues

Address findings by severity:

- **CRITICAL**: Missing referenced files, broken paths, missing required frontmatter fields, duplicate plugin names
- **WARNING**: Orphaned files, naming mismatches, overlapping keywords, color inconsistencies, git/CLAUDE.md alignment
- **INFO**: Suggestions for improvement, consolidation opportunities

### Step 4: Evaluate color harmony

After the script passes, review the color distribution and evaluate semantic harmony:

1. Read each plugin's description and category from marketplace.json
2. Consider domain: similar domains should have visually related colors; distinct domains should contrast
3. Guiding principles:
   - Warm colors (red, orange, yellow, pink) for creative / outward-facing plugins
   - Cool colors (blue, cyan, purple) for analytical / development plugins
   - Neutral (green) for tooling / infrastructure
4. If colors feel disharmonious, propose a new assignment with reasoning and apply after user confirmation

### Step 5: Re-validate

Run the script again after fixes to confirm a clean audit.

## Notes for marketplace maintainers

- This skill is marketplace-agnostic. It assumes the standard Claude Code plugin layout (`.claude-plugin/marketplace.json` + `plugins/<name>/`) but makes no assumption about which plugins, authors, or upstream sources are specific to your marketplace.
- Plugin categories, default author, upstream sources, and any project-specific conventions should be documented in your `CLAUDE.md` at the project root. The script and this skill respect those conventions but do not enforce a particular taxonomy.
