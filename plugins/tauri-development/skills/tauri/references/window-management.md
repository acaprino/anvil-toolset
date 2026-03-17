# Window Management

Multi-window, frameless, system tray, menus, and global shortcuts for Tauri 2 desktop apps.

## Quick Reference

| Task | API |
|------|-----|
| Create window | `WebviewWindowBuilder::new()` |
| Frameless window | `.decorations(false)` |
| System tray | `TrayIconBuilder::new()` |
| Native menu | `Menu::with_items()` |
| Global shortcut | `tauri-plugin-global-shortcut` |
| Window events | `.on_window_event()` |

## Creating Windows

### Rust: WebviewWindowBuilder

```rust
use tauri::{WebviewWindowBuilder, WebviewUrl};

#[tauri::command]
async fn open_settings(app: tauri::AppHandle) -> Result<(), String> {
    // Check if window already exists
    if let Some(window) = app.get_webview_window("settings") {
        window.set_focus().map_err(|e| e.to_string())?;
        return Ok(());
    }

    WebviewWindowBuilder::new(&app, "settings", WebviewUrl::App("/settings".into()))
        .title("Settings")
        .inner_size(600.0, 400.0)
        .min_inner_size(400.0, 300.0)
        .resizable(true)
        .center()
        .build()
        .map_err(|e| e.to_string())?;

    Ok(())
}
```

### Frontend: WebviewWindow

```typescript
import { WebviewWindow } from '@tauri-apps/api/webviewWindow';

async function openSettings() {
  // Check existing
  const existing = await WebviewWindow.getByLabel('settings');
  if (existing) {
    await existing.setFocus();
    return;
  }

  const win = new WebviewWindow('settings', {
    url: '/settings',
    title: 'Settings',
    width: 600,
    height: 400,
    center: true,
  });

  win.once('tauri://error', (e) => console.error('Window error:', e));
}
```

## Frameless & Transparent Windows

```rust
WebviewWindowBuilder::new(&app, "overlay", WebviewUrl::App("/overlay".into()))
    .decorations(false)        // No title bar
    .transparent(true)         // Transparent background
    .always_on_top(true)       // Float above other windows
    .skip_taskbar(true)        // Hide from taskbar
    .inner_size(300.0, 200.0)
    .build()?;
```

### Custom Drag Region (CSS)

```css
/* Make a custom title bar draggable */
.titlebar {
  height: 30px;
  -webkit-app-region: drag;    /* Enable dragging */
  user-select: none;
}

.titlebar button {
  -webkit-app-region: no-drag; /* Buttons remain clickable */
}
```

### Window Controls (Rust)

```rust
#[tauri::command]
async fn minimize_window(window: tauri::WebviewWindow) -> Result<(), String> {
    window.minimize().map_err(|e| e.to_string())
}

#[tauri::command]
async fn toggle_maximize(window: tauri::WebviewWindow) -> Result<(), String> {
    if window.is_maximized().map_err(|e| e.to_string())? {
        window.unmaximize().map_err(|e| e.to_string())?;
    } else {
        window.maximize().map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
async fn close_window(window: tauri::WebviewWindow) -> Result<(), String> {
    window.close().map_err(|e| e.to_string())
}
```

## System Tray

### Setup

```rust
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::menu::{Menu, MenuItem};

fn setup_tray(app: &tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
    let show = MenuItem::with_id(app, "show", "Show Window", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&show, &quit])?;

    TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .tooltip("My App")
        .on_menu_event(|app, event| match event.id.as_ref() {
            "quit" => app.exit(0),
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            _ => {}
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;

    Ok(())
}
```

### Minimize to Tray Instead of Closing

```rust
tauri::Builder::default()
    .setup(|app| {
        setup_tray(app)?;

        // Intercept close to minimize to tray
        let window = app.get_webview_window("main").unwrap();
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                // Hide instead of closing
                if let Some(win) = window.app_handle().get_webview_window("main") {
                    let _ = win.hide();
                }
            }
        });

        Ok(())
    })
```

## Native Menus

