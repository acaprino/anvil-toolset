# Framework integration patterns

> Source: official documentation for Next.js (`@next/third-parties` and `next/script`), React Router, WordPress action hooks, and common static site generators as of 2025-2026.

This reference covers per-framework patterns for installing GTM and the GA4 tag. For the snippet content itself and the Consent Mode v2 default block, see [`gtm-setup.md`](gtm-setup.md). For the legal/compliance layer that must precede any of these integrations, see [`gdpr-compliance-eu.md`](gdpr-compliance-eu.md).

## Vanilla HTML

The simplest case: every HTML page must contain the snippet. The two most common errors are forgetting pages and not centralizing the include.

### Single-page sites

Paste the head snippet and the noscript body snippet directly in the page source.

### Multi-page static sites without a build step

Use a server-side include if the host supports it (Apache SSI, Nginx SSI):

```html
<head>
  <!--#include virtual="/includes/head-tracking.html" -->
</head>
```

`/includes/head-tracking.html` then contains the Consent Mode v2 default, the CMP loader, and the GTM head snippet.

### Static site generators

Most static site generators have a layout / partial / template system that centralizes head injection.

**Jekyll**: edit `_includes/head.html` (or whatever the theme calls it) and add the snippet block.

**Hugo**: edit `layouts/partials/head.html` (or `layouts/_default/baseof.html` if the theme uses that pattern). Hugo also has a built-in Google Tag Manager partial - configure `googleTagManager` in `config.toml` and add `{{ template "_internal/google_tag_manager.html" . }}` to the head partial.

**Eleventy / 11ty**: edit `_includes/layout.njk` (or whatever your base layout is). Add the snippet directly in the head.

**Astro**: edit `src/layouts/Layout.astro` (or your base layout). The snippet goes inside `<head>`. Astro also has the `astro-google-analytics` and `@astrojs/partytown` integrations for cleaner installation.

**Gatsby**: use `gatsby-plugin-google-tagmanager` in `gatsby-config.js` for the simplest path. Manually, add the snippet to `html.js` (run `gatsby copy-html`).

After updating the template, rebuild the site and **verify with grep** that every output HTML file contains the GTM container ID:

```bash
grep -l "GTM-XXXXXXX" public/**/*.html
```

If any file is missing, the layout was not applied uniformly.

## Next.js

Next.js has the most refined integration story for GA4 and GTM thanks to the dedicated `@next/third-parties/google` package.

### App Router (Next.js 13.4+, recommended)

**Preferred approach**: use `@next/third-parties/google`:

```bash
npm install @next/third-parties
```

In `app/layout.tsx`:

```tsx
import { GoogleTagManager } from '@next/third-parties/google';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <head>
        {/* Consent Mode v2 default block - inline script before GTM */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('consent', 'default', {
                'ad_storage': 'denied',
                'ad_user_data': 'denied',
                'ad_personalization': 'denied',
                'analytics_storage': 'denied',
                'wait_for_update': 500
              });
            `,
          }}
        />
        {/* CMP loader - paste your CMP snippet here */}
      </head>
      <body>
        {children}
      </body>
      <GoogleTagManager gtmId="GTM-XXXXXXX" />
    </html>
  );
}
```

`<GoogleTagManager>` injects the GTM head snippet via `next/script` with an optimized loading strategy and adds the noscript iframe automatically. Place it inside `<html>` but after `<body>` to satisfy the noscript placement requirement.

**SPA route changes**: GA4 page_view events fire automatically when the GTM tag uses the Initialization - All Pages trigger and the Google Tag is configured to "Send a page view event when this configuration loads". For finer control, push virtual page views from a client component that listens to route changes:

```tsx
'use client';
import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

export function PageViewTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const url = pathname + (searchParams.toString() ? `?${searchParams.toString()}` : '');
    if (typeof window !== 'undefined' && (window as any).dataLayer) {
      (window as any).dataLayer.push({
        event: 'page_view',
        page_path: url,
      });
    }
  }, [pathname, searchParams]);

  return null;
}
```

Mount `<PageViewTracker />` once in `app/layout.tsx`.

### Pages Router (Next.js 12 and earlier, or legacy projects)

Use `next/script` with `strategy="afterInteractive"` in `pages/_app.tsx` or `pages/_document.tsx`:

```tsx
// pages/_document.tsx
import { Html, Head, Main, NextScript } from 'next/document';
import Script from 'next/script';

export default function Document() {
  return (
    <Html lang="it">
      <Head>
        <Script
          id="consent-mode-default"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('consent', 'default', {
                'ad_storage': 'denied',
                'ad_user_data': 'denied',
                'ad_personalization': 'denied',
                'analytics_storage': 'denied',
                'wait_for_update': 500
              });
            `,
          }}
        />
        {/* CMP loader */}
        <Script
          id="gtm-script"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
              new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
              j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
              'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
              })(window,document,'script','dataLayer','GTM-XXXXXXX');
            `,
          }}
        />
      </Head>
      <body>
        <noscript>
          <iframe
            src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
            height="0"
            width="0"
            style={{ display: 'none', visibility: 'hidden' }}
          />
        </noscript>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
