---
name: firefox-extension-dev
description: Expert Firefox extension (WebExtension) developer. Use PROACTIVELY when creating, debugging, or publishing any Firefox extension or browser add-on. Covers Manifest V2/V3, browser.* APIs, cross-browser compatibility, AMO publishing, and web-ext CLI.
---

# Firefox Extension Development Expert

Build, debug, publish, and maintain Firefox WebExtensions. Covers Manifest V2 and V3, all 51 browser.* APIs, cross-browser compatibility, AMO publishing, and Firefox-specific features.

## When to Use

Trigger on: Firefox extension, WebExtension, browser add-on, manifest.json for extensions, content scripts, background scripts, browser.tabs, browser.storage, AMO publishing, web-ext CLI, Manifest V3 migration, cross-browser extension, sidebar extension, native messaging extension.

## Documentation Source

All knowledge sourced from MDN WebExtensions documentation.

**Keep updated from:** `https://github.com/mdn/content/tree/main/files/en-us/mozilla/add-ons/webextensions`

**Key GitHub repos:**
- MDN docs source: [mdn/content](https://github.com/mdn/content/tree/main/files/en-us/mozilla/add-ons/webextensions)
- Official examples: [mdn/webextensions-examples](https://github.com/mdn/webextensions-examples)
- Browser API polyfill: [mozilla/webextension-polyfill](https://github.com/mozilla/webextension-polyfill)
- web-ext CLI: [mozilla/web-ext](https://github.com/mozilla/web-ext)
- Extension Workshop: [extensionworkshop.com](https://extensionworkshop.com)

---

## Extension Anatomy

Every extension is a collection of files packaged as a `.zip`. The only mandatory file is `manifest.json`.

### File Structure

```
my-extension/
  manifest.json              # REQUIRED - metadata + pointers
  background.js              # event handling, extension lifecycle
  content-scripts/
    content.js               # injected into web pages
    styles.css               # injected styles
  popup/
    popup.html               # toolbar button popup
    popup.js
    popup.css
  sidebar/
    sidebar.html             # sidebar panel (Firefox-only)
    sidebar.js
  options/
    options.html             # settings page
    options.js
  icons/
    icon-48.png
    icon-96.png
  _locales/                  # i18n strings
    en/messages.json
  web-accessible-resources/  # files accessible to page scripts
```

### Component Types

| Component | Purpose | API Access |
|---|---|---|
| Background scripts | Browser event handling, extension lifecycle | Full (all permitted APIs) |
| Content scripts | DOM manipulation in web pages | Limited subset + messaging |
| Popup | Toolbar button UI (HTML) | Full (same as background) |
| Sidebar | Side panel UI (Firefox-only) | Full (same as background) |
| Options page | User preferences UI | Full (same as background) |
| Extension pages | Custom HTML loaded via `tabs.create`/`windows.create` | Full (same as background) |
| DevTools page | Developer tools panel | Full + devtools APIs |

---

## Content Scripts

### Loading Methods

**1. Declarative (manifest.json):**

```json
{
  "content_scripts": [{
    "matches": ["*://*.example.com/*"],
    "exclude_matches": ["*://admin.example.com/*"],
    "js": ["jquery.js", "content.js"],
    "css": ["styles.css"],
    "run_at": "document_idle",
    "all_frames": false,
    "match_about_blank": false
  }]
}
```

`run_at` values:
- `document_start` - before DOM construction
- `document_end` - DOM ready, before subresources
- `document_idle` - default, after page load

**2. Programmatic (MV3 scripting API):**

```javascript
await browser.scripting.executeScript({ target: { tabId }, files: ["content.js"] });
await browser.scripting.insertCSS({ target: { tabId }, files: ["styles.css"] });
await browser.scripting.registerContentScripts([{
  id: "my-script", matches: ["*://*.example.com/*"],
  js: ["content.js"], persistAcrossSessions: true
}]);
```

### Content Script Environment

- **DOM access:** Full access to page DOM via standard Web APIs
- **JS isolation:** Cannot see page-defined JS variables (Xray vision in Firefox)
- **API access:** Limited subset - `runtime`, `i18n`, `storage`, `extension`, `menus.getTargetElement`

---

## Background Scripts

### MV3 Event Page (Firefox)

Firefox MV3 uses **event pages** (non-persistent background pages with DOM access), NOT service workers like Chrome.

**Critical rules for event pages:**
1. Register listeners at top level synchronously - deferred registration breaks wake-up
2. Persist state via `storage.session`/`storage.local`, not globals
3. Use `browser.alarms` instead of `setTimeout`/`setInterval`
4. `runtime.onSuspend` fires before unload - use for cleanup

---

## Message Passing

### One-Off Messages

```javascript
// Content script -> Background
browser.runtime.sendMessage({ type: "getData", key: "user" }).then(response => console.log(response));

// Background -> Content script
await browser.tabs.sendMessage(tabId, { type: "update", data: newData });
```

### Port Connections (Long-Lived)

```javascript
const port = browser.runtime.connect({ name: "data-stream" });
port.postMessage({ greeting: "hello" });
port.onMessage.addListener((msg) => { /* handle */ });
```

### Content Script to Page Script (window.postMessage)

**Security warning:** Never `eval()` data received from page scripts. Extensions are privileged code - hostile pages can exploit this.

---

## Match Patterns

**Syntax:** `<scheme>://<host><path>`

| Pattern | Matches |
|---|---|
| `<all_urls>` | All URLs with supported schemes |
| `*://*/*` | All HTTP/HTTPS/WS URLs |
| `*://*.mozilla.org/*` | mozilla.org + subdomains |
| `https://mozilla.org/` | Exact host, HTTPS only |

---

## Permissions

### Install-Time vs Optional

- `permissions` + `host_permissions` (MV3) granted at install
- `optional_permissions` + `optional_host_permissions` requested at runtime from user action handler
- Users can revoke optional permissions in Add-ons Manager (since Firefox 84)

---

## Native Messaging

Enables communication between extension and native applications.

- Permission: `nativeMessaging`
- Native app manifest: JSON with `name`, `path`, `type: "stdio"`, `allowed_extensions`
- Wire protocol: JSON UTF-8, 32-bit unsigned length prefix
- Limits: Max 1 MB from app, max 4 GB to app
- Use `runtime.connectNative()` for connection-based or `runtime.sendNativeMessage()` for one-off

---

## Firefox-Specific Features

| Feature | API | Notes |
|---|---|---|
| Container Tabs | `contextualIdentities` | Isolated cookie stores, requires `contextualIdentities` + `cookies` |
| Sidebar | `sidebarAction` | Firefox-exclusive sidebar panel |
| Protocol Handlers | manifest `protocol_handlers` | Register as URI protocol handler |
| userScripts (MV3) | `userScripts` | Isolated execution worlds, must be in `optional_permissions` |
| webRequest Blocking in MV3 | `webRequest` | Firefox retains blocking capability alongside DNR |
| Other exclusive | `dns`, `pkcs11`, `find`, `captivePortal`, `tabs.saveAsPDF()`, `tabs.print()` | |

---

## Manifest V3 Migration

### Firefox MV3 vs Chrome MV3

| Feature | Firefox MV3 | Chrome MV3 |
|---|---|---|
| Background | Event pages (DOM access) | Service workers (no DOM) |
| webRequest blocking | Fully supported + DNR | Removed; DNR only |
| host_permissions | Treated as optional (user-grantable) | Granted at install |
| MV2 support | Indefinite | Disabled (July 2025) |
| Data cloning | Structured clone algorithm | JSON serialization |

### Migration Checklist (MV2 to MV3)

1. Set `"manifest_version": 3`
2. Move host permissions from `permissions` to `host_permissions` / `optional_host_permissions`
3. Rename `browser_action` to `action`, `_execute_browser_action` to `_execute_action`
4. Remove `browser_style` from all manifest keys
5. Replace `tabs.executeScript`/`insertCSS`/`removeCSS` with `browser.scripting` API
6. Convert background to non-persistent
7. Move all event listeners to top-level synchronous registration
8. Replace global state variables with `storage.session`/`storage.local`
9. Replace `setTimeout`/`setInterval` with `browser.alarms`
10. Update CSP format: `"content_security_policy": { "extension_pages": "..." }`
11. Update `web_accessible_resources` to object array format
12. Remove all `eval()` usage (forbidden in MV3)

---

## Cross-Browser Compatibility

### Namespace

- Firefox: `browser.*` (Promises) + `chrome.*` (callbacks)
- Chrome: `chrome.*` (MV2: callbacks, MV3: Promises from Chrome 121+)
- Safari: `browser.*` (Promises)

### Strategy

1. Code for Firefox first using `browser.*` + Promises
2. Apply [webextension-polyfill](https://github.com/mozilla/webextension-polyfill) for Chrome/Edge/Opera
3. Use runtime feature detection for platform-specific APIs
4. Create separate `manifest.json` per browser

---

## Development Workflow

### web-ext CLI

```bash
web-ext run --firefox nightly --browser-console --start-url https://example.com
web-ext lint
web-ext build --overwrite-dest
web-ext sign --channel unlisted --api-key $WEB_EXT_API_KEY --api-secret $WEB_EXT_API_SECRET
```

### Loading Temporarily

1. Open Firefox - `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on..."
3. Select `manifest.json` from extension directory

### Debugging

- **Browser Console:** `Ctrl+Shift+J` - background script logs
- **Extension Debugger:** `about:debugging` - Inspect on extension
- **Content Script Console:** Regular page DevTools (select extension context)

---

## Common Patterns

- **Toolbar button with popup:** `action` manifest key + popup HTML/JS
- **Context menu:** `browser.menus.create()` + `menus.onClicked`
- **Page modification:** Content script with DOM manipulation
- **Options page:** `options_ui` manifest key + storage sync
- **Web request interception:** `webRequest.onBeforeRequest` with blocking
- **Badge text:** `browser.action.setBadgeText()` + `setBadgeBackgroundColor()`
- **Periodic tasks (MV3):** `browser.alarms.create()` + `alarms.onAlarm`

---

## Debugging Checklist

1. Check `about:debugging` - is the extension loaded? Any errors?
2. Browser Console (`Ctrl+Shift+J`) - background script errors
3. Page DevTools Console - content script errors (select extension context)
4. Permissions - are all needed permissions declared?
5. Match patterns - do content script patterns match the target URLs?
6. CSP violations - check for Content Security Policy blocks
7. MV3 event page - are listeners registered synchronously at top level?
8. Storage - using `browser.storage` instead of `window.localStorage`?
9. Run `web-ext lint` to catch common issues

---

## References

- `references/browser-api-reference.md` - Complete list of all 51 browser.* APIs with methods, events, and permissions
- `references/manifest-schema.md` - Full manifest.json key reference with MV2/MV3 examples
- `references/amo-publishing.md` - AMO publishing checklist, review policies, CSP, security best practices, i18n
