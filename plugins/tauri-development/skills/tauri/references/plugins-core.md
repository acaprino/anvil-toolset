# Tauri 2 Core Plugins

## Adding Plugins

```bash
npm run tauri add <plugin-name>
```

This automatically:
1. Adds Rust crate to `Cargo.toml`
2. Adds npm package
3. Updates capabilities if needed

## Universal Plugins

| Plugin | Desktop | Mobile | Description |
|--------|---------|--------|-------------|
| `fs` | yes | yes | File system access |
| `http` | yes | yes | HTTP client |
| `notification` | yes | yes | Push/local notifications |
| `clipboard-manager` | yes | yes | Clipboard access |
| `dialog` | yes | yes | Native dialogs |
| `opener` | yes | yes | Open URLs in system browser |
| `store` | yes | yes | Key-value storage |
| `sql` | yes | yes | SQLite database |
| `log` | yes | yes | Logging |
| `os` | yes | yes | OS information |
| `deep-link` | yes | yes | URL scheme handling |

For mobile-only plugins (biometric, barcode-scanner, haptics, nfc), see `references/plugins-mobile.md`.

## Plugin Configuration

### lib.rs Setup
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
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error");
}
```

### Permissions (capabilities/default.json)
```json
{
  "permissions": [
    "core:default",
    "opener:default",
    "deep-link:default",
    "fs:default",
    "http:default",
    "notification:default",
    "store:default",
    "clipboard-manager:default"
  ]
}
```

## Deep Linking Configuration

### tauri.conf.json
```json
{
  "plugins": {
    "deep-link": {
      "desktop": {
        "schemes": ["myapp"]
      }
    }
  }
}
```

For mobile deep link configuration (custom schemes, app links, Android Intent Filters, iOS Associated Domains), see `references/plugins-mobile.md`.

## Opener Plugin (External URLs)

The `opener` plugin opens URLs in the system browser on all platforms. On desktop, you can also use the `shell` plugin's `open` command as an alternative.

### Setup
```bash
npm run tauri add opener
```

### Usage
```typescript
import { openUrl } from '@tauri-apps/plugin-opener';

// Open URL in system browser
await openUrl('https://example.com');

// Open email client
await openUrl('mailto:hello@example.com');

// Open phone dialer
await openUrl('tel:+1234567890');
```

### Permissions
```json
{
  "permissions": [
    "opener:default"
  ]
}
```

### OAuth Use Case
Critical for OAuth flows where Google blocks WebView sign-in. See [authentication.md](authentication.md) for complete OAuth implementation guide.

## Logging Plugin

```rust
// Cargo.toml
tauri-plugin-log = "2"

// lib.rs
.plugin(
    tauri_plugin_log::Builder::new()
        .level(log::LevelFilter::Debug)
        .with_colors(tauri_plugin_log::fern::colors::ColoredLevelConfig::default())
        .build()
)

// Usage
log::info!("App started");
log::debug!("Debug info: {:?}", data);
log::error!("Error: {}", error);
```

## Store Plugin (Persistent Storage)

```typescript
import { Store } from '@tauri-apps/plugin-store';

const store = new Store('settings.json');

// Save
await store.set('theme', 'dark');
await store.set('user', { id: 1, name: 'John' });
await store.save();

// Load
const theme = await store.get<string>('theme');
const user = await store.get<{ id: number; name: string }>('user');

// Delete
await store.delete('theme');
await store.clear();
```

## SQL Plugin (SQLite)

```typescript
import Database from '@tauri-apps/plugin-sql';

const db = await Database.load('sqlite:app.db');

// Create table
await db.execute(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
  )
`);

// Insert
await db.execute(
  'INSERT INTO users (name, email) VALUES (?, ?)',
  ['John', 'john@example.com']
);

// Select
const users = await db.select<{ id: number; name: string; email: string }[]>(
  'SELECT * FROM users WHERE name LIKE ?',
  ['%John%']
);
```