```

For SPA route tracking in Pages Router, listen to `Router.events.routeChangeComplete` in `pages/_app.tsx`:

```tsx
import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function App({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    const handleRouteChange = (url) => {
      if (typeof window !== 'undefined' && (window as any).dataLayer) {
        (window as any).dataLayer.push({
          event: 'page_view',
          page_path: url,
        });
      }
    };
    router.events.on('routeChangeComplete', handleRouteChange);
    return () => router.events.off('routeChangeComplete', handleRouteChange);
  }, [router.events]);

  return <Component {...pageProps} />;
}
```

## React (CRA, Vite, non-Next)

For Create React App, Vite, or any React app served as a SPA:

### Static placement

Add the snippet directly to `public/index.html` (CRA) or `index.html` (Vite). Same Consent Mode v2 default + CMP + GTM head order in `<head>`, GTM noscript iframe after `<body>`.

### SPA route tracking with React Router

```tsx
// src/components/PageViewTracker.tsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export function PageViewTracker() {
  const location = useLocation();

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).dataLayer) {
      (window as any).dataLayer.push({
        event: 'page_view',
        page_path: location.pathname + location.search,
      });
    }
  }, [location]);

  return null;
}
```

Mount once inside `<BrowserRouter>` at the top of the component tree.

### React Strict Mode double-firing

In development, React Strict Mode double-invokes effects, which can cause `page_view` events to fire twice. This only happens in development - production builds don't have this behavior. Verify with the GA4 DebugView in production rather than dev.

## WordPress

WordPress has multiple deployment paths. Pick based on the user's technical comfort and the existing site setup.

### Approach A: theme `functions.php` action hook (technical)

Add to the active theme's `functions.php` (or better, a child theme's `functions.php`):

```php
function add_gtm_head() {
    ?>
    <!-- Consent Mode v2 defaults -->
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('consent', 'default', {
        'ad_storage': 'denied',
        'ad_user_data': 'denied',
        'ad_personalization': 'denied',
        'analytics_storage': 'denied',
        'wait_for_update': 500
      });
    </script>

    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
    <!-- End Google Tag Manager -->
    <?php
}
add_action('wp_head', 'add_gtm_head', 1);

function add_gtm_body() {
    ?>
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <!-- End Google Tag Manager (noscript) -->
    <?php
}
add_action('wp_body_open', 'add_gtm_body');
```

The priority `1` on `wp_head` ensures the snippet runs early. `wp_body_open` was added in WordPress 5.2 - older themes may not call it; in that case edit `header.php` directly to add the noscript right after `<body>`.

### Approach B: header.php direct edit (simple)

Edit the theme's `header.php` and paste the snippets in the right places. This works but is fragile - theme updates can overwrite changes. Use a child theme or move to Approach A.

### Approach C: plugins (non-technical)

For non-technical users, plugins handle the entire installation:

- **Site Kit by Google**: official Google plugin. Connects to GA4, Search Console, AdSense, PageSpeed Insights with a guided setup. Limited to standard configurations.
- **GTM4WP**: dedicated GTM plugin with rich dataLayer integration (WooCommerce events, Contact Form 7, Gravity Forms, scroll depth, video tracking). The most powerful option for serious GTM work on WordPress.
- **WP Cookie Notice / Complianz / iubenda for WordPress**: CMP plugins. Complianz is the most-used native WP CMP. Iubenda has an official WP plugin that handles the embed and Consent Mode v2.

The CMP plugin and the GTM plugin must be coordinated so the CMP fires Consent Mode v2 updates that GTM listens for.

### WordPress caching gotcha

WordPress caching plugins (W3 Total Cache, WP Rocket, LiteSpeed Cache, WP Super Cache) can strip or rewrite the GTM snippet, especially when HTML minification or "delay JavaScript execution" features are enabled. After deploying GTM, **always** flush the cache and verify the snippet still appears in the page source from the front-end (incognito).

If the cache plugin offers a "do not minify" or "exclude from delay" list, add `googletagmanager.com` and `gtm.js` to it.

## Server-side rendered apps (Rails, Django, Laravel, etc.)

Same pattern as WordPress: insert the snippet in the base layout template (Rails `application.html.erb`, Django `base.html`, Laravel Blade `app.blade.php`). The Consent Mode v2 default block, the CMP loader, and the GTM head snippet go in the head; the GTM noscript iframe goes after the opening body tag.

For SPAs hydrated from a server-rendered shell (Hotwire / Turbo / Inertia / Livewire), check that route changes do not skip page_view events. With Turbo, listen to the `turbo:load` event and push a virtual page_view to the dataLayer.

## Server-side GTM (sGTM)

Out of scope for this skill. Server-side GTM is a separate Google Cloud deployment that proxies tag requests through a first-party domain, improving cookie persistence and giving more control over data sent to vendors. It is appropriate for high-traffic sites with privacy-engineering requirements. For standard small business deployments, client-side GTM is sufficient.

If the user asks about sGTM, point them to Google's official Server-side tagging documentation.

## Common framework pitfalls

- **Hydration mismatch warnings (Next.js, React)**: caused by `dangerouslySetInnerHTML` differences between server and client render. Use `next/script` or `@next/third-parties/google` instead of inline `<script>` to avoid this.
- **Double-firing in React Strict Mode (development only)**: events fire twice in dev because effects run twice. Production builds are unaffected. Verify in production with DebugView.
- **Caching plugins stripping snippets (WordPress)**: always flush and re-verify after enabling or updating cache plugins.
- **Build-time inlining vs runtime injection (Next.js)**: `strategy="beforeInteractive"` only works in `_document.tsx`, not in pages or app components. The Consent Mode default block needs to run before GTM, so it must be `beforeInteractive` in Pages Router or inline in the head in App Router.
- **Static export (Next.js `next export`)**: works with GTM via the same `next/script` patterns. Verify the snippet appears in the exported HTML files.
- **Theme updates overwriting changes (WordPress)**: always use a child theme or `functions.php` action hooks rather than editing parent theme files directly.
- **Multiple GA4 properties / containers in the same project**: keep one property and one container per environment. Mixing dev and prod IDs causes confusing data corruption.
