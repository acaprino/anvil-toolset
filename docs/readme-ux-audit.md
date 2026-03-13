# README.md UX & Conversion Audit

**File:** `README.md` (1746 lines)
**Context:** Open-source Claude Code plugin marketplace on GitHub
**Audience:** Developers using Claude Code who want to extend it with plugins
**Date:** 2026-03-11

---

## Executive Summary

### Top 3 Conversion Blockers

1. **No value proposition or "why" section** - The page opens with a dry description and jumps straight to installation. A developer landing here from a search result, tweet, or GitHub Explore has no reason to care. There is no framing of the problem solved, time saved, or quality gained.

2. **1,300+ lines of plugin detail sections are undifferentiated wall of text** - Every plugin follows identical formatting (table, invocation block, expertise bullets). Nothing signals which plugins are popular, powerful, or recommended. The reader must scroll through all 22 to find what matters.

3. **Single CTA buried after the opener, no reinforcement** - The installation command appears once at line 47 and is never repeated. After reading 1,400 lines of plugin details, usage examples, and project structure, there is no closing CTA.

### Top 3 Quick Wins

1. Add a 3-4 line "Why use this" section immediately after the title with concrete outcomes (saves time, improves code quality, etc.)
2. Add badges (license, plugin count, last commit) to give instant credibility signals above the fold
3. Add a closing CTA after Usage Examples that repeats the install command

### Overall Assessment

The README is thorough, well-structured at the micro level (each plugin section is consistent), and clearly written. It is an excellent reference document but a poor landing page. The content serves someone who already decided to install -- not someone deciding whether to install. The main structural issue is that "catalog" content (22 detailed plugin sections) dominates 75% of the page, pushing actionable and persuasive content far down or off the page entirely.

---

## Category Findings

### 1. Page Layout & Visual Hierarchy

#### CRITICAL: No hero section or value framing above the fold

**Element:** Lines 1-5 (title + description)

**Issue:** The first thing a visitor reads is: "Custom Claude Code plugin marketplace with development workflow agents, skills, and commands for Python development, code review, Tauri/Rust, frontend, AI tooling, Obsidian plugins, constraint programming, and more."

This is a feature list masquerading as a description. It tells the reader WHAT this is but not WHY they should care or WHAT OUTCOME they get. On GitHub, the "above the fold" is roughly the first 15-20 lines rendered. Currently that space contains the title, one sentence, a horizontal rule, and the start of a 30-item Table of Contents.

**Fix:**

Before:
```markdown
# Anvil Toolset

Custom Claude Code plugin marketplace with development workflow agents, skills,
and commands for Python development, code review, Tauri/Rust, frontend, AI
tooling, Obsidian plugins, constraint programming, and more.
```

After:
```markdown
# Anvil Toolset

**22 ready-to-use plugins** that give Claude Code expert-level agents, reusable
skills, and slash commands for Python, TypeScript, Tauri, frontend, code review,
security auditing, and more.

> Install in one command. Each plugin adds specialized agents that know modern
> frameworks, testing patterns, and production best practices -- so you spend
> less time prompting and more time shipping.
```

---

#### CRITICAL: 75% of page is undifferentiated catalog

**Element:** Lines 126-1469 (22 plugin detail sections, ~1,340 lines)

**Issue:** The plugin detail sections account for roughly 1,340 of 1,746 lines. Each follows identical formatting with no visual differentiation, popularity signals, or grouping by use case. A developer scanning this page sees an endless scroll of identically-formatted sections. There is no guidance on "where to start" or "most popular."

**Fix (structural, two options):**

Option A - Keep in README but add grouping and highlights:
- Group plugins into 3-4 categories: "Development" (Python, TypeScript, Tauri, Frontend), "Quality" (Code Review, Humanize, Deep Dive), "Productivity" (AI Tooling, Workflows, Utilities, Project Setup), "Specialized" (CSP, Stripe, Messaging, etc.)
- Mark 3-5 "featured" or "start here" plugins in the overview table
- Collapse detail sections using `<details>` tags so the page is scannable

Option B (recommended) - Move plugin details to a separate `docs/plugins.md`:
- Keep the overview table in README (it is excellent as a quick reference)
- Link each plugin name in the table to its section in `docs/plugins.md`
- README stays under 400 lines: value prop, install, overview table, usage examples, contributing

---

#### IMPORTANT: No badges or quick credibility signals

**Element:** Missing from top of page

**Issue:** GitHub READMEs for popular projects universally use badge rows (license, version, last commit, stars) as quick trust signals. Their absence makes this look less established than it is.

**Fix:** Add badge row after the title:

```markdown
![License: MIT](https://img.shields.io/badge/license-MIT-blue)
![Plugins](https://img.shields.io/badge/plugins-22-brightgreen)
![Agents](https://img.shields.io/badge/agents-21-orange)
```

---

### 2. Calls-to-Action

#### CRITICAL: Primary CTA appears only once, early, with no reinforcement

**Element:** Lines 41-93 (Installation section)

