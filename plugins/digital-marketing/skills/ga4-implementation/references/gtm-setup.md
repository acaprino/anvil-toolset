# GTM setup walkthrough

> Source: Google Tag Manager and GA4 official documentation as of 2025-2026, plus the recommended snippet ordering for Consent Mode v2 compatibility.

This reference walks through the entire path from creating a GA4 property to publishing the first version of a GTM container with the GA4 tag firing correctly. Read [`gdpr-compliance-eu.md`](gdpr-compliance-eu.md) first if the site does not yet have a working CMP - GTM should not be deployed without one.

## Why GTM, not gtag.js direct

The official Google documentation as of March 2026 recommends GTM for any deployment by a non-developer: "If you're unfamiliar with javascript, we recommend using Google Tag Manager instead of gtag.js." Even on a small static HTML site, GTM is the better choice for three concrete reasons:

1. **Consent Mode v2 is dramatically easier with GTM** thanks to CMP templates in the Community Template Gallery and the GTM debug tools that show consent state per tag fire
2. **Future Google Ads work needs zero code changes** - conversion tags, remarketing tags, Floodlight tags can all be configured from the GTM web UI without touching the site source
3. **For non-developer site owners**, after the initial setup all tracking changes happen in the GTM web UI, not in the codebase

The exceptions where gtag.js direct can be acceptable: a developer-only project with strong reasons to avoid extra script tags, a single-tag deployment that will never grow, or a tightly controlled landing page where every byte matters. In every other case, default to GTM.

## Step 1: create the GA4 property

