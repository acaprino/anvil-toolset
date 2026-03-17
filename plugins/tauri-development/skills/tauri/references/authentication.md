# Authentication in Tauri Apps

## Google OAuth / Firebase Auth

### The WebView Problem

**Google explicitly blocks OAuth sign-in from WebViews/embedded browsers** for security reasons. This means:
- `signInWithPopup()` does not work in Tauri's WebView (desktop or mobile)
- `signInWithRedirect()` also fails
- This applies to both Firebase Auth and direct Google OAuth

### Solution: System Browser + Deep Links

The solution is to open OAuth in the system browser and return via deep links.

#### Required Plugins

```bash
npm run tauri add opener
npm run tauri add deep-link
```

On desktop, you can use either the `opener` plugin or the `shell` plugin (`shell:open`) to launch the system browser. On mobile, use the `opener` plugin -- the `shell` plugin does not work for URLs on Android.

### OAuth Flow Architecture

```
App --> System Browser (Google OAuth)
                              |
                       User signs in
                              |
                   Callback page / redirect
                   (parses tokens from URL)
                              |
                 myapp://auth/callback (deep link)
                              |
                       App (validates state, authenticated)
```

---

## Security Warning

> **Token Exposure Risk:** The implicit OAuth flow passes tokens through URLs, which may be logged in browser history, server access logs, or referrer headers. For high-security applications, consider using the **Authorization Code flow with PKCE** (documented below) instead of the implicit flow.

---

## TypeScript Interfaces

Define these types for type-safe OAuth handling:

```typescript
// src/types/auth.ts

/** OAuth state stored before redirect */
export interface OAuthState {
  continueUri: string;
  nonce: string;
  timestamp: number;
}

/** Parameters received in OAuth callback */
export interface OAuthCallbackParams {
  access_token?: string;
  id_token?: string;
  state?: string;
  error?: string;
  error_description?: string;
}

/** Auth configuration (validate at startup) */
export interface AuthConfig {
  googleClientId: string;
  callbackUrl: string;
  appScheme: string;
}

/** Auth context state */
export interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  clearError: () => void;
}
```

---

## Implementation

### 1. Configuration with Validation

```typescript
// src/config/auth.ts
import type { AuthConfig } from '../types/auth';

function getRequiredEnv(key: string): string {
  const value = import.meta.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

export function getAuthConfig(): AuthConfig {
  return {
    googleClientId: getRequiredEnv('VITE_GOOGLE_CLIENT_ID'),
    callbackUrl: getRequiredEnv('VITE_AUTH_CALLBACK_URL'),
    appScheme: import.meta.env.VITE_APP_SCHEME || 'myapp',
  };
}

// Validate config at app startup
export function validateAuthConfig(): void {
  const config = getAuthConfig();

  if (!config.googleClientId.endsWith('.apps.googleusercontent.com')) {
    throw new Error('Invalid Google Client ID format');
  }

  if (!config.callbackUrl.startsWith('https://')) {
    throw new Error('Callback URL must use HTTPS');
  }
}
```

### 2. Secure State Management

```typescript
// src/utils/oauth-state.ts
import { Store } from '@tauri-apps/plugin-store';
import type { OAuthState } from '../types/auth';

const OAUTH_STATE_KEY = 'pending_oauth_state';
const STATE_EXPIRY_MS = 10 * 60 * 1000; // 10 minutes

let store: Store | null = null;

async function getStore(): Promise<Store> {
  if (!store) {
    store = new Store('auth.json');
  }
  return store;
}

/** Store OAuth state before redirect */
export async function saveOAuthState(state: OAuthState): Promise<void> {
  const s = await getStore();
  await s.set(OAUTH_STATE_KEY, state);
  await s.save();
}

/** Retrieve and clear OAuth state */
export async function consumeOAuthState(): Promise<OAuthState | null> {
  const s = await getStore();
  const state = await s.get<OAuthState>(OAUTH_STATE_KEY);

  // Always clear state after retrieval (one-time use)
  await s.delete(OAUTH_STATE_KEY);
  await s.save();

  if (!state) {
    return null;
  }

  // Check if state has expired
  if (Date.now() - state.timestamp > STATE_EXPIRY_MS) {
    console.warn('OAuth state expired');
    return null;
  }

  return state;
}

/** Clear any pending OAuth state */
export async function clearOAuthState(): Promise<void> {
  const s = await getStore();
  await s.delete(OAUTH_STATE_KEY);
  await s.save();
}
```

