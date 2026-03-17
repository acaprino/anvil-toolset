# Platform WebViews

WebView2, WKWebView, and WebKitGTK differences for Tauri 2 desktop apps.

## Quick Reference

| Platform | WebView Engine | Browser Base | Auto-Installed |
|----------|---------------|--------------|----------------|
| Windows 10/11 | WebView2 | Chromium (Edge) | Yes (Win 10 1803+) |
| macOS | WKWebView | Safari/WebKit | Yes (built-in) |
| Linux | WebKitGTK | WebKit | No (package required) |

## WebView2 (Windows)

### Overview
- Chromium-based (shares engine with Microsoft Edge)
- Evergreen runtime: auto-updates independently of the app
- Available on Windows 10 (1803+) and Windows 11 by default
- Most consistent web standards support among the three

### Version Detection

```rust
// WebView2 is always available on supported Windows versions
// Tauri handles bootstrapping automatically
// For manual checks:
#[cfg(target_os = "windows")]
fn check_webview2() -> bool {
    // WebView2 runtime is pre-installed on Win 10 1803+ and Win 11
    // Tauri's NSIS installer can bundle the bootstrapper as fallback
    true
}
```

### NSIS Bootstrapper (Fallback)

If WebView2 isn't installed, the NSIS installer can include the bootstrapper:

```json
{
  "bundle": {
    "windows": {
      "nsis": {
        "installMode": "both"
      }
    }
  }
}
```

Tauri's NSIS template automatically downloads the WebView2 bootstrapper if needed.

### Windows-Specific Features

```rust
#[cfg(target_os = "windows")]
{
    use tauri::WebviewWindowBuilder;

    // WebView2 supports these well:
    // - Full ES2023+ support
    // - CSS Container Queries
    // - CSS :has() selector
    // - View Transitions API
    // - Web Workers + SharedArrayBuffer
    // - OffscreenCanvas
    // - WebGPU (behind flag)
}
```

### DevTools

```rust
// WebView2 devtools (F12 or right-click -> Inspect)
#[cfg(debug_assertions)]
{
    let window = app.get_webview_window("main").unwrap();
    window.open_devtools();
}
```

### Known Quirks
- `window.print()` may show Edge print dialog
- File input `accept` attribute: use MIME types, not extensions
- `user-select: none` may need `-webkit-user-select: none` fallback
- WebView2 ignores system proxy on some corporate networks

## WKWebView (macOS)

### Overview
- Safari/WebKit engine, tied to macOS version
- Cannot be updated independently -- features depend on macOS version
- Generally good standards support, but lags behind Chromium on some APIs
- Best native integration (scrolling, text rendering, accessibility)

### macOS Version Requirements

| macOS Version | Safari Version | Key Features |
|--------------|----------------|--------------|
| 10.15 (Catalina) | 13 | Baseline Tauri 2 support |
| 11 (Big Sur) | 14 | WebP, aspect-ratio |
| 12 (Monterey) | 15 | Dialog element, :has() |
| 13 (Ventura) | 16 | Container Queries, AVIF |
| 14 (Sonoma) | 17 | View Transitions, Popover |
| 15 (Sequoia) | 18 | CSS anchor positioning |

### JS/CSS Limitations
- No SharedArrayBuffer by default (requires COOP/COEP headers, not applicable in Tauri)
- `OffscreenCanvas` limited -- no 2D context until macOS 14
- `Intl.Segmenter` only since macOS 13
- `structuredClone` only since macOS 15 Safari 15.4
- Backdrop filter: use `-webkit-backdrop-filter`
- Scrollbar styling: limited to `::-webkit-scrollbar`

### IPC Differences
- WKWebView uses `window.webkit.messageHandlers` internally
- Tauri abstracts this -- use `invoke()` as normal
- Binary responses (ArrayBuffer) work the same across platforms

### DevTools

WKWebView devtools require Safari:

1. Enable: Safari > Settings > Advanced > "Show features for web developers"
2. Enable in app: Safari > Develop > [Your Machine] > [Your App Window]

```rust
// In Tauri, devtools open automatically in debug mode
// No programmatic devtools toggle for WKWebView in release
```

### Known Quirks
- `position: fixed` inside scrollable containers can jitter
- `font-smooth` rendering differs from Chromium
- `window.open()` may be blocked without user interaction
- CSS `env(safe-area-inset-*)` works natively
- Autofill/password manager integration is seamless
- `MediaRecorder` API not available until macOS 14.5

## WebKitGTK (Linux)

### Overview
- WebKit-based (shares engine with Safari, not Chromium)
- Version depends on distribution package manager
- Most variable behavior -- differs across distros and versions
- Requires explicit installation

### Distribution Requirements

| Distribution | Package | Version Command |
|-------------|---------|-----------------|
| Ubuntu/Debian | `libwebkit2gtk-4.1-0` | `dpkg -l \| grep webkit2gtk` |
| Fedora | `webkit2gtk4.1` | `rpm -q webkit2gtk4.1` |
| Arch | `webkit2gtk-4.1` | `pacman -Q webkit2gtk-4.1` |
| openSUSE | `libwebkit2gtk-4_1-0` | `rpm -q libwebkit2gtk-4_1-0` |

### Bundle Dependencies

```json
{
  "bundle": {
    "linux": {
      "deb": {
        "depends": [
          "libwebkit2gtk-4.1-0 (>= 2.40)"
        ]
      },
      "rpm": {
        "depends": [
          "webkit2gtk4.1 >= 2.40"
        ]
      }
    }
  }
}
```