1. Sign in at [analytics.google.com](https://analytics.google.com) with the Google account that should own the property
2. Click "Start Measuring" or Admin > + Create > Account
3. Account name: a name that represents the business or property owner
4. Create a property: name, time zone (e.g. "(GMT+01:00) Rome"), currency (EUR for Italian sites)
5. Business details: industry and size
6. Accept the Terms of Service, **selecting Italy (or the relevant EU country)** so the EU-specific terms apply
7. Accept the **Data Processing Terms** in Admin > Account Settings - this satisfies the Art. 28 GDPR DPA requirement with Google
8. Choose platform "Web", enter the site URL, name the stream (e.g. "Main Website"), leave Enhanced Measurement enabled
9. Click "Create stream"
10. On the "Web Stream Details" page, **copy the Measurement ID** (format: `G-XXXXXXXXXX`) shown in the top right - this is what GTM will use

## Step 2: configure GA4 account-level settings

Before moving to GTM, lock down the account-level configuration that affects compliance and data quality:

- **Admin > Data Collection and Modification > Data Retention**: set to 14 months (or 2 months for max compliance), enable "Reset user data on new activity"
- **Admin > Data Settings > Data Collection**: **disable Google Signals** for EEA properties
- **Admin > Data Display > Attribution Settings**: confirm data-driven attribution model, set lookback window appropriate for the business cycle (90 days for travel/hospitality, 30 days for ecommerce)

## Step 3: create the GTM account and container

1. Sign in at [tagmanager.google.com](https://tagmanager.google.com)
2. Click "Create Account"
3. Account name: same as the GA4 account (or the business name), Country: Italy (or the relevant country)
4. Container name: the site domain (e.g. `example.com`), platform: Web
5. Accept the Terms of Service
6. GTM immediately shows the two snippets to install on the site

## Step 4: install the GTM snippets

GTM provides **two snippets** that must be present on **every page** of the site.

**Snippet 1 - in `<head>`, as high as possible**:

```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
<!-- End Google Tag Manager -->
```

**Snippet 2 - immediately after the opening `<body>` tag**:

```html
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
```

### Snippet ordering with Consent Mode v2

If the CMP does not auto-handle Consent Mode v2 defaults (iubenda does), insert the default block **before** the GTM head snippet. The complete `<head>` order is:

1. Consent Mode v2 default block (sets all signals to `denied`, `wait_for_update: 500`)
2. CMP loader (iubenda embed, Cookiebot autoblock script, Orestbida config)
3. GTM head snippet

A complete page template:

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <!-- Consent Mode v2 defaults (skip if your CMP handles this automatically) -->
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

  <!-- CMP loader (paste your CMP snippet here) -->
  <!-- Example: iubenda Cookie Solution embed code -->

  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
  <!-- End Google Tag Manager -->

  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Site Title</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->

  <!-- Page content -->
</body>
</html>
```

For frameworks (Next.js, React, WordPress) instead of vanilla HTML, see [`framework-integration.md`](framework-integration.md).

**Replace `GTM-XXXXXXX`** with the actual container ID from the GTM web UI.

## Step 5: configure the GA4 Google Tag inside GTM

1. In GTM, click Tags > New
2. Tag name: `Google Tag | GA4` (or similar descriptive name)
3. Click Tag Configuration > select **Google Tag** (not "Google Analytics: GA4 Configuration" - the older type still exists but Google Tag is the current recommendation)
4. In the Tag ID field, paste the GA4 Measurement ID copied earlier (`G-XXXXXXXXXX`)
5. In the Triggering section, click the trigger area and select **"Initialization - All Pages"** (NOT "All Pages")
6. Save

**Why "Initialization - All Pages" instead of "All Pages"**: the Initialization trigger fires before all other triggers, which is critical for Consent Mode compatibility - the Google tag must initialize before any tag that depends on consent state.

## Step 6: test in Preview mode

1. Click "Preview" in the top right of GTM
2. Enter the site URL
3. Tag Assistant connects to the site in a new window with debug mode enabled
4. Browse the site - in the Tag Assistant panel verify the Google tag is "fired" with the correct Measurement ID
5. Switch back to GA4 > Admin > DebugView and verify events arrive in real time with the correct parameters

## Step 7: publish the container

1. Click "Submit" in the top right of GTM
2. Version name: descriptive (e.g. "GA4 setup iniziale")
3. Version description: short summary of what the version does
4. Click "Publish"

From this point on, GA4 is active on the site - subordinate to user consent via the CMP.

## Verification

Run all of these checks after publishing:

### 1. GA4 Realtime report

Admin > Reports > Realtime. Open the site in an **incognito window** without an ad blocker. Within 1-2 minutes the active user, page_view events, and visited page titles should appear.

If nothing appears after 5 minutes:
- Check the source HTML in the browser's view-source for the snippet
- Check DevTools > Network > filter `collect` for outgoing requests
- Check that the user accepted analytics cookies in the CMP banner
- Check that the Measurement ID in the GTM tag matches the one in GA4 > Admin > Data Streams

### 2. Google Tag Assistant

Open [tagassistant.google.com](https://tagassistant.google.com), enter the site URL, click Connect. The site opens with a debug banner. In the Tag Assistant tab verify that:

- The Google tag with the correct Measurement ID shows as "fired"
- The container ID matches the GTM container
- Consent state is reported correctly per signal

### 3. GA4 DebugView

In GA4, go to Admin > DebugView. The simplest way to enable it is to use Tag Assistant (it activates DebugView automatically) or to click Preview in GTM. DebugView shows every event in real time with all its parameters - useful for verifying that custom events fire with the right parameter values.

### 4. DevTools Network filter

Open DevTools > Network tab > filter for `collect`. Verify:

- Requests go to `google-analytics.com/g/collect`
- The `tid` parameter equals the Measurement ID
- The `en` parameter equals the event name (e.g. `page_view`, `book_now_click`)
- No duplicate requests for the same event from the same page (would indicate double tracking)

### 5. Tag Coverage report

GA4 > Admin > Data Streams > select the stream > Tag Coverage. Once Google has crawled the site, this report shows which pages are detected to have the tag. A page missing here is a page where the snippet is not installed - the most common static-site error.

### Standard reports timeline

The Realtime report works immediately after the first event. **Standard GA4 reports** (Acquisition, Engagement, etc.) take **24-48 hours** to populate after the initial installation. Do not panic if Reports > Engagement > Pages and Screens is empty for the first day - check Realtime instead.

## Container backups and version control

GTM containers can be exported as JSON for backup and version control:

1. Admin > Containers > Export Container
2. Choose the workspace and version
3. Save the JSON file in the project repository (e.g. `gtm-backup-YYYY-MM-DD.json`)

To restore: Admin > Containers > Import Container > select the JSON > choose Overwrite or Merge.

This is good practice before major changes and useful for migrating containers between staging and production environments.

## Environment workflows

For sites with staging and production environments, GTM supports **environments**:

1. Admin > Environments > New
2. Create "Staging" and "Production" environments
3. Each environment has its own snippet variant (with `&environment_auth=...` parameters)
4. The staging snippet goes on the staging site, the production snippet on the production site
5. Publish a container version to a specific environment first to test, then promote to production

For small sites this is overkill - most can publish directly to the default environment. For larger sites with multiple stakeholders or strict change control, environments are valuable.

## Common installation errors

See [`diagnostics-troubleshooting.md`](diagnostics-troubleshooting.md) for the full troubleshooting checklist. The most frequent installation errors are:

1. **Snippet on only `index.html`** - missing from other pages of the site
2. **Both gtag.js and GTM injecting the same Measurement ID** - causes silent double tracking
3. **Snippet inside a div or after `</head>`** - loses early page interactions
4. **Smart quotes from a word processor** breaking the script
5. **Wrong trigger type** - "All Pages" instead of "Initialization - All Pages" for the Google tag
