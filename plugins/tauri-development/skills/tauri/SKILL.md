---
name: tauri
description: >
  Unified Tauri 2 development knowledge base covering core patterns, desktop, and mobile.
  Use when working with Tauri commands, IPC, plugins, project setup, OAuth, CI/CD,
  window management, shell plugin, desktop bundling, platform WebViews,
  mobile environment setup, emulator/ADB, mobile plugins, IAP, and store deployment.
---

# Tauri 2 Development

Cross-platform patterns for Tauri 2 applications -- core, desktop, and mobile.

## Quick Reference

| Task | Command |
|------|---------|
| New project | `npm create tauri-app@latest` |
| Add plugin | `npm run tauri add <plugin-name>` |
| Dev mode | `cargo tauri dev` |
| Build | `cargo tauri build` |
| Info | `cargo tauri info` |
| Init Android | `npm run tauri android init` |
| Init iOS | `npm run tauri ios init` |
| Dev Android | `npm run tauri android dev` |
| Dev iOS | `npm run tauri ios dev` |
| Build APK | `npm run tauri android build --apk` |
| Build AAB | `npm run tauri android build --aab` |
| Build iOS | `npm run tauri ios build` |

## Core Patterns

### New Project Setup
1. Read [references/setup.md](references/setup.md) for environment prerequisites
2. Run `npm create tauri-app@latest`
3. Configure `tauri.conf.json` with app identifier

### Rust Backend & IPC
- **Commands, state, channels, events**: Read [references/rust-patterns.md](references/rust-patterns.md)
- **Frontend invoke, channels, TypeScript typing**: Read [references/frontend-patterns.md](references/frontend-patterns.md)

### Universal Plugins
- **fs, store, sql, http, log, dialog, opener**: Read [references/plugins-core.md](references/plugins-core.md)

### Authentication
- **OAuth/PKCE via system browser**: Read [references/authentication.md](references/authentication.md)

### CI/CD
- **Provider-agnostic pipelines**: Read [references/ci-cd.md](references/ci-cd.md)

## Desktop Patterns

### Window Management
- **Multi-window, frameless, system tray, menus, shortcuts**: Read [references/window-management.md](references/window-management.md)

### Shell Plugin
- **Child processes, sidecar binaries, scoped commands**: Read [references/shell-plugin.md](references/shell-plugin.md)

### Desktop Bundling & Deployment
- **.msi, .dmg, .AppImage, code signing, auto-updater**: Read [references/build-deploy-desktop.md](references/build-deploy-desktop.md)

### Platform WebViews
- **WebView2, WKWebView, WebKitGTK differences**: Read [references/platform-webviews.md](references/platform-webviews.md)

## Mobile Patterns

### Mobile Environment Setup
1. Read [references/setup-mobile.md](references/setup-mobile.md) for Android SDK / iOS Xcode setup
2. Run `npm run tauri android init` / `npm run tauri ios init`
3. Configure mobile-specific permissions

### Mobile Plugins
- **Biometric, haptics, NFC, barcode**: Read [references/plugins-mobile.md](references/plugins-mobile.md)

### In-App Purchases
- **Google Play / App Store IAP**: Read [references/iap.md](references/iap.md)

### Mobile Authentication
- **Deep link OAuth, Apple Sign-In, Firebase callback**: Read [references/authentication-mobile.md](references/authentication-mobile.md)

### Mobile Testing
- **Emulator, ADB, logcat, WebView debugging**: Read [references/testing.md](references/testing.md)
- Use `adb logcat | grep -iE "(tauri|RustStdout)"` for logs

### Mobile Builds & Deployment
- **APK/IPA builds, store submission**: Read [references/build-deploy-mobile.md](references/build-deploy-mobile.md)
- **Mobile CI/CD pipelines**: Read [references/ci-cd-mobile.md](references/ci-cd-mobile.md)

## Project Structure

```
my-app/
+-- src/                          # Frontend (React/Vue/Svelte/etc.)
+-- src-tauri/
|   +-- Cargo.toml
|   +-- tauri.conf.json           # Main config
|   +-- src/
|   |   +-- main.rs               # Desktop entry (don't modify)
|   |   +-- lib.rs                # Main code + mobile entry
|   +-- capabilities/
|   |   +-- default.json          # Permissions
|   +-- gen/
|       +-- android/              # Android project (if mobile)
|       +-- apple/                # Xcode project (if mobile)
```

## Essential Configuration

### tauri.conf.json
```json
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

### capabilities/default.json
```json
{
  "identifier": "default",
  "windows": ["main"],
  "permissions": ["core:default"]
}
```

### lib.rs (Mobile Entry)
```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        #[cfg(mobile)]
        .plugin(tauri_plugin_biometric::init())
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error");
}
```

## Common Issues

| Problem | Solution |
|---------|----------|
| White screen | Check JS console, verify `devUrl`, check capabilities |
| Command not found | Verify handler registered in `invoke_handler` |
| Permission denied | Add permission to capabilities/default.json |
| Plugin not loaded | Check `.plugin()` call in lib.rs |
| iOS won't connect | Use `--force-ip-prompt`, select IPv6 |
| Emulator not detected | Verify `adb devices`, restart ADB |
| HMR not working | Configure `vite.config.ts` with `TAURI_DEV_HOST` |

## Resources

- Docs: https://v2.tauri.app
- Plugins: https://v2.tauri.app/plugin/
- GitHub: https://github.com/tauri-apps/tauri
