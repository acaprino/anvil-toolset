# Frontend Patterns for Tauri

## Invoking Rust Commands

```typescript
import { invoke } from '@tauri-apps/api/core';

// Simple invoke
const result = await invoke<string>('greet', { name: 'World' });

// Type-safe wrapper
export async function greet(name: string): Promise<string> {
  return invoke('greet', { name });
}

export async function fetchData(url: string): Promise<string> {
  return invoke('fetch_data', { url });
}
```

## Channels (Streaming)

```typescript
import { invoke, Channel } from '@tauri-apps/api/core';

interface Progress {
  downloaded: number;
  total: number;
  percentage: number;
}

export async function downloadWithProgress(
  url: string,
  onProgress: (progress: Progress) => void
): Promise<Uint8Array> {
  const channel = new Channel<Progress>();
  channel.onmessage = onProgress;

  return invoke('download_with_progress', {
    url,
    onProgress: channel,
  });
}

// Usage
await downloadWithProgress('https://example.com/file.zip', (p) => {
  console.log(`${p.percentage}% complete`);
});
```

## Event Listeners

```typescript
import { listen, emit } from '@tauri-apps/api/event';

// Listen for events from Rust
const unlisten = await listen<{ timestamp: string }>('background-tick', (event) => {
  console.log('Tick:', event.payload.timestamp);
});

// Cleanup
unlisten();

// Emit event to Rust
await emit('user-action', { action: 'clicked' });
```

## Platform Detection

```typescript
import { platform, arch } from '@tauri-apps/plugin-os';

export async function getPlatform() {
  const p = await platform();
  return {
    isAndroid: p === 'android',
    isIOS: p === 'ios',
    isMobile: p === 'android' || p === 'ios',
    isDesktop: !['android', 'ios'].includes(p),
    arch: await arch(),
  };
}
```

## Plugin Usage Examples

### File System
```typescript
import { readTextFile, writeTextFile, BaseDirectory } from '@tauri-apps/plugin-fs';

async function saveData(filename: string, data: object) {
  await writeTextFile(filename, JSON.stringify(data), {
    baseDir: BaseDirectory.AppData,
  });
}

async function loadData<T>(filename: string): Promise<T | null> {
  try {
    const content = await readTextFile(filename, {
      baseDir: BaseDirectory.AppData,
    });
    return JSON.parse(content);
  } catch {
    return null;
  }
}
```

### HTTP Client
```typescript
import { fetch } from '@tauri-apps/plugin-http';

async function apiCall<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
}
```

## React Hooks Examples

```typescript
import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';

// Generic invoke hook
function useInvoke<T>(command: string, args?: Record<string, unknown>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    invoke<T>(command, args)
      .then(setData)
      .catch((e) => setError(e.toString()))
      .finally(() => setLoading(false));
  }, [command, JSON.stringify(args)]);

  return { data, loading, error };
}

// Event listener hook
function useEvent<T>(eventName: string, handler: (payload: T) => void) {
  useEffect(() => {
    const unlisten = listen<T>(eventName, (e) => handler(e.payload));
    return () => { unlisten.then(fn => fn()); };
  }, [eventName, handler]);
}
```

## Capabilities Configuration

Add permissions in `src-tauri/capabilities/default.json`:

```json
{
  "$schema": "https://schemas.tauri.app/config/2/Capability",
  "identifier": "default",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "fs:default",
    "http:default",
    "notification:default",
    "clipboard-manager:default"
  ]
}
```
