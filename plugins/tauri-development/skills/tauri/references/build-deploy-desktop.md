# Desktop Build & Deployment

Bundling, code signing, and auto-updates for Tauri 2 desktop applications.

## Quick Reference

| Platform | Format | Toolchain |
|----------|--------|-----------|
| Windows | `.msi` (WiX), `.nsis` | WiX Toolset / NSIS |
| macOS | `.dmg`, `.app` | Xcode Command Line Tools |
| Linux | `.AppImage`, `.deb`, `.rpm` | Various |

| Task | Command |
|------|---------|
| Build release | `cargo tauri build` |
| Build specific target | `cargo tauri build --target x86_64-pc-windows-msvc` |
| Build debug bundle | `cargo tauri build --debug` |
| Build with specific format | `cargo tauri build --bundles nsis` |

## Bundle Configuration

### tauri.conf.json

```json
{
  "bundle": {
    "active": true,
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "resources": [
      "assets/*",
      "config/default.toml"
    ],
    "copyright": "Copyright 2025 MyCompany",
    "category": "DeveloperTool",
    "shortDescription": "My Tauri App",
    "longDescription": "A desktop application built with Tauri 2.",
    "targets": "all",
    "windows": {
      "certificateThumbprint": null,
      "digestAlgorithm": "sha256",
      "timestampUrl": "http://timestamp.digicert.com",
      "wix": null,
      "nsis": {
        "displayLanguageSelector": true,
        "installerIcon": "icons/icon.ico",
        "installMode": "both"
      }
    },
    "macOS": {
      "frameworks": [],
      "minimumSystemVersion": "10.15",
      "signingIdentity": null,
      "providerShortName": null,
      "entitlements": null
    },
    "linux": {
      "deb": {
        "depends": ["libwebkit2gtk-4.1-0"],
        "section": "utils"
      },
      "appimage": {
        "bundleMediaFramework": false
      },
      "rpm": {
        "depends": ["webkit2gtk4.1"]
      }
    }
  }
}
```

## Windows Bundling

### NSIS Installer (Recommended)

```json
{
  "bundle": {
    "targets": ["nsis"],
    "windows": {
      "nsis": {
        "installMode": "both",
        "displayLanguageSelector": true,
        "installerIcon": "icons/icon.ico",
        "headerImage": "icons/nsis-header.bmp",
        "sidebarImage": "icons/nsis-sidebar.bmp"
      }
    }
  }
}
```

Install modes:
- `"currentUser"` -- no admin required, installs to AppData
- `"perMachine"` -- requires admin, installs to Program Files
- `"both"` -- user chooses at install time

### WiX MSI

```json
{
  "bundle": {
    "targets": ["msi"],
    "windows": {
      "wix": {
        "language": "en-US",
        "template": null
      }
    }
  }
}
```

Requires WiX Toolset 3.x installed.

### Windows Code Signing

```bash
# Sign with certificate from Windows Certificate Store
# Set environment variables before build:
export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="password"

# In tauri.conf.json:
# "certificateThumbprint": "YOUR_CERT_THUMBPRINT"
# "digestAlgorithm": "sha256"
# "timestampUrl": "http://timestamp.digicert.com"
```

Using signtool directly:

```bash
signtool sign /sha1 THUMBPRINT /fd sha256 /tr http://timestamp.digicert.com /td sha256 target/release/bundle/nsis/MyApp_1.0.0_x64-setup.exe
```

## macOS Bundling

### Build for Both Architectures

```bash
# Intel
cargo tauri build --target x86_64-apple-darwin

# Apple Silicon
cargo tauri build --target aarch64-apple-darwin

# Universal binary (both)
cargo tauri build --target universal-apple-darwin
```

### Code Signing

```bash
# Set signing identity
export APPLE_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"

# Or in tauri.conf.json:
# "macOS": { "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)" }
```

### Notarization

```bash
# Environment variables for notarization
export APPLE_ID="your@email.com"
export APPLE_PASSWORD="app-specific-password"
export APPLE_TEAM_ID="TEAM_ID"

# Tauri handles notarization automatically during `cargo tauri build`
# when these env vars are set
```

### Entitlements

```xml
<!-- src-tauri/entitlements.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

```json
{
  "bundle": {
    "macOS": {
      "entitlements": "entitlements.plist"
    }
  }
}
```

## Linux Bundling

### AppImage

```bash
cargo tauri build --bundles appimage
```

AppImage is self-contained, works on most distributions.

### Debian Package

```json
{
  "bundle": {
    "linux": {
      "deb": {
        "depends": [
          "libwebkit2gtk-4.1-0",
          "libssl3"
        ],
        "section": "utils",
        "priority": "optional"
      }
    }
  }
}
```

### RPM Package

```json
{
  "bundle": {
    "linux": {
      "rpm": {
        "depends": [
          "webkit2gtk4.1",
          "openssl"
        ]
      }
    }
  }
}
```

## Bundle Resources

Include extra files in the bundle:

```json
{
  "bundle": {
    "resources": [
      "assets/**/*",
      "config/default.toml",
      "models/model.onnx"
    ]
  }
}
```

Access at runtime:

```rust
use tauri::Manager;

