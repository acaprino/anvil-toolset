# Mobile Environment Setup

Android SDK + iOS Xcode tooling on top of the base prerequisites in `setup.md`.

## When to use

Adding Android or iOS targets to an existing Tauri 2 project, or setting up a new dev machine for mobile builds. Pure desktop projects can skip this entirely.

## Rust targets (the one thing easy to forget)

```bash
# Android
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android

# iOS (macOS only)
rustup target add aarch64-apple-ios x86_64-apple-ios aarch64-apple-ios-sim
```

`tauri android init` / `tauri ios init` won't add these for you -- the build will fail late with cryptic linker errors if they're missing.

## Gotchas

- **Strawberry Perl on Windows.** If your Rust deps include `reqwest` with `native-tls`, cross-compiling for Android pulls in the vendored `openssl-src` crate, which needs a full Perl install. Git Bash's bundled Perl is **not** sufficient. Install [Strawberry Perl](https://strawberryperl.com/) and put it on PATH before `tauri android build`. The error message ("Could not find Perl") doesn't make this obvious.
- **`TAURI_DEV_HOST` is set automatically** by `tauri android dev` / `tauri ios dev` -- your `vite.config.ts` should read it and bind `server.host` + HMR to it. If you hardcode `localhost`, the device can't reach the dev server.
- **Vite build target.** Mobile WebViews lag desktop -- target `chrome105` for Android WebView (matches Tauri 2's WebView2 floor) and `safari14` for iOS WKWebView. `esnext` will silently produce code the device WebView can't parse.
- **iOS needs the full Xcode**, not just CLI tools. CocoaPods via `brew install cocoapods` -- the gem version drifts.
- **Android NDK version**: install from SDK Manager, then `NDK_HOME` should resolve dynamically (e.g. `$ANDROID_HOME/ndk/$(ls -1 $ANDROID_HOME/ndk)`); pinning a specific version path breaks across machines.

## Vite config snippet (the parts that matter)

```typescript
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
  },
});
```

## Official docs

- Mobile prerequisites: https://v2.tauri.app/start/prerequisites/#mobile-targets
- Android setup: https://v2.tauri.app/develop/#android
- iOS setup: https://v2.tauri.app/develop/#ios
- Android permissions reference: https://developer.android.com/reference/android/Manifest.permission
- iOS Info.plist usage descriptions: https://developer.apple.com/documentation/bundleresources/information_property_list

## Related

- `setup.md` -- base prerequisites
- `build-deploy-mobile.md` -- store builds, signing, the full Android/iOS gotcha trail
- `testing.md` -- emulator + ADB + WebView debugging
- `ci-cd-mobile.md` -- CI build matrix for mobile
