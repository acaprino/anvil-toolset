# Mobile Plugins and Patterns

> For universal plugins (fs, store, sql, http, etc.), see `tauri-core/references/plugins-core.md`.

## Mobile-Only Plugins

| Plugin | Platform | Description |
|--------|----------|-------------|
| `biometric` | Android, iOS | Fingerprint/Face ID |
| `barcode-scanner` | Android, iOS | QR/barcode scanning |
| `haptics` | Android, iOS | Vibration feedback |
| `nfc` | Android, iOS | NFC read/write |

## Barcode Scanner

```typescript
import { scan, Format } from '@tauri-apps/plugin-barcode-scanner';

async function scanQR(): Promise<string | null> {
  try {
    const result = await scan({
      formats: [Format.QRCode, Format.EAN13],
      windowed: false,
    });
    return result.content;
  } catch (e) {
    console.error('Scan failed:', e);
    return null;
  }
}
```

## NFC Plugin

```typescript
import { scan, write } from '@tauri-apps/plugin-nfc';

// Read NFC tag
const data = await scan();
console.log('Tag ID:', data.id);
console.log('Records:', data.records);

// Write to NFC tag
await write([
  { format: 'text', value: 'Hello NFC!' }
]);
```

## Biometric Authentication

```typescript
import { authenticate } from '@tauri-apps/plugin-biometric';

async function biometricLogin(): Promise<boolean> {
  try {
    await authenticate('Confirm your identity', {
      allowDeviceCredential: true,
      cancelTitle: 'Cancel',
      fallbackTitle: 'Use password',
    });
    return true;
  } catch (e) {
    console.error('Biometric failed:', e);
    return false;
  }
}
```

## Geolocation

```typescript
import { getCurrentPosition, watchPosition } from '@tauri-apps/plugin-geolocation';

async function getLocation() {
  const position = await getCurrentPosition({
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0,
  });
  return {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
    accuracy: position.coords.accuracy,
  };
}

// Watch position changes
const watchId = await watchPosition(
  { enableHighAccuracy: true },
  (position) => console.log('New position:', position)
);
```

## Haptics

```typescript
import { vibrate, impactFeedback, notificationFeedback } from '@tauri-apps/plugin-haptics';

async function buttonTap() {
  await impactFeedback('light'); // light, medium, heavy
}

async function success() {
  await notificationFeedback('success'); // success, warning, error
}
```

## Deep Links

```typescript
import { onOpenUrl, getCurrent } from '@tauri-apps/plugin-deep-link';

async function setupDeepLinks(handler: (url: string) => void) {
  // Check if opened via deep link
  const urls = await getCurrent();
  if (urls?.length) {
    handler(urls[0]);
  }

  // Listen for future deep links
  await onOpenUrl((urls) => handler(urls[0]));
}
```

## Conditional Mobile Plugin Registration

Use `#[cfg(mobile)]` to register mobile-only plugins so desktop builds compile without them:

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_deep_link::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        #[cfg(mobile)]
        .plugin(tauri_plugin_biometric::init())
        #[cfg(mobile)]
        .plugin(tauri_plugin_haptics::init())
        #[cfg(mobile)]
        .plugin(tauri_plugin_geolocation::init())
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error");
}
```

## Mobile Deep Link Configuration

### Android Intent Filter

Add to `AndroidManifest.xml` for Universal Links:
```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https" android:host="app.example.com" />
</intent-filter>
```

### iOS Associated Domains

Add to Xcode: Signing & Capabilities - Associated Domains:
```
applinks:app.example.com
```

## Mobile Capabilities Configuration

For mobile-specific permissions, create `src-tauri/capabilities/mobile.json`:

```json
{
  "identifier": "mobile",
  "windows": ["main"],
  "platforms": ["iOS", "android"],
  "permissions": [
    "biometric:allow-authenticate",
    "biometric:allow-status",
    "geolocation:allow-get-current-position",
    "geolocation:allow-watch-position",
    "haptics:default"
  ]
}
```

## Safe Areas on Android WebView

CSS `env(safe-area-inset-*)` does **not** work by default on Android WebView. The WebView lacks the viewport-fit=cover meta and proper inset reporting.

### The Problem

```css
/* This won't work on Android WebView */
.header {
  padding-top: env(safe-area-inset-top, 0px);
}
```

### Solution: JavaScript Fallback for Android Only

The fix: use `env()` in CSS as the default, and only override with JS on Android where it doesn't work.

```typescript
import { platform } from '@tauri-apps/plugin-os';

export async function setupMobileSafeAreas(): Promise<void> {
  const p = await platform();

  if (p === 'android') {
    // Android WebView doesn't support env(safe-area-inset-*)
    // Override with typical values: status bar ~48px, navigation ~24px
    document.documentElement.style.setProperty('--safe-area-top', '48px');
    document.documentElement.style.setProperty('--safe-area-bottom', '24px');
  }
  // iOS and desktop: don't set variables, let CSS env() fallback handle it
}
```

### CSS Usage

Use CSS custom properties with `env()` as the fallback. This way iOS gets native values, and Android uses the JS-set overrides:

```css
:root {
  /* Defaults use env() - works on iOS, ignored on Android */
  --safe-area-top: env(safe-area-inset-top, 0px);
  --safe-area-bottom: env(safe-area-inset-bottom, 0px);
}

.header {
  padding-top: var(--safe-area-top);
}

.bottom-nav {
  padding-bottom: var(--safe-area-bottom);
}

.app-container {
  min-height: calc(100vh - var(--safe-area-top) - var(--safe-area-bottom));
}
```

### Typical Values

| Area | Android | iOS (varies by device) |
|------|---------|------------------------|
| Top (status bar) | ~48px | 44px - 59px |
| Bottom (navigation) | ~24px | 0px - 34px (home indicator) |

### React Integration

```tsx
import { useEffect } from 'react';
import { setupMobileSafeAreas } from './utils/safe-areas';

function App() {
  useEffect(() => {
    setupMobileSafeAreas();
  }, []);

  return <div className="app-container">...</div>;
}
```

## Community Plugins

### In-App Purchases (tauri-plugin-iap)
See [iap.md](iap.md) for complete IAP guide.

```bash
npm install @choochmeque/tauri-plugin-iap-api
cargo add tauri-plugin-iap
```

### Other Notable Community Plugins
- `tauri-plugin-keep-screen-on` - Prevent screen timeout
- `tauri-plugin-camera` - Camera access
- `tauri-plugin-share` - Native share sheet

Search: https://v2.tauri.app/plugin/ or https://github.com/tauri-apps/awesome-tauri