#[tauri::command]
fn get_resource_path(app: tauri::AppHandle) -> Result<String, String> {
    let resource_path = app
        .path()
        .resource_dir()
        .map_err(|e| e.to_string())?
        .join("assets/data.json");
    Ok(resource_path.to_string_lossy().to_string())
}
```

## Auto-Updater

### Plugin Setup

```bash
npm run tauri add updater
```

### Generate Update Keys

```bash
cargo tauri signer generate -w ~/.tauri/myapp.key
```

### tauri.conf.json

```json
{
  "bundle": {
    "createUpdaterArtifacts": "v2Compatible"
  },
  "plugins": {
    "updater": {
      "pubkey": "dW50cnVzdGVkIGNvbW1lbnQ...",
      "endpoints": [
        "https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"
      ]
    }
  }
}
```

### Update Server Response Format

The endpoint must return JSON:

```json
{
  "version": "1.1.0",
  "notes": "Bug fixes and improvements",
  "pub_date": "2025-01-15T12:00:00Z",
  "platforms": {
    "windows-x86_64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ...",
      "url": "https://releases.myapp.com/MyApp_1.1.0_x64-setup.nsis.zip"
    },
    "darwin-x86_64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ...",
      "url": "https://releases.myapp.com/MyApp_1.1.0_x64.app.tar.gz"
    },
    "darwin-aarch64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ...",
      "url": "https://releases.myapp.com/MyApp_1.1.0_aarch64.app.tar.gz"
    },
    "linux-x86_64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ...",
      "url": "https://releases.myapp.com/MyApp_1.1.0_amd64.AppImage.tar.gz"
    }
  }
}
```

### Rust: Check and Install Updates

```rust
use tauri_plugin_updater::UpdaterExt;

#[tauri::command]
async fn check_for_updates(app: tauri::AppHandle) -> Result<Option<String>, String> {
    let update = app
        .updater()
        .map_err(|e| e.to_string())?
        .check()
        .await
        .map_err(|e| e.to_string())?;

    match update {
        Some(update) => {
            println!("Update available: {}", update.version);
            // Download and install
            update
                .download_and_install(|progress, total| {
                    println!("Downloaded {} of {:?}", progress, total);
                }, || {
                    println!("Download complete");
                })
                .await
                .map_err(|e| e.to_string())?;
            Ok(Some(update.version))
        }
        None => Ok(None),
    }
}
```

### Frontend: Check for Updates

```typescript
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

async function checkForUpdates() {
  const update = await check();

  if (update) {
    console.log(`Update ${update.version} available`);

    await update.downloadAndInstall((event) => {
      switch (event.event) {
        case 'Started':
          console.log(`Downloading ${event.data.contentLength} bytes`);
          break;
        case 'Progress':
          console.log(`Downloaded ${event.data.chunkLength} bytes`);
          break;
        case 'Finished':
          console.log('Download complete');
          break;
      }
    });

    await relaunch();
  }
}
```

### Capabilities

```json
{
  "permissions": [
    "updater:default",
    "process:allow-restart"
  ]
}
```

### GitHub Releases as Update Server

Use `tauri-action` in GitHub Actions to publish releases with update artifacts:

```yaml
- uses: tauri-apps/tauri-action@v0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
    TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_KEY_PASSWORD }}
  with:
    tagName: v__VERSION__
    releaseName: 'v__VERSION__'
    releaseBody: 'See the release notes for details.'
    releaseDraft: true
```

Endpoint for GitHub releases:

```
https://github.com/OWNER/REPO/releases/latest/download/latest.json
```

## Build Optimization

### Cargo.toml Release Profile

```toml
[profile.release]
codegen-units = 1
lto = true
opt-level = 3
strip = true
panic = "abort"
```

See the `tauri-optimizer` agent for detailed build optimization guidance.

## Common Issues

| Problem | Solution |
|---------|----------|
| WiX not found | Install WiX Toolset 3.x, add to PATH |
| NSIS not found | Install NSIS, add to PATH |
| macOS signing fails | Verify `APPLE_SIGNING_IDENTITY`, run `security find-identity -v` |
| Notarization fails | Check Apple ID, app-specific password, team ID |
| AppImage won't run | `chmod +x MyApp.AppImage`, check FUSE installed |
| Update signature mismatch | Regenerate with correct key, ensure `pubkey` matches |
| Resources not found at runtime | Use `app.path().resource_dir()`, verify `bundle.resources` paths |
| Large bundle size | Enable LTO, strip symbols, check `bundle.resources` for unneeded files |