**Issue:** The installation command is the single most important action on this page. It appears once at line 47 and never again. After 1,650+ lines of content, the page ends with "Total: 21 Agents | 25 Skills | 18 Commands" -- a stat, not an action. A reader who scrolled through Usage Examples and got excited has no nearby CTA.

**Fix:** Add closing CTA after Usage Examples and before Project Structure:

```markdown
---

## Get Started

Add the marketplace and install any plugin in seconds:

\`\`\`bash
claude plugin marketplace add acaprino/anvil-toolset
claude plugin install <plugin-name>@anvil-toolset
\`\`\`

See the full list in [Plugins Overview](#plugins-overview).
```

Also add a brief CTA after the overview table:

```markdown
**Ready to try it?** Jump to [Installation](#installation) to add the
marketplace in one command.
```

---

#### IMPORTANT: Installation section lists all 22 install commands

**Element:** Lines 51-74

**Issue:** Showing all 22 `claude plugin install` commands at once is overwhelming and implies the user should install all of them. Most users want 1-3 plugins. The wall of commands adds visual noise and pushes the "From Local Path" and "Verify Installation" sections below the fold.

**Fix:**

Before (22 lines of install commands):
```bash
claude plugin install python-development@anvil-toolset
claude plugin install humanize@anvil-toolset
# ... 20 more
```

After:
```bash
# Install any plugin by name:
claude plugin install <plugin-name>@anvil-toolset

# Examples:
claude plugin install python-development@anvil-toolset
claude plugin install senior-review@anvil-toolset
claude plugin install ai-tooling@anvil-toolset
```

Then add a `<details>` block: "See all 22 plugin install commands" for those who want the full list.

---

#### NICE-TO-HAVE: No "quick start" flow

**Element:** Missing

**Issue:** There is no guided 30-second onboarding path. A new user must read the installation section, figure out which plugin to install from a 22-row table, then find the plugin detail section to learn how to use it. A "Quick Start" section bridging install to first use would reduce time-to-value.

**Fix:** Add a Quick Start section after Installation:

```markdown
## Quick Start

**1.** Add the marketplace:
\`\`\`bash
claude plugin marketplace add acaprino/anvil-toolset
\`\`\`

**2.** Install a plugin (try `senior-review` for instant value):
\`\`\`bash
claude plugin install senior-review@anvil-toolset
\`\`\`

**3.** Use it in Claude Code:
\`\`\`
/senior-review
\`\`\`

That's it. Browse all 22 plugins in the [overview table](#plugins-overview).
```

---

### 3. Social Proof & Trust Signals

#### IMPORTANT: Zero social proof elements

**Element:** Entire page

**Issue:** There are no download/install counts, no testimonials, no "used by" mentions, no GitHub stars badge, no screenshots showing the plugins in action, and no links to blog posts or tweets about the project. For a developer evaluating whether to install third-party plugins into their AI coding assistant, trust matters.

**Fix (incremental, as data becomes available):**
- Add a GitHub stars badge (even if low, it signals the project is public and tracked)
- If any users have tweeted or posted about the plugins, link to those
- Add a "Changelog" or "Recent updates" section showing active maintenance
- Consider adding 1-2 short screenshots or GIF demos showing a plugin in action (e.g., `/senior-review` output)

---

### 4. Navigation & Findability

#### IMPORTANT: Table of Contents is a flat list of 25 items

**Element:** Lines 7-37

**Issue:** The TOC lists all 22 plugins at the same level as "Installation," "Usage Examples," "Contributing," and "License." There is no grouping. A developer scanning the TOC cannot quickly find "I want code quality tools" vs. "I want Python development tools." The TOC mirrors the page's structural problem: everything is flat.

**Fix:** Group the TOC:

```markdown
## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Plugins Overview](#plugins-overview)
- **Development**
  - [Python Development](#python-development-plugin) | [TypeScript](#typescript-development-plugin) | [Tauri](#tauri-development-plugin) | [Frontend](#frontend-plugin) | [Frontend Design](#frontend-design-plugin)
- **Code Quality**
  - [Senior Review](#senior-review-plugin) | [Humanize](#humanize-plugin) | [Deep Dive Analysis](#deep-dive-analysis-plugin)
- **Productivity**
  - [AI Tooling](#ai-tooling-plugin) | [Workflows](#workflows-plugin) | [Project Setup](#project-setup-plugin) | [Utilities](#utilities-plugin)
- **Specialized**
  - [CSP](#csp-plugin) | [Stripe](#stripe-plugin) | [Digital Marketing](#digital-marketing-plugin) | [Messaging](#messaging-plugin) | [Research](#research-plugin) | [Mobile Development](#mobile-development-plugin) | [Business](#business-plugin) | [App Explorer](#app-explorer-plugin) | [Browser Extensions](#browser-extensions-plugin) | [Obsidian Development](#obsidian-development-plugin) | [Code Documentation](#code-documentation-plugin)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)
```

---

#### NICE-TO-HAVE: Overview table lacks category column

**Element:** Lines 96-123

**Issue:** The overview table is one of the strongest elements on the page -- it is scannable, informative, and well-formatted. Adding a "Category" column would help users filter mentally.

