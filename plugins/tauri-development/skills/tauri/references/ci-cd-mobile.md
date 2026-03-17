# Mobile CI/CD

> For base CI/CD patterns (caching, OS matrix, release profiles), see `tauri-core/references/ci-cd.md`.

## Mobile Build Requirements

### Android
- Java 17+ (JDK)
- Android SDK with Platform Tools, Build Tools, NDK
- Rust targets: `aarch64-linux-android`, `armv7-linux-androideabi`

### iOS
- macOS runner (required -- iOS builds cannot run on Linux/Windows)
- Xcode (full install)
- Rust targets: `aarch64-apple-ios`, `aarch64-apple-ios-sim`

## Android Signing in CI

1. Store keystore as base64-encoded secret
2. Decode at build time:
```bash
echo "$ANDROID_KEYSTORE_BASE64" | base64 -d > /tmp/keystore.jks
```
3. Write `keystore.properties` with alias, password, path

### Required Secrets
```
ANDROID_KEY_ALIAS
ANDROID_KEY_PASSWORD
ANDROID_KEYSTORE_BASE64    # base64 -i upload-keystore.jks | tr -d '\n'
```

## iOS Signing in CI

Use App Store Connect API key for headless signing:

### Required Secrets
```
APPLE_API_ISSUER
APPLE_API_KEY
APPLE_API_KEY_CONTENT      # Content of .p8 file
APPLE_TEAM_ID
```

## Mobile Caching

In addition to Rust and Node caches:

| Cache | Path | Key |
|-------|------|-----|
| Gradle | `~/.gradle/caches/` | OS + `gradle-wrapper.properties` hash |
| CocoaPods | `Pods/`, `~/Library/Caches/CocoaPods/` | OS + `Podfile.lock` hash |

## Store Upload Automation

### Google Play
Use Fastlane or the Google Play Developer API to upload AABs:
- Track options: internal, alpha, beta, production
- Requires service account JSON with appropriate permissions

### App Store
Use Fastlane or `xcrun altool` to upload IPAs:
- Requires App Store Connect API key
- Can skip screenshots/metadata for automated uploads

## Mobile Build Tips

- Build Android on Ubuntu runners (fastest, cheapest)
- Build iOS on macOS runners (required by Apple)
- Run Android and iOS builds in parallel
- Use `--target aarch64` to skip x86 builds if not needed
- 16KB page size alignment may be required for Google Play (NDK < 28)
