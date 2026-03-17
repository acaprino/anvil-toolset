# Mobile Environment Setup

> For base prerequisites (Rust, Node, Tauri CLI), see `tauri-core/references/setup.md`.

## Android Development

**Install Android Studio** with SDK Manager components:
- Android SDK Platform (API 34+)
- Android SDK Platform-Tools
- Android SDK Build-Tools
- NDK (Side by side)
- Android SDK Command-line Tools

**Environment Variables:**
```bash
# macOS
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export NDK_HOME="$ANDROID_HOME/ndk/$(ls -1 $ANDROID_HOME/ndk)"

# Linux
export JAVA_HOME=/opt/android-studio/jbr
export ANDROID_HOME="$HOME/Android/Sdk"
export NDK_HOME="$ANDROID_HOME/ndk/$(ls -1 $ANDROID_HOME/ndk)"

# Windows (PowerShell)
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:NDK_HOME = "$env:ANDROID_HOME\ndk\<version>"
```

**Windows: Strawberry Perl (if using `reqwest` with `native-tls`):**

If your Rust dependencies include `reqwest` with the `native-tls` feature, cross-compiling for Android requires OpenSSL. The vendored `openssl-src` crate needs a full Perl installation -- Git Bash's built-in Perl is insufficient. Install [Strawberry Perl](https://strawberryperl.com/) and ensure it is in your PATH before running `tauri android build`.

**Rust targets:**
```bash
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android
```

## iOS Development (macOS only)

- Xcode from Mac App Store (full install, not just CLI tools)
- Command Line Tools: `xcode-select --install`
- CocoaPods: `brew install cocoapods`
- Apple Developer account configured in Xcode

**Rust targets:**
```bash
rustup target add aarch64-apple-ios x86_64-apple-ios aarch64-apple-ios-sim
```

## Vite Configuration for Mobile

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: process.env.TAURI_DEV_HOST || 'localhost',
    port: 5173,
    strictPort: true,
    hmr: process.env.TAURI_DEV_HOST
      ? { protocol: 'ws', host: process.env.TAURI_DEV_HOST, port: 5174 }
      : undefined,
  },
  clearScreen: false,
  envPrefix: ['VITE_', 'TAURI_'],
  build: {
    target: process.env.TAURI_ENV_PLATFORM === 'windows' ? 'chrome105' : 'safari14',
    minify: !process.env.TAURI_ENV_DEBUG ? 'esbuild' : false,
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
  },
});
```

The `TAURI_DEV_HOST` variable is set automatically when running `cargo tauri android dev` or `cargo tauri ios dev`. It enables HMR over the local network so the mobile device can reach the dev server.

## Platform-Specific Configuration

### Android Permissions (AndroidManifest.xml)
Location: `src-tauri/gen/android/app/src/main/AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.USE_BIOMETRIC"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.VIBRATE"/>
</manifest>
```

### iOS Permissions (Info.plist)
Location: `src-tauri/Info.ios.plist`

```xml
<plist version="1.0">
<dict>
    <key>NSCameraUsageDescription</key>
    <string>Camera access for scanning</string>
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>Location for local features</string>
    <key>NSFaceIDUsageDescription</key>
    <string>Face ID for authentication</string>
</dict>
</plist>
```
