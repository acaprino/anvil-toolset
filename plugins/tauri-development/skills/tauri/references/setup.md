# Environment Setup

## Prerequisites

### All Platforms
- Rust (latest stable): `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Node.js LTS
- Tauri CLI: `npm install -D @tauri-apps/cli`

## Project Initialization

```bash
# New project
npm create tauri-app@latest
# Select targets during setup

# Add mobile to existing project
npm run tauri android init
npm run tauri ios init

# Verify setup
cargo tauri info
```

## Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  clearScreen: false,
  envPrefix: ['VITE_', 'TAURI_'],
  build: {
    target: 'esnext',
    minify: !process.env.TAURI_ENV_DEBUG ? 'esbuild' : false,
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
  },
});
```
