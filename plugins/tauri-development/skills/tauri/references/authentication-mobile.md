# Mobile Authentication

> For OAuth/PKCE architecture and security patterns, see `tauri-core/references/authentication.md`.

## Deep Link Callback Setup

Configure the deep-link plugin for mobile OAuth callbacks:

**tauri.conf.json:**
```json
{
  "plugins": {
    "deep-link": {
      "mobile": [
        { "scheme": ["myapp"], "appLink": false }
      ]
    }
  }
}
```

**capabilities/default.json:**
```json
{
  "permissions": [
    "deep-link:default",
    "opener:default",
    "store:default"
  ]
}
```

## Opener Plugin for System Browser

On mobile, Google blocks OAuth from WebViews. Use the `opener` plugin to launch the system browser (Chrome Custom Tabs on Android, Safari on iOS).

**Important:** The `shell` plugin's `open` command does NOT work on Android:
```
Scoped shell IO error: No such file or directory (os error 2)
```

Use `opener` plugin (v2.3.0+) instead:

```typescript
import { openUrl } from '@tauri-apps/plugin-opener';

// Opens in Chrome Custom Tabs (Android) or Safari (iOS)
await openUrl(authUrl.toString());
```

## Hosted Callback Page

Host this on Firebase Hosting (or similar) at `/auth/callback/index.html`. The system browser loads this page after OAuth completes, then it redirects back to your app via deep link.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Authenticating...</title>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      background: #f5f5f5;
    }
    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #ddd;
      border-top-color: #4285f4;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    p { color: #666; margin-top: 16px; }
    .error { color: #d32f2f; }
    .fallback { margin-top: 24px; }
    .fallback a {
      color: #4285f4;
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="spinner" id="spinner"></div>
  <p id="status">Redirecting to app...</p>
  <div class="fallback" id="fallback" style="display: none;">
    <p>If the app doesn't open automatically:</p>
    <a id="manual-link" href="#">Open App Manually</a>
  </div>

  <script>
    (function() {
      const fragment = window.location.hash.substring(1);
      const params = new URLSearchParams(fragment);

      // Check for errors
      const error = params.get('error');
      if (error) {
        document.getElementById('spinner').style.display = 'none';
        document.getElementById('status').textContent =
          params.get('error_description') || 'Authentication failed';
        document.getElementById('status').className = 'error';
        return;
      }

      // Get state to find the continue URI
      const state = params.get('state');
      let continueUri = 'myapp://auth/callback';

      if (state) {
        try {
          const stateObj = JSON.parse(decodeURIComponent(state));
          continueUri = stateObj.continueUri || continueUri;
        } catch (e) {
          console.error('Failed to parse state:', e);
        }
      }

      // Build deep link URL with tokens as query params
      // WARNING: Tokens in URL may be logged. See PKCE section for alternative.
      const deepLinkUrl = new URL(continueUri);

      const idToken = params.get('id_token');
      const accessToken = params.get('access_token');

      if (idToken) deepLinkUrl.searchParams.set('id_token', idToken);
      if (accessToken) deepLinkUrl.searchParams.set('access_token', accessToken);
      if (state) deepLinkUrl.searchParams.set('state', state);

      const finalUrl = deepLinkUrl.toString();

      // Set up manual fallback link
      document.getElementById('manual-link').href = finalUrl;

      // Try to redirect to app
      window.location.href = finalUrl;

      // Show fallback after delay if still on page
      setTimeout(function() {
        document.getElementById('fallback').style.display = 'block';
      }, 2000);
    })();
  </script>
</body>
</html>
```

## Firebase Hosting Configuration

```json
{
  "hosting": {
    "public": "public",
    "rewrites": [
      {
        "source": "/auth/callback",
        "destination": "/auth/callback/index.html"
      }
    ],
    "headers": [
      {
        "source": "/auth/**",
        "headers": [
          { "key": "Cache-Control", "value": "no-store" },
          { "key": "X-Content-Type-Options", "value": "nosniff" }
        ]
      }
    ]
  }
}
```

## Apple Sign-In

For iOS, Apple Sign-In follows a similar pattern but requires additional configuration.

### App Store Connect Setup

1. Register App ID with "Sign in with Apple" capability
2. Create Services ID for web authentication
3. Configure domains and redirect URLs

### Implementation

```typescript
// src/utils/oauth-apple.ts
import { openUrl } from '@tauri-apps/plugin-opener';
import { getAuthConfig } from '../config/auth';
import { saveOAuthState, OAuthState } from './oauth-state';

export async function initiateAppleSignIn(): Promise<void> {
  const config = getAuthConfig();
  const nonce = crypto.randomUUID();

  const oauthState: OAuthState = {
    continueUri: `${config.appScheme}://auth/callback`,
    nonce,
    timestamp: Date.now(),
    provider: 'apple',
  };

  await saveOAuthState(oauthState);

  const state = encodeURIComponent(JSON.stringify(oauthState));

  const authUrl = new URL('https://appleid.apple.com/auth/authorize');
  authUrl.searchParams.set('client_id', config.appleClientId); // Your Services ID
  authUrl.searchParams.set('redirect_uri', config.callbackUrl);
  authUrl.searchParams.set('response_type', 'code id_token');
  authUrl.searchParams.set('scope', 'name email');
  authUrl.searchParams.set('response_mode', 'fragment');
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('nonce', nonce);

  try {
    await openUrl(authUrl.toString());
  } catch (error) {
    await clearOAuthState();
    throw new OAuthError('Failed to open Apple Sign-In', 'OPEN_URL_FAILED');
  }
}
```

### Firebase Integration for Apple

```typescript
import { OAuthProvider, signInWithCredential } from 'firebase/auth';

export async function completeAppleSignIn(
  idToken: string,
  nonce: string
): Promise<void> {
  const auth = getAuth();
  const provider = new OAuthProvider('apple.com');
  const credential = provider.credential({
    idToken,
    rawNonce: nonce, // Must match nonce sent in auth request
  });

  await signInWithCredential(auth, credential);
}
```

### Apple-Specific Callback Handling

Apple may return user info (name, email) only on the first sign-in. Store this information:

```typescript
function handleAppleCallback(params: OAuthCallbackParams): void {
  // Apple returns user info as JSON in 'user' parameter (first sign-in only)
  const userParam = params.user;
  if (userParam) {
    try {
      const userInfo = JSON.parse(decodeURIComponent(userParam));
      // Store user info - won't be available on subsequent sign-ins
      localStorage.setItem('apple_user_info', JSON.stringify(userInfo));
    } catch (e) {
      console.warn('Failed to parse Apple user info');
    }
  }
}
```

## Complete Auth Context with Deep Link Listener

```typescript
// src/contexts/AuthContext.tsx
import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from 'react';
import { onOpenUrl } from '@tauri-apps/plugin-deep-link';
import {
  getAuth,
  onAuthStateChanged,
  signOut as firebaseSignOut,
  User,
} from 'firebase/auth';
import { initiateGoogleSignIn } from '../utils/oauth';
import { initiateAppleSignIn } from '../utils/oauth-apple';
import { handleOAuthCallback, OAuthError } from '../utils/oauth-callback';
import { clearOAuthState } from '../utils/oauth-state';
import type { AuthContextType } from '../types/auth';

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const auth = getAuth();

  const clearError = useCallback(() => setError(null), []);

  // Handle deep link callback
  const processCallback = useCallback(async (url: string) => {
    if (!url.includes('auth/callback')) return;

    setLoading(true);
    setError(null);

    try {
      await handleOAuthCallback(url);
      // Success - onAuthStateChanged will update user
    } catch (err) {
      const message = err instanceof OAuthError
        ? err.message
        : 'Authentication failed. Please try again.';
      setError(message);
      console.error('OAuth callback error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Listen for auth state changes
    const unsubscribeAuth = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      setLoading(false);
    });

    // Listen for deep link callbacks
    let unsubscribeDeepLink: (() => void) | undefined;

    onOpenUrl((urls) => {
      for (const url of urls) {
        processCallback(url);
      }
    }).then((unsub) => {
      unsubscribeDeepLink = unsub;
    });

    // Cleanup both listeners
    return () => {
      unsubscribeAuth();
      unsubscribeDeepLink?.();
    };
  }, [auth, processCallback]);

  const signInWithGoogle = useCallback(async () => {
    setError(null);
    setLoading(true);

    try {
      await initiateGoogleSignIn();
      // Note: loading stays true until callback is processed
    } catch (err) {
      setLoading(false);
      const message = err instanceof OAuthError
        ? err.message
        : 'Failed to start sign-in. Please try again.';
      setError(message);
    }
  }, []);

  const signInWithApple = useCallback(async () => {
    setError(null);
    setLoading(true);

    try {
      await initiateAppleSignIn();
    } catch (err) {
      setLoading(false);
      const message = err instanceof OAuthError
        ? err.message
        : 'Failed to start sign-in. Please try again.';
      setError(message);
    }
  }, []);

  const signOut = useCallback(async () => {
    setError(null);

    try {
      // Clear any pending OAuth state
      await clearOAuthState();
      await firebaseSignOut(auth);
    } catch (err) {
      setError('Failed to sign out. Please try again.');
    }
  }, [auth]);

  const value: AuthContextType = {
    user,
    loading,
    error,
    signInWithGoogle,
    signInWithApple,
    signOut,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

### Login Screen Usage

```typescript
// src/components/LoginScreen.tsx
import { useAuth } from '../contexts/AuthContext';

export function LoginScreen() {
  const { signInWithGoogle, signInWithApple, loading, error, clearError } = useAuth();

  return (
    <div className="login-screen">
      <h1>Welcome</h1>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      <button
        onClick={signInWithGoogle}
        disabled={loading}
      >
        {loading ? 'Signing in...' : 'Sign in with Google'}
      </button>

      <button
        onClick={signInWithApple}
        disabled={loading}
      >
        {loading ? 'Signing in...' : 'Sign in with Apple'}
      </button>
    </div>
  );
}
```

## Mobile-Specific Troubleshooting

| Problem | Solution |
|---------|----------|
| Shell plugin URL error | Use `opener` plugin instead of `shell:open` |
| Deep link not received | Check scheme in tauri.conf.json matches URL |
| Callback page not found | Ensure Firebase Hosting path matches redirect_uri |
| App not opening from browser | Verify deep-link plugin is initialized in lib.rs |
| Apple Sign-In fails | Verify Services ID and domain configuration |
| Token not in callback | Check response_type includes `token id_token` |
| CORS errors | Callback page must be on same domain as redirect_uri |
