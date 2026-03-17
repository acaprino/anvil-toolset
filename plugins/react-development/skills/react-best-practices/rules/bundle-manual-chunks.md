---
title: Manual Chunk Splitting Strategy
impact: CRITICAL
impactDescription: reduces initial bundle size and improves cache efficiency
tags: bundle, vite, rollup, manual-chunks, code-splitting, vendor-splitting
---

## Manual Chunk Splitting Strategy

Configure `build.rollupOptions.output.manualChunks` to split large vendor bundles into cacheable chunks. Without this, Vite may produce a single vendor chunk that exceeds 500 KB, hurting initial load and cache invalidation.

**Incorrect (single vendor chunk, 800KB+):**

```ts
// vite.config.ts
export default defineConfig({
  build: {
    // No chunk strategy -- everything lands in one vendor chunk
  }
})
```

**Correct (vendor splitting by domain):**

```ts
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-charts': ['recharts', 'd3-scale', 'd3-shape'],
          'vendor-state': ['zustand', '@tanstack/react-query'],
          'vendor-ui': ['@radix-ui/react-dialog', '@radix-ui/react-popover'],
        }
      }
    }
  }
})
```

**Function-based splitting for route isolation:**

```ts
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'vendor-react'
            if (id.includes('recharts') || id.includes('d3-')) return 'vendor-charts'
            return 'vendor-misc'
          }
        }
      }
    }
  }
})
```

**When to split:**
- Any chunk exceeding 500 KB (Vite warns at this threshold)
- Vendor libraries updated on different cadences (React vs charting vs state)
- Route-specific heavy dependencies (e.g. editor only on `/settings`)

**When NOT to split:**
- Small apps under 200 KB total -- splitting adds HTTP overhead
- Libraries always loaded together -- splitting them wastes parallel requests

**Analyze before splitting:**

```bash
npx vite-bundle-visualizer
# or
npx source-map-explorer dist/assets/*.js
```

Combine with `bundle-dynamic-imports` for route-level lazy loading and `bundle-preload` for critical chunk prefetching.
