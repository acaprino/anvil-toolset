# Registry System

Create and distribute custom shadcn/ui component sets.

Source: https://ui.shadcn.com/docs/registry

## Overview

The registry system lets you package and share components, hooks, pages, config, and full design systems. Works with any framework, not just React.

## registry.json (Root Entry Point)

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry.json",
  "name": "acme",
  "homepage": "https://acme.com",
  "items": [
    {
      "$schema": "https://ui.shadcn.com/schema/registry-item.json",
      "name": "hello-world",
      "type": "registry:component",
      "title": "Hello World",
      "description": "A greeting component with configurable message",
      "files": [
        { "path": "registry/new-york/hello-world/hello-world.tsx", "type": "registry:component" }
      ],
      "dependencies": ["lucide-react"],
      "registryDependencies": ["button"]
    }
  ]
}
```

## Item Types

| Type | Purpose |
|------|---------|
| `registry:component` | UI component |
| `registry:block` | Composable page section |
| `registry:hook` | React hook |
| `registry:lib` | Utility/library code |
| `registry:font` | Font configuration (CLI v4) |
| `registry:base` | Full design system bundle (CLI v4) |

## registry-item.json Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Component identifier (kebab-case) |
| `type` | yes | One of the item types above |
| `title` | no | Display name |
| `description` | no | Purpose (important for LLM context via `shadcn docs`) |
| `files` | yes | Array of `{ path, type }` objects |
| `dependencies` | no | npm packages (use `name@version` to pin) |
| `registryDependencies` | no | Other registry items this depends on |

## Directory Structure

```
your-project/
  registry/
    new-york/
      hello-world/
        hello-world.tsx
      fancy-button/
        fancy-button.tsx
  public/r/
    hello-world.json    # generated output
    fancy-button.json   # generated output
  registry.json         # root manifest
```

## Build and Publish

```bash
# Add build script to package.json
# "registry:build": "shadcn build"

pnpm registry:build   # generates public/r/*.json files
pnpm dev              # serve locally

# Users install components via:
pnpm dlx shadcn@latest add http://localhost:3000/r/hello-world.json

# Or from a deployed URL:
pnpm dlx shadcn@latest add https://your-registry.com/r/hello-world.json
```

## registry:base (CLI v4)

Bundle an entire design system (components, dependencies, CSS variables, fonts, and config) in a single installable unit:

```json
{
  "name": "acme-design-system",
  "type": "registry:base",
  "files": [...],
  "dependencies": [...],
  "cssVars": {
    "theme": {
      "--radius": "0.5rem",
      "--primary": "oklch(0.7 0.15 250)"
    }
  }
}
```

Install with: `shadcn add https://registry.acme.com/r/acme-design-system.json`

## Best Practices

- Use `@/registry` imports in source files, not relative paths
- List all dependencies explicitly -- don't rely on transitive deps
- Write descriptive `title` and `description` for LLM compatibility (`shadcn docs`)
- Use `registryDependencies` to declare which shadcn components yours builds on
- Test installations with `shadcn add --dry-run` before publishing