**Fix:** Add a Category column:

```markdown
| Plugin | Category | Description | Agents | Skills | Commands |
```

---

### 5. Information Architecture

#### IMPORTANT: Usage Examples section is buried at line 1472

**Element:** Lines 1472-1550

**Issue:** The Usage Examples section is the most persuasive content on the page. It shows real workflows, demonstrates plugin synergy, and helps the reader imagine using the tools. But it sits at line 1472 -- after 22 plugin detail sections. Most readers will never scroll that far. This is the classic case of the best content being in the worst position.

**Fix:** Move Usage Examples immediately after the Plugins Overview table, before individual plugin details. This follows the conversion pattern: overview (what it is) -> workflows (how you'd use it) -> details (deep dive for those who want it).

---

#### NICE-TO-HAVE: Project Structure section (90 lines of tree) adds little for most readers

**Element:** Lines 1553-1692

**Issue:** A 90-line directory tree is useful for contributors but not for users deciding whether to install. It adds scroll length for 95% of visitors.

**Fix:** Move to `<details>` block or to `CONTRIBUTING.md`.

---

### 6. Onboarding Flow

#### IMPORTANT: No explanation of concepts (agents vs. skills vs. commands)

**Element:** Missing

**Issue:** The overview table has columns for "Agents," "Skills," and "Commands" but the README never explains what these are, how they differ, or when to use each. A Claude Code user may not know the plugin taxonomy. The reader sees `3 | 8 | 2` for Python Development and has no context for what that means practically.

**Fix:** Add a brief "How Plugins Work" section before or within the overview:

```markdown
### How Plugins Work

- **Agents** - Specialized AI personas with deep expertise in a domain.
  Invoke with: `Use the <agent-name> agent to...`
- **Skills** - Reusable knowledge that Claude draws on automatically when
  relevant. No explicit invocation needed.
- **Commands** - Slash commands (like `/senior-review`) that trigger specific
  workflows with structured output.
```

---

## What Is Working Well

1. **Consistent plugin documentation structure** - Every plugin section follows the same pattern (description, agents table, invocation, expertise). This makes the content predictable and easy to scan once you understand the format.

2. **Overview table** - The plugin summary table at lines 96-123 is excellent. It gives a complete picture in 25 rows with clickable links. This is the single best element on the page.

3. **Usage Examples** - The workflow examples (lines 1472-1550) are concrete, actionable, and show plugin synergy. They answer "how would I actually use this?" better than the individual plugin sections.

4. **Installation is straightforward** - Two methods, clearly distinguished, with verification steps. The mechanics are clear.

5. **Contributing section** - Clean templates for agents and skills. Low barrier for contributors.

6. **Invocation examples** - Showing the exact prompt to use each agent/command is practical and reduces friction.

---

## Priority Matrix

### Quick Wins (High Impact, Low Effort)

| # | Change | Expected Impact |
|---|--------|----------------|
| 1 | Add value proposition / "why" paragraph after title | First-time visitors understand the benefit within 5 seconds |
| 2 | Add badges (license, plugin count, agents count) | Instant credibility, visual break, professional appearance |
| 3 | Add closing CTA after Usage Examples | Readers who scroll far enough to get excited have a next step |
| 4 | Collapse 22 install commands into pattern + 3 examples | Reduces visual noise, faster path to "Verify Installation" |
| 5 | Add "How Plugins Work" explainer (agents/skills/commands) | New users understand the table columns and know how to invoke |

### Medium Effort (High Impact)

| # | Change | Expected Impact |
|---|--------|----------------|
| 6 | Move Usage Examples above plugin detail sections | Best persuasive content moves from line 1472 to ~line 130 |
| 7 | Group TOC by category | Users find relevant plugins 3-4x faster |
| 8 | Add Quick Start section (3-step install-to-first-use) | Time-to-value drops from minutes of reading to 30 seconds |
| 9 | Wrap plugin detail sections in `<details>` tags | Page becomes scannable; detail is available but not forced |
| 10 | Add category column to overview table | Mental filtering without reading every description |

### Major Projects (High Impact, Higher Effort)

| # | Change | Expected Impact |
|---|--------|----------------|
| 11 | Move plugin details to `docs/plugins.md`, keep overview in README | README drops from 1746 to ~400 lines; becomes a landing page |
| 12 | Add screenshots/GIFs of plugins in action | Visual proof of value; dramatically improves shareability |
| 13 | Create a changelog or "What's New" section | Signals active maintenance; gives returning visitors a reason to check back |
| 14 | Add social proof as it becomes available (stars badge, testimonials, tweets) | Builds trust for new visitors evaluating the project |

---

## Recommended Implementation Order

1. Items 1-5 (quick wins) - can be done in a single commit
2. Items 6-8 (restructure for conversion flow)
3. Item 9 (collapsible details)
4. Items 11-14 (as the project grows)

The single highest-impact change is moving from "reference document" framing to "landing page" framing in the first 20 lines: what this is, why it matters, how to install, what you can do with it.
