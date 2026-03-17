# Shell Plugin

Child processes, sidecar binaries, and scoped commands with tauri-plugin-shell.

## Quick Reference

| Task | API |
|------|-----|
| Add plugin | `npm run tauri add shell` |
| Run command | `Command::new("cmd")` (Rust) |
| Run sidecar | `Command::sidecar("name")` (Rust) |
| Frontend command | `Command.create("cmd")` (TS) |
| Frontend sidecar | `Command.sidecar("name")` (TS) |
| Open URL | Use `tauri-plugin-opener` instead |

## Plugin Setup

### Install

```bash
npm run tauri add shell
```

### Cargo.toml

```toml
[dependencies]
tauri-plugin-shell = "2"
```

### lib.rs

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
```

## Scoped Commands (Permissions)

Shell commands must be explicitly allowed in capabilities. Tauri 2 uses a scope-based permission model.

### capabilities/default.json

```json
{
  "identifier": "default",
  "windows": ["main"],
  "permissions": [
    "core:default",
    {
      "identifier": "shell:allow-execute",
      "allow": [
        {
          "name": "git-status",
          "cmd": "git",
          "args": ["status"]
        },
        {
          "name": "node-version",
          "cmd": "node",
          "args": ["--version"]
        },
        {
          "name": "run-script",
          "cmd": "node",
          "args": [
            { "validator": "\\S+" }
          ]
        }
      ]
    },
    "shell:allow-spawn",
    "shell:allow-stdin-write"
  ]
}
```

### Argument Validators

```json
{
  "name": "flexible-git",
  "cmd": "git",
  "args": [
    { "validator": "(status|log|diff|branch)" },
    { "validator": ".*", "raw": true }
  ]
}
```

- Fixed string: `"status"` -- exact match only
- Validator regex: `{ "validator": "\\S+" }` -- matches pattern
- `"raw": true` -- pass through without shell escaping

## Rust API

### Execute Command (Collected Output)

```rust
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn run_git_status(app: tauri::AppHandle) -> Result<String, String> {
    let output = app
        .shell()
        .command("git")
        .args(["status", "--porcelain"])
        .output()
        .await
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}
```

### Spawn Command (Streaming)

```rust
use tauri_plugin_shell::{ShellExt, process::CommandEvent};

#[tauri::command]
async fn run_long_process(app: tauri::AppHandle) -> Result<(), String> {
    let (mut rx, child) = app
        .shell()
        .command("cargo")
        .args(["build", "--release"])
        .current_dir("/path/to/project")
        .envs([("RUST_LOG", "info")])
        .spawn()
        .map_err(|e| e.to_string())?;

    // Stream output
    tokio::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    println!("stdout: {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Stderr(line) => {
                    eprintln!("stderr: {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Terminated(status) => {
                    println!("Process exited: {:?}", status.code);
                    break;
                }
                CommandEvent::Error(err) => {
                    eprintln!("Error: {}", err);
                    break;
                }
                _ => {}
            }
        }
    });

    Ok(())
}
```

### Kill Process

```rust
// child from .spawn()
child.kill().map_err(|e| e.to_string())?;
```

### Write to Stdin

```rust
let (mut rx, mut child) = app
    .shell()
    .command("node")
    .args(["-i"]) // interactive mode
    .spawn()
    .map_err(|e| e.to_string())?;

// Write to stdin
child.write("console.log('hello')\n".as_bytes())
    .map_err(|e| e.to_string())?;
```

## Sidecar Binaries

Sidecar binaries are external executables bundled with your app.

### tauri.conf.json

```json
{
  "bundle": {
    "externalBin": [
      "binaries/my-tool",
      "binaries/ffmpeg"
    ]
  }
}
```

### File Naming Convention

Sidecar binaries must follow the target triple naming:

```
binaries/
  my-tool-x86_64-pc-windows-msvc.exe
  my-tool-x86_64-unknown-linux-gnu
  my-tool-aarch64-apple-darwin
  my-tool-x86_64-apple-darwin
```

Get the target triple:

```bash
rustc -Vv | grep host
```

### Rust: Run Sidecar

```rust
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn run_sidecar(app: tauri::AppHandle) -> Result<String, String> {
    let output = app
        .shell()
        .sidecar("my-tool")
        .map_err(|e| e.to_string())?
        .args(["--input", "data.json"])
        .output()
        .await
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}
```

### Sidecar Permissions

```json
{
  "identifier": "shell:allow-execute",
  "allow": [
    {
      "name": "my-tool",
      "sidecar": true,
      "args": [
        { "validator": ".*" }
      ]
    }
  ]
}
```

## Frontend API

### Execute Command

```typescript
import { Command } from '@tauri-apps/plugin-shell';

// Collected output
const output = await Command.create('git-status').execute();
console.log('stdout:', output.stdout);
console.log('stderr:', output.stderr);
console.log('code:', output.code);
```

### Spawn Command (Streaming)

```typescript
import { Command } from '@tauri-apps/plugin-shell';

const command = Command.create('run-script', ['build.js']);

command.on('close', (data) => {
  console.log(`Exited with code ${data.code} and signal ${data.signal}`);
});

command.stdout.on('data', (line) => {
  console.log(`stdout: ${line}`);
});

command.stderr.on('data', (line) => {
  console.error(`stderr: ${line}`);
});

const child = await command.spawn();

// Later: kill the process
await child.kill();
```

### Write to Stdin

```typescript
const child = await command.spawn();
await child.write('input data\n');
```

### Run Sidecar

```typescript
import { Command } from '@tauri-apps/plugin-shell';

const command = Command.sidecar('my-tool', ['--input', 'data.json']);
const output = await command.execute();
```

## Environment Variables

```rust
// Set env vars for child process
app.shell()
    .command("node")
    .args(["server.js"])
    .envs([
        ("NODE_ENV", "production"),
        ("PORT", "3000"),
    ])
    .spawn()?;
```

## Working Directory

```rust
app.shell()
    .command("npm")
    .args(["run", "build"])
    .current_dir("/path/to/project")
    .output()
    .await?;
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Command not allowed | Add scoped permission to capabilities/default.json |
| Sidecar not found | Check target triple in filename, verify `externalBin` path |
| Sidecar permission denied | Add `"sidecar": true` to permission scope |
| Args rejected | Verify args match validators exactly |
| Stdin not working | Ensure `shell:allow-stdin-write` permission |
| Open URL fails | Use `tauri-plugin-opener` (`openUrl()`), not shell plugin |
| Windows: cmd.exe popup | Use `.creation_flags(0x08000000)` (CREATE_NO_WINDOW) |
| PATH not found | Specify full path or set env vars explicitly |
