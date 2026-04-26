---
name: tauri
description: >
  Unified Tauri 2 development knowledge base covering core patterns, desktop, and mobile.
  TRIGGER WHEN: working with Tauri commands, IPC, plugins, project setup, OAuth, CI/CD, window management, shell plugin, desktop bundling, platform WebViews, mobile environment setup, emulator/ADB, mobile plugins, IAP, and store deployment.
  DO NOT TRIGGER WHEN: the task is outside the specific scope of this component.
---

# Tauri 2 Development

Index for Tauri 2 patterns -- core, desktop, mobile. Each section points to a focused reference; the references hold gotchas and link out to canonical docs at v2.tauri.app.

## Quick command reference

| Task | Command |
|------|---------|
| New project | `npm create tauri-app@latest` |
| Add plugin | `npm run tauri add <plugin-name>` |
| Dev (desktop) | `cargo tauri dev` |
| Build (desktop) | `cargo tauri build` |
| Info / sanity check | `cargo tauri info` |
| Init Android / iOS | `npm run tauri android init` / `ios init` |
| Dev mobile | `npm run tauri android dev` / `ios dev` |
| Build APK / AAB | `npm run tauri android build --apk` / `--aab` |
| Build IPA | `npm run tauri ios build` |

## Reading order by topic

### Core
- `setup.md` -- prerequisites (Rust, Node, Vite gotchas)
- `rust-patterns.md` -- commands, state, channels, events, error handling
- `frontend-patterns.md` -- invoke, channels, listeners, capabilities
- `plugins-core.md` -- universal plugins (fs, http, store, sql, deep-link, ...)

### Desktop
- `window-management.md` -- multi-window, frameless, tray, menus, global shortcuts
- `shell-plugin.md` -- spawn child processes, sidecar binaries, scoped commands
- `build-deploy-desktop.md` -- bundling, code signing, notarization, auto-updater
- `platform-webviews.md` -- WebView2 / WKWebView / WebKitGTK differences and floors
- `authentication.md` -- OAuth/PKCE via system browser
- `ci-cd.md` -- provider-agnostic pipeline patterns

### Mobile
- `setup-mobile.md` -- Android SDK + iOS Xcode tooling
- `plugins-mobile.md` -- biometric, barcode, haptics, NFC, geolocation, Android safe-area workaround
- `authentication-mobile.md` -- deep-link OAuth, Apple Sign-In, Firebase callback
- `iap.md` -- in-app purchases (Google Play + App Store)
- `testing.md` -- emulator, ADB, logcat, WebView debugging
- `build-deploy-mobile.md` -- signing, store builds, NDK / 16KB / RustWebViewClient gotchas
- `ci-cd-mobile.md` -- mobile signing in CI, store upload

### Specialized
- `high-frequency-ui.md` -- streaming/trading UI composition (atomic state, virtualization, rust-lld)
- `ipc-streaming.md` -- Channel-vs-emit benchmarks, rkyv zero-copy, backpressure

## Project skeleton

```
my-app/
+-- src/                          # Frontend (React/Vue/Svelte/...)
+-- src-tauri/
|   +-- Cargo.toml
|   +-- tauri.conf.json           # Main config
|   +-- src/
|   |   +-- main.rs               # Desktop entry (don't modify)
|   |   +-- lib.rs                # All your code + mobile entry
|   +-- capabilities/
|   |   +-- default.json          # Permissions
|   +-- gen/
|       +-- android/              # Generated Android project
|       +-- apple/                # Generated Xcode project
```

## Minimum viable config

```json
// tauri.conf.json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "MyApp",
  "identifier": "com.company.myapp",
  "build": {
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  }
}
```

```json
// capabilities/default.json
{ "identifier": "default", "windows": ["main"], "permissions": ["core:default"] }
```

```rust
// src-tauri/src/lib.rs
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error");
}
```

## Official docs

- Tauri 2: https://v2.tauri.app
- Plugin index: https://v2.tauri.app/plugin/
- GitHub: https://github.com/tauri-apps/tauri
- Awesome Tauri (community): https://github.com/tauri-apps/awesome-tauri