```rust
use tauri::menu::{Menu, Submenu, MenuItem, PredefinedMenuItem, CheckMenuItem};

fn setup_menu(app: &tauri::App) -> Result<Menu<tauri::Wry>, Box<dyn std::error::Error>> {
    let file_menu = Submenu::with_items(
        app,
        "File",
        true,
        &[
            &MenuItem::with_id(app, "new", "New", true, Some("CmdOrCtrl+N"))?,
            &MenuItem::with_id(app, "open", "Open...", true, Some("CmdOrCtrl+O"))?,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "save", "Save", true, Some("CmdOrCtrl+S"))?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::quit(app, Some("Quit"))?,
        ],
    )?;

    let view_menu = Submenu::with_items(
        app,
        "View",
        true,
        &[
            &CheckMenuItem::with_id(app, "sidebar", "Show Sidebar", true, true, None::<&str>)?,
            &PredefinedMenuItem::fullscreen(app, Some("Fullscreen"))?,
        ],
    )?;

    let menu = Menu::with_items(app, &[&file_menu, &view_menu])?;
    Ok(menu)
}
```

### Handle Menu Events

```rust
tauri::Builder::default()
    .menu(|app| setup_menu(app))
    .on_menu_event(|app, event| {
        match event.id.as_ref() {
            "new" => { /* handle new */ }
            "open" => { /* handle open */ }
            "save" => { /* handle save */ }
            _ => {}
        }
    })
```

## Global Shortcuts

### Plugin Setup

```bash
npm run tauri add global-shortcut
```

### Rust Registration

```rust
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Modifiers, Shortcut};

tauri::Builder::default()
    .plugin(tauri_plugin_global_shortcut::Builder::new().build())
    .setup(|app| {
        let shortcut = Shortcut::new(Some(Modifiers::CONTROL | Modifiers::SHIFT), Code::Space);

        app.global_shortcut().on_shortcut(shortcut, |app, _shortcut, event| {
            if event.state == tauri_plugin_global_shortcut::ShortcutState::Pressed {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })?;

        Ok(())
    })
```

### Frontend Registration

```typescript
import { register } from '@tauri-apps/plugin-global-shortcut';

await register('CommandOrControl+Shift+Space', (event) => {
  if (event.state === 'Pressed') {
    console.log('Global shortcut triggered');
  }
});
```

### Capabilities

```json
{
  "identifier": "default",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "global-shortcut:allow-register",
    "global-shortcut:allow-unregister"
  ]
}
```

## Window Events

```rust
window.on_window_event(|event| {
    match event {
        tauri::WindowEvent::CloseRequested { api, .. } => {
            // Prevent close, handle gracefully
            api.prevent_close();
        }
        tauri::WindowEvent::Focused(focused) => {
            println!("Window focused: {}", focused);
        }
        tauri::WindowEvent::Moved(position) => {
            println!("Window moved to: {:?}", position);
        }
        tauri::WindowEvent::Resized(size) => {
            println!("Window resized to: {:?}", size);
        }
        _ => {}
    }
});
```

### Frontend Window Events

```typescript
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';

const appWindow = getCurrentWebviewWindow();

const unlisten = await appWindow.onCloseRequested(async (event) => {
  const confirmed = await confirm('Are you sure?');
  if (!confirmed) {
    event.preventDefault();
  }
});

await appWindow.onMoved(({ payload: position }) => {
  console.log(`Moved to ${position.x}, ${position.y}`);
});

await appWindow.onResized(({ payload: size }) => {
  console.log(`Resized to ${size.width}x${size.height}`);
});
```

## Inter-Window Communication

### Via Tauri Events

```rust
// Emit to specific window
app.get_webview_window("settings")
    .unwrap()
    .emit("config-updated", &new_config)?;

// Emit to all windows
app.emit("global-update", &payload)?;
```

```typescript
// Listen in target window
import { listen } from '@tauri-apps/api/event';

const unlisten = await listen('config-updated', (event) => {
  console.log('Config updated:', event.payload);
});
```

### Via Shared State

```rust
use std::sync::Mutex;

struct AppState {
    config: Mutex<AppConfig>,
}

// Both windows access same state through commands
#[tauri::command]
fn get_config(state: tauri::State<AppState>) -> AppConfig {
    state.config.lock().unwrap().clone()
}
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Window not found | Check label matches exactly, window may not be created yet |
| Tray icon not showing | Verify icon path, use `.icon(app.default_window_icon().unwrap().clone())` |
| Global shortcut conflict | Check system-wide shortcuts, handle registration errors |
| Frameless window not draggable | Add `-webkit-app-region: drag` CSS to drag area |
| Close event not intercepted | Use `on_window_event` with `api.prevent_close()` |
| Menu accelerator not working | Use `CmdOrCtrl` for cross-platform, verify capability |