### 3. Initiate OAuth Flow (with CSRF Protection)

```typescript
// src/utils/oauth.ts
import { openUrl } from '@tauri-apps/plugin-opener';
import { getAuthConfig } from '../config/auth';
import { saveOAuthState } from './oauth-state';
import type { OAuthState } from '../types/auth';

export class OAuthError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'OAuthError';
  }
}

export async function initiateGoogleSignIn(): Promise<void> {
  const config = getAuthConfig();

  // Generate single nonce for both state and ID token validation
  const nonce = crypto.randomUUID();

  const oauthState: OAuthState = {
    continueUri: `${config.appScheme}://auth/callback`,
    nonce,
    timestamp: Date.now(),
  };

  // Store state BEFORE redirect for validation on callback
  await saveOAuthState(oauthState);

  const stateParam = encodeURIComponent(JSON.stringify(oauthState));

  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  authUrl.searchParams.set('client_id', config.googleClientId);
  authUrl.searchParams.set('redirect_uri', config.callbackUrl);
  authUrl.searchParams.set('response_type', 'token id_token');
  authUrl.searchParams.set('scope', 'openid email profile');
  authUrl.searchParams.set('state', stateParam);
  authUrl.searchParams.set('nonce', nonce); // Same nonce as in state
  authUrl.searchParams.set('prompt', 'select_account');

  try {
    await openUrl(authUrl.toString());
  } catch (error) {
    // Clear state on failure
    await clearOAuthState();
    throw new OAuthError(
      'Failed to open sign-in page. Please try again.',
      'OPEN_URL_FAILED'
    );
  }
}
```

### 4. Handle Callback with State Validation

```typescript
// src/utils/oauth-callback.ts
import {
  getAuth,
  GoogleAuthProvider,
  signInWithCredential,
} from 'firebase/auth';
import { consumeOAuthState } from './oauth-state';
import { OAuthError } from './oauth';
import type { OAuthCallbackParams, OAuthState } from '../types/auth';

/** Parse callback URL parameters */
function parseCallbackUrl(url: string): OAuthCallbackParams {
  const urlObj = new URL(url);
  const params = new URLSearchParams(urlObj.search);

  return {
    access_token: params.get('access_token') || undefined,
    id_token: params.get('id_token') || undefined,
    state: params.get('state') || undefined,
    error: params.get('error') || undefined,
    error_description: params.get('error_description') || undefined,
  };
}

/** Validate state parameter against stored state */
function validateState(
  returnedState: string | undefined,
  storedState: OAuthState
): boolean {
  if (!returnedState) {
    return false;
  }

  try {
    const parsed = JSON.parse(decodeURIComponent(returnedState)) as OAuthState;
    return parsed.nonce === storedState.nonce;
  } catch {
    return false;
  }
}

/** Handle OAuth callback with full validation */
export async function handleOAuthCallback(url: string): Promise<void> {
  const params = parseCallbackUrl(url);

  // Check for OAuth error response
  if (params.error) {
    throw new OAuthError(
      params.error_description || params.error,
      params.error
    );
  }

  // Retrieve stored state (one-time use)
  const storedState = await consumeOAuthState();

  if (!storedState) {
    throw new OAuthError(
      'No pending authentication. Please try signing in again.',
      'NO_PENDING_STATE'
    );
  }

  // CRITICAL: Validate state to prevent CSRF attacks
  if (!validateState(params.state, storedState)) {
    throw new OAuthError(
      'Invalid authentication response. Please try again.',
      'STATE_MISMATCH'
    );
  }

  // Validate required tokens
  if (!params.id_token) {
    throw new OAuthError(
      'Authentication failed. No ID token received.',
      'MISSING_ID_TOKEN'
    );
  }

  // Sign in with Firebase
  const auth = getAuth();
  const credential = GoogleAuthProvider.credential(
    params.id_token,
    params.access_token || null
  );

  try {
    await signInWithCredential(auth, credential);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    throw new OAuthError(
      `Firebase authentication failed: ${message}`,
      'FIREBASE_AUTH_FAILED'
    );
  }
}
```

---

## Recommended: Authorization Code Flow with PKCE

For production apps requiring higher security, use Authorization Code flow with PKCE instead of implicit flow. This avoids exposing tokens in URLs.

### PKCE Utilities

```typescript
// src/utils/pkce.ts

/** Generate cryptographically random code verifier */
export function generateCodeVerifier(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return base64UrlEncode(array);
}

