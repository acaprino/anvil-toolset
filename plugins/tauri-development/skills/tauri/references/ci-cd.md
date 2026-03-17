# CI/CD for Tauri Applications

## Pipeline Stages

A typical Tauri CI/CD pipeline has these stages:

1. **Setup** -- install toolchain (Rust, Node.js, platform SDK)
2. **Cache** -- restore Rust target/, node_modules/
3. **Build frontend** -- bundle the web assets
4. **Build Tauri** -- compile Rust + bundle into platform installer
5. **Sign** -- code signing for distribution
6. **Artifact** -- upload build output
7. **Release** (optional) -- create release, publish

## Caching Strategy

### Rust Compilation Cache
Cache `src-tauri/target/` keyed by:
- OS + architecture
- `Cargo.lock` hash
- Rust toolchain version

Typical cache sizes: 500MB-2GB. Use incremental compilation cache where supported.

### Node Dependencies
Cache `node_modules/` keyed by lockfile hash.

### Platform-Specific Caches
- **Gradle** (Android): `~/.gradle/caches/`
- **CocoaPods** (iOS): `~/Library/Caches/CocoaPods/`, `Pods/`

## OS Matrix

| Target Platform | CI Runner OS | Notes |
|----------------|-------------|-------|
| Windows (.msi, .nsis) | Windows | WebView2 bundled or bootstrapped |
| macOS (.dmg, .app) | macOS | WKWebView (system) |
| Linux (.AppImage, .deb) | Ubuntu | libwebkit2gtk-4.1 required |
| Android (.apk, .aab) | Ubuntu | Android SDK + NDK required |
| iOS (.ipa) | macOS | Xcode required |

## Release Profiles in CI

Ensure `Cargo.toml` has optimized release profile:

```toml
[profile.release]
lto = true
opt-level = "s"       # Optimize for size (or "3" for speed)
codegen-units = 1     # Better optimization
strip = true          # Remove debug symbols
panic = "abort"       # Smaller binary
```

## Code Signing Concepts

### Signing Secrets Management
- Store signing keys/certificates as CI secrets (base64-encoded for binary files)
- Decode at build time into temporary paths
- Never commit signing credentials to the repository

### Platform Signing Overview
| Platform | Signing Method | Required Credentials |
|----------|---------------|---------------------|
| Windows | Authenticode (optional) | Code signing certificate (.pfx) |
| macOS | codesign + notarization | Apple Developer ID, API key |
| Linux | None required | -- |
| Android | Keystore | .jks file + password + alias |
| iOS | Apple provisioning | Certificate + provisioning profile or API key |

## Artifact Management

Build outputs by platform:
| Platform | Output | Typical Location |
|----------|--------|-----------------|
| Windows | `.msi`, `.nsis` | `src-tauri/target/release/bundle/` |
| macOS | `.dmg`, `.app` | `src-tauri/target/release/bundle/` |
| Linux | `.AppImage`, `.deb` | `src-tauri/target/release/bundle/` |
| Android | `.apk`, `.aab` | `src-tauri/gen/android/app/build/outputs/` |
| iOS | `.ipa` | `src-tauri/gen/apple/build/` |

## Tauri Official CI Action

The `tauri-apps/tauri-action` simplifies desktop builds with automatic artifact upload and release creation. Works with GitHub Actions; for other CI providers, use direct CLI commands.

## Environment Variables

Common variables needed in CI:
```
TAURI_SIGNING_PRIVATE_KEY    # For auto-updater signing
TAURI_SIGNING_PRIVATE_KEY_PASSWORD
```

## Pipeline Anti-Patterns

- **No caching** -- Rust builds are slow; always cache target/
- **Building all targets sequentially** -- use parallel jobs per platform
- **Hardcoded paths** -- use CI variables for temp dirs and artifact paths
- **Skipping release profile** -- debug builds are 10-50x larger