### Version Matrix

| WebKitGTK Version | Ubuntu Version | Key Features |
|-------------------|---------------|--------------|
| 2.38 | 22.04 LTS | Baseline |
| 2.40 | 23.04 | Container Queries |
| 2.42 | 23.10 | :has(), CSS nesting |
| 2.44 | 24.04 LTS | View Transitions |

### DevTools

```bash
# Enable WebKitGTK inspector
export WEBKIT_INSPECTOR_SERVER=127.0.0.1:9222

# Then open in any browser:
# http://127.0.0.1:9222
```

Or programmatically:

```rust
#[cfg(debug_assertions)]
{
    let window = app.get_webview_window("main").unwrap();
    window.open_devtools(); // Opens built-in inspector
}
```

### Known Quirks
- `OffscreenCanvas` not available on older versions
- GPU acceleration may not work on all drivers (mesa/nvidia)
- `window.showOpenFilePicker()` not supported -- use Tauri's dialog plugin
- Font rendering varies by fontconfig settings
- Drag-and-drop may require `gtk-layer-shell` on Wayland
- Wayland: some window operations (position, always-on-top) may not work

## Cross-Platform Feature Detection

### CSS Feature Queries

```css
/* Container Queries -- not available on older WebKitGTK */
@supports (container-type: inline-size) {
  .sidebar { container-type: inline-size; }
}

/* Fallback for missing backdrop-filter */
@supports not (backdrop-filter: blur(10px)) {
  .overlay { background: rgba(0, 0, 0, 0.8); }
}

/* View Transitions */
@supports (view-transition-name: any) {
  ::view-transition-old(root) { animation: fade-out 0.3s; }
}
```

### JavaScript Feature Detection

```typescript
// OffscreenCanvas
const hasOffscreen = typeof OffscreenCanvas !== 'undefined';

// SharedArrayBuffer
const hasSAB = typeof SharedArrayBuffer !== 'undefined';

// Check WebView engine
function detectEngine(): 'chromium' | 'webkit' {
  const ua = navigator.userAgent;
  if (ua.includes('Chrome') || ua.includes('Edg')) return 'chromium';
  return 'webkit'; // WKWebView and WebKitGTK both report WebKit
}

// Platform detection via Tauri
import { platform } from '@tauri-apps/plugin-os';
const os = await platform(); // 'windows' | 'macos' | 'linux'
```

### Platform-Specific Workarounds

```typescript
import { platform } from '@tauri-apps/plugin-os';

const os = await platform();

// Scrollbar styling
if (os === 'macos') {
  // macOS hides scrollbars by default, overlay style
  document.documentElement.classList.add('macos-scrollbars');
} else {
  // Windows/Linux: style scrollbars explicitly
  document.documentElement.classList.add('custom-scrollbars');
}

// Font rendering
if (os === 'windows') {
  // ClearType rendering -- text may look different
  document.documentElement.style.setProperty('-webkit-font-smoothing', 'auto');
}
```

```css
/* Platform-specific scrollbar styling */
.custom-scrollbars::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbars::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbars::-webkit-scrollbar-thumb {
  background: rgba(128, 128, 128, 0.5);
  border-radius: 4px;
}

.macos-scrollbars {
  /* macOS overlay scrollbars -- minimal styling needed */
}
```

## User-Agent Strings

| Platform | User-Agent Pattern |
|----------|-------------------|
| Windows (WebView2) | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ... Chrome/1xx ... Edg/1xx` |
| macOS (WKWebView) | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 ... Safari/605.1.15` |
| Linux (WebKitGTK) | `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 ... Safari/605.1.15` |

Note: WKWebView and WebKitGTK share similar UA patterns. Use `platform()` from `@tauri-apps/plugin-os` for reliable detection.

## Rendering Differences Summary

| Feature | WebView2 | WKWebView | WebKitGTK |
|---------|----------|-----------|-----------|
| Container Queries | Yes | macOS 13+ | 2.40+ |
| :has() selector | Yes | macOS 12+ | 2.42+ |
| View Transitions | Yes | macOS 14+ | 2.44+ |
| OffscreenCanvas | Yes | macOS 14+ (2D) | Partial |
| SharedArrayBuffer | Yes | No (needs COOP) | Version-dependent |
| CSS Nesting | Yes | macOS 12+ | 2.42+ |
| Popover API | Yes | macOS 14+ | 2.44+ |
| WebGPU | Flag | macOS 14+ | No |

## Testing Strategy

1. **Primary development**: WebView2 (Windows) -- most forgiving, latest features
2. **Cross-platform check**: WKWebView (macOS) -- catches Safari-specific issues
3. **Compatibility floor**: WebKitGTK (Linux) -- oldest engine, catches missing features
4. **CI matrix**: Test all three platforms in CI (see ci-cd.md)

## Common Issues

| Problem | Solution |
|---------|----------|
| Feature works on Windows, not macOS | Check Safari version compatibility, add fallback |
| Feature works on Windows, not Linux | Check WebKitGTK version, use `@supports` |
| CSS looks different per platform | Normalize fonts, scrollbars, focus outlines |
| Devtools won't open on macOS | Enable Safari developer features in settings |
| WebKitGTK inspector blank | Set `WEBKIT_INSPECTOR_SERVER` env var |
| Performance varies by platform | Profile per-platform, Canvas may need fallbacks |
| Drag-and-drop broken on Linux | Check Wayland vs X11, test on both |