/** Generate code challenge from verifier */
export async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return base64UrlEncode(new Uint8Array(hash));
}

/** Base64 URL-safe encoding */
function base64UrlEncode(buffer: Uint8Array): string {
  const base64 = btoa(String.fromCharCode(...buffer));
  return base64
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}
```

### PKCE OAuth Flow

```typescript
// src/utils/oauth-pkce.ts
import { openUrl } from '@tauri-apps/plugin-opener';
import { Store } from '@tauri-apps/plugin-store';
import { getAuthConfig } from '../config/auth';
import { generateCodeVerifier, generateCodeChallenge } from './pkce';

interface PKCEState {
  codeVerifier: string;
  nonce: string;
  timestamp: number;
}

export async function initiateGoogleSignInPKCE(): Promise<void> {
  const config = getAuthConfig();
  const store = new Store('auth.json');

  // Generate PKCE parameters
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);
  const nonce = crypto.randomUUID();

  // Store verifier for token exchange
  const pkceState: PKCEState = {
    codeVerifier,
    nonce,
    timestamp: Date.now(),
  };
  await store.set('pkce_state', pkceState);
  await store.save();

  const state = encodeURIComponent(JSON.stringify({
    continueUri: `${config.appScheme}://auth/callback`,
    nonce,
  }));

  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  authUrl.searchParams.set('client_id', config.googleClientId);
  authUrl.searchParams.set('redirect_uri', config.callbackUrl);
  authUrl.searchParams.set('response_type', 'code'); // Code instead of token
  authUrl.searchParams.set('scope', 'openid email profile');
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('nonce', nonce);
  authUrl.searchParams.set('code_challenge', codeChallenge);
  authUrl.searchParams.set('code_challenge_method', 'S256');
  authUrl.searchParams.set('prompt', 'select_account');

  await openUrl(authUrl.toString());
}

export async function exchangeCodeForTokens(code: string): Promise<{
  idToken: string;
  accessToken: string;
}> {
  const config = getAuthConfig();
  const store = new Store('auth.json');

  const pkceState = await store.get<PKCEState>('pkce_state');
  if (!pkceState) {
    throw new Error('No pending PKCE state');
  }

  // Clear state after retrieval
  await store.delete('pkce_state');
  await store.save();

  // Exchange code for tokens (requires backend or Google's token endpoint)
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: config.googleClientId,
      code,
      code_verifier: pkceState.codeVerifier,
      grant_type: 'authorization_code',
      redirect_uri: config.callbackUrl,
    }),
  });

  if (!response.ok) {
    throw new Error('Token exchange failed');
  }

  const data = await response.json();
  return {
    idToken: data.id_token,
    accessToken: data.access_token,
  };
}
```

> **Note:** PKCE with Google requires your callback page to capture the authorization code and pass it to your app, where the token exchange happens. This keeps tokens out of URLs entirely.

---

## Token Refresh

Firebase Auth handles token refresh automatically, but you can listen for token changes:

```typescript
// src/utils/token-refresh.ts
import { getAuth, onIdTokenChanged, getIdToken } from 'firebase/auth';

/** Set up token refresh listener */
export function setupTokenRefreshListener(
  onTokenRefresh: (token: string) => void
): () => void {
  const auth = getAuth();

  return onIdTokenChanged(auth, async (user) => {
    if (user) {
      // Get current token (refreshed automatically if expired)
      const token = await getIdToken(user);
      onTokenRefresh(token);
    }
  });
}

/** Force refresh token (e.g., before critical API calls) */
export async function forceRefreshToken(): Promise<string | null> {
  const auth = getAuth();
  const user = auth.currentUser;

  if (!user) {
    return null;
  }

  return getIdToken(user, /* forceRefresh */ true);
}
```

---

## Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID (Web application type)
3. Add authorized JavaScript origins:
   - `https://your-app.web.app`
4. Add authorized redirect URIs:
   - `https://your-app.web.app/auth/callback`

---

## Security Checklist

- [ ] HTTPS for all callback URLs
- [ ] State parameter validated on every callback
- [ ] Nonce validated for ID token (single nonce used)
- [ ] OAuth state expires after 10 minutes
- [ ] State cleared after use (one-time)
- [ ] Tokens stored securely (not in localStorage)
- [ ] Error messages don't leak sensitive info
- [ ] PKCE used for high-security applications
- [ ] Token refresh listener configured
- [ ] Deep link listener properly cleaned up
