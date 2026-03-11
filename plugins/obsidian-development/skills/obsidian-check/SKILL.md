---
name: obsidian-check
description: Use when preparing an Obsidian plugin for submission or before pushing code. Reviews code against all ObsidianReviewBot rules and reports violations with fixes. Use PROACTIVELY before any git push on an Obsidian plugin project.
---

# Obsidian Check

Review code against all ObsidianReviewBot rules before pushing. Reports violations grouped by severity with exact file locations and fixes.

## Usage

`/obsidian-check` — scans the current Obsidian plugin project for all bot violations.

## Procedure

### Step 1: Verify project structure

Check that `manifest.json`, `package.json`, and `src/` exist. If not, abort with message.

### Step 2: Run TypeScript check

```bash
npx tsc --noEmit
```

Report any type errors.

### Step 3: Run eslint-plugin-obsidianmd (if installed)

```bash
npx eslint src/ --ext .ts 2>&1
```

If not installed, skip and note it.

### Step 4: Manual checks (scan all .ts files in src/)

Run these checks by reading the source code:

#### Required (blocking)

| # | Check | How to detect |
|---|-------|---------------|
| 1 | **Sentence case** | Search for string literals in `setName()`, `setDesc()`, `createEl()` text, `setText()`, button labels, modal titles, `Notice()` — flag any Title Case |
| 2 | **No inline styles** | Search for `.style.` assignments (`.style.display`, `.style.transform`, etc.) |
| 3 | **No unnecessary type assertions** | Search for `as Type` where `??` fallback makes it redundant |
| 4 | **Promises handled** | Search for async function calls without `await`, `void`, `.catch()`, or `.then()` with rejection |
| 5 | **No async without await** | Search for `async` methods with no `await` inside |
| 6 | **No promise where void expected** | Search for async callbacks in event handlers that expect void |
| 7 | **No object stringification** | Search for template literals with `??` where left side could be an object |
| 8 | **Setting.setHeading()** | Search for `createEl('h1')`, `createEl('h2')`, `createEl('h3')` in settings/modals |
| 9 | **No detachLeavesOfType in onunload** | Search for `detachLeavesOfType` in `onunload()` |
| 10 | **No TFile/TFolder cast** | Search for `as TFile` or `as TFolder` — should use `instanceof` |
| 11 | **No forbidden elements** | Search for `createElement('style')`, `createElement('link')` |
| 12 | **No plugin as component** | Search for `MarkdownRenderer.render(` where 5th arg is `this` in a Plugin class |
| 13 | **No view refs in plugin** | Search for view type stored as plugin property |
| 14 | **Use configDir** | Search for hardcoded `.obsidian` string |
| 15 | **Platform API** | Search for `navigator.userAgent` or `navigator.platform` |
| 16 | **No regex lookbehind** | Search for `(?<=` in regex (unless isDesktopOnly) |
| 17 | **Command rules** | Check command IDs/names for "command", plugin ID, plugin name |
| 18 | **No default hotkeys** | Check `addCommand()` for `hotkeys` property |
| 19 | **File operations** | Check for `Vault.trash()`, `Vault.delete()` instead of `FileManager.trashFile()` |
| 20 | **No sample code** | Search for `MyPlugin`, `SampleModal`, `SampleSettingTab` |
| 21 | **Object.assign** | Search for `Object.assign(this.settings,` or similar 2-arg patterns |

#### Optional (warnings)

| # | Check | How to detect |
|---|-------|---------------|
| 1 | **Unused imports** | TypeScript check catches these |
| 2 | **Unused variables** | TypeScript check catches these |
| 3 | **console.log in lifecycle** | Search for `console.log` in `onload()`/`onunload()` |

### Step 5: Check manifest.json

- `id`: alphanumeric + dashes, no "obsidian", no "plugin" suffix
- `name`: no "Obsidian", no "Plugin" suffix
- `description`: no "Obsidian", no "This plugin", must end with `. ? ! )`, under 250 chars
- All required fields present: `id`, `name`, `version`, `minAppVersion`, `description`, `author`
- `version` matches latest git tag (if any)

### Step 6: Check LICENSE

- File exists
- Copyright year is current year
- Copyright holder is not placeholder

### Step 7: Report

Output a structured report:

```
## Obsidian Lint Report

### TypeScript: [PASS/FAIL]
[errors if any]

### ESLint: [PASS/FAIL/SKIPPED]
[errors if any]

### Required Violations: [count]
[grouped by rule, with file:line and suggested fix]

### Optional Warnings: [count]
[grouped by rule]

### Manifest: [PASS/FAIL]
[issues if any]

### License: [PASS/FAIL]
[issues if any]

---
**Result: [READY TO PUSH / FIX REQUIRED ISSUES FIRST]**
[count] required issues, [count] warnings
```

### Step 8: Offer to fix

If violations are found, ask:
1. Fix all automatically
2. Fix only required violations
3. Show me the details, I'll fix manually

For auto-fix, apply changes following the obsidian-plugin-development skill rules (move styles to CSS classes, fix sentence case, remove unnecessary assertions, void unhandled promises, etc.).
